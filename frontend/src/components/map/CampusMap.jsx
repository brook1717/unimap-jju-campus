import { MapContainer, TileLayer, ZoomControl } from 'react-leaflet';
import '../../utils/fixLeafletIcons';
import { CAMPUS_CENTER, DEFAULT_ZOOM } from '../../utils/constants';

export default function CampusMap({ children }) {
  return (
    <MapContainer
      center={CAMPUS_CENTER}
      zoom={DEFAULT_ZOOM}
      zoomControl={false}
      className="h-full w-full z-0"
      minZoom={14}
      maxZoom={19}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
        url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
        subdomains="abcd"
      />
      {/* Children render before ZoomControl so LocateControl sits above it */}
      {children}
      <ZoomControl position="bottomright" />
    </MapContainer>
  );
}
