from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter

from .models import CampusLocation
from .serializers import CampusLocationSerializer


class CampusLocationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CampusLocation.objects.all()
    serializer_class = CampusLocationSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['category']
    search_fields = ['name', 'description']
