# UniMap API — Quick Reference

**Version:** 1.0.0  
**Base URL:** `http://localhost:8000`  
**Format:** All responses use [GeoJSON](https://geojson.org/) (`FeatureCollection` for lists, `Feature` for single objects).  
**Interactive docs:** [`/api/docs/`](http://localhost:8000/api/docs/) · [`/api/redoc/`](http://localhost:8000/api/redoc/) · [`/api/schema/`](http://localhost:8000/api/schema/)

---

## Locations — `/api/locations/`

Campus buildings and points of interest. Each feature carries its coordinates in the `geometry.point` field (SRID 4326) and all scalar attributes inside `properties`.

| Method | URL | Description |
|--------|-----|-------------|
| `GET` | `/api/locations/` | Paginated FeatureCollection of all **active** locations (100/page) |
| `GET` | `/api/locations/{id}/` | Single Feature by primary key |
| `GET` | `/api/locations/nearest/` | Nearest active building to a coordinate (PostGIS Distance) |
| `GET` | `/api/locations/?category=<value>` | Filter by category |
| `GET` | `/api/locations/?search=<term>` | Full-text search on `name` and `description` |
| `GET` | `/api/locations/?page=2` | Fetch the next page |

### Category values
`academic` · `classroom` · `office` · `lab` · `library` · `dormitory` · `cafeteria` · `gate` · `facility`

### `/nearest/` query parameters
| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `lat` | float | ✅ | Latitude of the reference point (WGS 84) |
| `lng` | float | ✅ | Longitude of the reference point (WGS 84) |

### Example response — list
```json
{
  "type": "FeatureCollection",
  "count": 123,
  "next": "http://localhost:8000/api/locations/?page=2",
  "previous": null,
  "features": [
    {
      "id": 1,
      "type": "Feature",
      "geometry": { "type": "Point", "coordinates": [42.8266, 9.3570] },
      "properties": {
        "name": "Point 1",
        "slug": "point-1",
        "category": "academic",
        "description": "Academic building...",
        "image": null,
        "is_active": true,
        "facilities": [],
        "entrance_point": null,
        "created_at": "2026-04-15T16:57:22Z",
        "updated_at": "2026-04-15T16:57:22Z"
      }
    }
  ]
}
```

---

## Facilities — `/api/facilities/`

Individual rooms, offices, or labs that belong to a `CampusLocation`. They are also **nested** inside each location's `properties.facilities` array.

| Method | URL | Description |
|--------|-----|-------------|
| `GET` | `/api/facilities/` | Paginated list of all facilities |
| `GET` | `/api/facilities/{id}/` | Single facility by primary key |
| `GET` | `/api/facilities/?location={id}` | Filter by parent CampusLocation |

### Example response
```json
{
  "count": 0,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Registrar Office",
      "description": "Student registration and records.",
      "image": null,
      "location": 5
    }
  ]
}
```

---

## Routing — `/api/routing/`

Walkable path segments between campus locations and the routing engine.

| Method | URL | Description |
|--------|-----|-------------|
| `GET` | `/api/routing/paths/` | FeatureCollection of all CampusPath segments |
| `GET` | `/api/routing/paths/{id}/` | Single CampusPath feature |
| `GET` | `/api/routing/paths/?is_accessible=true` | Wheelchair-accessible paths only |
| `GET` | `/api/routing/paths/?start_location={id}` | Paths starting at a given location |
| `GET` | `/api/routing/paths/?end_location={id}` | Paths ending at a given location |
| `GET` | `/api/routing/route/?start={id}&end={id}` | ⏳ Shortest-path route (NetworkX — coming soon) |

### CampusPath feature structure
```json
{
  "id": 1,
  "type": "Feature",
  "geometry": {
    "type": "LineString",
    "coordinates": [[42.826, 9.357], [42.827, 9.358]]
  },
  "properties": {
    "name": "Path A→B",
    "start_location": 1,
    "end_location": 2,
    "distance_in_meters": 145.3,
    "is_accessible": true
  }
}
```

---

## Documentation & Schema

| URL | Description |
|-----|-------------|
| `GET /api/schema/` | Raw OpenAPI 3.0 schema (YAML download) |
| `GET /api/docs/` | Swagger UI — interactive browser |
| `GET /api/redoc/` | ReDoc — readable reference |

---

## Pagination

All list endpoints use `PageNumberPagination` with **100 items per page**.  
Navigate with `?page=<n>`. The `next` and `previous` links in the response envelope provide absolute URLs.

---

## Filtering & Search Cheat-Sheet

```bash
# Filter locations by category
GET /api/locations/?category=dormitory

# Search across name + description
GET /api/locations/?search=block+a

# Combine filter + search
GET /api/locations/?category=academic&search=registrar

# Nearest building to a GPS coordinate
GET /api/locations/nearest/?lat=9.3571&lng=42.8243

# Filter facilities by parent location
GET /api/facilities/?location=5

# Accessible paths only
GET /api/routing/paths/?is_accessible=true
```
