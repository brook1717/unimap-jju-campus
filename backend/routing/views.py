from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_gis.pagination import GeoJsonPagination

from .models import CampusPath
from .serializers import CampusPathSerializer


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


class RouteView(APIView):
    """
    GET /api/routing/route/?start=<id>&end=<id>
    Returns the shortest walking path between two campus locations.
    Implementation deferred to routing services.py.
    """

    def get(self, request):
        return Response(
            {'detail': 'Routing engine not yet implemented.'},
            status=status.HTTP_501_NOT_IMPLEMENTED,
        )
