"""
Configuration loader utilities for easy integration with existing services.

This module provides simple functions to load configuration and integrate
with the existing codebase without major refactoring.
"""

import os
import logging
from typing import Dict, Any, Optional
from pathlib import Path

from .settings import get_config, setup_logging as _setup_logging


def load_config(env_file: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration and return as a dictionary for backward compatibility.
    
    Args:
        env_file: Optional path to .env file
    
    Returns:
        Dictionary containing all configuration values
    """
    config = get_config(env_file)
    
    return {
        # API Configuration
        "nvidia_api_key": config.api.nvidia_api_key,
        "llama_api_key": config.api.llama_api_key,
        "llama_api_url": config.api.llama_api_url,
        "openai_api_key": config.api.openai_api_key,
        "api_server_host": config.api.api_server_host,
        "api_server_port": config.api.api_server_port,
        "dashboard_api_port": config.api.dashboard_api_port,
        "mcp_server_port": config.api.mcp_server_port,
        "prometheus_url": config.api.prometheus_url,
        
        # Kubernetes Configuration
        "k8s_namespace": config.kubernetes.namespace,
        "kubeconfig_path": config.kubernetes.kubeconfig_path,
        "k8s_in_cluster": config.kubernetes.in_cluster,
        "k8s_test_mode": config.kubernetes.test_mode,
        
        # Database Configuration
        "chroma_db_path": config.database.chroma_db_path,
        "metrics_csv_path": config.database.metrics_csv_path,
        "insights_json_path": config.database.insights_json_path,
        "knowledge_base_path": config.database.knowledge_base_path,
        
        # Logging Configuration
        "log_level": config.logging.level,
        "log_format": config.logging.format,
        "log_file": config.logging.log_file,
        
        # Security Configuration
        "cors_origins": config.security.cors_origins,
        "rate_limit_per_minute": config.security.rate_limit_per_minute,
        "max_request_size": config.security.max_request_size,
        
        # Monitoring Configuration
        "metrics_collection_interval": config.monitoring.metrics_collection_interval,
        "anomaly_detection_threshold": config.monitoring.anomaly_detection_threshold,
        "enable_health_checks": config.monitoring.enable_health_checks,
        "performance_metrics": config.monitoring.performance_metrics,
    }


def get_api_config() -> Dict[str, Any]:
    """
    Get API configuration for LLM services.
    
    Returns:
        Dictionary with API configuration
    """
    config = get_config()
    return config.get_llm_config()


def get_database_paths() -> Dict[str, str]:
    """
    Get database and file paths.
    
    Returns:
        Dictionary with database paths
    """
    config = get_config()
    return {
        "chroma_db_path": config.database.chroma_db_path,
        "metrics_csv_path": config.database.metrics_csv_path,
        "insights_json_path": config.database.insights_json_path,
        "knowledge_base_path": config.database.knowledge_base_path,
    }


def get_kubernetes_config() -> Dict[str, Any]:
    """
    Get Kubernetes configuration.
    
    Returns:
        Dictionary with Kubernetes configuration
    """
    config = get_config()
    return {
        "namespace": config.kubernetes.namespace,
        "kubeconfig_path": config.kubernetes.kubeconfig_path,
        "in_cluster": config.kubernetes.in_cluster,
        "test_mode": config.kubernetes.test_mode,
    }


def setup_logging(env_file: Optional[str] = None) -> None:
    """
    Setup logging using centralized configuration.
    
    Args:
        env_file: Optional path to .env file
    """
    _setup_logging(env_file)


def ensure_data_directories() -> None:
    """
    Ensure all required data directories exist.
    """
    config = get_config()
    
    # Create data directories
    directories = [
        Path(config.database.chroma_db_path).parent,
        Path(config.database.metrics_csv_path).parent,
        Path(config.database.insights_json_path).parent,
        Path(config.database.knowledge_base_path).parent,
    ]
    
    # Add log directory if log file is configured
    if config.logging.log_file:
        directories.append(Path(config.logging.log_file).parent)
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)


def validate_environment() -> bool:
    """
    Validate that the environment is properly configured.
    
    Returns:
        True if environment is valid, False otherwise
    """
    config = get_config()
    logger = logging.getLogger(__name__)
    
    is_valid = True
    
    # Check for at least one LLM API key (warning only, not fatal)
    if not any([config.api.nvidia_api_key, config.api.llama_api_key, config.api.openai_api_key]):
        logger.warning("No LLM API keys configured. AI features will not work. Please set NVIDIA_API_KEY, LLAMA_API_KEY, or OPENAI_API_KEY")
        # Don't mark as invalid - system can still run without AI features
    
    # Check if data directories can be created
    try:
        ensure_data_directories()
    except Exception as e:
        logger.error(f"Cannot create required data directories: {e}")
        is_valid = False
    
    return is_valid


# Backward compatibility functions for existing code
def get_nvidia_api_key() -> Optional[str]:
    """Get NVIDIA API key from configuration."""
    return get_config().api.nvidia_api_key


def get_llama_api_key() -> Optional[str]:
    """Get Llama API key from configuration."""
    return get_config().api.llama_api_key


def get_openai_api_key() -> Optional[str]:
    """Get OpenAI API key from configuration."""
    return get_config().api.openai_api_key


def get_prometheus_url() -> Optional[str]:
    """Get Prometheus URL from configuration."""
    return get_config().api.prometheus_url


def is_test_mode() -> bool:
    """Check if test mode is enabled."""
    return get_config().kubernetes.test_mode


def is_debug_mode() -> bool:
    """Check if debug mode is enabled."""
    return os.getenv("K8S_DEBUG_MODE", "false").lower() == "true"