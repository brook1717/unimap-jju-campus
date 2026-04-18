import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const fetchLocations = () => api.get('/locations/')
export const fetchAutocomplete = (q) => api.get('/locations/autocomplete/', { params: { q } })
export const fetchFacilities = (locationId) => api.get(`/facilities/?location=${locationId}`)
export const fetchDirections = (startId, endId) =>
  api.get('/routing/directions/', { params: { start_location_id: startId, end_location_id: endId } })
export const fetchNearestLocation = (lat, lng) =>
  api.get('/locations/nearest/', { params: { lat, lng } })

export default api
