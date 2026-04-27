# UniMap: Jigjiga University Smart Campus Navigation

UniMap is a high-performance geographic information system (GIS) designed to solve the challenge of navigating the dense environment of the Jigjiga University campus.

## Overview

Built with a "Mobile-First" philosophy, UniMap allows students and guests to:

- **Locate** — Find specific blocks, departments, and facilities across campus.
- **Navigate** — Generate shortest walking paths between buildings using A* pathfinding.
- **Identify** — View images and internal facility details for over 80 university blocks.
- **Install** — Add to home screen as a PWA or build as a native Android app via Capacitor.

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Django 4.2, GeoDjango, Django REST Framework, PostGIS |
| **Database** | PostgreSQL 16 + PostGIS 3.4 |
| **Frontend** | React 18 (Vite 5), Tailwind CSS 3, React-Leaflet 4 |
| **PWA** | vite-plugin-pwa, Workbox (CacheFirst for tiles, fonts, images) |
| **Mobile** | Capacitor 8 (Android) |
| **Infra** | Docker, Docker Compose, Gunicorn, WhiteNoise |

## Project Structure

```
unimap-jju-campus/
├── backend/           # Django + GeoDjango API
│   ├── locations/     # CampusLocation model, views, serializers
│   ├── routing/       # A* pathfinding, CampusPath, topology
│   ├── facilities/    # Facility model
│   └── Dockerfile     # Multi-stage production build
├── frontend/          # Vite + React SPA
│   ├── src/           # Components, hooks, services, i18n
│   ├── public/icons/  # PWA icons (192, 512, maskable)
│   ├── vercel.json    # SPA rewrite rules for Vercel
│   └── android/       # Capacitor Android project
├── data/              # GeoJSON topology, CSV datasets
├── docker-compose.yml # Production orchestration
└── .env.example       # Environment variable template
```

## Quick Start

### Backend (Docker)

```bash
cp .env.example .env        # Edit with your values
docker compose up --build    # Starts PostGIS + Django
# Dev override auto-applies (runserver + source mount)
```

### Frontend (Local Dev)

```bash
cd frontend
npm install
npm run dev                  # Vite dev server at :5173
```

### Production Build

```bash
cd frontend
npm run build                # Output in dist/
npm run preview              # Test production build locally at :4173
```

## Frontend Deployment

### Option A: Vercel

1. Push repository to GitHub.
2. Import the project in [Vercel](https://vercel.com).
3. Set **Root Directory** to `frontend`.
4. Set **Framework Preset** to `Vite`.
5. Add environment variable: `VITE_API_BASE_URL` = your backend URL (e.g. `https://api.unimap.example.com/api`).
6. Deploy — `vercel.json` handles SPA rewrites automatically.

### Option B: AWS Amplify

1. Connect your GitHub repository in the Amplify Console.
2. Set **App root** to `frontend`.
3. Set build command: `npm run build`, output directory: `dist`.
4. Add environment variable: `VITE_API_BASE_URL`.
5. Add this custom redirect rule in **Rewrites and redirects**:

| Source | Target | Type |
|---|---|---|
| `</^[^.]+$\|\.(?!(css\|gif\|ico\|jpg\|js\|png\|txt\|svg\|woff\|woff2\|ttf\|map\|json\|webmanifest)$)([^.]+$)/>` | `/index.html` | 200 (Rewrite) |

### Environment Variables (Frontend)

| Variable | Description | Default |
|---|---|---|
| `VITE_API_BASE_URL` | Backend API base URL | `/api` (proxied in dev) |

## Backend Deployment

### Docker (Production)

```bash
# Production — Gunicorn, no source mount
docker compose -f docker-compose.yml up --build -d
```

### Environment Variables (Backend)

| Variable | Description | Default |
|---|---|---|
| `SECRET_KEY` | Django secret key | `dev-insecure-change-me` |
| `DEBUG` | Enable debug mode | `False` |
| `ALLOWED_HOSTS` | Comma-separated hosts | `localhost,127.0.0.1` |
| `DATABASE_URL` | PostGIS connection URL | *(falls back to POSTGRES_* vars)* |
| `POSTGRES_DB` | Database name | `unimap_db` |
| `POSTGRES_USER` | Database user | `unimap_user` |
| `POSTGRES_PASSWORD` | Database password | `unimap_pass` |
| `CORS_ALLOWED_ORIGINS` | Comma-separated frontend origins | Vite dev defaults |
| `GUNICORN_WORKERS` | Gunicorn worker count | `3` |
| `TOPOLOGY_GEOJSON_PATH` | Path to topology GeoJSON | `../data/topology_paths.geojson` |

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/locations/` | GeoJSON FeatureCollection of all locations |
| GET | `/api/locations/autocomplete/?q=` | Search autocomplete (top 20) |
| GET | `/api/locations/nearest/?lat=&lng=` | Nearest location to GPS point |
| GET | `/api/locations/{id}/` | Single location detail |
| GET | `/api/routing/directions/?start_location_id=X&end_location_id=Y` | A* walking route (GeoJSON LineString) |
| GET | `/api/routing/paths/` | All topology edges |
| GET | `/api/docs/` | Swagger UI |
| GET | `/api/redoc/` | ReDoc documentation |

---

*Developed as a Capstone Project for Jigjiga University.*