"use client";

import React, { createContext, useContext, useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

type User = { email: string };

type AuthContextType = {
  isAuthenticated: boolean;
  user: User | null;
  login: () => void;
  signup: () => void;
  logout: () => void;
  verify: () => void;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const router = useRouter();

  useEffect(() => {
    // Basic mock session persistence
    const checkSession = async () => {
      const session = localStorage.getItem('hempguard_auth');
      if (session === 'true') {
        setIsAuthenticated(true);
        setUser({ email: 'user@example.com' });
      }
    };
    checkSession();
  }, []);

  const login = () => {
    setIsAuthenticated(true);
    setUser({ email: 'user@example.com' });
    localStorage.setItem('hempguard_auth', 'true');
    router.push('/dashboard');
  };

  const signup = () => {
    router.push('/verify');
  };

  const verify = () => {
    setIsAuthenticated(true);
    setUser({ email: 'user@example.com' });
    localStorage.setItem('hempguard_auth', 'true');
    router.push('/dashboard');
  };

  const logout = () => {
    setIsAuthenticated(false);
    setUser(null);
    localStorage.removeItem('hempguard_auth');
    router.push('/login');
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, user, login, signup, logout, verify }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
