import { useState, useEffect, useCallback } from 'react';
import { AnimatePresence } from 'framer-motion';
import { fetchLocations } from '../services/api';
import useOnlineStatus from '../hooks/useOnlineStatus';
import OfflineBanner from '../components/ui/OfflineBanner';

import CampusMap from '../components/map/CampusMap';
import MapMarkers from '../components/map/MapMarkers';
import RouteLayer from '../components/map/RouteLayer';
import LocateControl from '../components/map/LocateControl';
import RecenterControl from '../components/map/RecenterControl';
import SearchCard from '../components/ui/SearchCard';
import LocationDetailsCard from '../components/ui/LocationDetailsCard';
import NavigationCard from '../components/ui/NavigationCard';
import MenuButton from '../components/ui/MenuButton';
import SideDrawer from '../components/ui/SideDrawer';

/*
  UI modes:  'search'     – SearchCard visible
             'details'    – LocationDetailsCard visible
             'navigation' – NavigationCard + RouteLayer visible
*/

export default function MapLayout() {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [locations, setLocations] = useState([]);
  const [selectedLocation, setSelectedLocation] = useState(null);
  const [uiMode, setUiMode] = useState('search');
  const [routeData, setRouteData] = useState(null);
  const [userPosition, setUserPosition] = useState(null);
  const isOnline = useOnlineStatus();

  useEffect(() => {
    fetchLocations()
      .then(({ data }) => setLocations(data?.features ?? []))
      .catch((err) => console.error('Failed to load locations:', err));
  }, []);

  /* ── Callbacks ──────────────────────────────────────────────────────── */

  const handleLocationSelect = useCallback(
    (id) => {
      const loc = locations.find((l) => l.id === id);
      if (loc) {
        setSelectedLocation(loc);
        setUiMode('details');
      }
    },
    [locations],
  );

  const clearSelection = useCallback(() => {
    setSelectedLocation(null);
    setRouteData(null);
    setUiMode('search');
  }, []);

  const startNavigation = useCallback((loc) => {
    setSelectedLocation(loc);
    setRouteData(null);
    setUiMode('navigation');
  }, []);

  const cancelNavigation = useCallback(() => {
    setRouteData(null);
    setUiMode('details');
  }, []);

  const handleRouteReady = useCallback((data) => {
    setRouteData(data ?? null);
  }, []);

  return (
    <div className="relative flex h-screen w-screen flex-col overflow-hidden">
      <OfflineBanner isOffline={!isOnline} />
      {/* ── Map canvas (fills remaining space, z-0) ────────────────────── */}
      <div className="relative flex-1 overflow-hidden">
      <CampusMap selectedLocation={selectedLocation}>
        <MapMarkers
          locations={locations}
          selectedLocationId={selectedLocation?.id}
          onSelect={(loc) => {
            setSelectedLocation(loc);
            setUiMode('details');
          }}
        />
        <RouteLayer route={routeData} />
        <LocateControl
          userPosition={userPosition}
          onUserPosition={setUserPosition}
        />
        <RecenterControl />
      </CampusMap>

      {/* ── Floating UI layer (above map) ──────────────────────────────── */}
      <AnimatePresence mode="wait">
        {uiMode === 'details' && selectedLocation && (
          <LocationDetailsCard
            key="details"
            location={selectedLocation}
            onClose={clearSelection}
            onDirections={startNavigation}
            isOffline={!isOnline}
          />
        )}

        {uiMode === 'navigation' && selectedLocation && (
          <NavigationCard
            key="navigation"
            destination={selectedLocation}
            userPosition={userPosition}
            onRouteReady={handleRouteReady}
            onCancel={cancelNavigation}
          />
        )}
      </AnimatePresence>

      {uiMode === 'search' && (
        <SearchCard onLocationSelect={handleLocationSelect} />
      )}

      <MenuButton
        isOpen={drawerOpen}
        onClick={() => setDrawerOpen((v) => !v)}
      />
      <SideDrawer
        isOpen={drawerOpen}
        onClose={() => setDrawerOpen(false)}
      />
      </div>
    </div>
  );
}
