"""
seed_campus.py
--------------
Management command that populates the development database with a balanced
'Mini-Campus' of CampusLocation records and then loads the routing topology.

Usage:
    python manage.py seed_campus
    python manage.py seed_campus --clear          # wipe existing locations first
    python manage.py seed_campus --skip-topology  # skip load_topology step
"""

from django.contrib.gis.geos import Point
from django.core.management import call_command
from django.core.management.base import BaseCommand

from locations.models import CampusLocation

# ---------------------------------------------------------------------------
# Mini-campus dataset
# Coordinates are placed within the JJU topology graph bounds
# (nodes clustered around lon ≈ 42.826–42.829, lat ≈ 9.355–9.360).
# Every location is well within the 500 m snap-distance guard.
# ---------------------------------------------------------------------------

MINI_CAMPUS: list[tuple] = [
    # (name, category, lon, lat, description)

    # Gates
    ('Main Gate',               'gate',       42.82571, 9.35592, 'Main vehicle and pedestrian entrance to JJU campus'),
    ('North Gate',              'gate',       42.82761, 9.35830, 'Secondary northern entrance near dormitory zone'),

    # Academic buildings
    ('College of Engineering',  'academic',   42.82660, 9.35710, 'Engineering, computing, and technology faculty'),
    ('College of Natural Sciences', 'academic', 42.82700, 9.35690, 'Natural sciences, mathematics, and physics'),
    ('College of Medicine',     'academic',   42.82720, 9.35650, 'Medical sciences and public health faculty'),

    # Library
    ('University Library',      'library',    42.82620, 9.35660, 'Central library, reading rooms, and digital lab'),

    # Administrative
    ('Administration Building', 'office',     42.82640, 9.35680, 'Rector office, registrar, and student affairs'),

    # Dining
    ('Student Cafeteria',       'cafeteria',  42.82580, 9.35720, 'Main dining hall — breakfast, lunch, and dinner'),
    ('Staff Canteen',           'cafeteria',  42.82650, 9.35740, 'Canteen reserved for academic and support staff'),

    # Residential
    ('Dormitory Block A',       'dormitory',  42.82550, 9.35750, 'Undergraduate male residential building'),
    ('Dormitory Block B',       'dormitory',  42.82540, 9.35770, 'Undergraduate female residential building'),

    # Facilities
    ('Health Centre',           'facility',   42.82600, 9.35640, 'Campus medical clinic and wellness services'),
    ('Sports Complex',          'facility',   42.82700, 9.35760, 'Gymnasium, athletics track, and football pitch'),
]


class Command(BaseCommand):
    help = (
        'Seed the database with a balanced Mini-Campus for development, '
        'then load the routing topology.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            default=False,
            help='Delete all existing CampusLocation rows before seeding.',
        )
        parser.add_argument(
            '--skip-topology',
            action='store_true',
            default=False,
            dest='skip_topology',
            help='Skip calling load_topology after seeding locations.',
        )

    def handle(self, *args, **options):
        if options['clear']:
            deleted, _ = CampusLocation.objects.all().delete()
            self.stdout.write(f'  Cleared {deleted} existing CampusLocation row(s).')

        created = 0
        skipped = 0

        for name, category, lon, lat, description in MINI_CAMPUS:
            obj, was_created = CampusLocation.objects.get_or_create(
                name=name,
                defaults={
                    'category':    category,
                    'description': description,
                    'point':       Point(lon, lat, srid=4326),
                    'is_active':   True,
                },
            )
            if was_created:
                created += 1
                self.stdout.write(f'  [+] {name} ({category})')
            else:
                skipped += 1
                self.stdout.write(f'  [=] {name} already exists — skipped')

        self.stdout.write(self.style.SUCCESS(
            f'\nSeeding complete: {created} created, {skipped} already existed.'
        ))

        # ── Integrate with load_topology ─────────────────────────────────────
        if options['skip_topology']:
            self.stdout.write(self.style.WARNING('Skipping topology load (--skip-topology).'))
            return

        self.stdout.write('\nLoading routing topology...')
        try:
            call_command('load_topology', stdout=self.stdout, stderr=self.stderr)
        except Exception as exc:
            self.stdout.write(self.style.WARNING(
                f'Could not load topology: {exc}\n'
                'Run `python manage.py load_topology` manually once '
                'topology_paths.geojson is available.'
            ))
