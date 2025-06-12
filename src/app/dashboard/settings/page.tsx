'use client';

import { useState } from 'react';
import { 
  Cog6ToothIcon,
  BellIcon,
  UserIcon,
  KeyIcon,
  CloudIcon,
  ShieldCheckIcon,
  ClockIcon,
  DocumentTextIcon,
  ArrowPathIcon,
  CheckIcon,
  XMarkIcon
} from '@heroicons/react/24/outline';

interface SettingsTab {
  id: string;
  name: string;
  icon: React.ForwardRefExoticComponent<React.SVGProps<SVGSVGElement>>;
}

export default function SettingsPage() {
  const tabs: SettingsTab[] = [
    { id: 'general', name: 'General', icon: Cog6ToothIcon },
    { id: 'notifications', name: 'Notifications', icon: BellIcon },
    { id: 'account', name: 'Account', icon: UserIcon },
    { id: 'api-access', name: 'API Access', icon: KeyIcon },
    { id: 'clusters', name: 'Clusters', icon: CloudIcon },
    { id: 'security', name: 'Security', icon: ShieldCheckIcon },
    { id: 'backups', name: 'Backups', icon: ClockIcon },
    { id: 'logs', name: 'Logs', icon: DocumentTextIcon },
  ];

  const [activeTab, setActiveTab] = useState('general');
  const [refreshInterval, setRefreshInterval] = useState('30');
  const [darkMode, setDarkMode] = useState(true);
  const [showSystemNamespaces, setShowSystemNamespaces] = useState(true);
  const [defaultNamespace, setDefaultNamespace] = useState('default');
  const [dateFormat, setDateFormat] = useState('relative');
  const [apiEndpoint, setApiEndpoint] = useState('https://kubernetes.default.svc');
  const [kubeconfig, setKubeconfig] = useState('');
  const [notificationSettings, setNotificationSettings] = useState({
    podFailures: true,
    nodeIssues: true,
    deploymentUpdates: true,
    resourceConstraints: true,
    securityAlerts: true,
    email: true,
    browser: true,
    slack: false,
  });
  const [accountSettings, setAccountSettings] = useState({
    name: 'Admin User',
    email: 'admin@example.com',
    role: 'Administrator',
    twoFactorEnabled: false,
  });
  const [apiTokens, setApiTokens] = useState([
    {
      id: 'token-1',
      name: 'Dashboard API Token',
      created: '2023-09-15T10:30:00Z',
      expires: '2024-09-15T10:30:00Z',
      lastUsed: '2023-10-10T08:45:22Z',
    },
  ]);
  const [clusterSettings, setClusterSettings] = useState({
    currentContext: 'production',
    availableContexts: ['production', 'staging', 'development'],
    autoConnect: true,
    validateCertificates: true,
  });
  const [securitySettings, setSecuritySettings] = useState({
    sessionTimeout: '60',
    enforceRBAC: true,
    auditLogging: true,
    networkPolicies: true,
    podSecurityPolicies: true,
  });
  const [backupSettings, setBackupSettings] = useState({
    autoBackup: true,
    backupSchedule: 'daily',
    backupRetention: '30',
    includeSecrets: false,
    backupLocation: 's3://k8s-backups',
  });
  const [logSettings, setLogSettings] = useState({
    logLevel: 'info',
    retentionDays: '7',
    enableStackTraces: true,
    enableAuditLogs: true,
    enableAccessLogs: true,
  });

  const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'success' | 'error'>('idle');

  const handleSave = () => {
    setSaveStatus('saving');
    // Simulate API call
    setTimeout(() => {
      setSaveStatus('success');
      setTimeout(() => setSaveStatus('idle'), 3000);
    }, 1500);
  };

  const renderTabContent = () => {
    switch (activeTab) {
      case 'general':
        return (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-medium text-gray-900 dark:text-white">Dashboard Settings</h3>
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                Configure general dashboard settings and preferences.
              </p>
            </div>

            <div className="grid grid-cols-1 gap-y-6 sm:grid-cols-2 sm:gap-x-6">
              <div>
                <label htmlFor="refresh-interval" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  Auto-refresh Interval (seconds)
                </label>
                <select
                  id="refresh-interval"
                  name="refresh-interval"
                  className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                  value={refreshInterval}
                  onChange={(e) => setRefreshInterval(e.target.value)}
                >
                  <option value="0">Disabled</option>
                  <option value="10">10 seconds</option>
                  <option value="30">30 seconds</option>
                  <option value="60">1 minute</option>
                  <option value="300">5 minutes</option>
                </select>
              </div>

              <div>
                <label htmlFor="date-format" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  Date Format
                </label>
                <select
                  id="date-format"
                  name="date-format"
                  className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                  value={dateFormat}
                  onChange={(e) => setDateFormat(e.target.value)}
                >
                  <option value="relative">Relative (e.g., 5 minutes ago)</option>
                  <option value="absolute">Absolute (e.g., Oct 12, 2023 14:30)</option>
                  <option value="iso">ISO 8601 (e.g., 2023-10-12T14:30:00Z)</option>
                </select>
              </div>

              <div>
                <label htmlFor="default-namespace" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  Default Namespace
                </label>
                <select
                  id="default-namespace"
                  name="default-namespace"
                  className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                  value={defaultNamespace}
                  onChange={(e) => setDefaultNamespace(e.target.value)}
                >
                  <option value="default">default</option>
                  <option value="kube-system">kube-system</option>
                  <option value="kube-public">kube-public</option>
                  <option value="all-namespaces">All Namespaces</option>
                </select>
              </div>

              <div>
                <label htmlFor="api-endpoint" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  Kubernetes API Endpoint
                </label>
                <input
                  type="text"
                  name="api-endpoint"
                  id="api-endpoint"
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                  value={apiEndpoint}
                  onChange={(e) => setApiEndpoint(e.target.value)}
                />
              </div>
            </div>

            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="text-sm font-medium text-gray-900 dark:text-white">Dark Mode</h4>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Enable dark mode for the dashboard interface.</p>
                </div>
                <button
                  type="button"
                  className={`${darkMode ? 'bg-primary-600' : 'bg-gray-200 dark:bg-gray-700'} relative inline-flex flex-shrink-0 h-6 w-11 border-2 border-transparent rounded-full cursor-pointer transition-colors ease-in-out duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500`}
                  role="switch"
                  aria-checked={darkMode}
                  onClick={() => setDarkMode(!darkMode)}
                >
                  <span
                    aria-hidden="true"
                    className={`${darkMode ? 'translate-x-5' : 'translate-x-0'} pointer-events-none inline-block h-5 w-5 rounded-full bg-white shadow transform ring-0 transition ease-in-out duration-200`}
                  ></span>
                </button>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <h4 className="text-sm font-medium text-gray-900 dark:text-white">Show System Namespaces</h4>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Display system namespaces in namespace lists.</p>
                </div>
                <button
                  type="button"
                  className={`${showSystemNamespaces ? 'bg-primary-600' : 'bg-gray-200 dark:bg-gray-700'} relative inline-flex flex-shrink-0 h-6 w-11 border-2 border-transparent rounded-full cursor-pointer transition-colors ease-in-out duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500`}
                  role="switch"
                  aria-checked={showSystemNamespaces}
                  onClick={() => setShowSystemNamespaces(!showSystemNamespaces)}
                >
                  <span
                    aria-hidden="true"
                    className={`${showSystemNamespaces ? 'translate-x-5' : 'translate-x-0'} pointer-events-none inline-block h-5 w-5 rounded-full bg-white shadow transform ring-0 transition ease-in-out duration-200`}
                  ></span>
                </button>
              </div>
            </div>
          </div>
        );

      case 'notifications':
        return (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-medium text-gray-900 dark:text-white">Notification Preferences</h3>
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                Configure which events trigger notifications and how you receive them.
              </p>
            </div>

            <div>
              <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-4">Event Types</h4>
              <div className="space-y-4">
                {[
                  { id: 'podFailures', label: 'Pod Failures' },
                  { id: 'nodeIssues', label: 'Node Issues' },
                  { id: 'deploymentUpdates', label: 'Deployment Updates' },
                  { id: 'resourceConstraints', label: 'Resource Constraints' },
                  { id: 'securityAlerts', label: 'Security Alerts' },
                ].map((item) => (
                  <div key={item.id} className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-700 dark:text-gray-300">{item.label}</p>
                    </div>
                    <button
                      type="button"
                      className={`${notificationSettings[item.id as keyof typeof notificationSettings] ? 'bg-primary-600' : 'bg-gray-200 dark:bg-gray-700'} relative inline-flex flex-shrink-0 h-6 w-11 border-2 border-transparent rounded-full cursor-pointer transition-colors ease-in-out duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500`}
                      role="switch"
                      aria-checked={notificationSettings[item.id as keyof typeof notificationSettings]}
                      onClick={() => setNotificationSettings({
                        ...notificationSettings,
                        [item.id]: !notificationSettings[item.id as keyof typeof notificationSettings],
                      })}
                    >
                      <span
                        aria-hidden="true"
                        className={`${notificationSettings[item.id as keyof typeof notificationSettings] ? 'translate-x-5' : 'translate-x-0'} pointer-events-none inline-block h-5 w-5 rounded-full bg-white shadow transform ring-0 transition ease-in-out duration-200`}
                      ></span>
                    </button>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-4">Notification Channels</h4>
              <div className="space-y-4">
                {[
                  { id: 'email', label: 'Email Notifications' },
                  { id: 'browser', label: 'Browser Notifications' },
                  { id: 'slack', label: 'Slack Notifications' },
                ].map((item) => (
                  <div key={item.id} className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-700 dark:text-gray-300">{item.label}</p>
                    </div>
                    <button
                      type="button"
                      className={`${notificationSettings[item.id as keyof typeof notificationSettings] ? 'bg-primary-600' : 'bg-gray-200 dark:bg-gray-700'} relative inline-flex flex-shrink-0 h-6 w-11 border-2 border-transparent rounded-full cursor-pointer transition-colors ease-in-out duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500`}
                      role="switch"
                      aria-checked={notificationSettings[item.id as keyof typeof notificationSettings]}
                      onClick={() => setNotificationSettings({
                        ...notificationSettings,
                        [item.id]: !notificationSettings[item.id as keyof typeof notificationSettings],
                      })}
                    >
                      <span
                        aria-hidden="true"
                        className={`${notificationSettings[item.id as keyof typeof notificationSettings] ? 'translate-x-5' : 'translate-x-0'} pointer-events-none inline-block h-5 w-5 rounded-full bg-white shadow transform ring-0 transition ease-in-out duration-200`}
                      ></span>
                    </button>
                  </div>
                ))}
              </div>
            </div>

            {notificationSettings.slack && (
              <div>
                <label htmlFor="slack-webhook" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  Slack Webhook URL
                </label>
                <input
                  type="text"
                  name="slack-webhook"
                  id="slack-webhook"
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                  placeholder="https://hooks.slack.com/services/..."
                />
              </div>
            )}
          </div>
        );

      case 'account':
        return (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-medium text-gray-900 dark:text-white">Account Settings</h3>
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                Manage your account information and security settings.
              </p>
            </div>

            <div className="grid grid-cols-1 gap-y-6 sm:grid-cols-2 sm:gap-x-6">
              <div>
                <label htmlFor="name" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  Name
                </label>
                <input
                  type="text"
                  name="name"
                  id="name"
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                  value={accountSettings.name}
                  onChange={(e) => setAccountSettings({ ...accountSettings, name: e.target.value })}
                />
              </div>

              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  Email
                </label>
                <input
                  type="email"
                  name="email"
                  id="email"
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                  value={accountSettings.email}
                  onChange={(e) => setAccountSettings({ ...accountSettings, email: e.target.value })}
                />
              </div>
            </div>

            <div>
              <label htmlFor="role" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Role
              </label>
              <select
                id="role"
                name="role"
                className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                value={accountSettings.role}
                onChange={(e) => setAccountSettings({ ...accountSettings, role: e.target.value })}
                disabled
              >
                <option>Administrator</option>
                <option>Editor</option>
                <option>Viewer</option>
              </select>
              <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                Role changes must be performed by an administrator.
              </p>
            </div>

            <div className="flex items-center justify-between">
              <div>
                <h4 className="text-sm font-medium text-gray-900 dark:text-white">Two-Factor Authentication</h4>
                <p className="text-sm text-gray-500 dark:text-gray-400">Add an extra layer of security to your account.</p>
              </div>
              <button
                type="button"
                className={`${accountSettings.twoFactorEnabled ? 'bg-primary-600' : 'bg-gray-200 dark:bg-gray-700'} relative inline-flex flex-shrink-0 h-6 w-11 border-2 border-transparent rounded-full cursor-pointer transition-colors ease-in-out duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500`}
                role="switch"
                aria-checked={accountSettings.twoFactorEnabled}
                onClick={() => setAccountSettings({ ...accountSettings, twoFactorEnabled: !accountSettings.twoFactorEnabled })}
              >
                <span
                  aria-hidden="true"
                  className={`${accountSettings.twoFactorEnabled ? 'translate-x-5' : 'translate-x-0'} pointer-events-none inline-block h-5 w-5 rounded-full bg-white shadow transform ring-0 transition ease-in-out duration-200`}
                ></span>
              </button>
            </div>

            <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
              <button
                type="button"
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
              >
                Change Password
              </button>
            </div>
          </div>
        );

      case 'api-access':
        return (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-medium text-gray-900 dark:text-white">API Access</h3>
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                Manage API tokens for programmatic access to the dashboard.
              </p>
            </div>

            <div>
              <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-4">API Tokens</h4>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                  <thead className="bg-gray-50 dark:bg-gray-800">
                    <tr>
                      <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                        Name
                      </th>
                      <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                        Created
                      </th>
                      <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                        Expires
                      </th>
                      <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                        Last Used
                      </th>
                      <th scope="col" className="relative px-6 py-3">
                        <span className="sr-only">Actions</span>
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-800">
                    {apiTokens.map((token) => (
                      <tr key={token.id}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                          {token.name}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                          {new Date(token.created).toLocaleDateString()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                          {new Date(token.expires).toLocaleDateString()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                          {new Date(token.lastUsed).toLocaleDateString()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                          <button
                            type="button"
                            className="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300"
                          >
                            Revoke
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            <div>
              <button
                type="button"
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              >
                Generate New Token
              </button>
            </div>

            <div className="pt-6 border-t border-gray-200 dark:border-gray-700">
              <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-4">Kubeconfig</h4>
              <div>
                <label htmlFor="kubeconfig" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  Upload Kubeconfig File
                </label>
                <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-md dark:border-gray-600">
                  <div className="space-y-1 text-center">
                    <svg
                      className="mx-auto h-12 w-12 text-gray-400"
                      stroke="currentColor"
                      fill="none"
                      viewBox="0 0 48 48"
                      aria-hidden="true"
                    >
                      <path
                        d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                        strokeWidth={2}
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      />
                    </svg>
                    <div className="flex text-sm text-gray-600 dark:text-gray-400">
                      <label
                        htmlFor="file-upload"
                        className="relative cursor-pointer bg-white dark:bg-gray-800 rounded-md font-medium text-primary-600 hover:text-primary-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-primary-500"
                      >
                        <span>Upload a file</span>
                        <input id="file-upload" name="file-upload" type="file" className="sr-only" />
                      </label>
                      <p className="pl-1">or drag and drop</p>
                    </div>
                    <p className="text-xs text-gray-500 dark:text-gray-400">YAML file up to 10MB</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        );

      case 'clusters':
        return (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-medium text-gray-900 dark:text-white">Cluster Configuration</h3>
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                Manage Kubernetes cluster connections and contexts.
              </p>
            </div>

            <div>
              <label htmlFor="current-context" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Current Context
              </label>
              <select
                id="current-context"
                name="current-context"
                className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                value={clusterSettings.currentContext}
                onChange={(e) => setClusterSettings({ ...clusterSettings, currentContext: e.target.value })}
              >
                {clusterSettings.availableContexts.map((context) => (
                  <option key={context} value={context}>
                    {context}
                  </option>
                ))}
              </select>
            </div>

            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="text-sm font-medium text-gray-900 dark:text-white">Auto-connect on Startup</h4>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Automatically connect to the cluster when the dashboard starts.</p>
                </div>
                <button
                  type="button"
                  className={`${clusterSettings.autoConnect ? 'bg-primary-600' : 'bg-gray-200 dark:bg-gray-700'} relative inline-flex flex-shrink-0 h-6 w-11 border-2 border-transparent rounded-full cursor-pointer transition-colors ease-in-out duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500`}
                  role="switch"
                  aria-checked={clusterSettings.autoConnect}
                  onClick={() => setClusterSettings({ ...clusterSettings, autoConnect: !clusterSettings.autoConnect })}
                >
                  <span
                    aria-hidden="true"
                    className={`${clusterSettings.autoConnect ? 'translate-x-5' : 'translate-x-0'} pointer-events-none inline-block h-5 w-5 rounded-full bg-white shadow transform ring-0 transition ease-in-out duration-200`}
                  ></span>
                </button>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <h4 className="text-sm font-medium text-gray-900 dark:text-white">Validate Certificates</h4>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Verify SSL certificates when connecting to the Kubernetes API.</p>
                </div>
                <button
                  type="button"
                  className={`${clusterSettings.validateCertificates ? 'bg-primary-600' : 'bg-gray-200 dark:bg-gray-700'} relative inline-flex flex-shrink-0 h-6 w-11 border-2 border-transparent rounded-full cursor-pointer transition-colors ease-in-out duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500`}
                  role="switch"
                  aria-checked={clusterSettings.validateCertificates}
                  onClick={() => setClusterSettings({ ...clusterSettings, validateCertificates: !clusterSettings.validateCertificates })}
                >
                  <span
                    aria-hidden="true"
                    className={`${clusterSettings.validateCertificates ? 'translate-x-5' : 'translate-x-0'} pointer-events-none inline-block h-5 w-5 rounded-full bg-white shadow transform ring-0 transition ease-in-out duration-200`}
                  ></span>
                </button>
              </div>
            </div>

            <div className="pt-6 border-t border-gray-200 dark:border-gray-700">
              <button
                type="button"
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              >
                Add New Cluster
              </button>
            </div>
          </div>
        );

      case 'security':
        return (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-medium text-gray-900 dark:text-white">Security Settings</h3>
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                Configure security policies and access controls.
              </p>
            </div>

            <div>
              <label htmlFor="session-timeout" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Session Timeout (minutes)
              </label>
              <select
                id="session-timeout"
                name="session-timeout"
                className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                value={securitySettings.sessionTimeout}
                onChange={(e) => setSecuritySettings({ ...securitySettings, sessionTimeout: e.target.value })}
              >
                <option value="15">15 minutes</option>
                <option value="30">30 minutes</option>
                <option value="60">1 hour</option>
                <option value="120">2 hours</option>
                <option value="240">4 hours</option>
              </select>
            </div>

            <div className="space-y-4">
              {[
                { id: 'enforceRBAC', label: 'Enforce RBAC', description: 'Strictly enforce role-based access control for all dashboard operations.' },
                { id: 'auditLogging', label: 'Audit Logging', description: 'Log all user actions for security auditing purposes.' },
                { id: 'networkPolicies', label: 'Network Policies', description: 'Enable network policy enforcement for cluster resources.' },
                { id: 'podSecurityPolicies', label: 'Pod Security Policies', description: 'Enforce pod security policies for all workloads.' },
              ].map((item) => (
                <div key={item.id} className="flex items-center justify-between">
                  <div>
                    <h4 className="text-sm font-medium text-gray-900 dark:text-white">{item.label}</h4>
                    <p className="text-sm text-gray-500 dark:text-gray-400">{item.description}</p>
                  </div>
                  <button
                    type="button"
                    className={`${securitySettings[item.id as keyof typeof securitySettings] ? 'bg-primary-600' : 'bg-gray-200 dark:bg-gray-700'} relative inline-flex flex-shrink-0 h-6 w-11 border-2 border-transparent rounded-full cursor-pointer transition-colors ease-in-out duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500`}
                    role="switch"
                    aria-checked={securitySettings[item.id as keyof typeof securitySettings]}
                    onClick={() => setSecuritySettings({
                      ...securitySettings,
                      [item.id]: !securitySettings[item.id as keyof typeof securitySettings],
                    })}
                  >
                    <span
                      aria-hidden="true"
                      className={`${securitySettings[item.id as keyof typeof securitySettings] ? 'translate-x-5' : 'translate-x-0'} pointer-events-none inline-block h-5 w-5 rounded-full bg-white shadow transform ring-0 transition ease-in-out duration-200`}
                    ></span>
                  </button>
                </div>
              ))}
            </div>
          </div>
        );

      case 'backups':
        return (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-medium text-gray-900 dark:text-white">Backup Configuration</h3>
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                Configure automated backups for your Kubernetes resources.
              </p>
            </div>

            <div className="flex items-center justify-between">
              <div>
                <h4 className="text-sm font-medium text-gray-900 dark:text-white">Automatic Backups</h4>
                <p className="text-sm text-gray-500 dark:text-gray-400">Enable scheduled backups of cluster resources.</p>
              </div>
              <button
                type="button"
                className={`${backupSettings.autoBackup ? 'bg-primary-600' : 'bg-gray-200 dark:bg-gray-700'} relative inline-flex flex-shrink-0 h-6 w-11 border-2 border-transparent rounded-full cursor-pointer transition-colors ease-in-out duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500`}
                role="switch"
                aria-checked={backupSettings.autoBackup}
                onClick={() => setBackupSettings({ ...backupSettings, autoBackup: !backupSettings.autoBackup })}
              >
                <span
                  aria-hidden="true"
                  className={`${backupSettings.autoBackup ? 'translate-x-5' : 'translate-x-0'} pointer-events-none inline-block h-5 w-5 rounded-full bg-white shadow transform ring-0 transition ease-in-out duration-200`}
                ></span>
              </button>
            </div>

            {backupSettings.autoBackup && (
              <div className="grid grid-cols-1 gap-y-6 sm:grid-cols-2 sm:gap-x-6">
                <div>
                  <label htmlFor="backup-schedule" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Backup Schedule
                  </label>
                  <select
                    id="backup-schedule"
                    name="backup-schedule"
                    className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                    value={backupSettings.backupSchedule}
                    onChange={(e) => setBackupSettings({ ...backupSettings, backupSchedule: e.target.value })}
                  >
                    <option value="hourly">Hourly</option>
                    <option value="daily">Daily</option>
                    <option value="weekly">Weekly</option>
                    <option value="monthly">Monthly</option>
                  </select>
                </div>

                <div>
                  <label htmlFor="backup-retention" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Retention Period (days)
                  </label>
                  <select
                    id="backup-retention"
                    name="backup-retention"
                    className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                    value={backupSettings.backupRetention}
                    onChange={(e) => setBackupSettings({ ...backupSettings, backupRetention: e.target.value })}
                  >
                    <option value="7">7 days</option>
                    <option value="14">14 days</option>
                    <option value="30">30 days</option>
                    <option value="90">90 days</option>
                    <option value="365">365 days</option>
                  </select>
                </div>

                <div>
                  <label htmlFor="backup-location" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Backup Storage Location
                  </label>
                  <input
                    type="text"
                    name="backup-location"
                    id="backup-location"
                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                    value={backupSettings.backupLocation}
                    onChange={(e) => setBackupSettings({ ...backupSettings, backupLocation: e.target.value })}
                  />
                </div>

                <div className="flex items-center">
                  <input
                    id="include-secrets"
                    name="include-secrets"
                    type="checkbox"
                    className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded dark:bg-gray-700 dark:border-gray-600"
                    checked={backupSettings.includeSecrets}
                    onChange={(e) => setBackupSettings({ ...backupSettings, includeSecrets: e.target.checked })}
                  />
                  <label htmlFor="include-secrets" className="ml-2 block text-sm text-gray-900 dark:text-white">
                    Include Secrets (not recommended)
                  </label>
                </div>
              </div>
            )}

            <div className="pt-6 border-t border-gray-200 dark:border-gray-700">
              <button
                type="button"
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              >
                Create Manual Backup
              </button>
            </div>
          </div>
        );

      case 'logs':
        return (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-medium text-gray-900 dark:text-white">Logging Configuration</h3>
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                Configure logging settings for the dashboard and Kubernetes resources.
              </p>
            </div>

            <div className="grid grid-cols-1 gap-y-6 sm:grid-cols-2 sm:gap-x-6">
              <div>
                <label htmlFor="log-level" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  Log Level
                </label>
                <select
                  id="log-level"
                  name="log-level"
                  className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                  value={logSettings.logLevel}
                  onChange={(e) => setLogSettings({ ...logSettings, logLevel: e.target.value })}
                >
                  <option value="debug">Debug</option>
                  <option value="info">Info</option>
                  <option value="warn">Warning</option>
                  <option value="error">Error</option>
                </select>
              </div>

              <div>
                <label htmlFor="retention-days" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  Log Retention (days)
                </label>
                <select
                  id="retention-days"
                  name="retention-days"
                  className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                  value={logSettings.retentionDays}
                  onChange={(e) => setLogSettings({ ...logSettings, retentionDays: e.target.value })}
                >
                  <option value="1">1 day</option>
                  <option value="3">3 days</option>
                  <option value="7">7 days</option>
                  <option value="14">14 days</option>
                  <option value="30">30 days</option>
                </select>
              </div>
            </div>

            <div className="space-y-4">
              {[
                { id: 'enableStackTraces', label: 'Enable Stack Traces', description: 'Include stack traces in error logs for debugging.' },
                { id: 'enableAuditLogs', label: 'Enable Audit Logs', description: 'Log all user actions for security auditing.' },
                { id: 'enableAccessLogs', label: 'Enable Access Logs', description: 'Log all API access and requests.' },
              ].map((item) => (
                <div key={item.id} className="flex items-center justify-between">
                  <div>
                    <h4 className="text-sm font-medium text-gray-900 dark:text-white">{item.label}</h4>
                    <p className="text-sm text-gray-500 dark:text-gray-400">{item.description}</p>
                  </div>
                  <button
                    type="button"
                    className={`${logSettings[item.id as keyof typeof logSettings] ? 'bg-primary-600' : 'bg-gray-200 dark:bg-gray-700'} relative inline-flex flex-shrink-0 h-6 w-11 border-2 border-transparent rounded-full cursor-pointer transition-colors ease-in-out duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500`}
                    role="switch"
                    aria-checked={logSettings[item.id as keyof typeof logSettings]}
                    onClick={() => setLogSettings({
                      ...logSettings,
                      [item.id]: !logSettings[item.id as keyof typeof logSettings],
                    })}
                  >
                    <span
                      aria-hidden="true"
                      className={`${logSettings[item.id as keyof typeof logSettings] ? 'translate-x-5' : 'translate-x-0'} pointer-events-none inline-block h-5 w-5 rounded-full bg-white shadow transform ring-0 transition ease-in-out duration-200`}
                    ></span>
                  </button>
                </div>
              ))}
            </div>

            <div className="pt-6 border-t border-gray-200 dark:border-gray-700">
              <button
                type="button"
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              >
                Download Logs
              </button>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <h1 className="text-2xl font-bold">Settings</h1>
        
        <div className="mt-4 sm:mt-0">
          <button
            type="button"
            onClick={handleSave}
            disabled={saveStatus === 'saving'}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {saveStatus === 'idle' && 'Save Changes'}
            {saveStatus === 'saving' && (
              <>
                <ArrowPathIcon className="-ml-1 mr-2 h-4 w-4 animate-spin" />
                Saving...
              </>
            )}
            {saveStatus === 'success' && (
              <>
                <CheckIcon className="-ml-1 mr-2 h-4 w-4" />
                Saved
              </>
            )}
            {saveStatus === 'error' && (
              <>
                <XMarkIcon className="-ml-1 mr-2 h-4 w-4" />
                Error
              </>
            )}
          </button>
        </div>
      </div>

      <div className="card p-0 overflow-hidden">
        <div className="sm:hidden">
          <label htmlFor="tabs" className="sr-only">Select a tab</label>
          <select
            id="tabs"
            name="tabs"
            className="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            value={activeTab}
            onChange={(e) => setActiveTab(e.target.value)}
          >
            {tabs.map((tab) => (
              <option key={tab.id} value={tab.id}>
                {tab.name}
              </option>
            ))}
          </select>
        </div>
        <div className="hidden sm:block">
          <div className="border-b border-gray-200 dark:border-gray-700">
            <nav className="-mb-px flex space-x-8 px-6" aria-label="Tabs">
              {tabs.map((tab) => {
                const Icon = tab.icon;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`${activeTab === tab.id
                      ? 'border-primary-500 text-primary-600 dark:text-primary-400'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
                      } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center`}
                  >
                    <Icon className="-ml-0.5 mr-2 h-5 w-5" />
                    {tab.name}
                  </button>
                );
              })}
            </nav>
          </div>
        </div>

        <div className="p-6">
          {renderTabContent()}
        </div>
      </div>
    </div>
  );
}