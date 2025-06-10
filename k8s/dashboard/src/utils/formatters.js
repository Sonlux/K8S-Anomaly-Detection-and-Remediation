// Utility functions for formatting data

export const formatPercentage = (value) => {
  return `${(value * 100).toFixed(1)}%`;
};

export const formatMemory = (bytes) => {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`;
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  return `${(bytes / (1024 * 1024 * 1024)).toFixed(2)} GB`;
};

export const formatDate = (timestamp) => {
  return new Date(timestamp).toLocaleString();
};