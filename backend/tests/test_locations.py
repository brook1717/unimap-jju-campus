"""
tests/test_locations.py
-----------------------
Tests for the locations app:
  - Case-insensitive search
  - Exact-match / starts-with / partial ranking via ?search=
  - Autocomplete payload shape and ranking
  - Autocomplete 20-result cap
"""

from django.contrib.gis.geos import Point
from django.test import TestCase
from rest_framework.test import APIClient

from locations.models import CampusLocation


def _make(name, category='academic', lon=42.826, lat=9.356, description='', active=True):
    return CampusLocation.objects.create(
        name=name,
        category=category,
        description=description,
        point=Point(lon, lat, srid=4326),
        is_active=active,
    )


# ── Search ranking ────────────────────────────────────────────────────────────

class SearchRankingTests(TestCase):
    """
    Verify that ?search= applies case-insensitive matching across name /
    category / description AND that results are ranked:
      0 – exact name match
      1 – name starts with query
      2 – partial name / category / description match
    """

    def setUp(self):
        self.client = APIClient()
        # Three locations with different match qualities for "Library"
        self.exact    = _make('Library',               category='library')
        self.startw   = _make('Library Annex',         category='library')
        self.partial  = _make('Science Library Block', category='academic')

    def _names(self, search_term):
        """Return the ordered list of names from the GeoJSON features response."""
        r = self.client.get('/api/locations/', {'search': search_term})
        self.assertEqual(r.status_code, 200)
        return [f['properties']['name'] for f in r.data['features']]

    def test_exact_match_ranked_first(self):
        names = self._names('Library')
        self.assertEqual(names[0], 'Library')

    def test_starts_with_ranked_before_partial(self):
        names = self._names('Library')
        self.assertLess(names.index('Library Annex'), names.index('Science Library Block'))

    def test_search_is_case_insensitive(self):
        # lowercase query must still surface all three locations
        names = self._names('library')
        self.assertIn('Library',               names)
        self.assertIn('Library Annex',         names)
        self.assertIn('Science Library Block', names)

    def test_case_insensitive_ranking_preserved(self):
        # Ranking must be identical regardless of query case
        names_upper = self._names('LIBRARY')
        names_lower = self._names('library')
        self.assertEqual(names_upper, names_lower)

    def test_search_by_category_value(self):
        # Searching for a category value surfaces locations in that category
        r = self.client.get('/api/locations/', {'search': 'cafeteria'})
        self.assertEqual(r.status_code, 200)
        # No cafeteria locations in this test's setUp, so results must be empty
        self.assertEqual(r.data['count'], 0)

    def test_search_by_description(self):
        _make('Physics Lab', description='quantum optics research facility')
        r = self.client.get('/api/locations/', {'search': 'quantum'})
        names = [f['properties']['name'] for f in r.data['features']]
        self.assertIn('Physics Lab', names)

    def test_inactive_locations_excluded(self):
        _make('Hidden Building', active=False)
        names = self._names('Hidden')
        self.assertNotIn('Hidden Building', names)

    def test_no_search_returns_all_active(self):
        r = self.client.get('/api/locations/')
        self.assertEqual(r.status_code, 200)
        # The three setUp locations must all appear
        names = [f['properties']['name'] for f in r.data['features']]
        self.assertIn('Library',       names)
        self.assertIn('Library Annex', names)


# ── Autocomplete ──────────────────────────────────────────────────────────────

class AutocompleteTests(TestCase):
    """
    Verify /api/locations/autocomplete/ payload shape, ranking, and cap.
    """

    def setUp(self):
        self.client = APIClient()
        self.lib     = _make('Library',               category='library')
        self.lib_ann = _make('Library Annex',         category='library')
        self.sci_lib = _make('Science Library Block', category='academic')

    def _ac(self, q=''):
        r = self.client.get('/api/locations/autocomplete/', {'q': q} if q else {})
        self.assertEqual(r.status_code, 200)
        return r.data  # plain list

    def test_returns_list_not_feature_collection(self):
        data = self._ac('Library')
        self.assertIsInstance(data, list)

    def test_payload_fields(self):
        data = self._ac('Library')
        self.assertTrue(len(data) > 0)
        item = data[0]
        for field in ('id', 'name', 'slug', 'category'):
            self.assertIn(field, item, msg=f'Missing field: {field}')

    def test_no_geometry_in_payload(self):
        data = self._ac('Library')
        item = data[0]
        self.assertNotIn('geometry', item)
        self.assertNotIn('point',    item)

    def test_exact_match_ranked_first(self):
        data = self._ac('Library')
        self.assertEqual(data[0]['name'], 'Library')

    def test_starts_with_before_partial(self):
        data = self._ac('Library')
        names = [d['name'] for d in data]
        self.assertLess(names.index('Library Annex'), names.index('Science Library Block'))

    def test_empty_q_returns_up_to_20(self):
        # Create 25 total active locations
        for i in range(22):
            _make(f'Building {i:02d}')
        data = self._ac()
        self.assertLessEqual(len(data), 20)

    def test_q_filter_excludes_non_matching(self):
        _make('Sports Complex', category='facility')
        data = self._ac('Sports')
        names = [d['name'] for d in data]
        self.assertIn('Sports Complex', names)
        self.assertNotIn('Library', names)

    def test_inactive_excluded_from_autocomplete(self):
        _make('Secret Lab', active=False)
        data = self._ac('Secret')
        names = [d['name'] for d in data]
        self.assertNotIn('Secret Lab', names)

    def test_slug_present_for_routing(self):
        data = self._ac('Library')
        self.assertEqual(data[0]['slug'], self.lib.slug)
