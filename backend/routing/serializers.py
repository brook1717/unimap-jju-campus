from rest_framework_gis.serializers import GeoFeatureModelSerializer

from .models import CampusPath


class CampusPathSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = CampusPath
        geo_field = 'path_line'
        fields = ('id', 'start_location', 'end_location', 'path_line', 'distance_in_meters')
