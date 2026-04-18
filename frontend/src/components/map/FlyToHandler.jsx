import { useEffect } from 'react';
import { useMap } from 'react-leaflet';

/**
 * Imperatively flies the map to `target` whenever it changes.
 * `target` is a GeoJSON Feature with geometry.coordinates = [lng, lat].
 */
export default function FlyToHandler({ target }) {
  const map = useMap();

  useEffect(() => {
    if (!target) return;
    const [lng, lat] = target.geometry.coordinates;
    map.flyTo([lat, lng], 18, { animate: true, duration: 1.5 });
  }, [target, map]);

  return null;
}
