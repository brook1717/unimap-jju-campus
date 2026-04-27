"""
Safe metadata-only update for CampusLocation records.

Reads data/buildings.csv and updates ONLY name, category, and description.
Never creates, deletes, or modifies coordinates / geometry.

Usage:
    python manage.py update_building_metadata
    python manage.py update_building_metadata --file /data/buildings.csv --dry-run
"""

import csv
import os

from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.core.management.base import BaseCommand

from locations.models import CampusLocation

# ── Map CSV human-readable categories → model choice keys ────────────────────
CATEGORY_MAP = {
    'Classroom Block':    'classroom',
    'College Faculty':    'college',
    'Laboratory':         'lab',
    'Dining & Recreation':'dining',
    'Library':            'library',
    'Administrative':     'administrative',
    'Recreation':         'recreation',
    'Dormitory':          'dormitory',
    'Utility':            'utility',
    'Student Services':   'student_services',
    'Campus Facility':    'campus_facility',
    'Academic Facility':  'academic',
    'General Facility':   'facility',
    'Lecture Hall':       'lecture_hall',
    'Campus Entrance':    'gate',
}

# Maximum distance (metres) for coordinate-based fallback matching
COORD_TOLERANCE_M = 30


class Command(BaseCommand):
    help = (
        'Safe metadata update: reads buildings.csv and patches name, category, '
        'and description on existing CampusLocation records. '
        'Never creates or deletes rows. Never touches coordinates.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default=os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data', 'buildings.csv'),
            help='Path to the buildings CSV file (default: <project>/data/buildings.csv)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview changes without writing to the database.',
        )

    def handle(self, *args, **options):
        csv_path = os.path.abspath(options['file'])
        dry_run = options['dry_run']

        if not os.path.isfile(csv_path):
            self.stderr.write(self.style.ERROR(f'CSV not found: {csv_path}'))
            return

        if dry_run:
            self.stdout.write(self.style.WARNING('=== DRY RUN — no changes will be saved ===\n'))

        updated = 0
        skipped_no_match = 0
        skipped_no_change = 0
        warnings = []

        with open(csv_path, newline='', encoding='utf-8') as fh:
            reader = csv.DictReader(fh)

            for row_num, row in enumerate(reader, start=2):  # row 1 = header
                csv_name = row.get('name', '').strip()
                csv_category = row.get('category', '').strip()
                csv_description = row.get('description', '').strip()
                lat_raw = row.get('latitude', '').strip()
                lon_raw = row.get('longitude', '').strip()

                if not csv_name:
                    continue

                # ── Resolve category ─────────────────────────────────────
                db_category = CATEGORY_MAP.get(csv_category)
                if db_category is None:
                    msg = f'[ROW {row_num}] Unknown category "{csv_category}" for "{csv_name}" — defaulting to "facility"'
                    warnings.append(msg)
                    self.stdout.write(self.style.WARNING(msg))
                    db_category = 'facility'

                # ── Match existing record ────────────────────────────────
                # Strategy 1: exact name match (case-insensitive)
                location = CampusLocation.objects.filter(name__iexact=csv_name).first()

                # Strategy 2: coordinate proximity fallback
                if location is None and lat_raw and lon_raw:
                    try:
                        lat, lon = float(lat_raw), float(lon_raw)
                        ref = Point(lon, lat, srid=4326)
                        location = (
                            CampusLocation.objects
                            .filter(point__distance_lte=(ref, D(m=COORD_TOLERANCE_M)))
                            .order_by('point')
                            .first()
                        )
                        if location:
                            self.stdout.write(
                                self.style.NOTICE(
                                    f'[ROW {row_num}] Name "{csv_name}" not found — '
                                    f'matched by proximity to "{location.name}" (id={location.pk})'
                                )
                            )
                    except (ValueError, TypeError):
                        pass

                if location is None:
                    msg = f'[ROW {row_num}] WARNING: No DB match for "{csv_name}" — skipped (not creating)'
                    warnings.append(msg)
                    self.stdout.write(self.style.WARNING(msg))
                    skipped_no_match += 1
                    continue

                # ── Compare & update only changed fields ─────────────────
                changes = []
                if location.name != csv_name:
                    changes.append(f'name: "{location.name}" → "{csv_name}"')
                    location.name = csv_name
                if location.category != db_category:
                    changes.append(f'category: "{location.category}" → "{db_category}"')
                    location.category = db_category
                if location.description != csv_description:
                    changes.append(f'description updated')
                    location.description = csv_description

                if not changes:
                    skipped_no_change += 1
                    continue

                if dry_run:
                    self.stdout.write(
                        f'  [DRY] {location.name} (id={location.pk}): {", ".join(changes)}'
                    )
                else:
                    location.save(update_fields=['name', 'category', 'description', 'updated_at'])
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'  [OK] {location.name} (id={location.pk}): {", ".join(changes)}'
                        )
                    )
                updated += 1

        # ── Summary ──────────────────────────────────────────────────────
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'Updated:    {updated}'))
        self.stdout.write(f'No change:  {skipped_no_change}')
        self.stdout.write(f'No match:   {skipped_no_match}')
        if warnings:
            self.stdout.write(self.style.WARNING(f'Warnings:   {len(warnings)}'))
        if dry_run:
            self.stdout.write(self.style.WARNING('\nDry run complete — nothing was saved.'))
        else:
            self.stdout.write(self.style.SUCCESS('\nMetadata sync complete.'))
