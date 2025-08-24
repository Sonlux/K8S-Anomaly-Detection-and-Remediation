"""
Centralized configuration management for the Kubernetes monitoring system.

This module provides a centralized way to manage all configuration settings,
environment variables, and application defaults.
"""

import os
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class DatabaseConfig:
    """Database configuration settings."""
    chroma_db_path: str = "backend/data/chroma_db"
    metrics_csv_path: str = "backend/data/pod_metrics.csv"
    insights_json_path: str = "backend/data/pod_insights.json"
    knowledge_base_path: str = "backend/data/k8s_knowledge.json"


@dataclass
class APIConfig:
    """API configuration settings."""
    # LLM API Keys
    nvidia_api_key: Optional[str] = None
    llama_api_key: Optional[str] = None
    llama_api_url: Optional[str] = None
    openai_api_key: Optional[str] = None
    
    # Server Configuration
    api_server_host: str = "0.0.0.0"
    api_server_port: int = 8000
    dashboard_api_port: int = 5000
    mcp_server_port: int = 8000
    
    # External Services
    prometheus_url: Optional[str] = None


@dataclass
class KubernetesConfig:
    """Kubernetes configuration settings."""
    namespace: str = "default"
    kubeconfig_path: Optional[str] = None
    in_cluster: bool = False
    test_mode: bool = False


