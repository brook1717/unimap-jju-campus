from django.contrib.gis.db import models


class CampusLocation(models.Model):
    CATEGORY_CHOICES = [
        ('academic', 'Academic'),
        ('office', 'Office'),
        ('lab', 'Lab'),
        ('library', 'Library'),
        ('dormitory', 'Dormitory'),
        ('cafeteria', 'Cafeteria'),
        ('gate', 'Gate'),
        ('facility', 'Facility'),
    ]

    name = models.CharField(max_length=255)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='locations/', blank=True, null=True)
    point = models.PointField()

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
