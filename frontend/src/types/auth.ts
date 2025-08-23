export interface User {
  id: string;
  email: string;
  username: string;
  full_name?: string;
  created_at: string;
  updated_at: string;
  is_active: boolean;
}

export interface AuthTokens {
  access_token: string;
  token_type: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

export interface DemoAccount {
  email: string;
  password: string;
  displayName: string;
  description: string;
}