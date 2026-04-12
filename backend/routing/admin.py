from django.contrib.gis import admin

from .models import CampusPath


@admin.register(CampusPath)
class CampusPathAdmin(admin.OSMGeoAdmin):
    list_display = ('start_location', 'end_location', 'distance_in_meters')
    search_fields = ('start_location__name', 'end_location__name')
