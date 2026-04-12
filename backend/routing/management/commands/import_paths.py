from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Import campus walking paths from data/paths.geojson'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='/data/paths.geojson',
            help='Path to the paths GeoJSON file',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Path import not yet implemented.'))