@dataclass
class LoggingConfig:
    """Logging configuration settings."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_file: Optional[str] = None
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5


@dataclass
class SecurityConfig:
    """Security configuration settings."""
    cors_origins: list = field(default_factory=lambda: ["*"])
    rate_limit_per_minute: int = 60
    max_request_size: int = 16 * 1024 * 1024  # 16MB
    
    
@dataclass
class MonitoringConfig:
    """Monitoring and metrics configuration."""
    metrics_collection_interval: int = 30  # seconds
    anomaly_detection_threshold: float = 0.8
    enable_health_checks: bool = True
    performance_metrics: bool = True


class ConfigurationManager:
    """
    Centralized configuration manager that loads and validates all settings.
    
    This class handles loading configuration from environment variables,
    providing defaults, and validating required settings.
    """
    
    def __init__(self, env_file: Optional[str] = None):
        """
        Initialize configuration manager.
        
        Args:
            env_file: Optional path to .env file to load
        """
        self.logger = logging.getLogger(__name__)
        
        # Load environment variables from .env file if provided
        if env_file and Path(env_file).exists():
            self._load_env_file(env_file)
        
        # Initialize configuration sections
        self.database = self._load_database_config()
        self.api = self._load_api_config()
        self.kubernetes = self._load_kubernetes_config()
        self.logging = self._load_logging_config()
        self.security = self._load_security_config()
        self.monitoring = self._load_monitoring_config()
        
        # Validate configuration
        self._validate_config()
    
    def _load_env_file(self, env_file: str) -> None:
        """Load environment variables from .env file."""
        try:
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ.setdefault(key.strip(), value.strip())
        except Exception as e:
            self.logger.warning(f"Could not load .env file {env_file}: {e}")
    
    def _load_database_config(self) -> DatabaseConfig:
        """Load database configuration from environment variables."""
        return DatabaseConfig(
            chroma_db_path=os.getenv("CHROMA_DB_PATH", "backend/data/chroma_db"),
            metrics_csv_path=os.getenv("METRICS_CSV_PATH", "backend/data/pod_metrics.csv"),
            insights_json_path=os.getenv("INSIGHTS_JSON_PATH", "backend/data/pod_insights.json"),
            knowledge_base_path=os.getenv("KNOWLEDGE_BASE_PATH", "backend/data/k8s_knowledge.json")
        )
    
    def _load_api_config(self) -> APIConfig:
        """Load API configuration from environment variables."""
        return APIConfig(
            nvidia_api_key=os.getenv("NVIDIA_API_KEY"),
            llama_api_key=os.getenv("LLAMA_API_KEY"),
            llama_api_url=os.getenv("LLAMA_API_URL", "https://api.llama-api.com"),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            api_server_host=os.getenv("API_SERVER_HOST", "0.0.0.0"),
            api_server_port=int(os.getenv("API_SERVER_PORT", "8000")),
            dashboard_api_port=int(os.getenv("DASHBOARD_API_PORT", "5000")),
            mcp_server_port=int(os.getenv("MCP_SERVER_PORT", "8000")),
            prometheus_url=os.getenv("PROMETHEUS_URL")
        )
    
    def _load_kubernetes_config(self) -> KubernetesConfig:
        """Load Kubernetes configuration from environment variables."""
        return KubernetesConfig(
            namespace=os.getenv("K8S_NAMESPACE", "default"),
            kubeconfig_path=os.getenv("KUBECONFIG"),
            in_cluster=os.getenv("K8S_IN_CLUSTER", "false").lower() == "true",
            test_mode=os.getenv("K8S_TEST_MODE", "false").lower() == "true"
        )
    
    def _load_logging_config(self) -> LoggingConfig:
        """Load logging configuration from environment variables."""
        return LoggingConfig(
            level=os.getenv("LOG_LEVEL", "INFO").upper(),
            format=os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
            log_file=os.getenv("LOG_FILE"),
            max_file_size=int(os.getenv("LOG_MAX_FILE_SIZE", str(10 * 1024 * 1024))),
            backup_count=int(os.getenv("LOG_BACKUP_COUNT", "5"))
        )
    
    def _load_security_config(self) -> SecurityConfig:
        """Load security configuration from environment variables."""
        cors_origins = os.getenv("CORS_ORIGINS", "*")
        if cors_origins == "*":
            origins = ["*"]
        else:
            origins = [origin.strip() for origin in cors_origins.split(",")]
        
        return SecurityConfig(
            cors_origins=origins,
            rate_limit_per_minute=int(os.getenv("RATE_LIMIT_PER_MINUTE", "60")),
            max_request_size=int(os.getenv("MAX_REQUEST_SIZE", str(16 * 1024 * 1024)))
        )
    
    def _load_monitoring_config(self) -> MonitoringConfig:
        """Load monitoring configuration from environment variables."""
        return MonitoringConfig(
            metrics_collection_interval=int(os.getenv("METRICS_COLLECTION_INTERVAL", "30")),
            anomaly_detection_threshold=float(os.getenv("ANOMALY_DETECTION_THRESHOLD", "0.8")),
            enable_health_checks=os.getenv("ENABLE_HEALTH_CHECKS", "true").lower() == "true",
            performance_metrics=os.getenv("PERFORMANCE_METRICS", "true").lower() == "true"
        )
    
    def _validate_config(self) -> None:
        """Validate configuration and log warnings for missing required settings."""
        warnings = []
        
        # Check for at least one LLM API key
        if not any([self.api.nvidia_api_key, self.api.llama_api_key, self.api.openai_api_key]):
            warnings.append("No LLM API keys configured. AI features will not work.")
        
        # Validate logging level
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.logging.level not in valid_levels:
            warnings.append(f"Invalid log level '{self.logging.level}'. Using INFO instead.")
            self.logging.level = "INFO"
        
        # Validate ports
        if not (1 <= self.api.api_server_port <= 65535):
            warnings.append(f"Invalid API server port {self.api.api_server_port}. Using 8000.")
            self.api.api_server_port = 8000
        
        if not (1 <= self.api.dashboard_api_port <= 65535):
            warnings.append(f"Invalid dashboard API port {self.api.dashboard_api_port}. Using 5000.")
            self.api.dashboard_api_port = 5000
        
        # Log warnings
        for warning in warnings:
            self.logger.warning(warning)
    
    def get_llm_config(self) -> Dict[str, Any]:
        """
        Get LLM configuration for the multi-agent system.
        
        Returns:
            Dictionary with LLM configuration settings
        """
        return {
            "nvidia_api_key": self.api.nvidia_api_key,
            "llama_api_key": self.api.llama_api_key,
            "llama_api_url": self.api.llama_api_url,
            "openai_api_key": self.api.openai_api_key,
            "use_llm": any([self.api.nvidia_api_key, self.api.llama_api_key, self.api.openai_api_key])
        }
    
    def setup_logging(self) -> None:
        """Configure logging based on the logging configuration."""
        # Configure root logger
        logging.basicConfig(
            level=getattr(logging, self.logging.level),
            format=self.logging.format,
            handlers=[]
        )
        
        # Add console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(self.logging.format))
        logging.getLogger().addHandler(console_handler)
        
        # Add file handler if log file is specified
        if self.logging.log_file:
            try:
                from logging.handlers import RotatingFileHandler
                file_handler = RotatingFileHandler(
                    self.logging.log_file,
                    maxBytes=self.logging.max_file_size,
                    backupCount=self.logging.backup_count
                )
                file_handler.setFormatter(logging.Formatter(self.logging.format))
                logging.getLogger().addHandler(file_handler)
            except Exception as e:
                logging.warning(f"Could not setup file logging: {e}")


# Global configuration instance
_config_instance: Optional[ConfigurationManager] = None


def get_config(env_file: Optional[str] = None) -> ConfigurationManager:
    """
    Get the global configuration instance.
    
    Args:
        env_file: Optional path to .env file (only used on first call)
    
    Returns:
        ConfigurationManager instance
    """
    global _config_instance
    
    if _config_instance is None:
        _config_instance = ConfigurationManager(env_file)
    
    return _config_instance


def setup_logging(env_file: Optional[str] = None) -> None:
    """
    Setup logging using the configuration manager.
    
    Args:
        env_file: Optional path to .env file
    """
    config = get_config(env_file)
    config.setup_logging()