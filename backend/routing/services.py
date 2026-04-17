"""
routing/services.py
-------------------
PathfindingService — thread-safe singleton that builds an in-memory NetworkX
graph from topology_paths.geojson on first use, then answers A* route queries
in subsequent calls without reloading.

Graph layout
  Nodes  : integer IDs (0 … N-1) with x/y attributes (WGS-84 lon/lat)
  Edges  : undirected, weight = distance_m, coords = [[lon,lat], …]
"""

import json
import logging
import math
import threading
import time
from pathlib import Path

import networkx as nx
from django.conf import settings

logger = logging.getLogger(__name__)


# ── Haversine helper ──────────────────────────────────────────────────────────

def _haversine_m(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    """Return geodesic distance in metres between two WGS-84 coordinates."""
    R = 6_371_000.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi  = math.radians(lat2 - lat1)
    dlam  = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))


def _resolve_topology_path() -> str:
    """Return the filesystem path to topology_paths.geojson."""
    # 1. Explicit Django setting
    explicit = getattr(settings, 'TOPOLOGY_GEOJSON_PATH', None)
    if explicit and Path(explicit).exists():
        return explicit

    # 2. Relative to BASE_DIR (local dev: backend/../data/)
    candidate = Path(settings.BASE_DIR).parent / 'data' / 'topology_paths.geojson'
    if candidate.exists():
        return str(candidate)

    # 3. Docker volume mount
    docker_path = Path('/data/topology_paths.geojson')
    if docker_path.exists():
        return str(docker_path)

    raise FileNotFoundError(
        'topology_paths.geojson not found. '
        'Run data/build_network_topology.py and set TOPOLOGY_GEOJSON_PATH in settings.'
    )


# ── PathfindingService ────────────────────────────────────────────────────────

class PathfindingService:
    """
    Singleton.  The NetworkX graph is built once on first access and cached
    in memory for the lifetime of the Django process.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    inst = super().__new__(cls)
                    inst._graph = None
                    cls._instance = inst
        return cls._instance

    # ── Graph access ──────────────────────────────────────────────────────────

    @property
    def graph(self) -> nx.Graph:
        if self._graph is None:
            with self._lock:
                if self._graph is None:
                    self._graph = self._build_graph()
        return self._graph

    def _build_graph(self) -> nx.Graph:
        topo_path = _resolve_topology_path()
        t0 = time.perf_counter()

        with open(topo_path, encoding='utf-8') as fh:
            fc = json.load(fh)

        G = nx.Graph()

        for feat in fc['features']:
            props  = feat['properties']
            coords = feat['geometry']['coordinates']  # [[lon,lat], ...]

            start_id = props['start_node']
            end_id   = props['end_node']
            dist_m   = props['distance_m'] or 0.0

            # Register nodes with their WGS-84 position.
            if start_id not in G:
                G.add_node(start_id, x=coords[0][0], y=coords[0][1])
            if end_id not in G:
                G.add_node(end_id, x=coords[-1][0], y=coords[-1][1])

            G.add_edge(
                start_id, end_id,
                weight=dist_m,
                coords=coords,
                is_access=props.get('is_access_path', False),
                building=props.get('building_name'),
            )

        elapsed_ms = (time.perf_counter() - t0) * 1000
        logger.info(
            'Graph loaded from %s: %d nodes, %d edges in %.1f ms',
            topo_path, G.number_of_nodes(), G.number_of_edges(), elapsed_ms,
        )
        return G

    # ── Public API ────────────────────────────────────────────────────────────

    def find_nearest_node(self, lon: float, lat: float) -> tuple[int, float]:
        """
        Return (node_id, distance_m) of the graph node closest to (lon, lat).
        Linear scan over ≤ 579 nodes — fast enough without a spatial index.
        """
        best_id, best_dist = None, float('inf')
        for nid, data in self.graph.nodes(data=True):
            d = _haversine_m(lon, lat, data['x'], data['y'])
            if d < best_dist:
                best_dist = d
                best_id   = nid
        return best_id, best_dist

    def calculate_route(
        self, start_node: int, end_node: int
    ) -> tuple[list[int], float, list[list[float]]]:
        """
        Run A* from start_node to end_node.

        Returns
        -------
        path_nodes  : ordered list of node IDs traversed
        total_dist  : sum of edge weights in metres
        route_coords: flat [[lon, lat], …] coordinate sequence for a LineString
        """
        t0 = time.perf_counter()

        def heuristic(u: int, v: int) -> float:
            nu, nv = self.graph.nodes[u], self.graph.nodes[v]
            return _haversine_m(nu['x'], nu['y'], nv['x'], nv['y'])

        path = nx.astar_path(
            self.graph, start_node, end_node,
            heuristic=heuristic,
            weight='weight',
        )

        total_dist = sum(
            self.graph[u][v]['weight']
            for u, v in zip(path[:-1], path[1:])
        )

        route_coords = self._reconstruct_geometry(path)

        elapsed_ms = (time.perf_counter() - t0) * 1000
        logger.info(
            'A* %d->%d: %d hops, %.1f m, %.1f ms',
            start_node, end_node, len(path), total_dist, elapsed_ms,
        )
        return path, total_dist, route_coords

    # ── Geometry reconstruction ───────────────────────────────────────────────

    def _reconstruct_geometry(self, path: list[int]) -> list[list[float]]:
        """
        Walk the node path, stitch together edge coordinate arrays in the
        correct traversal direction, and return a deduplicated coordinate list.
        """
        full: list[list[float]] = []

        for u, v in zip(path[:-1], path[1:]):
            edge    = self.graph[u][v]
            coords  = edge['coords']
            node_u  = self.graph.nodes[u]

            # Determine traversal direction by comparing the edge's first
            # coordinate with node u's stored position.
            first = coords[0]
            forward = (
                abs(first[0] - node_u['x']) < 1e-6 and
                abs(first[1] - node_u['y']) < 1e-6
            )
            segment = coords if forward else list(reversed(coords))

            if full:
                full.extend(segment[1:])   # skip duplicate junction point
            else:
                full.extend(segment)

        return full
