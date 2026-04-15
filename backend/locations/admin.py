from django.contrib.gis import admin

from .models import CampusLocation


@admin.register(CampusLocation)
class CampusLocationAdmin(admin.OSMGeoAdmin):
    list_display = ('name', 'slug', 'category', 'is_active', 'created_at')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')
