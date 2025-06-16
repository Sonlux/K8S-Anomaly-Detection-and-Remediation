import { useState, useEffect } from "react";
import { Outlet, NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  SatelliteDish,
  Box,
  ActivitySquare,
  Wrench,
  Lightbulb,
  Settings,
  Menu,
  X,
  Moon,
  Sun,
  Bot,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import ChatbotUI from "../components/CHATBOT";

export default function Layout() {
  const [collapsed, setCollapsed] = useState(false);
  const [showBot, setShowBot] = useState(false);

  return (
    <div className="relative flex min-h-screen font-sans">
      <AnimatePresence>
        {!collapsed && (
          <motion.aside
            initial={{ x: -300, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: -300, opacity: 0 }}
            transition={{ type: "spring", stiffness: 200, damping: 20 }}
            className="w-64 bg-white dark:bg-gray-950 shadow-md flex flex-col justify-between z-20"
          >
            <div className="space-y-6">
              <div className="flex justify-end px-4 pt-4">
                <ThemeToggle />
              </div>
              <div className="p-6 text-blue-600 dark:text-blue-400 font-bold text-2xl border-b border-gray-100 dark:border-gray-800 tracking-tight">
                K8s Dashboard
              </div>
              <div className="px-6 text-gray-800 dark:text-gray-100 font-medium text-sm">
                👋 Welcome, Admin
              </div>
              <nav className="flex flex-col px-4 py-2 space-y-2 text-gray-700 dark:text-gray-300 font-medium">
                <SidebarLink
                  to="/"
                  icon={<LayoutDashboard size={18} />}
                  label="Dashboard"
                />
                <SidebarLink
                  to="/clusters"
                  icon={<SatelliteDish size={18} />}
                  label="Clusters"
                />
                <SidebarLink to="/pods" icon={<Box size={18} />} label="Pods" />
                <SidebarLink
                  to="/anomalies"
                  icon={<ActivitySquare size={18} />}
                  label="Anomalies"
                />
                <SidebarLink
                  to="/remediations"
                  icon={<Wrench size={18} />}
                  label="Remediations"
                />
                <SidebarLink
                  to="/insights"
                  icon={<Lightbulb size={18} />}
                  label="Insights"
                />
                <SidebarLink
                  to="/settings"
                  icon={<Settings size={18} />}
                  label="Settings"
                />
              </nav>
            </div>
            <div className="text-xs text-gray-400 dark:text-gray-500 text-center p-4 italic border-t border-gray-100 dark:border-gray-800">
              ⓘ All data is sourced from your local Minikube cluster
            </div>
          </motion.aside>
        )}
      </AnimatePresence>

      <main className="flex-1">
        <div className="bg-white dark:bg-gray-900 shadow p-4 border-b border-gray-100 dark:border-gray-800 flex justify-between items-center">
          <button
            className="text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 transition"
            onClick={() => setCollapsed(!collapsed)}
          >
            {collapsed ? <Menu size={22} /> : <X size={22} />}
          </button>
          <span className="text-sm text-gray-500 dark:text-gray-400">
            Top NavBar Placeholder
          </span>
        </div>
        <div className="p-6 bg-gray-50 dark:bg-gray-900 min-h-screen">
          <Outlet />
        </div>

        <motion.button
          className="fixed bottom-6 right-6 bg-blue-600 hover:bg-blue-700 text-white rounded-full p-3 shadow-lg z-30"
          whileHover={{
            scale: 1.1,
            boxShadow: "0 0 20px rgba(59,130,246,0.6)",
          }}
          whileTap={{ scale: 0.95 }}
          onClick={() => setShowBot(!showBot)}
        >
          <Bot size={24} />
        </motion.button>

        <AnimatePresence>
          {showBot && (
            <motion.div
              className="fixed bottom-20 right-6 bg-white dark:bg-gray-800 rounded-xl shadow-lg p-4 w-96 h-96 z-40"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              transition={{ type: "spring", stiffness: 300, damping: 25 }}
            >
              <ChatbotUI />
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
}

function ThemeToggle() {
  const [isDark, setIsDark] = useState(() => {
    const stored = localStorage.getItem("theme");
    if (stored) return stored === "dark";
    return window.matchMedia("(prefers-color-scheme: dark)").matches;
  });

  useEffect(() => {
    document.documentElement.classList.toggle("dark", isDark);
    localStorage.setItem("theme", isDark ? "dark" : "light");
  }, [isDark]);

  return (
    <div className="relative">
      <motion.button
        whileTap={{ scale: 0.9 }}
        className="ml-2 p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors shadow-md hover:shadow-lg hover:shadow-blue-400/30 dark:hover:shadow-blue-500/40"
        onClick={() => setIsDark(!isDark)}
      >
        <motion.div
          key={isDark ? "moon" : "sun"}
          initial={{ rotate: -90, opacity: 0 }}
          animate={{ rotate: 0, opacity: 1 }}
          exit={{ rotate: 90, opacity: 0 }}
          transition={{ duration: 0.4 }}
        >
          {isDark ? (
            <Moon size={20} className="text-blue-400" />
          ) : (
            <Sun size={20} className="text-yellow-400" />
          )}
        </motion.div>
      </motion.button>
    </div>
  );
}

function SidebarLink({ to, icon, label }) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) =>
        `group flex items-center space-x-2 px-3 py-2 rounded hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors ${
          isActive
            ? "text-blue-600 dark:text-blue-400 font-semibold"
            : "text-gray-700 dark:text-gray-300"
        }`
      }
    >
      <motion.span
        whileHover={{ rotate: 15, scale: 1.2 }}
        whileTap={{ scale: 0.95 }}
        transition={{ type: "spring", stiffness: 300 }}
        className="transition-colors duration-300 group-hover:text-blue-500"
      >
        {icon}
      </motion.span>
      <span className="text-sm tracking-wide">{label}</span>
    </NavLink>
  );
}
