import networkx as nx
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_gis.pagination import GeoJsonPagination

from locations.models import CampusLocation
from .models import CampusPath
from .serializers import CampusPathSerializer
from .services import PathfindingService

WALKING_SPEED_MS = 1.4   # metres per second (average pedestrian pace)


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
        'A* (NetworkX) on the pre-built topology graph. '
        'Returns a GeoJSON Feature with a LineString geometry and route metadata.'
    ),
    responses={
        200: {
            'description': 'GeoJSON Feature — LineString route with distance and walking time.',
        },
        400: {'description': 'Missing or invalid query parameters.'},
        404: {'description': 'Location not found or no path exists between the two points.'},
    },
)
class DirectionsView(APIView):
    """
    GET /api/routing/directions/?start_location_id=X&end_location_id=Y

    1. Look up CampusLocation for X and Y (must be is_active).
    2. Find the nearest graph node to each location coordinate.
    3. Run A* via PathfindingService.
    4. Return a GeoJSON Feature (LineString) with distance + walking time.
    """

    def get(self, request):
        start_id_raw = request.query_params.get('start_location_id')
        end_id_raw   = request.query_params.get('end_location_id')

        if not start_id_raw or not end_id_raw:
            return Response(
                {'detail': 'start_location_id and end_location_id are required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            start_int = int(start_id_raw)
            end_int   = int(end_id_raw)
        except ValueError:
            return Response(
                {'detail': 'start_location_id and end_location_id must be integers.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if start_int == end_int:
            return Response(
                {'detail': 'start_location_id and end_location_id must be different.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            start_loc = CampusLocation.objects.get(pk=start_int, is_active=True)
            end_loc   = CampusLocation.objects.get(pk=end_int,   is_active=True)
        except CampusLocation.DoesNotExist:
            return Response(
                {'detail': 'One or both locations were not found or are inactive.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        svc = PathfindingService()

        start_node, start_snap_m = svc.find_nearest_node(
            start_loc.point.x, start_loc.point.y
        )
        end_node, end_snap_m = svc.find_nearest_node(
            end_loc.point.x, end_loc.point.y
        )

        try:
            path_nodes, total_dist_m, route_coords = svc.calculate_route(
                start_node, end_node
            )
        except nx.NetworkXNoPath:
            return Response(
                {'detail': 'No connected path exists between the two locations.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        except nx.NodeNotFound:
            return Response(
                {'detail': 'Graph node not found — topology may need to be rebuilt.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        walking_time_s   = total_dist_m / WALKING_SPEED_MS
        walking_time_min = walking_time_s / 60.0

        return Response(
            {
                'type': 'Feature',
                'geometry': {
                    'type': 'LineString',
                    'coordinates': route_coords,
                },
                'properties': {
                    'start_location': {
                        'id':   start_loc.id,
                        'name': start_loc.name,
                        'slug': start_loc.slug,
                    },
                    'end_location': {
                        'id':   end_loc.id,
                        'name': end_loc.name,
                        'slug': end_loc.slug,
                    },
                    'total_distance_m':        round(total_dist_m, 1),
                    'estimated_walking_time_s': round(walking_time_s),
                    'estimated_walking_time_min': round(walking_time_min, 1),
                    'path_node_count':          len(path_nodes),
                    'snap_distance_start_m':    round(start_snap_m, 1),
                    'snap_distance_end_m':      round(end_snap_m, 1),
                },
            },
            status=status.HTTP_200_OK,
        )
