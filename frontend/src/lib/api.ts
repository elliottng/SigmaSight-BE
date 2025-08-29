import axios from 'axios'

export const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? 'https://api.sigmasight.com/v1' 
  : 'http://localhost:8001/api/v1'

// Create axios instance with default config
export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds
})

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor to handle errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Redirect to login on unauthorized
      localStorage.removeItem('auth_token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Helper function to handle API responses
export const handleApiResponse = <T>(response: any): T => {
  if (response.data?.success !== false) {
    return response.data?.data || response.data
  }
  throw new Error(response.data?.errors?.[0]?.message || 'API request failed')
}

// API response types
export interface ApiResponse<T> {
  success: boolean
  data: T
  meta?: {
    timestamp: string
    request_id: string
    execution_time_ms: number
    cache_status?: 'hit' | 'miss' | 'partial'
  }
  errors?: Array<{
    code: string
    message: string
    field?: string
  }>
}

export interface AsyncJobResponse {
  success: boolean
  job_id: string
  status: 'queued' | 'processing' | 'completed' | 'failed'
  poll_url: string
  estimated_duration_ms: number
}

// Auth token management
export const getAuthToken = (): string | null => {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('auth_token')
  }
  return null
}

export const setAuthToken = (token: string): void => {
  if (typeof window !== 'undefined') {
    localStorage.setItem('auth_token', token)
  }
}

export const removeAuthToken = (): void => {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('auth_token')
    localStorage.removeItem('user')
  }
}

// User management
export const getCurrentUser = () => {
  if (typeof window !== 'undefined') {
    const userStr = localStorage.getItem('user')
    return userStr ? JSON.parse(userStr) : null
  }
  return null
}

export const setCurrentUser = (user: any): void => {
  if (typeof window !== 'undefined') {
    localStorage.setItem('user', JSON.stringify(user))
  }
}