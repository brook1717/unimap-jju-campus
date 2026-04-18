/**
 * fixLeafletIcons.js
 * ------------------
 * Vite rewrites asset URLs at build time, which breaks Leaflet's default
 * marker icons (they 404 on marker-icon.png / marker-shadow.png).
 * This module patches L.Icon.Default so the correct bundled paths are used.
 *
 * Import this file once — before any <Marker> renders — to apply the fix.
 */

import L from 'leaflet';
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png';
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';

delete L.Icon.Default.prototype._getIconUrl;

L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});
