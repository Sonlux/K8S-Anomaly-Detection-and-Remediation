"use client";

import React, { createContext, useContext, useState, useEffect } from "react";

type User = {
  name: string;
  role: string;
  avatar?: string;
};

type AuthContextType = {
  isAuthenticated: boolean;
  user: User | null;
  login: (username: string, password: string) => Promise<boolean>;
  logout: () => void;
  isLoading: boolean;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Check if user is already authenticated on mount
  useEffect(() => {
    const checkAuth = () => {
      // In a real app, you would verify the token with your backend
      const token = localStorage.getItem("auth_token");
      const savedUser = localStorage.getItem("user");

      if (token && savedUser) {
        // Ensure cookie is also set for server-side auth
        if (!document.cookie.includes("auth_token=")) {
          document.cookie = `auth_token=${token}; path=/; max-age=86400; SameSite=Strict`;
          document.cookie = `user=${savedUser}; path=/; max-age=86400; SameSite=Strict`;
        }

        setIsAuthenticated(true);
        setUser(JSON.parse(savedUser));
      }

      setIsLoading(false);
    };

    checkAuth();
  }, []);

  // Login function - in a real app, this would call your API
  const login = async (
    username: string,
    password: string
  ): Promise<boolean> => {
    setIsLoading(true);

    try {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 1500));

      // For demo purposes, accept any non-empty username/password
      if (username && password) {
        // Create mock user data
        const userData: User = {
          name: username,
          role: "Admin",
          avatar: username.substring(0, 2).toUpperCase(),
        };

        // Generate token
        const token = "demo_token_" + Date.now();

        // Save auth data to localStorage
        localStorage.setItem("auth_token", token);
        localStorage.setItem("user", JSON.stringify(userData));

        // Save auth data to cookies for server-side authentication
        document.cookie = `auth_token=${token}; path=/; max-age=86400; SameSite=Strict`;
        document.cookie = `user=${JSON.stringify(
          userData
        )}; path=/; max-age=86400; SameSite=Strict`;

        // Update state
        setUser(userData);
        setIsAuthenticated(true);
        return true;
      }

      return false;
    } catch (error) {
      console.error("Login error:", error);
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  // Logout function
  const logout = () => {
    // Clear localStorage
    localStorage.removeItem("auth_token");
    localStorage.removeItem("user");

    // Clear cookies
    document.cookie =
      "auth_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT; SameSite=Strict";
    document.cookie =
      "user=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT; SameSite=Strict";

    // Update state
    setUser(null);
    setIsAuthenticated(false);
  };

  return (
    <AuthContext.Provider
      value={{ isAuthenticated, user, login, logout, isLoading }}
    >
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook to use the auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
