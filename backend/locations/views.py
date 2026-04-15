from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.response import Response

from .models import CampusLocation
from .serializers import CampusLocationSerializer


class CampusLocationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        CampusLocation.objects
        .filter(is_active=True)
        .prefetch_related('facilities')
    )
    serializer_class = CampusLocationSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['category']
    search_fields = ['name', 'description']

    @action(detail=False, methods=['get'], url_path='nearest')
    def nearest(self, request):
        """
        GET /api/locations/nearest/?lat=<float>&lng=<float>
        Returns the single nearest active CampusLocation to the given coordinate.
        """
        lat_raw = request.query_params.get('lat')
        lng_raw = request.query_params.get('lng')

        if not lat_raw or not lng_raw:
            return Response(
                {'detail': 'lat and lng query parameters are required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            lat = float(lat_raw)
            lng = float(lng_raw)
        except ValueError:
            return Response(
                {'detail': 'lat and lng must be valid decimal numbers.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

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
            return Response(
                {'detail': 'No active locations found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.get_serializer(location)
        return Response(serializer.data)
