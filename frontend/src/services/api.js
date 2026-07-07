import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE || 'http://localhost:8001/api/v1',
  timeout: 20000,
})

const token = localStorage.getItem('token')
if (token) {
  api.defaults.headers.common['Authorization'] = `Bearer ${token}`
}

export default api
