import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE || 'http://localhost:8001/api/v1',
  timeout: 20000,
})

export default api
