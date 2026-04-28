<p align="center">
  <img src="frontend/public/icons/icon-192x192.png" alt="UniMap Logo" width="96" />
</p>

<h1 align="center">UniMap — Smart Campus Navigation System</h1>

<p align="center">
  <strong>Jigjiga University &middot; Graduation Capstone Project</strong><br />
  A full-stack, mobile-first Geographic Information System (GIS) for real-time campus wayfinding.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/React-18.2-61DAFB?logo=react&logoColor=white" alt="React" />
  <img src="https://img.shields.io/badge/Django-4.2-092E20?logo=django&logoColor=white" alt="Django" />
  <img src="https://img.shields.io/badge/PostGIS-3.4-336791?logo=postgresql&logoColor=white" alt="PostGIS" />
  <img src="https://img.shields.io/badge/Leaflet-1.9-199900?logo=leaflet&logoColor=white" alt="Leaflet" />
  <img src="https://img.shields.io/badge/PWA-Installable-5A0FC8?logo=pwa&logoColor=white" alt="PWA" />
  <img src="https://img.shields.io/badge/License-MIT-yellow" alt="License" />
</p>

---

## 📋 Table of Contents

1. [Abstract](#-abstract)
2. [Key Features](#-key-features)
3. [Technology Stack](#-technology-stack)
4. [System Architecture](#-system-architecture)
5. [Project Structure](#-project-structure)
6. [Getting Started](#-getting-started)
7. [Deployment](#-deployment)
8. [API Reference](#-api-reference)
9. [Environment Variables](#-environment-variables)
10. [Testing](#-testing)
11. [Performance](#-performance)
12. [Localization](#-localization)
13. [Contributing](#-contributing)
14. [License](#-license)
15. [Acknowledgements](#-acknowledgements)

---

## 📄 Abstract

Navigating large university campuses presents a recurring challenge for new students, visitors, and staff, particularly when physical signage is limited or outdated. **UniMap** addresses this problem by providing an interactive, map-based navigation system tailored specifically for the Jigjiga University (JJU) campus.

The system catalogs **120+ campus buildings** across 17 facility categories, renders them on a high-resolution satellite/street map, and computes optimal walking routes between any two points using the **A\* (A-star) pathfinding algorithm** over a custom campus topology graph. The application is delivered as a **Progressive Web App (PWA)** with offline resilience and can be compiled to a **native Android APK** via Capacitor.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 🗺️ **Interactive Campus Map** | Satellite and street tile layers with smooth zoom (14–20), pan constraints, and dark mode |
| 🔍 **Instant Search** | Ranked full-text search with autocomplete across building names, categories, and descriptions |
| 🧭 **A\* Wayfinding** | Shortest walking path computation over a 660-edge campus topology graph |
| 📍 **GPS Locate** | Browser geolocation with pulsing blue-dot marker and one-tap recenter |
| 📦 **Marker Clustering** | Automatic grouping of nearby markers at low zoom levels to prevent visual clutter |
| 🏷️ **Zoom-Based Labels** | Building name labels that appear only at high zoom (≥ 17) for a clean overview |
| 📱 **Progressive Web App** | Installable on any device; Workbox caches tiles, fonts, and API responses for offline use |
| 🤖 **Native Android** | Capacitor 8 bridge generates a production APK from the same React codebase |
| 🌍 **Trilingual UI** | Full localization in English, Amharic (አማርኛ), and Somali (Soomaali) |
| 🌙 **Dark Mode** | System-aware theme toggle with consistent contrast across all UI components |
| ♿ **Accessibility** | ARIA labels, keyboard navigation, semantic HTML, and WCAG-compliant color contrast |
| 📶 **Offline Banner** | Real-time network detection with graceful UI degradation when connectivity is lost |

---

## 🛠️ Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Frontend** | React 18, Vite 5, Tailwind CSS 3 | Component-based SPA with hot-reload development |
| **Mapping** | React-Leaflet 4, Leaflet 1.9, react-leaflet-cluster | Interactive map rendering with clustering |
| **Animation** | Framer Motion 12 | Spring-physics UI transitions and gesture handling |
| **Icons** | Lucide React + custom SVG | Consistent iconography (240+ icons) |
| **i18n** | react-i18next, i18next | Runtime language switching (EN / AM / SO) |
| **PWA** | vite-plugin-pwa, Workbox | Service worker generation, precaching, runtime caching |
| **Mobile** | Capacitor 8 | Native Android bridge and APK compilation |
| **Backend** | Django 4.2, Django REST Framework | RESTful API with GeoJSON serialization |
| **GIS Engine** | GeoDjango, PostGIS 3.4 | Spatial queries (nearest-neighbor, bounding-box) |
| **Pathfinding** | NetworkX (Python) | A\* shortest-path computation on campus graph |
| **Database** | PostgreSQL 16 + PostGIS | Spatial-indexed storage for locations and topology |
| **Containerization** | Docker, Docker Compose | Reproducible multi-service orchestration |
| **Production Server** | Gunicorn, WhiteNoise | WSGI application server with static file compression |

---

## 🏗️ System Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                        Client (Browser / PWA / Android)          │
│  React 18 + Leaflet Map + Service Worker (Workbox)               │
└──────────────┬───────────────────────────────────────────────────┘
               │  HTTPS  (JSON / GeoJSON)
               ▼
┌──────────────────────────────────────────────────────────────────┐
│                   Django REST Framework API                       │
│  /api/locations/  ·  /api/routing/directions/  ·  /api/docs/     │
├──────────────────────────────────────────────────────────────────┤
│  GeoDjango ORM  ←→  PostGIS 3.4  ←→  PostgreSQL 16              │
│  NetworkX A* Pathfinding Service (Singleton, cached 15 min)      │
└──────────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
unimap-jju-campus/
├── backend/                    # Django + GeoDjango REST API
│   ├── locations/              # CampusLocation model, views, serializers
│   ├── routing/                # A* pathfinding service, topology loader
│   ├── facilities/             # Internal facility model
│   ├── unimap_backend/         # Project settings, URLs, exception handler
│   ├── tests/                  # 58 unit/integration tests
│   ├── Dockerfile              # Multi-stage production image
│   └── entrypoint.sh           # wait-for-db → migrate → collectstatic → gunicorn
│
├── frontend/                   # Vite + React SPA
│   ├── src/
│   │   ├── components/
│   │   │   ├── map/            # CampusMap, MapMarkers, RouteLayer, LocateControl, RecenterControl
│   │   │   └── ui/             # SearchCard, LocationDetailsCard, NavigationCard, SideDrawer, ...
│   │   ├── hooks/              # useTheme, useOnlineStatus, useMediaQuery
│   │   ├── layouts/            # MapLayout (main orchestrator)
│   │   ├── services/           # Axios API client
│   │   ├── utils/              # mapIcons, constants, fixLeafletIcons
│   │   └── i18n/locales/       # en.json, am.json, so.json
│   ├── public/icons/           # PWA icons (192, 512, maskable variants)
│   ├── scripts/                # generate-icons.mjs (sharp)
│   └── android/                # Capacitor Android project (gitignored)
│
├── data/                       # Source datasets
│   ├── buildings.csv           # 120+ buildings with GPS coordinates
│   └── topology_paths.geojson  # 660-edge walking path network
│
├── docker-compose.yml          # Production: PostGIS + Django (Gunicorn)
├── docker-compose.override.yml # Development: runserver + source mount
├── .env.example                # Environment variable template (no secrets)
└── .gitignore                  # Comprehensive ignore rules
```

---

## 🚀 Getting Started

### Prerequisites

- **Node.js** ≥ 18 and **npm** ≥ 9 (frontend)
- **Docker** and **Docker Compose** v2 (backend)
- **Git**

### 1. Clone the Repository

```bash
git clone https://github.com/brook1717/unimap-jju-campus.git
cd unimap-jju-campus
```

### 2. Start the Backend

```bash
cp .env.example .env                  # Edit with your own SECRET_KEY and passwords
docker compose up --build             # Starts PostGIS + Django (dev mode auto-applies)
```

The API will be available at `http://localhost:8000/api/`.

**Seed sample data:**

```bash
docker compose exec web python manage.py seed_campus
```

### 3. Start the Frontend

```bash
cd frontend
npm install
npm run dev                           # Vite dev server → http://localhost:5173
```

### 4. Production Build

```bash
cd frontend
npm run build                         # Optimized output in dist/
npm run preview                       # Preview locally at http://localhost:4173
```

---

## ☁️ Deployment

### Frontend — AWS S3 + CloudFront

1. **Build** the production bundle:

```bash
cd frontend
npm run build
```

2. **Sync** to your S3 bucket:

```bash
aws s3 sync dist/ s3://YOUR_BUCKET_NAME \
  --delete \
  --cache-control "public, max-age=31536000, immutable" \
  --exclude "index.html" \
  --exclude "sw.js" \
  --exclude "registerSW.js" \
  --exclude "manifest.webmanifest"

aws s3 cp dist/index.html s3://YOUR_BUCKET_NAME/index.html \
  --cache-control "no-cache, no-store, must-revalidate"

aws s3 cp dist/sw.js s3://YOUR_BUCKET_NAME/sw.js \
  --cache-control "no-cache, no-store, must-revalidate"

aws s3 cp dist/registerSW.js s3://YOUR_BUCKET_NAME/registerSW.js \
  --cache-control "no-cache, no-store, must-revalidate"

aws s3 cp dist/manifest.webmanifest s3://YOUR_BUCKET_NAME/manifest.webmanifest \
  --cache-control "no-cache, no-store, must-revalidate"
```

3. **Invalidate** the CloudFront cache:

```bash
aws cloudfront create-invalidation \
  --distribution-id YOUR_DISTRIBUTION_ID \
  --paths "/index.html" "/sw.js" "/registerSW.js" "/manifest.webmanifest"
```

> **Note:** Hashed assets (`/assets/*`) are immutable and do not need cache invalidation. Only `index.html`, `sw.js`, `registerSW.js`, and `manifest.webmanifest` should be invalidated on each deploy.

### Frontend — Vercel (Alternative)

1. Import the repository in [Vercel](https://vercel.com).
2. Set **Root Directory** to `frontend`, **Framework Preset** to `Vite`.
3. Add environment variable: `VITE_API_BASE_URL` = your backend API URL.
4. Deploy — `vercel.json` handles SPA rewrites automatically.

### Backend — Docker (Production)

```bash
docker compose -f docker-compose.yml up --build -d
```

This starts **PostgreSQL 16 + PostGIS 3.4** and **Django with Gunicorn**, with WhiteNoise serving static files and Brotli compression.

---

## 📡 API Reference

All endpoints return JSON. Spatial endpoints use the [GeoJSON](https://geojson.org/) specification.

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/locations/` | GeoJSON FeatureCollection — filter by `category`, search by `search` param |
| `GET` | `/api/locations/autocomplete/?q=` | Top 20 results ranked by relevance `[{id, name, slug, category}]` |
| `GET` | `/api/locations/nearest/?lat=&lng=` | Nearest location to a GPS coordinate (PostGIS) |
| `GET` | `/api/locations/{id}/` | Single location detail (GeoJSON Feature) |
| `GET` | `/api/routing/directions/?start_location_id=X&end_location_id=Y` | A\* walking route (GeoJSON LineString + distance + ETA) |
| `GET` | `/api/routing/paths/` | All 660 topology edges (for debug/visualization) |
| `GET` | `/api/docs/` | Swagger UI (interactive API explorer) |
| `GET` | `/api/redoc/` | ReDoc (API documentation) |
| `GET` | `/api/schema/` | OpenAPI 3.0 schema (YAML) |

**Error Format** (consistent across all endpoints):

```json
{
  "error": "ErrorType",
  "message": "Human-readable description.",
  "status_code": 400
}
```

---

## 🔐 Environment Variables

### Backend

| Variable | Description | Default |
|---|---|---|
| `SECRET_KEY` | Django secret key | `dev-insecure-change-me` |
| `DEBUG` | Enable debug mode | `False` |
| `ALLOWED_HOSTS` | Comma-separated hosts | `localhost,127.0.0.1` |
| `DATABASE_URL` | PostGIS connection URL | *(falls back to POSTGRES_\* vars)* |
| `POSTGRES_DB` | Database name | `unimap_db` |
| `POSTGRES_USER` | Database user | `unimap_user` |
| `POSTGRES_PASSWORD` | Database password | `unimap_pass` |
| `CORS_ALLOWED_ORIGINS` | Comma-separated frontend origins | Vite dev defaults |
| `GUNICORN_WORKERS` | Gunicorn worker count | `3` |
| `TOPOLOGY_GEOJSON_PATH` | Path to topology GeoJSON file | `../data/topology_paths.geojson` |

### Frontend

| Variable | Description | Default |
|---|---|---|
| `VITE_API_BASE_URL` | Backend API base URL | `/api` (proxied in dev) |

---

## 🧪 Testing

### Backend (58 Tests)

```bash
docker compose exec web python manage.py test tests
```

| Suite | Tests | Coverage |
|---|---|---|
| `SearchRankingTests` | 8 | Full-text search ordering and filtering |
| `AutocompleteTests` | 9 | Autocomplete ranking, limits, edge cases |
| `LoadTopologyCommandTests` | 11 | GeoJSON import, idempotency, error handling |
| `PathfindingServiceTests` | 8 | A\* correctness, graph construction, singleton |
| `DirectionsAPITests` | 21 | Route computation, caching, boundary validation |
| `CachePerformanceBenchmark` | 3 | p95 < 10 ms for cached route lookups |

---

## ⚡ Performance

| Metric | Value |
|---|---|
| **Frontend Build** | ~14 s (Vite 5, code-split into 5 chunks) |
| **Total Bundle (gzip)** | ~217 KB (React + Leaflet + Motion + i18n) |
| **PWA Precache** | 22 entries, ~709 KB |
| **Cached API Response** | p95 = 7.57 ms, avg = 3.45 ms |
| **Topology Graph** | 660 edges, loaded once (singleton) |

---

## 🌍 Localization

UniMap supports three languages, switchable at runtime from the side drawer:

| Code | Language | Script |
|---|---|---|
| `en` | English | Latin |
| `am` | Amharic | Ge'ez (አማርኛ) |
| `so` | Somali | Latin (Soomaali) |

Translation files are located in `frontend/src/i18n/locales/`.

---

## 🤝 Contributing

1. Fork the repository.
2. Create a feature branch: `git checkout -b feat/your-feature`.
3. Commit with [Conventional Commits](https://www.conventionalcommits.org/): `git commit -m "feat(map): add building floor plans"`.
4. Push and open a Pull Request.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

## 🙏 Acknowledgements

- **Jigjiga University** — Department of Software Engineering, for academic supervision and campus access.
- **OpenStreetMap** contributors and **CARTO** for base map tiles.
- **Esri** for satellite imagery tiles.
- The open-source communities behind React, Django, Leaflet, PostGIS, and NetworkX.

---

<p align="center">
  <strong>Developed by Biruk Kasahun</strong><br />
  Capstone Project &middot; Jigjiga University &middot; 2024–2025
</p>