import axios from 'axios'

// API instance yaratish
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
  timeout: parseInt(import.meta.env.VITE_API_TIMEOUT) || 30000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
})

// Request interceptor - token qo'shish
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor - xatolarni ushlash
api.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    const { response } = error

    // Token eskirgan yoki noto'g'ri
    if (response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      localStorage.removeItem('isAuthenticated')
      window.location.href = '/login'
    }

    // Server xatosi
    if (response?.status >= 500) {
      console.error('Server xatosi:', response.data)
    }

    // Xato xabarini qaytarish
    const message = response?.data?.message || response?.data?.error || 'Xatolik yuz berdi'

    return Promise.reject({
      status: response?.status,
      message,
      errors: response?.data?.errors || {}
    })
  }
)

export default api
