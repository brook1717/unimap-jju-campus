import logging

import networkx as nx
from django.core.cache import cache
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_gis.pagination import GeoJsonPagination

from locations.models import CampusLocation
from unimap_backend.exceptions import error_response
from .models import CampusPath
from .serializers import CampusPathSerializer
from .services import PathfindingService

logger = logging.getLogger(__name__)

WALKING_SPEED_MS = 1.4      # m/s — average pedestrian pace
ROUTE_CACHE_TTL  = 60 * 15  # 15-minute route cache (LocMemCache by default)
CAMPUS_BOUND_M   = 500.0    # reject if nearest path node is further than this


def _loc_stub(loc) -> dict:
    return {'id': loc.id, 'name': loc.name, 'slug': loc.slug}


def _route_properties(
    start_loc, end_loc,
    total_dist_m: float,
    path_node_count: int,
    start_snap_m: float,
    end_snap_m: float,
) -> dict:
    walking_s   = total_dist_m / WALKING_SPEED_MS
    walking_min = walking_s / 60.0
    return {
        'start_location':             _loc_stub(start_loc),
        'end_location':               _loc_stub(end_loc),
        'total_distance_m':           round(total_dist_m, 1),
        'estimated_walking_time_s':   round(walking_s),
        'estimated_walking_time_min': round(walking_min, 1),
        'path_node_count':            path_node_count,
        'snap_distance_start_m':      round(start_snap_m, 1),
        'snap_distance_end_m':        round(end_snap_m, 1),
    }


class CampusPathViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        CampusPath.objects
        .select_related('start_location', 'end_location')
        .all()
    )
    serializer_class = CampusPathSerializer
    pagination_class = GeoJsonPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_accessible', 'start_location', 'end_location']


@extend_schema(
    parameters=[
        OpenApiParameter(
            'start_location_id', OpenApiTypes.INT, OpenApiParameter.QUERY,
            required=True,
            description='Primary key of the starting CampusLocation.',
        ),
        OpenApiParameter(
            'end_location_id', OpenApiTypes.INT, OpenApiParameter.QUERY,
            required=True,
            description='Primary key of the destination CampusLocation.',
        ),
    ],
    description=(
        'Calculate the shortest walking route between two campus buildings using '
        'A* (NetworkX) on the pre-built topology graph.\n\n'
        '**Same location**: returns a zero-distance Point feature.\n'
        '**Outside campus** (nearest path node > 500 m): returns 400.\n'
        'Results are cached for 15 minutes per unique start/end pair.'
    ),
    responses={
        200: {'description': 'GeoJSON Feature (LineString or Point) with distance and walking time.'},
        400: {'description': 'Missing / invalid parameters or location outside campus bounds.'},
        404: {'description': 'Location not found, inactive, or no path exists.'},
    },
)
class DirectionsView(APIView):
    """
    GET /api/routing/directions/?start_location_id=X&end_location_id=Y

    Special cases
    -------------
    start == end  → 200, Point geometry, distance 0
    snap > 500 m  → 400, location outside campus bounds
    No A* path    → 404, "No walking path found between these locations."
    """

    def get(self, request):
        start_raw = request.query_params.get('start_location_id')
        end_raw   = request.query_params.get('end_location_id')

        # ── 1. Param validation ───────────────────────────────────────────────
        if not start_raw or not end_raw:
            return error_response(
                'start_location_id and end_location_id are required.',
                400,
            )

        try:
            start_int = int(start_raw)
            end_int   = int(end_raw)
        except ValueError:
            return error_response(
                'start_location_id and end_location_id must be integers.',
                400,
            )

        # ── 2. Same-location short-circuit → 200 Point, distance 0 ──────────
        if start_int == end_int:
            try:
                loc = CampusLocation.objects.get(pk=start_int, is_active=True)
            except CampusLocation.DoesNotExist:
                return error_response('Location not found or inactive.', 404)

            logger.debug('Same-location request for pk=%d (%s)', loc.id, loc.name)
            return Response({
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [loc.point.x, loc.point.y],
                },
                'properties': _route_properties(loc, loc, 0.0, 1, 0.0, 0.0),
            })

        # ── 3. Cache lookup ───────────────────────────────────────────────────
        cache_key = f'directions_{start_int}_{end_int}'
        cached = cache.get(cache_key)
        if cached is not None:
            logger.debug('Cache hit: route %d->%d', start_int, end_int)
            return Response(cached)

        # ── 4. Fetch locations ────────────────────────────────────────────────
        try:
            start_loc = CampusLocation.objects.get(pk=start_int, is_active=True)
            end_loc   = CampusLocation.objects.get(pk=end_int,   is_active=True)
        except CampusLocation.DoesNotExist:
            return error_response(
                'One or both locations were not found or are inactive.',
                404,
            )

        # ── 5. Snap to graph ──────────────────────────────────────────────────
        # Prefer entrance_point (the actual walkable entrance) when available;
        # fall back to the building centroid (point).
        start_pt = start_loc.entrance_point or start_loc.point
        end_pt   = end_loc.entrance_point   or end_loc.point

        if start_pt is None or end_pt is None:
            return error_response(
                'One or both locations are missing coordinate data. '
                'No route found.',
                404,
                'NoRouteFound',
            )

        svc = PathfindingService()
        start_node, start_snap_m = svc.find_nearest_node(
            start_pt.x, start_pt.y
        )
        end_node, end_snap_m = svc.find_nearest_node(
            end_pt.x, end_pt.y
        )

        # Boundary guard: reject locations that are too far from any path.
        if start_snap_m > CAMPUS_BOUND_M:
            return error_response(
                f'"{start_loc.name}" appears to be outside campus path bounds '
                f'({start_snap_m:.0f} m from the nearest path node).',
                400,
                'OutsideCampusBounds',
            )
        if end_snap_m > CAMPUS_BOUND_M:
            return error_response(
                f'"{end_loc.name}" appears to be outside campus path bounds '
                f'({end_snap_m:.0f} m from the nearest path node).',
                400,
                'OutsideCampusBounds',
            )

        # ── 6. A* routing ─────────────────────────────────────────────────────
        try:
            path_nodes, total_dist_m, route_coords = svc.calculate_route(
                start_node, end_node
            )
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return error_response(
                'No walking path found between these locations.',
                404,
                'NoPathFound',
            )

        # ── 7. Build, cache, and return ───────────────────────────────────────
        result = {
            'type': 'Feature',
            'geometry': {
                'type': 'LineString',
                'coordinates': route_coords,
            },
            'properties': _route_properties(
                start_loc, end_loc,
                total_dist_m, len(path_nodes),
                start_snap_m, end_snap_m,
            ),
        }

        cache.set(cache_key, result, ROUTE_CACHE_TTL)
        logger.debug(
            'Route %d->%d computed and cached (%.1f m)',
            start_int, end_int, total_dist_m,
        )
        return Response(result)
