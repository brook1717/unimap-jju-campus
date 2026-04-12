import { Polyline } from 'react-leaflet'

function RouteLayer({ route = null }) {
  if (!route) return null

  const positions = route.coordinates.map(([lng, lat]) => [lat, lng])

  return <Polyline positions={positions} color="#1E4D8C" weight={4} opacity={0.85} />
}

export default RouteLayer
