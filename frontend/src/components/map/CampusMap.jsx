import { MapContainer, TileLayer, ZoomControl } from 'react-leaflet';
import '../../utils/fixLeafletIcons';
import { CAMPUS_CENTER, DEFAULT_ZOOM } from '../../utils/constants';
import FlyToHandler from './FlyToHandler';
import useTheme from '../../hooks/useTheme';

const TILE_URLS = {
  light: 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
  dark:  'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
};

export default function CampusMap({ children, selectedLocation }) {
  const { theme } = useTheme();

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
        key={theme}
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
        url={TILE_URLS[theme] || TILE_URLS.light}
        subdomains="abcd"
      />
      <FlyToHandler target={selectedLocation} />
      {children}
      <ZoomControl position="bottomright" />
    </MapContainer>
  );
}
