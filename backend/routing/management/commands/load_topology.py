"""
load_topology.py
----------------
Django management command that wipes the CampusPath table and imports all 660
edges from data/topology_paths.geojson (produced by build_network_topology.py).

Usage (inside the backend container):
    python manage.py load_topology
    python manage.py load_topology --path /data/topology_paths.geojson
"""

import json
from pathlib import Path

from django.conf import settings
from django.contrib.gis.geos import LineString
from django.core.management.base import BaseCommand, CommandError

from locations.models import CampusLocation
from routing.models import CampusPath


class Command(BaseCommand):
    help = 'Wipe CampusPath table and import topology edges from topology_paths.geojson.'

    def add_arguments(self, parser):
        default = getattr(
            settings,
            'TOPOLOGY_GEOJSON_PATH',
            str(Path(settings.BASE_DIR).parent / 'data' / 'topology_paths.geojson'),
        )
        parser.add_argument(
            '--path',
            default=default,
            help='Absolute path to topology_paths.geojson (default: %(default)s)',
        )

    def handle(self, *args, **options):
        geojson_path = options['path']

        if not Path(geojson_path).exists():
            raise CommandError(
                f'File not found: {geojson_path}\n'
                'Run data/build_network_topology.py first, then re-run this command.'
            )

        self.stdout.write(f'Loading topology from {geojson_path} ...')

        with open(geojson_path, encoding='utf-8') as fh:
            fc = json.load(fh)

        features = fc.get('features', [])
        self.stdout.write(f'  {len(features)} edge(s) found in GeoJSON.')

        # Build name -> CampusLocation lookup for access-edge matching.
        loc_by_name = {
            loc.name.strip().lower(): loc
            for loc in CampusLocation.objects.only('id', 'name')
        }
        self.stdout.write(f'  {len(loc_by_name)} CampusLocation(s) available for matching.')

        # Wipe existing paths.
        deleted_count, _ = CampusPath.objects.all().delete()
        self.stdout.write(f'  Deleted {deleted_count} existing CampusPath row(s).')

        created = 0
        skipped = 0
        paths_to_create = []

        for feat in features:
            props   = feat.get('properties', {})
            geom    = feat.get('geometry', {})
            coords  = geom.get('coordinates', [])

            if not coords or len(coords) < 2:
                skipped += 1
                continue

            start_id = props.get('start_node')
            end_id   = props.get('end_node')
            dist_m   = props.get('distance_m', 0.0) or 0.0
            is_access = bool(props.get('is_access_path', False))
            bname     = props.get('building_name') or ''

            # Match building name to a CampusLocation for access edges.
            start_loc = loc_by_name.get(bname.strip().lower()) if is_access and bname else None

            # Build the path name.
            if is_access and bname:
                edge_name = f'Access: {bname}'
            else:
                edge_name = ''

            try:
                line = LineString(coords, srid=4326)
            except Exception as exc:
                self.stderr.write(f'  [SKIP] Invalid geometry for node {start_id}->{end_id}: {exc}')
                skipped += 1
                continue

            paths_to_create.append(
                CampusPath(
                    name=edge_name,
                    start_location=start_loc,
                    end_location=None,
                    start_node_id=start_id,
                    end_node_id=end_id,
                    path_line=line,
                    distance_in_meters=round(dist_m, 2),
                    is_accessible=True,
                )
            )
            created += 1

        # Bulk insert for speed.
        CampusPath.objects.bulk_create(paths_to_create, batch_size=200)

        self.stdout.write(self.style.SUCCESS(
            f'\nDone.  Imported {created} path(s), skipped {skipped}.'
        ))
