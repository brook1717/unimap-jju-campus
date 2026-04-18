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
export const fetchRoute = (startId, endId) => api.get(`/routes/?start=${startId}&end=${endId}`)

export default api
