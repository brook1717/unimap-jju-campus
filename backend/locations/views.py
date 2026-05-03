import logging

from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.db.models import Case, IntegerField, Q, Value, When
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework_gis.pagination import GeoJsonPagination

from unimap_backend.exceptions import error_response
from .models import CampusLocation
from .serializers import CampusLocationSerializer

logger = logging.getLogger(__name__)

# ── Spelling normalization ───────────────────────────────────────────────────
# Common misspelling pairs.  When one variant is searched, we also check the
# other so that "Jijiga University" still finds "Jigjiga University" results.
SPELLING_VARIANTS = {
    'jijiga': 'jigjiga',
    'jigjiga': 'jijiga',
}


def _expand_query(q: str) -> list[str]:
    """Return a list of query variants (original + any misspelling expansions)."""
    queries = [q]
    q_lower = q.lower()
    for wrong, correct in SPELLING_VARIANTS.items():
        if wrong in q_lower:
            queries.append(q_lower.replace(wrong, correct))
    return queries


class CampusLocationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        CampusLocation.objects
        .filter(is_active=True)
        .prefetch_related('facilities')
    )
    serializer_class = CampusLocationSerializer
    pagination_class = GeoJsonPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['category']
    # Search across name, category value, and description — all case-insensitive
    search_fields = ['name', 'category', 'description']

    def get_queryset(self):
        """
        Extend the base queryset to rank search results by exactness when a
        ?search= query is present:
          0 — exact name match  (Library)
          1 — name starts with  (Lib…)
          2 — partial / category / description match
        Also expands common misspelling variants (e.g. Jijiga ↔ Jigjiga)
        so both spellings surface results.
        """
        qs = super().get_queryset()
        q  = self.request.query_params.get('search', '').strip()
        if q:
            # Expand misspelling variants and build an OR filter across all
            variants = _expand_query(q)
            variant_q = Q()
            for v in variants:
                variant_q |= (
                    Q(name__icontains=v) |
                    Q(category__icontains=v) |
                    Q(description__icontains=v)
                )
            qs = qs.filter(variant_q).annotate(
                _search_rank=Case(
                    When(name__iexact=q,       then=Value(0)),
                    When(name__istartswith=q,  then=Value(1)),
                    default=Value(2),
                    output_field=IntegerField(),
                )
            ).order_by('_search_rank', 'name')
        return qs

    # ── autocomplete ──────────────────────────────────────────────────────────

    @extend_schema(
        parameters=[
            OpenApiParameter(
                'q', OpenApiTypes.STR, OpenApiParameter.QUERY,
                required=False,
                description='Partial name to match (case-insensitive). Returns up to 20 results.',
            ),
        ],
        description=(
            'Lightweight suggestion list for a frontend search box. '
            'Returns `[{id, name, slug, category}, …]` — no geometry, no pagination.'
        ),
    )
    @action(detail=False, methods=['get'], url_path='autocomplete')
    def autocomplete(self, request):
        """
        GET /api/locations/autocomplete/?q=lib
        Returns up to 20 {id, name, slug, category} dicts for instant suggestions.
        No pagination, no geometry — designed for fast typeahead.
        """
        q  = request.query_params.get('q', '').strip()
        qs = CampusLocation.objects.filter(is_active=True)
        if q:
            # Expand misspelling variants for autocomplete too
            variants = _expand_query(q)
            name_q = Q()
            for v in variants:
                name_q |= Q(name__icontains=v)
            qs = qs.filter(name_q).annotate(
                _rank=Case(
                    When(name__iexact=q,      then=Value(0)),
                    When(name__istartswith=q, then=Value(1)),
                    default=Value(2),
                    output_field=IntegerField(),
                )
            ).order_by('_rank', 'name')
        else:
            qs = qs.order_by('name')

        data = list(qs.values('id', 'name', 'slug', 'category')[:20])
        logger.debug('Autocomplete q=%r → %d result(s)', q, len(data))
        return Response(data)

    # ── nearest ───────────────────────────────────────────────────────────────

    @extend_schema(
        parameters=[
            OpenApiParameter(
                'lat', OpenApiTypes.FLOAT, OpenApiParameter.QUERY,
                required=True,
                description='Latitude of the reference coordinate (WGS 84).',
            ),
            OpenApiParameter(
                'lng', OpenApiTypes.FLOAT, OpenApiParameter.QUERY,
                required=True,
                description='Longitude of the reference coordinate (WGS 84).',
            ),
        ],
        description=(
            'Returns the single nearest **active** CampusLocation to the '
            'supplied coordinate, ranked by PostGIS geodesic distance.'
        ),
    )
    @action(detail=False, methods=['get'], url_path='nearest')
    def nearest(self, request):
        """
        GET /api/locations/nearest/?lat=<float>&lng=<float>
        Returns the single nearest active CampusLocation to the given coordinate.
        """
        lat_raw = request.query_params.get('lat')
        lng_raw = request.query_params.get('lng')

        if not lat_raw or not lng_raw:
            return error_response('lat and lng query parameters are required.', 400)

        try:
            lat = float(lat_raw)
            lng = float(lng_raw)
        except ValueError:
            return error_response('lat and lng must be valid decimal numbers.', 400)

        ref_point = Point(lng, lat, srid=4326)

        location = (
            CampusLocation.objects
            .filter(is_active=True)
            .prefetch_related('facilities')
            .annotate(distance=Distance('point', ref_point))
            .order_by('distance')
            .first()
        )

        if location is None:
            return error_response('No active locations found.', 404)

        serializer = self.get_serializer(location)
        return Response(serializer.data)
