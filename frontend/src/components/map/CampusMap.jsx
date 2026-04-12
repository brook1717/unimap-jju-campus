import { MapContainer, TileLayer } from 'react-leaflet'

import { CAMPUS_CENTER, CAMPUS_BOUNDS, DEFAULT_ZOOM } from '../../utils/constants'

function CampusMap({ children }) {
  return (
    <MapContainer
      center={CAMPUS_CENTER}
      zoom={DEFAULT_ZOOM}
      bounds={CAMPUS_BOUNDS}
      className="h-full w-full"
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {children}
    </MapContainer>
  )
}

export default CampusMap
