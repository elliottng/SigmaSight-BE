'use client';

import React, { createContext, useContext, useReducer, useEffect, ReactNode } from 'react';
import { AuthState, LoginCredentials, User, DemoAccount } from '@/types/auth';
import { apiClient, DEMO_ACCOUNTS } from '@/lib/api';

interface AuthContextType extends AuthState {
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => void;
  demoAccounts: DemoAccount[];
}

const AuthContext = createContext<AuthContextType | null>(null);

type AuthAction = 
  | { type: 'LOGIN_START' }
  | { type: 'LOGIN_SUCCESS'; payload: { user: User; token: string } }
  | { type: 'LOGIN_FAILURE'; payload: { error: string } }
  | { type: 'LOGOUT' }
  | { type: 'RESTORE_AUTH'; payload: { user: User; token: string } };

const initialState: AuthState = {
  user: null,
  token: null,
  isAuthenticated: false,
  isLoading: true,
  error: null,
};

function authReducer(state: AuthState, action: AuthAction): AuthState {
  switch (action.type) {
    case 'LOGIN_START':
      return {
        ...state,
        isLoading: true,
        error: null,
      };
    
    case 'LOGIN_SUCCESS':
      return {
        ...state,
        user: action.payload.user,
        token: action.payload.token,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      };
    
    case 'LOGIN_FAILURE':
      return {
        ...state,
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
        error: action.payload.error,
      };
    
    case 'LOGOUT':
      return {
        ...state,
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,
      };
    
    case 'RESTORE_AUTH':
      return {
        ...state,
        user: action.payload.user,
        token: action.payload.token,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      };
    
    default:
      return state;
  }
}

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [state, dispatch] = useReducer(authReducer, initialState);
  
  // Restore authentication on app load
  useEffect(() => {
    const restoreAuth = async () => {
      try {
        const token = localStorage.getItem('auth_token');
        if (token) {
          const user = await apiClient.getCurrentUser();
          dispatch({ type: 'RESTORE_AUTH', payload: { user, token } });
        } else {
          dispatch({ type: 'LOGOUT' });
        }
      } catch (error) {
        console.error('Failed to restore auth:', error);
        localStorage.removeItem('auth_token');
        dispatch({ type: 'LOGOUT' });
      }
    };
    
    restoreAuth();
  }, []);
  
  const login = async (credentials: LoginCredentials): Promise<void> => {
    dispatch({ type: 'LOGIN_START' });
    
    try {
      const authTokens = await apiClient.login(credentials);
      localStorage.setItem('auth_token', authTokens.access_token);
      
      const user = await apiClient.getCurrentUser();
      dispatch({ 
        type: 'LOGIN_SUCCESS', 
        payload: { user, token: authTokens.access_token } 
      });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Login failed';
      dispatch({ 
        type: 'LOGIN_FAILURE', 
        payload: { error: errorMessage } 
      });
      throw error;
    }
  };
  
  const logout = (): void => {
    localStorage.removeItem('auth_token');
    dispatch({ type: 'LOGOUT' });
  };
  
  const value: AuthContextType = {
    ...state,
    login,
    logout,
    demoAccounts: DEMO_ACCOUNTS,
  };
  
  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}