import React from "react";

interface MetricCardProps {
  title: string;
  value: number | string;
  period?: string;
  trend?: "up" | "down" | "neutral";
  trendValue?: string;
  icon?: React.ReactNode;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  period,
  trend,
  trendValue,
  icon,
}) => {
  // Determine trend color based on direction and context
  const getTrendColor = () => {
    if (trend === "up") {
      // For metrics where up is good (like uptime)
      if (
        title.toLowerCase().includes("uptime") ||
        title.toLowerCase().includes("availability")
      ) {
        return "text-green-500 dark:text-green-400";
      }
      // For metrics where up might be concerning (like CPU, memory)
      return "text-yellow-500 dark:text-yellow-400";
    }
    if (trend === "down") {
      // For metrics where down is concerning (like availability)
      if (
        title.toLowerCase().includes("uptime") ||
        title.toLowerCase().includes("availability")
      ) {
        return "text-red-500 dark:text-red-400";
      }
      // For metrics where down might be good (like CPU, memory)
      return "text-green-500 dark:text-green-400";
    }
    return "text-gray-500 dark:text-gray-400";
  };

  // Determine trend icon
  const getTrendIcon = () => {
    if (trend === "up") {
      return (
        <svg
          className="h-3 w-3"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M5 10l7-7m0 0l7 7m-7-7v18"
          />
        </svg>
      );
    }
    if (trend === "down") {
      return (
        <svg
          className="h-3 w-3"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M19 14l-7 7m0 0l-7-7m7 7V3"
          />
        </svg>
      );
    }
    return null;
  };

  return (
    <div className="bg-white dark:bg-gray-700 rounded-lg shadow-sm p-6 border border-gray-100 dark:border-gray-600 transition-all hover:shadow-md">
      <div className="flex items-center">
        {icon && <div className="mr-4">{icon}</div>}
        <div>
          <h3 className="text-gray-500 dark:text-gray-300 text-sm">{title}</h3>
          <p className="text-3xl font-bold text-gray-800 dark:text-white mt-1">
            {value}
          </p>
          <div className="flex items-center mt-1">
            {period && (
              <p className="text-xs text-gray-500 dark:text-gray-400">
                {period}
              </p>
            )}
            {trend && trendValue && (
              <div className={`flex items-center ml-2 ${getTrendColor()}`}>
                {getTrendIcon()}
                <span className="text-xs ml-1">{trendValue}</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
