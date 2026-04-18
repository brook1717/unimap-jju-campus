"""
tests/test_routing.py
---------------------
Tests for the routing app:

  PathfindingServiceTests
    - A* finds the correct path and distance between two known nodes
    - NetworkXNoPath raised when nodes are disconnected
    - find_nearest_node returns the closest node

  DirectionsAPITests (all via mocked PathfindingService)
    - Same location → 200 Point GeoJSON, zero distance
    - Successful route → full GeoJSON contract check
    - Outside campus bounds (snap > 500 m) → 400 OutsideCampusBounds
    - No path found → 404 NoPathFound  (NetworkXNoPath + NodeNotFound)
    - Missing parameters → 400
    - Non-integer parameters → 400
    - Non-existent / inactive location → 404
"""

from unittest.mock import MagicMock, patch

import networkx as nx
from django.contrib.gis.geos import Point
from django.test import TestCase
from rest_framework.test import APIClient

from locations.models import CampusLocation
from routing.services import PathfindingService


# ── Helpers ───────────────────────────────────────────────────────────────────

def _loc(name, lon=42.826, lat=9.356, category='academic', active=True):
    return CampusLocation.objects.create(
        name=name, category=category,
        point=Point(lon, lat, srid=4326),
        is_active=active,
    )


# ── PathfindingService unit tests ────────────────────────────────────────────

class PathfindingServiceTests(TestCase):
    """
    Inject a minimal 3-node, 2-edge graph directly into the singleton so
    these tests run without the topology GeoJSON file.

    Graph:
        0 ──150 m── 1 ──150 m── 2
    Coords:
        0: [42.826, 9.356]
        1: [42.827, 9.357]
        2: [42.828, 9.358]
    """

    def setUp(self):
        PathfindingService.reset_instance()
        svc = PathfindingService()
        G = nx.Graph()
        G.add_node(0, x=42.826, y=9.356)
        G.add_node(1, x=42.827, y=9.357)
        G.add_node(2, x=42.828, y=9.358)
        G.add_edge(0, 1, weight=150.0, coords=[[42.826, 9.356], [42.827, 9.357]])
        G.add_edge(1, 2, weight=150.0, coords=[[42.827, 9.357], [42.828, 9.358]])
        svc._graph = G

    def tearDown(self):
        PathfindingService.reset_instance()

    # ── A* path ───────────────────────────────────────────────────────────────

    def test_astar_finds_correct_path_between_known_nodes(self):
        svc = PathfindingService()
        path, dist, coords = svc.calculate_route(0, 2)
        self.assertEqual(path, [0, 1, 2])
        self.assertAlmostEqual(dist, 300.0, places=1)

    def test_astar_single_hop_path(self):
        svc = PathfindingService()
        path, dist, _ = svc.calculate_route(0, 1)
        self.assertEqual(path, [0, 1])
        self.assertAlmostEqual(dist, 150.0, places=1)

    def test_astar_geometry_has_correct_coordinate_count(self):
        svc = PathfindingService()
        _, _, coords = svc.calculate_route(0, 2)
        # 2-hop path through 3 nodes → 3 distinct coordinate pairs
        self.assertEqual(len(coords), 3)

    def test_astar_no_path_raises_networkx_no_path(self):
        svc = PathfindingService()
        # Add an isolated node with no connecting edges
        svc._graph.add_node(99, x=42.890, y=9.400)
        with self.assertRaises(nx.NetworkXNoPath):
            svc.calculate_route(0, 99)

    def test_astar_missing_node_raises_node_not_found(self):
        svc = PathfindingService()
        with self.assertRaises(nx.NodeNotFound):
            svc.calculate_route(0, 9999)   # node 9999 doesn't exist

    # ── Nearest-node search ───────────────────────────────────────────────────

    def test_find_nearest_node_returns_closest_to_query(self):
        svc = PathfindingService()
        nid, dist = svc.find_nearest_node(42.8261, 9.3561)   # close to node 0
        self.assertEqual(nid, 0)
        self.assertLess(dist, 50.0)   # definitely under 50 m

    def test_find_nearest_node_other_end(self):
        svc = PathfindingService()
        nid, dist = svc.find_nearest_node(42.8279, 9.3579)   # close to node 2
        self.assertEqual(nid, 2)

    def test_find_nearest_node_returns_float_distance(self):
        svc = PathfindingService()
        _, dist = svc.find_nearest_node(42.827, 9.357)
        self.assertIsInstance(dist, float)


