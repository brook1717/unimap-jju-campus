# Project Specification: UniMap (Jigjiga University Smart Campus)

## 1. Project Overview & Scope
UniMap is a web-based and mobile-ready smart campus navigation system built exclusively for the main campus of Jigjiga University. It provides an interactive map for students, staff, and guests to search for buildings, view internal facilities, and generate walking directions between any two points on campus.

## 2. Tech Stack & Architecture
* **Backend:** Python 3.12, Django, Django REST Framework (DRF), GeoDjango.
* **Database:** PostgreSQL 16 with the PostGIS extension.
* **Frontend:** React 18 (Vite environment), Tailwind CSS, `react-leaflet` (v4 API).
* **Mobile Wrapper:** Capacitor (Targeting Android compilation).
* **Infrastructure:** Docker and Docker-Compose (local development environment).

## 3. User Roles & Core Features
### Actors
1. **System Admin:** Accesses the secured Django backend to manage, edit, and input campus geographic data using visual map tools.
2. **Student/Guest:** Uses the public frontend interface to view maps, search, and get routes. No authentication is required.

### Functional Requirements
1. **Interactive Base Map:** Render the Jigjiga University campus map with categorized, custom-styled markers (Academic Blocks, Offices, Cafeterias, Gates).
2. **Smart Search:** Implement real-time, case-insensitive search by exact building name, partial match, or category filter.
3. **Location Details:** Clicking a map marker or search result opens a detail panel displaying the location's name, image, description, and a list of nested internal facilities.
4. **Pathfinding (Routing):** Users can select a Start and End location. The system must calculate the shortest walking path, draw the GeoJSON route on the map, and display total distance and estimated walking time.

## 4. Database Schema (Core Entities)
* **Model: CampusLocation**
  * `name` (CharField)
  * `category` (ChoiceField: Academic, Office, Lab, Library, Dormitory, Cafeteria, Gate, Facility)
  * `description` (TextField, optional)
  * `image` (ImageField or URLField, optional)
  * `point` (PointField - PostGIS)
* **Model: Facility**
  * `name` (CharField)
  * `description` (TextField)
  * `location` (ForeignKey -> CampusLocation)
* **Model: CampusPath**
  * `start_location` (ForeignKey -> CampusLocation)
  * `end_location` (ForeignKey -> CampusLocation)
  * `path_line` (LineStringField - PostGIS)
  * `distance_in_meters` (FloatField)

## 5. API Data Contracts
* **GeoJSON Standard:** All geographic backend API endpoints (e.g., `/api/locations/`, `/api/routes/`) MUST serialize and return data in valid `GeoJSON` format (`FeatureCollection`, `Point`, `LineString`).
* **Pagination:** Standard list endpoints should be paginated, except for the primary map load which requires the full dataset of coordinates to render markers.

## 6. Strict Engineering Constraints (AI Directives)
* **Routing Calculation:** Do NOT use pure Python loops to calculate routes. The shortest path algorithm (Dijkstra/A*) must be executed using database-level geographic logic (e.g., PostGIS queries or the `networkx` library building an in-memory graph).
* **Frontend Routing (Mobile Compatibility):** Because the React app will be packaged using Capacitor for native mobile, you MUST use `HashRouter` instead of `BrowserRouter` to prevent white-screen routing errors on Android webviews. Set `base: './'` in `vite.config.js`.
* **React Leaflet Version:** Use modern `react-leaflet` v4 functional component syntax. Do not use legacy class-based implementations.
* **Mobile-First UI:** The user interface must be fully responsive. On desktop, use a split-pane layout (left-aligned sidebar). On mobile viewports, the sidebar MUST convert into a touch-friendly bottom-sheet layout.
* **Admin Interface:** Use `OSMGeoAdmin` for the Django Admin panels to allow for visual drag-and-drop editing of geographic points and lines directly in the browser.
* **Workspace Structure:** Maintain a strict separation of concerns. All Python code lives in `/backend`, and all React code lives in `/frontend`.