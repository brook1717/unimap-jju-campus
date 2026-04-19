from django.contrib import admin
from leaflet.admin import LeafletGeoAdmin

from .models import CampusPath


@admin.register(CampusPath)
class CampusPathAdmin(LeafletGeoAdmin):
    list_display = ('__str__', 'distance_in_meters', 'is_accessible')
    list_filter = ('is_accessible',)
    search_fields = ('name', 'start_location__name', 'end_location__name')
    fieldsets = (
        (None, {
            'fields': ('name', 'start_location', 'end_location', 'is_accessible',
                        'distance_in_meters', 'start_node_id', 'end_node_id'),
        }),
        ('Geometry', {
            'fields': ('path_line',),
            'description': 'Draw or edit the path. Drag vertices to refine.',
        }),
    )
