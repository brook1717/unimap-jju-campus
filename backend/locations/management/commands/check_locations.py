"""
Read-only diagnostic audit for CampusLocation records.

Reports inactive locations, missing entrance points (unroutable for A*),
missing categories, and summary statistics.

Usage:
    python manage.py check_locations
"""

from django.core.management.base import BaseCommand

from locations.models import CampusLocation


class Command(BaseCommand):
    help = 'Read-only audit of CampusLocation data quality (inactive, missing entrance, missing category).'

    def handle(self, *args, **options):
        all_locs = CampusLocation.objects.all()
        total = all_locs.count()

        if total == 0:
            self.stdout.write(self.style.WARNING('No CampusLocation records found.'))
            return

        # ── Collect problem sets ─────────────────────────────────────────
        inactive = all_locs.filter(is_active=False).order_by('name')
        no_entrance = all_locs.filter(entrance_point__isnull=True).order_by('name')
        no_category = all_locs.filter(category__in=['', None]).order_by('name')
        valid_keys = {k for k, _ in CampusLocation.CATEGORY_CHOICES}
        all_records = all_locs.values_list('id', 'name', 'category')
        invalid_category = [
            (pk, name, cat)
            for pk, name, cat in all_records
            if cat and cat not in valid_keys
        ]

        # Derived sets
        active_locs = all_locs.filter(is_active=True)
        active_total = active_locs.count()
        ghosts = active_locs.filter(entrance_point__isnull=True)
        healthy = active_locs.filter(
            entrance_point__isnull=False,
        ).exclude(category__in=['', None])

        # ── Report ───────────────────────────────────────────────────────
        SEP = '=' * 64

        self.stdout.write(f'\n{SEP}')
        self.stdout.write('  CAMPUS LOCATION DATA AUDIT')
        self.stdout.write(f'{SEP}\n')

        # 1. Inactive
        self.stdout.write(self.style.HTTP_INFO('1. INACTIVE LOCATIONS (is_active=False)'))
        self.stdout.write('   These buildings are hidden from search and the map.\n')
        if inactive.exists():
            for loc in inactive:
                self.stdout.write(f'   - [id={loc.pk}] {loc.name} (category: {loc.category or "—"})')
        else:
            self.stdout.write(self.style.SUCCESS('   None — all locations are active.'))
        self.stdout.write('')

        # 2. Missing entrance points
        self.stdout.write(self.style.HTTP_INFO('2. MISSING ENTRANCE POINTS (entrance_point IS NULL)'))
        self.stdout.write(
            '   ⚠  These buildings are UNROUTABLE. The A* pathfinding engine\n'
            '      snaps to the nearest graph node from a location\'s entrance_point.\n'
            '      Without one, the routing API cannot compute directions to or from\n'
            '      these buildings. Fix via Django Admin → set entrance_point.\n'
        )
        if no_entrance.exists():
            for loc in no_entrance:
                status = 'ACTIVE' if loc.is_active else 'inactive'
                self.stdout.write(
                    f'   - [id={loc.pk:>3}] {loc.name:<55} [{status}]'
                )
        else:
            self.stdout.write(self.style.SUCCESS('   None — all locations have entrance points.'))
        self.stdout.write('')

        # 3. Missing / invalid categories
        self.stdout.write(self.style.HTTP_INFO('3. MISSING OR INVALID CATEGORIES'))
        self.stdout.write('   Buildings without a category may display incorrect icons/filters.\n')
        has_issues = False
        if no_category.exists():
            has_issues = True
            self.stdout.write('   Empty category:')
            for loc in no_category:
                self.stdout.write(f'   - [id={loc.pk}] {loc.name}')
        if invalid_category:
            has_issues = True
            self.stdout.write('   Invalid category (not in CATEGORY_CHOICES):')
            for pk, name, cat in invalid_category:
                self.stdout.write(f'   - [id={pk}] {name} → "{cat}"')
        if not has_issues:
            self.stdout.write(self.style.SUCCESS('   None — all categories are valid.'))
        self.stdout.write('')

        # 4. Summary
        ghost_count = ghosts.count()
        healthy_count = healthy.count()

        self.stdout.write(f'{SEP}')
        self.stdout.write('  SUMMARY')
        self.stdout.write(f'{SEP}')
        self.stdout.write(f'  Total locations:       {total}')
        self.stdout.write(f'  Active:                {active_total}')
        self.stdout.write(f'  Inactive:              {inactive.count()}')
        self.stdout.write(f'  Missing entrance:      {no_entrance.count()}')
        self.stdout.write(f'  Missing/bad category:  {no_category.count() + len(invalid_category)}')
        self.stdout.write('')
        self.stdout.write(
            self.style.SUCCESS(f'  ✓ Healthy (active + entrance + category): {healthy_count}')
        )
        self.stdout.write(
            self.style.WARNING(f'  ⚠ Ghost   (active but NO entrance):       {ghost_count}')
            if ghost_count > 0
            else f'  ⚠ Ghost   (active but NO entrance):       {ghost_count}'
        )
        self.stdout.write(f'{SEP}\n')
