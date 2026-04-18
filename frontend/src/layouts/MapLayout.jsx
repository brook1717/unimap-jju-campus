import { useState, useEffect } from 'react';
import { fetchLocations } from '../services/api';

import CampusMap from '../components/map/CampusMap';
import MapMarkers from '../components/map/MapMarkers';
import LocateControl from '../components/map/LocateControl';
import SearchCard from '../components/ui/SearchCard';
import MenuButton from '../components/ui/MenuButton';
import SideDrawer from '../components/ui/SideDrawer';

export default function MapLayout() {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [locations, setLocations] = useState([]);

  useEffect(() => {
    fetchLocations()
      .then(({ data }) => setLocations(data?.features ?? []))
      .catch((err) => console.error('Failed to load locations:', err));
  }, []);

  return (
    <div className="relative h-screen w-screen overflow-hidden">
      {/* ── Map canvas (full-screen, z-0) ──────────────────────────────── */}
      <CampusMap>
        <MapMarkers locations={locations} />
        <LocateControl />
      </CampusMap>

      {/* ── Floating UI layer (above map) ──────────────────────────────── */}
      <SearchCard />
      <MenuButton
        isOpen={drawerOpen}
        onClick={() => setDrawerOpen((v) => !v)}
      />
      <SideDrawer
        isOpen={drawerOpen}
        onClose={() => setDrawerOpen(false)}
      />
    </div>
  );
}
