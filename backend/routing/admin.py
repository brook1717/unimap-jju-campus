from django.contrib.gis import admin

from .models import CampusPath


@admin.register(CampusPath)
class CampusPathAdmin(admin.OSMGeoAdmin):
    list_display = ('__str__', 'distance_in_meters', 'is_accessible')
    list_filter = ('is_accessible',)
    search_fields = ('name', 'start_location__name', 'end_location__name')
