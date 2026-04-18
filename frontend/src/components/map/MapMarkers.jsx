import { useRef, useEffect } from 'react';
import { Marker, Popup } from 'react-leaflet';
import { createCategoryIcon } from '../../utils/mapIcons';

/* ── Single marker with auto-open-popup support ───────────────────────── */

function LocationMarker({ loc, isSelected, onSelect }) {
  const markerRef = useRef(null);

  useEffect(() => {
    if (isSelected && markerRef.current) {
      markerRef.current.openPopup();
    }
  }, [isSelected]);

  const [lng, lat] = loc.geometry.coordinates;
  const { name, category } = loc.properties;

  return (
    <Marker
      ref={markerRef}
      position={[lat, lng]}
      icon={createCategoryIcon(category)}
      eventHandlers={{ click: () => onSelect?.(loc) }}
    >
      <Popup closeButton={false} className="campus-popup">
        <div className="min-w-[140px]">
          <p className="text-sm font-semibold text-slate-900 leading-snug">
            {name}
          </p>
          <p className="mt-0.5 text-xs capitalize text-slate-500">
            {category}
          </p>
        </div>
      </Popup>
    </Marker>
  );
}

/* ── Marker layer ─────────────────────────────────────────────────────── */

export default function MapMarkers({ locations = [], selectedLocationId, onSelect }) {
  return (
    <>
      {locations.map((loc) => (
        <LocationMarker
          key={loc.id}
          loc={loc}
          isSelected={loc.id === selectedLocationId}
          onSelect={onSelect}
        />
      ))}
    </>
  );
}
