'use client';

import { useState } from 'react';
import { 
  Bars3Icon, 
  BellIcon, 
  MagnifyingGlassIcon, 
  SunIcon, 
  MoonIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline';

interface HeaderProps {
  toggleSidebar: () => void;
}

const Header: React.FC<HeaderProps> = ({ toggleSidebar }) => {
  const [darkMode, setDarkMode] = useState(false);
  const [notifications, setNotifications] = useState([
    { id: 1, message: 'CPU usage spike detected in cluster-1', time: '5m ago', read: false },
    { id: 2, message: 'Memory leak detected in pod web-frontend-3', time: '15m ago', read: false },
    { id: 3, message: 'Deployment database-1 scaled up successfully', time: '1h ago', read: true },
  ]);
  const [showNotifications, setShowNotifications] = useState(false);

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
    // In a real application, you would toggle a class on the html element
    // or use a context to manage the theme
    document.documentElement.classList.toggle('dark');
  };

  const toggleNotifications = () => {
    setShowNotifications(!showNotifications);
  };

  const markAllAsRead = () => {
    setNotifications(notifications.map(n => ({ ...n, read: true })));
  };

  const unreadCount = notifications.filter(n => !n.read).length;

  return (
    <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
      <div className="flex items-center justify-between h-16 px-4 md:px-6">
        <div className="flex items-center">
          <button
            type="button"
            className="text-gray-500 hover:text-gray-600 dark:text-gray-400 dark:hover:text-gray-300 focus:outline-none"
            onClick={toggleSidebar}
          >
            <Bars3Icon className="h-6 w-6" />
          </button>

          <div className="hidden md:block ml-4">
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
              </div>
              <input
                type="text"
                className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white dark:bg-gray-700 dark:border-gray-600 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm transition duration-150 ease-in-out"
                placeholder="Search"
              />
            </div>
          </div>
        </div>

        <div className="flex items-center space-x-4">
          <button
            type="button"
            className="p-1 rounded-full text-gray-500 hover:text-gray-600 dark:text-gray-400 dark:hover:text-gray-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            onClick={() => {}}
          >
            <ArrowPathIcon className="h-6 w-6" />
          </button>

          <button
            type="button"
            className="p-1 rounded-full text-gray-500 hover:text-gray-600 dark:text-gray-400 dark:hover:text-gray-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            onClick={toggleDarkMode}
          >
            {darkMode ? (
              <SunIcon className="h-6 w-6" />
            ) : (
              <MoonIcon className="h-6 w-6" />
            )}
          </button>

          <div className="relative">
            <button
              type="button"
              className="p-1 rounded-full text-gray-500 hover:text-gray-600 dark:text-gray-400 dark:hover:text-gray-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              onClick={toggleNotifications}
            >
              <BellIcon className="h-6 w-6" />
              {unreadCount > 0 && (
                <span className="absolute top-0 right-0 block h-2 w-2 rounded-full bg-danger-500 ring-2 ring-white dark:ring-gray-800"></span>
              )}
            </button>

            {showNotifications && (
              <div className="origin-top-right absolute right-0 mt-2 w-80 rounded-md shadow-lg bg-white dark:bg-gray-800 ring-1 ring-black ring-opacity-5 focus:outline-none z-10">
                <div className="py-1">
                  <div className="px-4 py-2 border-b border-gray-200 dark:border-gray-700">
                    <div className="flex items-center justify-between">
                      <h3 className="text-sm font-medium text-gray-900 dark:text-white">Notifications</h3>
                      <button
                        type="button"
                        className="text-xs text-primary-600 hover:text-primary-500 dark:text-primary-400 dark:hover:text-primary-300"
                        onClick={markAllAsRead}
                      >
                        Mark all as read
                      </button>
                    </div>
                  </div>
                  <div className="max-h-60 overflow-y-auto">
                    {notifications.length > 0 ? (
                      notifications.map((notification) => (
                        <div
                          key={notification.id}
                          className={`px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-700 ${!notification.read ? 'bg-primary-50 dark:bg-gray-750' : ''}`}
                        >
                          <p className="text-sm text-gray-900 dark:text-white">{notification.message}</p>
                          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">{notification.time}</p>
                        </div>
                      ))
                    ) : (
                      <div className="px-4 py-2">
                        <p className="text-sm text-gray-500 dark:text-gray-400">No notifications</p>
                      </div>
                    )}
                  </div>
                  <div className="border-t border-gray-200 dark:border-gray-700">
                    <a
                      href="/dashboard/alerts"
                      className="block px-4 py-2 text-sm text-center text-primary-600 hover:text-primary-500 dark:text-primary-400 dark:hover:text-primary-300"
                    >
                      View all notifications
                    </a>
                  </div>
                </div>
              </div>
            )}
          </div>

          <div className="flex items-center">
            <div className="flex-shrink-0 h-8 w-8 rounded-full bg-gray-300 flex items-center justify-center">
              <span className="text-sm font-medium text-gray-700">EH</span>
            </div>
            <span className="hidden md:inline-block ml-2 text-sm font-medium text-gray-700 dark:text-gray-300">
              Essie Howell
            </span>
          </div>
        </div>
      </div>

      <div className="md:hidden px-4 pb-3">
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
          </div>
          <input
            type="text"
            className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white dark:bg-gray-700 dark:border-gray-600 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm transition duration-150 ease-in-out"
            placeholder="Search"
          />
        </div>
      </div>
    </header>
  );
};

export default Header;