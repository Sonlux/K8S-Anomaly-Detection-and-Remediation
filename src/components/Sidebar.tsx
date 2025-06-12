'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import Image from 'next/image';
import { 
  HomeIcon, 
  ServerIcon, 
  CubeIcon, 
  ShieldCheckIcon, 
  ChartBarIcon, 
  CogIcon, 
  BellIcon,
  ChatBubbleLeftRightIcon,
  DocumentTextIcon
} from '@heroicons/react/24/outline';

interface SidebarProps {
  isOpen: boolean;
}

const Sidebar: React.FC<SidebarProps> = ({ isOpen }) => {
  const pathname = usePathname();
  const [userProfile, setUserProfile] = useState({
    name: 'Essie Howell',
    role: 'Admin',
    avatar: '/avatar.png' // This would be a real avatar path in production
  });

  const navItems = [
    { name: 'Overview', href: '/dashboard', icon: HomeIcon },
    { name: 'Clusters', href: '/dashboard/clusters', icon: ServerIcon },
    { name: 'Workloads', href: '/dashboard/workloads', icon: CubeIcon },
    { name: 'Security', href: '/dashboard/security', icon: ShieldCheckIcon },
    { name: 'Metrics', href: '/dashboard/metrics', icon: ChartBarIcon },
    { name: 'Alerts', href: '/dashboard/alerts', icon: BellIcon },
    { name: 'Chat', href: '/dashboard/chat', icon: ChatBubbleLeftRightIcon },
    { name: 'Logs', href: '/dashboard/logs', icon: DocumentTextIcon },
    { name: 'Settings', href: '/dashboard/settings', icon: CogIcon },
  ];

  return (
    <aside 
      className={`${isOpen ? 'w-64' : 'w-20'} bg-white dark:bg-gray-800 h-full transition-all duration-300 ease-in-out border-r border-gray-200 dark:border-gray-700 flex flex-col`}
    >
      <div className="flex items-center justify-center h-16 border-b border-gray-200 dark:border-gray-700">
        <div className={`${isOpen ? 'px-4' : 'px-0'} flex items-center`}>
          <span className="text-xl font-bold text-primary-600 dark:text-primary-400">
            {isOpen ? 'Boardash' : 'B'}
          </span>
        </div>
      </div>

      <div className="flex flex-col flex-grow overflow-y-auto">
        <div className="flex items-center p-4 border-b border-gray-200 dark:border-gray-700">
          <div className="flex-shrink-0 h-10 w-10 rounded-full bg-gray-300 flex items-center justify-center overflow-hidden">
            {/* In a real app, you would use a real avatar image */}
            <div className="text-xl font-bold text-gray-700">{userProfile.name.charAt(0)}</div>
          </div>
          {isOpen && (
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-900 dark:text-white">{userProfile.name}</p>
              <p className="text-xs font-medium text-gray-500 dark:text-gray-400">{userProfile.role}</p>
            </div>
          )}
        </div>

        <nav className="mt-5 px-2 space-y-1">
          {navItems.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.name}
                href={item.href}
                className={`${isActive
                  ? 'bg-primary-50 text-primary-600 dark:bg-gray-700 dark:text-white'
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900 dark:text-gray-300 dark:hover:bg-gray-700 dark:hover:text-white'
                  } group flex items-center px-2 py-2 text-sm font-medium rounded-md transition-colors duration-150 ease-in-out`}
              >
                <item.icon
                  className={`${isActive ? 'text-primary-600 dark:text-white' : 'text-gray-400 group-hover:text-gray-500 dark:text-gray-400 dark:group-hover:text-gray-300'}
                  ${isOpen ? 'mr-3 h-6 w-6' : 'mx-auto h-6 w-6'} flex-shrink-0 transition-colors duration-150 ease-in-out`}
                  aria-hidden="true"
                />
                {isOpen && <span>{item.name}</span>}
              </Link>
            );
          })}
        </nav>
      </div>

      <div className="p-4 border-t border-gray-200 dark:border-gray-700">
        {isOpen ? (
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <ShieldCheckIcon className="h-6 w-6 text-success-500" />
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-900 dark:text-white">System Status</p>
              <p className="text-xs text-success-500">All systems operational</p>
            </div>
          </div>
        ) : (
          <div className="flex justify-center">
            <ShieldCheckIcon className="h-6 w-6 text-success-500" />
          </div>
        )}
      </div>
    </aside>
  );
};

export default Sidebar;