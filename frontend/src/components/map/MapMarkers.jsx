import { Marker, Popup } from 'react-leaflet'

function MapMarkers({ locations = [], onSelect }) {
  return (
    <>
      {locations.map((loc) => {
        const [lng, lat] = loc.geometry.coordinates
        return (
          <Marker
            key={loc.id}
            position={[lat, lng]}
            eventHandlers={{ click: () => onSelect && onSelect(loc) }}
          >
            <Popup>{loc.properties.name}</Popup>
          </Marker>
        )
      })}
    </>
  )
}

export default MapMarkers
