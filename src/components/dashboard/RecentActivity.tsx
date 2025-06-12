'use client';

import { 
  ClockIcon, 
  ServerIcon, 
  CubeTransparentIcon, 
  ShieldCheckIcon,
  ExclamationTriangleIcon,
  ArrowPathIcon,
  PlusIcon,
  MinusIcon,
  WrenchIcon
} from '@heroicons/react/24/outline';

interface Activity {
  id: string;
  type: 'deployment' | 'scaling' | 'alert' | 'update' | 'creation' | 'deletion' | 'maintenance';
  message: string;
  timestamp: string;
  user?: string;
  resource: {
    type: string;
    name: string;
    namespace: string;
  };
}

interface RecentActivityProps {
  activities: Activity[];
}

const RecentActivity: React.FC<RecentActivityProps> = ({ activities }) => {
  const getActivityIcon = (type: Activity['type']) => {
    switch (type) {
      case 'deployment':
        return <ArrowPathIcon className="h-5 w-5 text-primary-500" />;
      case 'scaling':
        return <ArrowPathIcon className="h-5 w-5 text-primary-500" />;
      case 'alert':
        return <ExclamationTriangleIcon className="h-5 w-5 text-warning-500" />;
      case 'update':
        return <ArrowPathIcon className="h-5 w-5 text-primary-500" />;
      case 'creation':
        return <PlusIcon className="h-5 w-5 text-success-500" />;
      case 'deletion':
        return <MinusIcon className="h-5 w-5 text-danger-500" />;
      case 'maintenance':
        return <WrenchIcon className="h-5 w-5 text-gray-500" />;
      default:
        return <ClockIcon className="h-5 w-5 text-gray-500" />;
    }
  };

  const getResourceIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'pod':
      case 'pods':
        return <CubeTransparentIcon className="h-4 w-4 text-secondary-500" />;
      case 'node':
      case 'nodes':
        return <ServerIcon className="h-4 w-4 text-primary-500" />;
      case 'security':
        return <ShieldCheckIcon className="h-4 w-4 text-success-500" />;
      default:
        return <CubeTransparentIcon className="h-4 w-4 text-gray-500" />;
    }
  };

  return (
    <div className="card p-6">
      <div className="flex items-center mb-6">
        <ClockIcon className="h-6 w-6 text-primary-500 mr-2" />
        <h2 className="text-lg font-bold text-gray-900 dark:text-white">Recent Activity</h2>
      </div>

      <div className="space-y-6">
        {activities.map((activity) => (
          <div key={activity.id} className="relative pl-6 pb-6">
            {/* Timeline connector */}
            <div className="absolute top-0 left-2.5 -ml-px h-full w-0.5 bg-gray-200 dark:bg-gray-700"></div>
            
            {/* Activity dot */}
            <div className="absolute top-0 left-0 flex h-5 w-5 items-center justify-center rounded-full bg-white dark:bg-gray-800 border-2 border-gray-200 dark:border-gray-700">
              {getActivityIcon(activity.type)}
            </div>
            
            <div className="ml-4">
              <div className="flex flex-wrap items-baseline justify-between">
                <div className="text-sm font-medium text-gray-900 dark:text-white">
                  {activity.message}
                </div>
                <div className="text-xs text-gray-500 dark:text-gray-400">
                  {activity.timestamp}
                </div>
              </div>
              
              <div className="mt-1 flex items-center text-xs text-gray-500 dark:text-gray-400">
                <div className="flex items-center mr-2">
                  {getResourceIcon(activity.resource.type)}
                  <span className="ml-1">{activity.resource.type}</span>
                </div>
                <span>{activity.resource.namespace}/{activity.resource.name}</span>
              </div>
              
              {activity.user && (
                <div className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                  By: {activity.user}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      <div className="mt-4 text-center">
        <button className="text-sm text-primary-600 hover:text-primary-500 dark:text-primary-400 dark:hover:text-primary-300 font-medium">
          View All Activity
        </button>
      </div>
    </div>
  );
};

export default RecentActivity;