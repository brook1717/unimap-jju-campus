from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend

from .models import Facility
from .serializers import FacilitySerializer


class FacilityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Facility.objects.select_related('location').all()
    serializer_class = FacilitySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['location']
