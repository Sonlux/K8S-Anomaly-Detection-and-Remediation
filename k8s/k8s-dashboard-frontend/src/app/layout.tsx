// src/app/layout.tsx
"use client";

import { Inter, Montserrat } from "next/font/google";
import "./globals.css";
import { ThemeProvider } from "@/contexts/ThemeContext";
import { useTheme } from "@/contexts/ThemeContext";
import { AuthProvider } from "@/contexts/AuthContext";
import { Sidebar } from "@/components/Sidebar";
import { useState } from "react";
import Link from "next/link";

const inter = Inter({ subsets: ["latin"] });
const montserrat = Montserrat({
  subsets: ["latin"],
  variable: "--font-montserrat",
});

// Wrapper component to access theme context
function LayoutContent({ children }: { children: React.ReactNode }) {
  const { theme, toggleTheme } = useTheme();
  const [sidebarVisible, setSidebarVisible] = useState(true);

  const toggleSidebar = () => {
    setSidebarVisible(!sidebarVisible);
  };

  return (
    <div className="flex h-screen bg-gray-100 dark:bg-gray-900 transition-theme">
      {/* Sidebar */}
      {sidebarVisible && <Sidebar />}

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header for KODA dashboard */}
        <header className="bg-indigo-900 border-b border-indigo-800 h-16 flex items-center justify-between px-6">
          <div className="flex items-center space-x-3">
            {/* Sidebar Toggle */}
            <button
              onClick={toggleSidebar}
              className="p-1 rounded-md text-indigo-100 hover:text-white focus:outline-none"
            >
              <svg
                className="h-6 w-6"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 6h16M4 12h16M4 18h16"
                />
              </svg>
            </button>

            {/* Dashboard Title */}
            <div className="flex items-center">
              <h1 className="text-xl font-semibold text-white">
                KODA Dashboard
              </h1>
              <span className="ml-2 px-2 py-1 text-xs bg-indigo-800 text-indigo-100 rounded-md">
                v1.0
              </span>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            {/* Cluster Status Indicator */}
            <div className="flex items-center mr-2">
              <div className="h-2.5 w-2.5 rounded-full bg-green-500 mr-2"></div>
              <span className="text-sm text-indigo-100">Cluster: Healthy</span>
            </div>

            {/* Alerts Button */}
            <button className="p-1.5 rounded-md text-indigo-100 hover:text-white hover:bg-indigo-800 focus:outline-none relative">
              <svg
                className="h-6 w-6"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
                />
              </svg>
              <span className="absolute top-0 right-0 h-4 w-4 bg-red-500 rounded-full text-xs flex items-center justify-center text-white">
                3
              </span>
            </button>

            {/* Theme Toggle */}
            <button
              onClick={toggleTheme}
              className="p-1 rounded-md text-gray-500 hover:text-gray-900 focus:outline-none"
              aria-label={`Switch to ${
                theme === "light" ? "dark" : "light"
              } mode`}
            >
              {theme === "light" ? (
                <svg
                  className="h-5 w-5"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"
                  />
                </svg>
              ) : (
                <svg
                  className="h-5 w-5"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"
                  />
                </svg>
              )}
            </button>

            {/* User Profile */}
            <div className="relative">
              <button className="flex items-center text-sm rounded-full focus:outline-none">
                <div className="h-7 w-7 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 text-sm font-bold font-montserrat">
                  E
                </div>
              </button>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="flex-1 overflow-auto bg-gray-50 p-4">{children}</main>

        {/* Footer - Simplified */}
        <footer className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 py-2 px-6">
          <div className="flex justify-between items-center">
            <div className="flex items-center">
              <span className="text-sm text-gray-600 dark:text-gray-300">
                Kubernetes Operations & Detection Agent
              </span>
            </div>
            <div className="text-xs text-gray-500 dark:text-gray-400">
              © 2023 KODA | All rights reserved
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
}

// Export the main layout component
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${montserrat.variable}`}>
      <body className={`${inter.className} antialiased`}>
        <ThemeProvider>
          <AuthProvider>
            <LayoutContent>{children}</LayoutContent>
          </AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
