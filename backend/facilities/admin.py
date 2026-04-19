from django.contrib import admin
from django.utils.html import format_html

from .models import Facility


@admin.register(Facility)
class FacilityAdmin(admin.ModelAdmin):
    list_display = ('image_thumbnail', 'name', 'location')
    list_display_links = ('image_thumbnail', 'name')
    list_filter = ('location__category', 'location')
    search_fields = ('name', 'description', 'location__name')
    autocomplete_fields = ('location',)

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
            'font-size:18px;">⚙️</span>'
        )
