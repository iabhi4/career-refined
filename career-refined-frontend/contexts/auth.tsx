'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useRouter } from 'next/navigation';
import { AuthService } from '@/services/auth';
import axios from 'axios';
import { API_URL } from '@/config/api';

interface AuthState {
  isAuthenticated: boolean;
  userId: number | null;
  isOnboarded: boolean;
}

interface AuthContextType extends AuthState {
  login: (userId: number, isOnboarded: boolean) => void;
  logout: () => void;
  updateIsOnboarded: (status: boolean) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const router = useRouter();
  const [authState, setAuthState] = useState<AuthState>({
    isAuthenticated: false,
    userId: null,
    isOnboarded: false,
  });
  const [isLoading, setIsLoading] = useState(true);

  const updateIsOnboarded = (status: boolean) => {
    setAuthState((prev) => ({ ...prev, isOnboarded: status }));
  };

  // Check auth status on initial load
  useEffect(() => {
    const checkAuth = async () => {
      try {
        // Try to get user info using the cookie
        const response = await axios.get(`${API_URL}/auth/me`, {
          withCredentials: true
        });
        
        if (response.data) {
          setAuthState({
            isAuthenticated: true,
            userId: response.data.user_id,
            isOnboarded: response.data.is_onboarded,
          });
        }
      } catch (error) {
        // If request fails, user is not authenticated
        setAuthState({
          isAuthenticated: false,
          userId: null,
          isOnboarded: false,
        });
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, []);

  const login = (userId: number, isOnboarded: boolean) => {
    setAuthState({
      isAuthenticated: true,
      userId,
      isOnboarded,
    });
  };

  const logout = async () => {
    try {
      await AuthService.logout();
      setAuthState({
        isAuthenticated: false,
        userId: null,
        isOnboarded: false,
      });
      router.push('/auth/login');
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  if (isLoading) {
    // You can return a loading spinner here
    return null;
  }

  return (
    <AuthContext.Provider value={{ ...authState, login, logout, updateIsOnboarded }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};