'use client'

import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { useRouter } from 'next/navigation'
import { authApi } from '../services/api'
import { setAuthToken, removeAuthToken, getCurrentUser, setCurrentUser } from '../lib/api'
import type { User, LoginRequest, RegisterRequest } from '../lib/types'

interface AuthContextType {
  user: User | null
  loading: boolean
  login: (credentials: LoginRequest) => Promise<void>
  register: (userData: RegisterRequest) => Promise<void>
  logout: () => void
  refreshToken: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

interface AuthProviderProps {
  children: ReactNode
}

export const AuthProvider = ({ children }: AuthProviderProps) => {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const router = useRouter()

  // Initialize auth state from localStorage
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        const storedUser = getCurrentUser()
        if (storedUser) {
          // Verify token is still valid by calling /auth/me
          const currentUser = await authApi.getCurrentUser()
          setUser(currentUser)
          setCurrentUser(currentUser)
        }
      } catch (error) {
        console.error('Failed to initialize auth:', error)
        removeAuthToken()
      } finally {
        setLoading(false)
      }
    }

    initializeAuth()
  }, [])

  const login = async (credentials: LoginRequest) => {
    try {
      const tokenResponse = await authApi.login(credentials)
      setAuthToken(tokenResponse.access_token)
      
      // Use user info from token response (no need for extra API call)
      const userInfo = tokenResponse.user
      setUser(userInfo)
      setCurrentUser(userInfo)
      
      router.push('/dashboard')
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.message || 'Login failed'
      throw new Error(errorMessage)
    }
  }

  const register = async (userData: RegisterRequest) => {
    try {
      const newUser = await authApi.register(userData)
      // After successful registration, log the user in
      await login({ email: userData.email, password: userData.password })
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.message || 'Registration failed'
      throw new Error(errorMessage)
    }
  }

  const logout = () => {
    removeAuthToken()
    setUser(null)
    router.push('/login')
  }

  const refreshToken = async () => {
    try {
      const tokenResponse = await authApi.refreshToken()
      setAuthToken(tokenResponse.access_token)
    } catch (error) {
      console.error('Failed to refresh token:', error)
      logout()
    }
  }

  const value: AuthContextType = {
    user,
    loading,
    login,
    register,
    logout,
    refreshToken,
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}