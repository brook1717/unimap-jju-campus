from django.contrib.gis import admin

from .models import CampusLocation


@admin.register(CampusLocation)
class CampusLocationAdmin(admin.OSMGeoAdmin):
    list_display = ('name', 'category')
    list_filter = ('category',)
    search_fields = ('name',)
