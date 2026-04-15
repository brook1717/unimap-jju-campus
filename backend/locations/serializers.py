from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from facilities.models import Facility
from .models import CampusLocation


class FacilityBriefSerializer(serializers.ModelSerializer):
    """Compact facility representation used when nested inside a location feature."""

    class Meta:
        model = Facility
        fields = ('id', 'name', 'description', 'image')


class CampusLocationSerializer(GeoFeatureModelSerializer):
    facilities = FacilityBriefSerializer(many=True, read_only=True)

    class Meta:
        model = CampusLocation
        geo_field = 'point'
        fields = (
            'id',
            'name',
            'slug',
            'category',
            'description',
            'image',
            'is_active',
            'facilities',
            'point',
            'entrance_point',
            'created_at',
            'updated_at',
        )
