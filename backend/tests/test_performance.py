"""
tests/test_performance.py
-------------------------
DevOps / benchmarking tests.

CachePerformanceBenchmark
  - Warms the route cache with a single request (cache miss)
  - Issues 99 subsequent requests (cache hits)
  - Asserts the average response time of ALL 100 requests is under 10 ms

The test patches PathfindingService so it runs without a topology file and
the cache-miss cost is dominated by one mock call, not a real A* search.
"""

import time
from unittest.mock import MagicMock, patch

from django.contrib.gis.geos import Point
from django.core.cache import cache
from django.test import TestCase
from rest_framework.test import APIClient

from locations.models import CampusLocation


N_REQUESTS   = 100       # total requests (1 cache-miss + 99 cache-hits)
MAX_AVG_MS   = 10.0      # hard limit for average response time in milliseconds
WARN_AVG_MS  = 5.0       # informational threshold written to stdout


def _loc(name, lon, lat):
    return CampusLocation.objects.create(
        name=name, category='academic',
        point=Point(lon, lat, srid=4326),
        is_active=True,
    )


class CachePerformanceBenchmark(TestCase):
    """
    Ensure that cached route lookups are fast enough to support real-time
    React map interactions.  The Django test client is synchronous and
    in-process, so results are conservative (actual HTTP adds ~1–3 ms extra).
    """

    def setUp(self):
        cache.clear()
        self.client = APIClient()
        self.start = _loc('Perf Start Building', lon=42.826, lat=9.356)
        self.end   = _loc('Perf End Building',   lon=42.827, lat=9.357)

    def tearDown(self):
        cache.clear()

    @patch('routing.views.PathfindingService')
    def test_100_requests_average_under_10ms(self, mock_cls):
        """
        After the first request populates the cache, every subsequent call
        should be a sub-millisecond LocMemCache read.  The 10 ms ceiling
        provides generous headroom for CI environment variability.
        """
        mock_svc = MagicMock()
        mock_cls.return_value = mock_svc
        # Side-effects for the single cache-miss call only:
        # find_nearest_node is called twice (start + end), then cached.
        mock_svc.find_nearest_node.side_effect = [(0, 5.0), (1, 8.0)]
        mock_svc.calculate_route.return_value = (
            [0, 1],
            150.0,
            [[42.826, 9.356], [42.827, 9.357]],
        )

        url = (
            f'/api/routing/directions/'
            f'?start_location_id={self.start.id}'
            f'&end_location_id={self.end.id}'
        )

        times_ms: list[float] = []

        for i in range(N_REQUESTS):
            t0 = time.perf_counter()
            r  = self.client.get(url)
            elapsed = (time.perf_counter() - t0) * 1000
            times_ms.append(elapsed)

            # Correctness check on every response
            self.assertEqual(
                r.status_code, 200,
                msg=f'Request #{i+1} failed with status {r.status_code}',
            )

        avg_ms = sum(times_ms) / len(times_ms)
        p95_ms = sorted(times_ms)[int(0.95 * len(times_ms))]

        print(
            f'\n[Benchmark] {N_REQUESTS} requests — '
            f'avg={avg_ms:.2f} ms, p95={p95_ms:.2f} ms, '
            f'max={max(times_ms):.2f} ms'
        )

        self.assertLess(
            avg_ms,
            MAX_AVG_MS,
            msg=(
                f'Average response time {avg_ms:.2f} ms exceeds the '
                f'{MAX_AVG_MS} ms threshold (p95={p95_ms:.2f} ms).'
            ),
        )

    @patch('routing.views.PathfindingService')
    def test_cache_is_populated_after_first_request(self, mock_cls):
        """Service must only be called once; subsequent hits bypass it."""
        mock_svc = MagicMock()
        mock_cls.return_value = mock_svc
        mock_svc.find_nearest_node.side_effect = [(0, 5.0), (1, 8.0)]
        mock_svc.calculate_route.return_value = (
            [0, 1], 150.0, [[42.826, 9.356], [42.827, 9.357]],
        )

        url = (
            f'/api/routing/directions/'
            f'?start_location_id={self.start.id}'
            f'&end_location_id={self.end.id}'
        )

        for _ in range(5):
            self.client.get(url)

        # calculate_route must have been called exactly once (cache-miss only)
        self.assertEqual(mock_svc.calculate_route.call_count, 1)

    @patch('routing.views.PathfindingService')
    def test_cache_miss_and_hit_both_return_identical_payload(self, mock_cls):
        """Cached and fresh responses must be bit-for-bit identical."""
        mock_svc = MagicMock()
        mock_cls.return_value = mock_svc
        mock_svc.find_nearest_node.side_effect = [(0, 5.0), (1, 8.0)]
        mock_svc.calculate_route.return_value = (
            [0, 1], 150.0, [[42.826, 9.356], [42.827, 9.357]],
        )

        url = (
            f'/api/routing/directions/'
            f'?start_location_id={self.start.id}'
            f'&end_location_id={self.end.id}'
        )

        r1 = self.client.get(url)   # cache miss
        r2 = self.client.get(url)   # cache hit

        self.assertEqual(r1.data, r2.data)
