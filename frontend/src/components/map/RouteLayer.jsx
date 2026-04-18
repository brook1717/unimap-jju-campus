import { useEffect, useMemo } from 'react';
import { Polyline, useMap } from 'react-leaflet';
import L from 'leaflet';

/**
 * Renders a walking-route polyline with a white glow outline.
 * Accepts `route` as a GeoJSON Feature (geometry.type === 'LineString').
 * Auto-fits the map viewport to the route bounds.
 */
export default function RouteLayer({ route = null }) {
  const map = useMap();

  const positions = useMemo(() => {
    if (!route?.geometry?.coordinates) return null;
    return route.geometry.coordinates.map(([lng, lat]) => [lat, lng]);
  }, [route]);

  // Fit map to route bounds
  useEffect(() => {
    if (!positions || positions.length < 2) return;
    const bounds = L.latLngBounds(positions);
    map.fitBounds(bounds, { padding: [50, 50], maxZoom: 18, animate: true });
  }, [positions, map]);

  if (!positions) return null;

  return (
    <>
      {/* White glow / outline */}
      <Polyline
        positions={positions}
        pathOptions={{ color: '#ffffff', weight: 10, opacity: 0.6, lineCap: 'round', lineJoin: 'round' }}
      />
      {/* Signal-blue route */}
      <Polyline
        positions={positions}
        pathOptions={{ color: '#1E4D8C', weight: 6, opacity: 0.9, lineCap: 'round', lineJoin: 'round' }}
      />
    </>
  );
}
