from django.db import models

from locations.models import CampusLocation


class Facility(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='facilities/', blank=True, null=True)
    location = models.ForeignKey(
        CampusLocation,
        on_delete=models.CASCADE,
        related_name='facilities',
    )

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'facilities'

    def __str__(self):
        return f'{self.name} @ {self.location.name}'
