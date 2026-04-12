from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import CampusLocation


class CampusLocationSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = CampusLocation
        geo_field = 'point'
        fields = ('id', 'name', 'category', 'description', 'image', 'point')
