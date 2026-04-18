import { useState, useEffect, useCallback } from 'react';
import { createPortal } from 'react-dom';
import { Marker } from 'react-leaflet';
import { useMap } from 'react-leaflet';
import L from 'leaflet';
import { Crosshair } from 'lucide-react';
import { userLocationIcon } from '../../utils/mapIcons';

export default function LocateControl() {
  const map = useMap();
  const [userPos, setUserPos] = useState(null);
  const [locating, setLocating] = useState(false);

  // Persistent DOM node for the Leaflet control
  const [container] = useState(() => {
    const div = L.DomUtil.create('div', 'leaflet-control leaflet-bar');
    L.DomEvent.disableClickPropagation(div);
    L.DomEvent.disableScrollPropagation(div);
    return div;
  });

  const handleLocate = useCallback(() => {
    if (!navigator.geolocation) return;
    setLocating(true);
    navigator.geolocation.getCurrentPosition(
      ({ coords }) => {
        const latlng = [coords.latitude, coords.longitude];
        setUserPos(latlng);
        map.flyTo(latlng, 18, { duration: 1.2 });
        setLocating(false);
      },
      () => setLocating(false),
      { enableHighAccuracy: true, timeout: 10000 },
    );
  }, [map]);

  // Register the control with Leaflet's bottomright container
  useEffect(() => {
    const ctrl = L.control({ position: 'bottomright' });
    ctrl.onAdd = () => container;
    ctrl.addTo(map);
    return () => ctrl.remove();
  }, [map, container]);

  return (
    <>
      {/* React portal renders into the Leaflet control DOM node */}
      {createPortal(
        <button
          onClick={handleLocate}
          className="locate-btn"
          title="Locate me"
          aria-label="Locate me"
        >
          {locating ? (
            <span className="block h-4 w-4 animate-spin rounded-full border-2 border-slate-300 border-t-brand-primary" />
          ) : (
            <Crosshair className="h-[18px] w-[18px]" />
          )}
        </button>,
        container,
      )}

      {/* User-position marker (pulsing blue dot) */}
      {userPos && (
        <Marker
          position={userPos}
          icon={userLocationIcon}
          zIndexOffset={1000}
        />
      )}
    </>
  );
}
