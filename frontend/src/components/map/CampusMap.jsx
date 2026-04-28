import { MapContainer, TileLayer, LayersControl, ZoomControl } from 'react-leaflet';
import '../../utils/fixLeafletIcons';
import { CAMPUS_CENTER, DEFAULT_ZOOM, CAMPUS_BOUNDS } from '../../utils/constants';
import FlyToHandler from './FlyToHandler';
import useTheme from '../../hooks/useTheme';

const STREET_TILES = {
  light: 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
  dark:  'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
};

const SATELLITE_URL =
  'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}';

const STREET_ATTR =
  '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>';

const SATELLITE_ATTR =
  'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community';

export default function CampusMap({ children, selectedLocation }) {
  const { theme } = useTheme();

  return (
    <MapContainer
      center={CAMPUS_CENTER}
      zoom={DEFAULT_ZOOM}
      zoomControl={false}
      className="h-full w-full z-0"
      minZoom={14}
      maxZoom={20}
      maxBounds={CAMPUS_BOUNDS}
      maxBoundsViscosity={1.0}
    >
      <LayersControl position="topright">
        <LayersControl.BaseLayer name="Street View">
          <TileLayer
            key={`street-${theme}`}
            attribution={STREET_ATTR}
            url={STREET_TILES[theme] || STREET_TILES.light}
            subdomains="abcd"
            maxNativeZoom={19}
            maxZoom={20}
          />
        </LayersControl.BaseLayer>

        <LayersControl.BaseLayer checked name="Satellite">
          <TileLayer
            attribution={SATELLITE_ATTR}
            url={SATELLITE_URL}
            maxNativeZoom={18}
            maxZoom={20}
          />
        </LayersControl.BaseLayer>
      </LayersControl>

      <FlyToHandler target={selectedLocation} />
      {children}
      <ZoomControl position="bottomright" />
    </MapContainer>
  );
}
