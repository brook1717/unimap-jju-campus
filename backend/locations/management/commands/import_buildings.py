from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Import campus buildings from data/buildings.csv'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='/data/buildings.csv',
            help='Path to the buildings CSV file',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Building import not yet implemented.'))
