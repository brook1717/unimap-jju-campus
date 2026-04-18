import { Marker, Popup } from 'react-leaflet';
import { createCategoryIcon } from '../../utils/mapIcons';

export default function MapMarkers({ locations = [], onSelect }) {
  return (
    <>
      {locations.map((loc) => {
        const [lng, lat] = loc.geometry.coordinates;
        const { name, category } = loc.properties;

        return (
          <Marker
            key={loc.id}
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
      })}
    </>
  );
}
