// src/components/Sidebar.tsx
"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { useTheme } from "@/contexts/ThemeContext";

interface SidebarProps {
  visible?: boolean;
}

export const Sidebar = ({ visible = true }: SidebarProps) => {
  const pathname = usePathname();
  const { logout, user } = useAuth();
  const { theme } = useTheme();

  const isActive = (path: string) => {
    return pathname === path;
  };

  const navItems = [
    {
      name: "Overview",
      path: "/",
      icon: "M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6",
    },
    {
      name: "Anomalies",
      path: "/anomalies",
      icon: "M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z",
    },
    {
      name: "Remediation",
      path: "/remediation",
      icon: "M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15",
    },
    {
      name: "Clusters",
      path: "/clusters",
      icon: "M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01",
    },
    {
      name: "Metrics",
      path: "/metrics",
      icon: "M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z",
    },
    {
      name: "Alerts",
      path: "/alerts",
      icon: "M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9",
    },
    {
      name: "Settings",
      path: "/settings",
      icon: "M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z",
    },
  ];

  return (
    <div
      className={`${
        visible ? "block" : "hidden"
      } md:block bg-indigo-900 dark:bg-gray-900 border-r border-indigo-800 dark:border-gray-800 w-64 min-h-screen p-4 flex flex-col transition-theme overflow-y-auto`}
    >
      <div className="mb-8 mt-4">
        <div className="flex items-center justify-center mb-6">
          <div className="relative">
            <div className="h-20 w-20 rounded-full bg-indigo-100 dark:bg-indigo-900 flex items-center justify-center text-indigo-600 dark:text-indigo-300 text-2xl font-bold font-montserrat">
              <span className="text-3xl">K</span>
            </div>
            <div className="absolute bottom-0 right-0 h-5 w-5 rounded-full bg-green-500 border-2 border-white dark:border-gray-800"></div>
          </div>
        </div>
        <div className="text-center">
          <h2 className="text-lg font-medium text-gray-800 dark:text-gray-200">
            KODA
          </h2>
          <p className="text-gray-500 dark:text-gray-400 text-sm">
            Kubernetes Operations & Detection Agent
          </p>
        </div>
      </div>

      <nav className="flex-1">
        <ul className="space-y-1">
          {navItems.map((item) => (
            <li key={item.path}>
              <Link
                href={item.path}
                className={`flex items-center py-3 px-4 rounded-md transition-colors duration-200 ${
                  isActive(item.path)
                    ? "bg-indigo-800 text-white font-medium"
                    : "text-indigo-100 hover:bg-indigo-800/50 hover:text-white"
                }`}
              >
                <svg
                  className={`h-5 w-5 mr-3 ${
                    isActive(item.path) ? "text-white" : "text-indigo-300"
                  }`}
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d={item.icon}
                  />
                </svg>
                {item.name}
                {isActive(item.path) && (
                  <div className="ml-auto w-1.5 h-6 rounded-sm bg-cyan-400"></div>
                )}
              </Link>
            </li>
          ))}
        </ul>
      </nav>

      <div className="mt-auto pt-4 border-t border-indigo-800 dark:border-gray-800">
        <button
          onClick={logout}
          className="flex w-full items-center py-3 px-4 rounded-md text-indigo-100 hover:bg-indigo-800/50 hover:text-white transition-colors duration-200"
        >
          <svg
            className="h-5 w-5 mr-3 text-indigo-300"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
            />
          </svg>
          Logout
        </button>
      </div>
    </div>
  );
};
