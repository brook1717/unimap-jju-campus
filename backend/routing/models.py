from django.contrib.gis.db import models

from locations.models import CampusLocation


class CampusPath(models.Model):
    start_location = models.ForeignKey(
        CampusLocation,
        on_delete=models.CASCADE,
        related_name='paths_from',
    )
    end_location = models.ForeignKey(
        CampusLocation,
        on_delete=models.CASCADE,
        related_name='paths_to',
    )
    path_line = models.LineStringField()
    distance_in_meters = models.FloatField()

    def __str__(self):
        return f'{self.start_location.name} → {self.end_location.name}'
