"""
tests/test_data_import.py
-------------------------
Tests for the `load_topology` management command:
  - Missing file raises CommandError
  - Malformed JSON raises JSONDecodeError
  - Degenerate features (< 2 coords) are skipped
  - Valid GeoJSON imports the correct number of CampusPath rows
  - Running the command twice wipes the previous import (idempotent)
  - Access-edge building-name matching creates CampusPath linked to a location
"""

import json
import os
import tempfile

from django.contrib.gis.geos import Point
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from locations.models import CampusLocation
from routing.models import CampusPath


# ── Helpers ───────────────────────────────────────────────────────────────────

def _geojson(*features):
    return {"type": "FeatureCollection", "features": list(features)}


def _feature(start, end, dist=100.0, coords=None, is_access=False, building=None):
    if coords is None:
        coords = [[42.826 + start * 0.001, 9.356], [42.826 + end * 0.001, 9.357]]
    props = {
        "start_node": start,
        "end_node":   end,
        "distance_m": dist,
        "is_access_path": is_access,
    }
    if building:
        props["building_name"] = building
    return {
        "type": "Feature",
        "properties": props,
        "geometry": {"type": "LineString", "coordinates": coords},
    }


def _tmp_geojson(data: dict) -> str:
    """Write data to a temp file and return the path. Caller must delete."""
    f = tempfile.NamedTemporaryFile(
        mode='w', suffix='.geojson', delete=False, encoding='utf-8'
    )
    json.dump(data, f)
    f.close()
    return f.name


# ── Tests ─────────────────────────────────────────────────────────────────────

class LoadTopologyCommandTests(TestCase):

    # ── Error handling ────────────────────────────────────────────────────────

    def test_missing_file_raises_command_error(self):
        with self.assertRaises(CommandError):
            call_command('load_topology', path='/nonexistent/path/topology.geojson')

    def test_malformed_json_raises_decode_error(self):
        f = tempfile.NamedTemporaryFile(
            mode='w', suffix='.geojson', delete=False, encoding='utf-8'
        )
        f.write('{ this is : not valid json !!! }')
        f.close()
        try:
            with self.assertRaises(json.JSONDecodeError):
                call_command('load_topology', path=f.name)
        finally:
            os.unlink(f.name)

    # ── Degenerate feature skipping ───────────────────────────────────────────

    def test_feature_with_one_coord_is_skipped(self):
        tmp = _tmp_geojson(_geojson(
            _feature(0, 1, coords=[[42.826, 9.356]])   # only 1 point
        ))
        try:
            call_command('load_topology', path=tmp)
            self.assertEqual(CampusPath.objects.count(), 0)
        finally:
            os.unlink(tmp)

    def test_feature_with_empty_coords_is_skipped(self):
        tmp = _tmp_geojson(_geojson(
            _feature(0, 1, coords=[])
        ))
        try:
            call_command('load_topology', path=tmp)
            self.assertEqual(CampusPath.objects.count(), 0)
        finally:
            os.unlink(tmp)

    # ── Correct import ────────────────────────────────────────────────────────

    def test_valid_geojson_creates_correct_row_count(self):
        tmp = _tmp_geojson(_geojson(
            _feature(0, 1, dist=120.5),
            _feature(1, 2, dist=80.0),
        ))
        try:
            call_command('load_topology', path=tmp)
            self.assertEqual(CampusPath.objects.count(), 2)
        finally:
            os.unlink(tmp)

    def test_distance_stored_correctly(self):
        tmp = _tmp_geojson(_geojson(_feature(0, 1, dist=137.25)))
        try:
            call_command('load_topology', path=tmp)
            path = CampusPath.objects.get(start_node_id=0)
            self.assertAlmostEqual(path.distance_in_meters, 137.25, places=1)
        finally:
            os.unlink(tmp)

    def test_node_ids_stored(self):
        tmp = _tmp_geojson(_geojson(_feature(42, 99)))
        try:
            call_command('load_topology', path=tmp)
            path = CampusPath.objects.get(start_node_id=42)
            self.assertEqual(path.end_node_id, 99)
        finally:
            os.unlink(tmp)

    def test_all_paths_marked_accessible(self):
        tmp = _tmp_geojson(_geojson(
            _feature(0, 1), _feature(1, 2), _feature(2, 3),
        ))
        try:
            call_command('load_topology', path=tmp)
            non_accessible = CampusPath.objects.filter(is_accessible=False).count()
            self.assertEqual(non_accessible, 0)
        finally:
            os.unlink(tmp)

    # ── Idempotency ───────────────────────────────────────────────────────────

    def test_second_import_replaces_first(self):
        """Running the command twice must not double the row count."""
        tmp = _tmp_geojson(_geojson(_feature(0, 1)))
        try:
            call_command('load_topology', path=tmp)
            call_command('load_topology', path=tmp)
            self.assertEqual(CampusPath.objects.count(), 1)
        finally:
            os.unlink(tmp)

    def test_mixed_valid_and_degenerate_features(self):
        """Only valid features create rows; degenerate ones are silently skipped."""
        tmp = _tmp_geojson(_geojson(
            _feature(0, 1),                              # valid
            _feature(1, 2, coords=[[42.827, 9.357]]),   # degenerate — skipped
            _feature(2, 3),                              # valid
        ))
        try:
            call_command('load_topology', path=tmp)
            self.assertEqual(CampusPath.objects.count(), 2)
        finally:
            os.unlink(tmp)

    # ── Access-edge building matching ─────────────────────────────────────────

    def test_access_edge_linked_to_matching_location(self):
        loc = CampusLocation.objects.create(
            name='Engineering Building',
            category='academic',
            point=Point(42.826, 9.356, srid=4326),
        )
        tmp = _tmp_geojson(_geojson(
            _feature(0, 1, is_access=True, building='Engineering Building'),
        ))
        try:
            call_command('load_topology', path=tmp)
            path = CampusPath.objects.get(start_node_id=0)
            self.assertEqual(path.start_location_id, loc.id)
        finally:
            os.unlink(tmp)

    def test_access_edge_unmatched_building_leaves_fk_null(self):
        tmp = _tmp_geojson(_geojson(
            _feature(0, 1, is_access=True, building='Nonexistent Hall'),
        ))
        try:
            call_command('load_topology', path=tmp)
            path = CampusPath.objects.get(start_node_id=0)
            self.assertIsNone(path.start_location_id)
        finally:
            os.unlink(tmp)
