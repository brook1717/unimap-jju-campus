import { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { useMap } from 'react-leaflet';
import L from 'leaflet';
import { Compass } from 'lucide-react';
import { CAMPUS_CENTER, DEFAULT_ZOOM } from '../../utils/constants';

export default function RecenterControl() {
  const map = useMap();

  const [container] = useState(() => {
    const div = L.DomUtil.create('div', 'leaflet-control leaflet-bar');
    L.DomEvent.disableClickPropagation(div);
    L.DomEvent.disableScrollPropagation(div);
    return div;
  });

  useEffect(() => {
    const ctrl = L.control({ position: 'bottomright' });
    ctrl.onAdd = () => container;
    ctrl.addTo(map);
    return () => ctrl.remove();
  }, [map, container]);

  const handleRecenter = () => {
    map.flyTo(CAMPUS_CENTER, DEFAULT_ZOOM, { duration: 1.2 });
  };

  return createPortal(
    <button
      onClick={handleRecenter}
      className="locate-btn"
      title="Center to campus"
      aria-label="Center to campus"
    >
      <Compass className="h-[18px] w-[18px]" />
    </button>,
    container,
  );
}
