from django.contrib import admin
from django.utils.html import format_html
from leaflet.admin import LeafletGeoAdmin

from .models import CampusLocation


@admin.register(CampusLocation)
class CampusLocationAdmin(LeafletGeoAdmin):
    list_display = ('image_thumbnail', 'name', 'slug', 'category', 'is_active', 'created_at')
    list_display_links = ('image_thumbnail', 'name')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at', 'image_preview')
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'category', 'description', 'is_active'),
        }),
        ('Image', {
            'fields': ('image', 'image_preview'),
        }),
        ('Geometry', {
            'fields': ('point', 'entrance_point'),
            'description': 'Click the map to place or drag to refine the point.',
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description='Photo')
    def image_thumbnail(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width:40px;height:40px;object-fit:cover;border-radius:4px;" />',
                obj.image.url,
            )
        return format_html(
            '<span style="display:inline-block;width:40px;height:40px;'
            'background:#e2e8f0;border-radius:4px;text-align:center;line-height:40px;'
            'font-size:18px;">📍</span>'
        )

    @admin.display(description='Image Preview')
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width:300px;max-height:200px;border-radius:8px;" />',
                obj.image.url,
            )
        return format_html('<em>No image uploaded</em>')
