from django.contrib.gis.db import models

from locations.models import CampusLocation


class CampusPath(models.Model):
    name = models.CharField(max_length=255, blank=True)
    start_location = models.ForeignKey(
        CampusLocation,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='paths_starting_at',
    )
    end_location = models.ForeignKey(
        CampusLocation,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='paths_ending_at',
    )
    start_node_id = models.IntegerField(
        null=True,
        blank=True,
        help_text='Topology graph node ID for the start endpoint',
    )
    end_node_id = models.IntegerField(
        null=True,
        blank=True,
        help_text='Topology graph node ID for the end endpoint',
    )
    path_line = models.LineStringField(srid=4326, spatial_index=True)
    distance_in_meters = models.FloatField()
    is_accessible = models.BooleanField(
        default=True,
        help_text='Whether this path is navigable by wheelchair or similar mobility aid',
    )

    def __str__(self):
        if self.name:
            return self.name
        start = self.start_location.name if self.start_location_id else f'node_{self.start_node_id}'
        end   = self.end_location.name   if self.end_location_id   else f'node_{self.end_node_id}'
        return f'{start} -> {end}'
