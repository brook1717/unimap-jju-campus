import { useRef, useEffect, useState } from 'react';
import { Marker, Popup, useMapEvents } from 'react-leaflet';
import MarkerClusterGroup from 'react-leaflet-cluster';
import { createCategoryIcon, createLabelIcon } from '../../utils/mapIcons';

/* ── Zoom threshold for showing text labels ───────────────────────────── */

const LABEL_ZOOM = 17;

/* ── Single marker with auto-open-popup support ───────────────────────── */

function LocationMarker({ loc, isSelected, onSelect, showLabels }) {
  const markerRef = useRef(null);

  useEffect(() => {
    if (isSelected && markerRef.current) {
      markerRef.current.openPopup();
    }
  }, [isSelected]);

  const [lng, lat] = loc.geometry.coordinates;
  const { name, category } = loc.properties;

  const icon = showLabels
    ? createLabelIcon(category, name)
    : createCategoryIcon(category);

  return (
    <Marker
      ref={markerRef}
      position={[lat, lng]}
      icon={icon}
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

/* ── Marker layer with clustering + zoom-based labels ─────────────────── */

export default function MapMarkers({ locations = [], selectedLocationId, onSelect }) {
  const [showLabels, setShowLabels] = useState(false);

  useMapEvents({
    zoomend(e) {
      setShowLabels(e.target.getZoom() >= LABEL_ZOOM);
    },
  });

  return (
    <MarkerClusterGroup
      chunkedLoading
      maxClusterRadius={50}
      spiderfyOnMaxZoom
      showCoverageOnHover={false}
      zoomToBoundsOnClick
      disableClusteringAtZoom={18}
    >
      {locations.map((loc) => (
        <LocationMarker
          key={loc.id}
          loc={loc}
          isSelected={loc.id === selectedLocationId}
          onSelect={onSelect}
          showLabels={showLabels}
        />
      ))}
    </MarkerClusterGroup>
  );
}
