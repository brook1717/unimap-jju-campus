from django.contrib.gis.db import models

from locations.models import CampusLocation


class CampusPath(models.Model):
    name = models.CharField(max_length=255, blank=True)
    start_location = models.ForeignKey(
        CampusLocation,
        on_delete=models.CASCADE,
        related_name='paths_starting_at',
    )
    end_location = models.ForeignKey(
        CampusLocation,
        on_delete=models.CASCADE,
        related_name='paths_ending_at',
    )
    # spatial_index=True (default) creates a PostGIS GIST index on path_line
    path_line = models.LineStringField(srid=4326, spatial_index=True)
    distance_in_meters = models.FloatField()
    is_accessible = models.BooleanField(
        default=True,
        help_text='Whether this path is navigable by wheelchair or similar mobility aid',
    )

    def __str__(self):
        return self.name or f'{self.start_location.name} → {self.end_location.name}'
