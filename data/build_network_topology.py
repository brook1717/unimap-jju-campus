#!/usr/bin/env python3
"""
build_network_topology.py
─────────────────────────
Five-stage pipeline that converts raw campus path geometry and building
points into a fully connected, routable network:

  1. Load paths.geojson + buildings.csv
  2. Node the network  – snap near-coincident vertices (≤ 2 m) then take
     the GEOS planar union to split every T/X crossing.
  3. Snap buildings  – project each building pin onto its nearest segment,
     split that segment, and add a short "access edge".
  4. Extract graph   – assign integer IDs to every endpoint / intersection;
     emit (start_node, end_node, distance_m) edge records.
  5. Save topology_paths.geojson for QGIS / frontend verification.

Usage
─────
  python build_network_topology.py
  python build_network_topology.py --paths ../data/paths.geojson \\
                                   --buildings ../data/buildings.csv \\
                                   --out ../data/topology_paths.geojson

Dependencies (pip install shapely geopandas networkx)
──────────────────────────────────────────────────────
  shapely  >= 2.0
  geopandas >= 0.14
  networkx  >= 3.2
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

# ── 0. Dependency guard ───────────────────────────────────────────────────────

_MISSING: list[str] = []

try:
    from shapely.geometry import LineString, MultiLineString, Point, mapping
    from shapely.ops import snap, unary_union
    from shapely.strtree import STRtree
except ImportError:
    _MISSING.append("shapely>=2.0")

try:
    import geopandas as gpd
except ImportError:
    _MISSING.append("geopandas>=0.14")

try:
    import networkx as nx
except ImportError:
    _MISSING.append("networkx>=3.2")

if _MISSING:
    print("[ERROR] Missing packages:  pip install " + " ".join(_MISSING))
    sys.exit(1)

# ── Constants ─────────────────────────────────────────────────────────────────

SNAP_TOL    = 0.00002   # ~2 m in decimal degrees at 9 °N
MIN_LEN     = 1e-9      # discard zero-length artefacts
WGS84       = "EPSG:4326"
UTM_37N     = "EPSG:32637"   # UTM Zone 37 N — covers Ethiopia; used for metres

# ── Stage 1 helpers: loading ──────────────────────────────────────────────────

def load_paths(geojson_path: str) -> list[LineString]:
    """Return flat list of LineStrings from a GeoJSON file."""
    gdf = gpd.read_file(geojson_path)
    lines: list[LineString] = []
    for geom in gdf.geometry:
        if geom is None:
            continue
        if geom.geom_type == "LineString":
            lines.append(geom)
        elif geom.geom_type == "MultiLineString":
            lines.extend(geom.geoms)
    return lines


def load_buildings(csv_path: str) -> list[tuple[str, Point]]:
    """Return [(name, Point(lon, lat)), …] from buildings CSV."""
    buildings: list[tuple[str, Point]] = []
    with open(csv_path, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            name = row.get("name", "").strip()
            try:
                lat = float(row["latitude"])
                lon = float(row["longitude"])
            except (KeyError, ValueError, TypeError):
                print(f"  [SKIP] '{name}' – missing or invalid coordinates.")
                continue
            buildings.append((name, Point(lon, lat)))
    return buildings

# ── Stage 2: topological cleaning ────────────────────────────────────────────

def node_network(lines: list[LineString]) -> list[LineString]:
    """
    1. Snap every vertex within SNAP_TOL to collapse near-coincident coords.
    2. Take the GEOS planar union → GEOS splits all T- and X-crossings.
    Returns a list of clean, non-overlapping LineString segments.
    """
    reference = unary_union(lines)
    snapped   = [snap(ln, reference, SNAP_TOL) for ln in lines]
    planar    = unary_union(snapped)

    if planar.geom_type == "LineString":
        raw = [planar]
    elif planar.geom_type == "MultiLineString":
        raw = list(planar.geoms)
    elif planar.geom_type == "GeometryCollection":
        raw = [g for g in planar.geoms if g.geom_type == "LineString"]
    else:
        raw = []

    return [s for s in raw if s.length > MIN_LEN]

# ── Stage 3: building snapping ────────────────────────────────────────────────

def _split_at_point(line: LineString, proj_pt: Point) -> list[LineString]:
    """
    Insert proj_pt into the coordinate list of `line` and return two parts.
    Uses cumulative-distance walking (robust with multi-vertex lines).
    """
    dist   = line.project(proj_pt)
    coords = list(line.coords)
    cum    = 0.0

    for i in range(len(coords) - 1):
        seg_len = Point(coords[i]).distance(Point(coords[i + 1]))
        if cum + seg_len >= dist - 1e-12:
            insert = (proj_pt.x, proj_pt.y)
            p1 = LineString(coords[: i + 1] + [insert])
            p2 = LineString([insert]         + coords[i + 1 :])
            return [p for p in (p1, p2) if p.length > MIN_LEN]
        cum += seg_len

    return [line]


def snap_buildings(
    buildings: list[tuple[str, Point]],
    segments:  list[LineString],
) -> tuple[list[LineString], list[dict], int]:
    """
    For each building pin:
      a) Find nearest segment (STRtree, rebuilt each iteration after splits).
      b) Project the pin onto that segment → `proj_pt`.
      c) Unless proj_pt is already at an endpoint, split the segment there.
      d) Add a short access-edge LineString(building_pin → proj_pt).

    Returns (updated_segments, access_edge_dicts, snapped_count).
    """
    current_segs   = list(segments)
    access_edges:  list[dict] = []
    snapped_count  = 0

    for bname, bpt in buildings:
        tree = STRtree(current_segs)
        idx  = tree.nearest(bpt)
        seg  = current_segs[idx]

        proj_pt = seg.interpolate(seg.project(bpt))

        start_dist = proj_pt.distance(Point(seg.coords[0]))
        end_dist   = proj_pt.distance(Point(seg.coords[-1]))
        at_endpoint = (start_dist < SNAP_TOL or end_dist < SNAP_TOL)

        if not at_endpoint:
            parts = _split_at_point(seg, proj_pt)
            if len(parts) == 2:
                current_segs.pop(idx)
                current_segs.extend(parts)

        if bpt.distance(proj_pt) > MIN_LEN:
            access_edges.append(
                {
                    "geometry":      LineString([bpt, proj_pt]),
                    "building_name": bname,
                    "is_access":     True,
                }
            )

        snapped_count += 1

    return current_segs, access_edges, snapped_count

# ── Stage 4: graph extraction ─────────────────────────────────────────────────

def extract_graph(
    segments:     list[LineString],
    access_edges: list[dict],
) -> tuple[dict, list[dict]]:
    """
    Collect every segment endpoint as a node (rounding to 7 dp to merge
    near-identical coords), assign integer IDs, and return edge records.
    """
    node_map: dict[tuple[float, float], dict] = {}
    _next_id = [0]

    def node_id(pt: Point) -> int:
        key = (round(pt.x, 7), round(pt.y, 7))
        if key not in node_map:
            node_map[key] = {"id": _next_id[0], "x": key[0], "y": key[1]}
            _next_id[0] += 1
        return node_map[key]["id"]

    all_items = (
        [{"geometry": s, "building_name": None, "is_access": False} for s in segments]
        + access_edges
    )

    edges: list[dict] = []
    for item in all_items:
        geom = item["geometry"]
        if geom.length < MIN_LEN:
            continue
        edges.append(
            {
                "start_node":   node_id(Point(geom.coords[0])),
                "end_node":     node_id(Point(geom.coords[-1])),
                "geometry":     geom,
                "is_access":    item["is_access"],
                "building":     item["building_name"],
            }
        )

    return node_map, edges

# ── Stage 5: output ───────────────────────────────────────────────────────────

def save_geojson(edges: list[dict], out_path: str) -> None:
    """Batch-reproject to UTM for accurate metre distances, then write GeoJSON."""
    geoms = [e["geometry"] for e in edges]
    utm_lengths = (
        gpd.GeoDataFrame(geometry=geoms, crs=WGS84)
        .to_crs(UTM_37N)
        .geometry.length.tolist()
    )

    features = [
        {
            "type": "Feature",
            "properties": {
                "start_node":    e["start_node"],
                "end_node":      e["end_node"],
                "distance_m":    round(dist_m, 2),
                "is_access_path": e["is_access"],
                "building_name": e["building"],
            },
            "geometry": mapping(e["geometry"]),
        }
        for e, dist_m in zip(edges, utm_lengths)
    ]

    fc = {"type": "FeatureCollection", "features": features}
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(fc, fh, separators=(",", ": "), indent=2)

    print(f"  -> {len(features)} edge(s) written to {out_path}")

# ── Main pipeline ─────────────────────────────────────────────────────────────

def main() -> None:
    ap = argparse.ArgumentParser(
        description="Build a routable campus network from raw GeoJSON paths + CSV buildings."
    )
    ap.add_argument("--paths",     default="paths.geojson",        help="Input path GeoJSON")
    ap.add_argument("--buildings", default="buildings.csv",         help="Input buildings CSV")
    ap.add_argument("--out",       default="topology_paths.geojson",help="Output topology GeoJSON")
    args = ap.parse_args()

    # ─ 1. Load ────────────────────────────────────────────────────────────────
    print("\n[1/5] Loading ...")
    raw_lines = load_paths(args.paths)
    buildings = load_buildings(args.buildings)
    print(f"  {len(raw_lines)} raw path segment(s)  |  {len(buildings)} building pin(s)")

    # ─ 2. Node the network ────────────────────────────────────────────────────
    print("[2/5] Snapping vertices + resolving crossings (GEOS planar union) ...")
    clean_segs = node_network(raw_lines)
    crossings  = max(0, len(clean_segs) - len(raw_lines))
    print(f"  {len(raw_lines)} raw -> {len(clean_segs)} clean segment(s)  "
          f"(~{crossings} crossing intersection(s) resolved)")

    # ─ 3. Snap buildings ──────────────────────────────────────────────────────
    print("[3/5] Projecting buildings onto nearest path segment ...")
    final_segs, access_edges, snapped = snap_buildings(buildings, clean_segs)
    print(f"  {snapped} building(s) snapped  |  {len(access_edges)} access edge(s) created")

    # ─ 4. Extract graph ───────────────────────────────────────────────────────
    print("[4/5] Extracting nodes and edges ...")
    node_map, edges = extract_graph(final_segs, access_edges)
    print(f"  {len(node_map)} unique node(s)  |  {len(edges)} edge(s)")

    # ─ 5. Write output ────────────────────────────────────────────────────────
    print(f"[5/5] Computing UTM distances and writing {args.out} ...")
    save_geojson(edges, args.out)

    # ─ Summary ────────────────────────────────────────────────────────────────
    print(
        f"\n{'='*50}\n"
        f"  Crossings resolved : ~{crossings}\n"
        f"  Buildings snapped  :  {snapped}\n"
        f"  Graph nodes        :  {len(node_map)}\n"
        f"  Graph edges        :  {len(edges)}\n"
        f"  Output             :  {args.out}\n"
        f"{'='*50}"
    )


if __name__ == "__main__":
    main()
