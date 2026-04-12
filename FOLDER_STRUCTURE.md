unimap-project/                     # ROOT WORKSPACE DIRECTORY
│
├── PROJECT_SPEC.md                 # The 2-page spec sheet for Windsurf
├── FOLDER_STRUCTURE.md             # This file
├── docker-compose.yml              # Spins up PostgreSQL/PostGIS and the Backend
├── .gitignore                      # Root ignore (node_modules, venv, .env, media)
│
├── data/                           # GEOGRAPHIC RAW DATA
│   ├── buildings.csv               # Exported from Google My Maps/Mobile GPS
│   └── paths.geojson               # The walking network lines for routing
│
├── backend/                        # DJANGO / PYTHON ENVIRONMENT
│   ├── Dockerfile                  # Instructions to build the Django container
│   ├── requirements.txt            # Python dependencies (Django, GeoDjango, etc.)
│   ├── .env.example                # Template for database URLs and secret keys
│   ├── manage.py                   # Django execution script
│   │
│   ├── unimap_backend/             # Core Django Settings
│   │   ├── settings.py             # DB, DRF, and GeoDjango configurations
│   │   ├── urls.py                 # Main API router (e.g., /api/locations/)
│   │   └── wsgi.py / asgi.py       # Production server entry points
│   │
│   ├── locations/                  # APP: Buildings & Maps
│   │   ├── models.py               # CampusLocation model (PointField)
│   │   ├── views.py                # Location search and filter API
│   │   ├── serializers.py          # Formats data to GeoJSON
│   │   ├── admin.py                # OSMGeoAdmin configuration for map editing
│   │   └── management/commands/    
│   │       └── import_buildings.py # Script to read data/buildings.csv
│   │
│   ├── facilities/                 # APP: Internal Rooms/Cafes
│   │   ├── models.py               # Facility model (ForeignKey to CampusLocation)
│   │   └── views.py / serializers.py
│   │
│   └── routing/                    # APP: Pathfinding & Navigation
│       ├── models.py               # CampusPath model (LineStringField)
│       ├── views.py                # GET /api/routes/?start=X&end=Y
│       ├── services.py             # Dijkstra / NetworkX / pgRouting logic
│       └── management/commands/    
│           └── import_paths.py     # Script to read data/paths.geojson
│
└── frontend/                       # REACT / VITE / CAPACITOR ENVIRONMENT
    ├── package.json                # Node dependencies (react-leaflet, etc.)
    ├── vite.config.js              # Vite build settings (MUST have base: './')
    ├── tailwind.config.js          # UI styling rules and brand colors
    ├── capacitor.config.ts         # Native mobile wrapper configuration
    │
    ├── android/                    # Generated later in Week 4 by Capacitor
    │
    ├── public/                     # Static assets that bypass the bundler
    │   ├── manifest.json           # PWA configuration for browser installation
    │   └── icons/                  # App icons for the Play Store/Home Screen
    │
    └── src/                        # REACT SOURCE CODE
        ├── main.jsx                # React mount point (HashRouter setup here)
        ├── App.jsx                 # Main layout wrapper
        ├── index.css               # Tailwind imports
        │
        ├── assets/                 # Custom SVG markers and logos
        │
        ├── services/               # API Communication
        │   └── api.js              # Axios or Fetch calls to Django (e.g., fetchLocations)
        │
        ├── components/             # REUSABLE UI PIECES
        │   ├── map/                
        │   │   ├── CampusMap.jsx   # The react-leaflet MapContainer
        │   │   ├── MapMarkers.jsx  # Renders the location pins
        │   │   └── RouteLayer.jsx  # Draws the blue path line
        │   │
        │   ├── ui/                 
        │   │   ├── Sidebar.jsx     # Desktop sidebar / Mobile bottom sheet
        │   │   ├── SearchBar.jsx   # The input field for finding buildings
        │   │   └── DetailPanel.jsx # Shows images, descriptions, and 'Directions' button
        │
        └── utils/                  # Helper Functions
            ├── geoHelpers.js       # Functions to parse/validate GeoJSON
            └── constants.js        # Jigjiga Map bounds, API base URLs