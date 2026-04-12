export function isValidGeoJSON(data) {
  return (
    data &&
    typeof data === 'object' &&
    typeof data.type === 'string' &&
    Array.isArray(data.features)
  )
}

export function extractCoordinates(point) {
  if (!point || !Array.isArray(point.coordinates)) return null
  const [lng, lat] = point.coordinates
  return { lat, lng }
}

export function featureCollectionFromLocations(locations) {
  return {
    type: 'FeatureCollection',
    features: locations.map((loc) => ({
      type: 'Feature',
      geometry: loc.point,
      properties: {
        id: loc.id,
        name: loc.name,
        category: loc.category,
      },
    })),
  }
}
