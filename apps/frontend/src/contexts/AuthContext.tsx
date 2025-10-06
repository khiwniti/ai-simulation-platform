'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';
import { apiClient } from '../lib/api/client';

interface User {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  company?: string;
  role: string;
  subscriptionTier: string;
  isVerified: boolean;
  createdAt: string;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (userData: {
    firstName: string;
    lastName: string;
    email: string;
    password: string;
    company?: string;
  }) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const token = apiClient.getToken();
      if (!token) {
        setLoading(false);
        return;
      }

      const response = await apiClient.verifyToken();
      if (response.valid && response.user) {
        setUser(response.user);
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      apiClient.clearToken();
    } finally {
      setLoading(false);
    }
  };

  const login = async (email: string, password: string) => {
    try {
      const response = await apiClient.login({ email, password });
      if (response.user) {
        setUser(response.user);
      }
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  };

  const register = async (userData: {
    firstName: string;
    lastName: string;
    email: string;
    password: string;
    company?: string;
  }) => {
    try {
      const response = await apiClient.register(userData);
      if (response.user) {
        setUser(response.user);
      }
    } catch (error) {
      console.error('Registration failed:', error);
      throw error;
    }
  };

  const logout = () => {
    apiClient.logout();
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        register,
        logout,
        isAuthenticated: !!user,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}