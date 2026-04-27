from django.contrib.gis.db import models
from django.utils.text import slugify


class CampusLocation(models.Model):
    CATEGORY_CHOICES = [
        ('academic', 'Academic Facility'),
        ('administrative', 'Administrative'),
        ('cafeteria', 'Cafeteria'),
        ('campus_facility', 'Campus Facility'),
        ('classroom', 'Classroom Block'),
        ('college', 'College Faculty'),
        ('dining', 'Dining & Recreation'),
        ('dormitory', 'Dormitory'),
        ('facility', 'General Facility'),
        ('gate', 'Campus Entrance'),
        ('lab', 'Laboratory'),
        ('lecture_hall', 'Lecture Hall'),
        ('library', 'Library'),
        ('office', 'Office'),
        ('recreation', 'Recreation'),
        ('student_services', 'Student Services'),
        ('utility', 'Utility'),
    ]

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='locations/', blank=True, null=True)
    is_active = models.BooleanField(default=True)

    # spatial_index=True (default) creates a PostGIS GIST index on each column
    point = models.PointField(
        srid=4326,
        spatial_index=True,
        help_text='Main coordinate for the building',
    )
    entrance_point = models.PointField(
        srid=4326,
        spatial_index=True,
        null=True,
        blank=True,
        help_text='The exact navigation entry point',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['category']),
            models.Index(fields=['is_active']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while CampusLocation.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base_slug}-{counter}'
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