# ── Directions API contract tests ────────────────────────────────────────────

class DirectionsAPITests(TestCase):
    """
    HTTP-level tests for GET /api/routing/directions/.
    PathfindingService is patched at the view layer so these tests are
    self-contained and require no topology GeoJSON file.
    """

    def setUp(self):
        self.client = APIClient()
        self.loc_a = _loc('Building A', lon=42.826, lat=9.356)
        self.loc_b = _loc('Building B', lon=42.827, lat=9.357)

    def _url(self, start, end):
        return f'/api/routing/directions/?start_location_id={start}&end_location_id={end}'

    # ── Same-location short-circuit (no mock needed) ──────────────────────────

    def test_same_location_returns_200_with_point_geometry(self):
        r = self.client.get(self._url(self.loc_a.id, self.loc_a.id))
        self.assertEqual(r.status_code, 200)
        data = r.data
        self.assertEqual(data['type'],              'Feature')
        self.assertEqual(data['geometry']['type'],  'Point')

    def test_same_location_zero_distance(self):
        r = self.client.get(self._url(self.loc_a.id, self.loc_a.id))
        props = r.data['properties']
        self.assertEqual(props['total_distance_m'],           0.0)
        self.assertEqual(props['estimated_walking_time_s'],   0)
        self.assertEqual(props['estimated_walking_time_min'], 0.0)
        self.assertEqual(props['path_node_count'],            1)

    def test_same_location_coordinates_match_location(self):
        r = self.client.get(self._url(self.loc_a.id, self.loc_a.id))
        coords = r.data['geometry']['coordinates']
        self.assertAlmostEqual(coords[0], self.loc_a.point.x, places=4)
        self.assertAlmostEqual(coords[1], self.loc_a.point.y, places=4)

    # ── Parameter validation ──────────────────────────────────────────────────

    def test_missing_both_params_returns_400(self):
        r = self.client.get('/api/routing/directions/')
        self.assertEqual(r.status_code, 400)

    def test_missing_end_param_returns_400(self):
        r = self.client.get(f'/api/routing/directions/?start_location_id={self.loc_a.id}')
        self.assertEqual(r.status_code, 400)

    def test_non_integer_params_returns_400(self):
        r = self.client.get('/api/routing/directions/?start_location_id=abc&end_location_id=xyz')
        self.assertEqual(r.status_code, 400)

    def test_inactive_location_returns_404(self):
        inactive = _loc('Closed Building', active=False)
        r = self.client.get(self._url(inactive.id, self.loc_b.id))
        self.assertEqual(r.status_code, 404)

    def test_nonexistent_location_returns_404(self):
        r = self.client.get(self._url(99999, self.loc_b.id))
        self.assertEqual(r.status_code, 404)

    # ── Mocked routing scenarios ──────────────────────────────────────────────

    def _mock_svc(self, mock_class, snap_start=5.0, snap_end=8.0,
                  path=None, dist=300.0, coords=None):
        """Wire a MagicMock PathfindingService onto mock_class."""
        svc = MagicMock()
        mock_class.return_value = svc
        svc.find_nearest_node.side_effect = [(0, snap_start), (2, snap_end)]
        svc.calculate_route.return_value = (
            path or [0, 1, 2],
            dist,
            coords or [[42.826, 9.356], [42.827, 9.357], [42.828, 9.358]],
        )
        return svc

    @patch('routing.views.PathfindingService')
    def test_successful_route_returns_200(self, mock_cls):
        self._mock_svc(mock_cls)
        r = self.client.get(self._url(self.loc_a.id, self.loc_b.id))
        self.assertEqual(r.status_code, 200)

    @patch('routing.views.PathfindingService')
    def test_geojson_contract_top_level_keys(self, mock_cls):
        self._mock_svc(mock_cls)
        r = self.client.get(self._url(self.loc_a.id, self.loc_b.id))
        data = r.data
        self.assertEqual(data['type'],             'Feature')
        self.assertEqual(data['geometry']['type'], 'LineString')
        self.assertIn('coordinates', data['geometry'])
        self.assertIsInstance(data['geometry']['coordinates'], list)

    @patch('routing.views.PathfindingService')
    def test_geojson_contract_required_properties(self, mock_cls):
        self._mock_svc(mock_cls)
        r = self.client.get(self._url(self.loc_a.id, self.loc_b.id))
        props = r.data['properties']
        required = (
            'start_location', 'end_location',
            'total_distance_m', 'estimated_walking_time_s',
            'estimated_walking_time_min', 'path_node_count',
            'snap_distance_start_m', 'snap_distance_end_m',
        )
        for key in required:
            self.assertIn(key, props, msg=f'Missing property: {key}')

    @patch('routing.views.PathfindingService')
    def test_geojson_location_stubs_have_id_name_slug(self, mock_cls):
        self._mock_svc(mock_cls)
        r = self.client.get(self._url(self.loc_a.id, self.loc_b.id))
        for stub in (r.data['properties']['start_location'],
                     r.data['properties']['end_location']):
            self.assertIn('id',   stub)
            self.assertIn('name', stub)
            self.assertIn('slug', stub)

    @patch('routing.views.PathfindingService')
    def test_walking_time_computed_correctly(self, mock_cls):
        # 300 m / 1.4 m/s = ~214 s = ~3.6 min
        self._mock_svc(mock_cls, dist=300.0)
        r = self.client.get(self._url(self.loc_a.id, self.loc_b.id))
        props = r.data['properties']
        self.assertEqual(props['total_distance_m'], 300.0)
        self.assertEqual(props['estimated_walking_time_s'], round(300.0 / 1.4))
        self.assertAlmostEqual(props['estimated_walking_time_min'], round(300.0 / 1.4 / 60, 1), places=1)

    # ── Boundary guard ────────────────────────────────────────────────────────

    @patch('routing.views.PathfindingService')
    def test_start_outside_bounds_returns_400(self, mock_cls):
        svc = MagicMock()
        mock_cls.return_value = svc
        svc.find_nearest_node.side_effect = [(0, 600.0), (2, 8.0)]  # start > 500 m
        r = self.client.get(self._url(self.loc_a.id, self.loc_b.id))
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.data['error'], 'OutsideCampusBounds')

    @patch('routing.views.PathfindingService')
    def test_end_outside_bounds_returns_400(self, mock_cls):
        svc = MagicMock()
        mock_cls.return_value = svc
        svc.find_nearest_node.side_effect = [(0, 5.0), (2, 800.0)]  # end > 500 m
        r = self.client.get(self._url(self.loc_a.id, self.loc_b.id))
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.data['error'], 'OutsideCampusBounds')

    @patch('routing.views.PathfindingService')
    def test_exactly_500m_is_accepted(self, mock_cls):
        """Boundary is exclusive: exactly 500.0 m must be accepted."""
        self._mock_svc(mock_cls, snap_start=500.0, snap_end=500.0)
        r = self.client.get(self._url(self.loc_a.id, self.loc_b.id))
        self.assertEqual(r.status_code, 200)

    # ── No-path handling ──────────────────────────────────────────────────────

    @patch('routing.views.PathfindingService')
    def test_no_path_returns_404_with_correct_error_type(self, mock_cls):
        svc = MagicMock()
        mock_cls.return_value = svc
        svc.find_nearest_node.side_effect = [(0, 5.0), (2, 8.0)]
        svc.calculate_route.side_effect = nx.NetworkXNoPath()
        r = self.client.get(self._url(self.loc_a.id, self.loc_b.id))
        self.assertEqual(r.status_code, 404)
        self.assertEqual(r.data['error'],   'NoPathFound')
        self.assertIn('No walking path', r.data['message'])

    @patch('routing.views.PathfindingService')
    def test_node_not_found_returns_404_no_path(self, mock_cls):
        svc = MagicMock()
        mock_cls.return_value = svc
        svc.find_nearest_node.side_effect = [(0, 5.0), (2, 8.0)]
        svc.calculate_route.side_effect = nx.NodeNotFound('99')
        r = self.client.get(self._url(self.loc_a.id, self.loc_b.id))
        self.assertEqual(r.status_code, 404)
        self.assertEqual(r.data['error'], 'NoPathFound')
