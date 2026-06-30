import axios from 'axios'
import { useAuthStore } from '../store/useAuthStore'

// In production (Netlify), use the Render backend URL
// In development, use the Vite proxy (/api)
const BASE_URL = import.meta.env.PROD
  ? (import.meta.env.VITE_API_URL || 'https://novaflix-backend.onrender.com/api')
  : '/api'

const api = axios.create({ baseURL: BASE_URL })

// Attach JWT token to every request
api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// On 401, log the user out
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      useAuthStore.getState().logout()
    }
    return Promise.reject(err)
  }
)

export default api
