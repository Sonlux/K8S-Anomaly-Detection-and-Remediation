#!/usr/bin/env python3
"""
Test script for the configuration management system.

This script validates that the configuration system is working correctly
and displays the current configuration values.
"""

import sys
import os
from pathlib import Path

# Add the backend src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.loader import (
    get_config, setup_logging, validate_environment, 
    ensure_data_directories, load_config
)


def test_configuration():
    """Test the configuration management system."""
    print("=" * 60)
    print("Configuration Management System Test")
    print("=" * 60)
    
    # Setup logging
    print("\n1. Setting up logging...")
    try:
        setup_logging()
        print("✓ Logging setup successful")
    except Exception as e:
        print(f"✗ Logging setup failed: {e}")
        return False
    
    # Load configuration
    print("\n2. Loading configuration...")
    try:
        config = get_config()
        print("✓ Configuration loaded successfully")
    except Exception as e:
        print(f"✗ Configuration loading failed: {e}")
        return False
    
    # Validate environment
    print("\n3. Validating environment...")
    try:
        is_valid = validate_environment()
        if is_valid:
            print("✓ Environment validation passed")
        else:
            print("⚠ Environment validation failed (some features may not work)")
    except Exception as e:
        print(f"✗ Environment validation error: {e}")
        return False
    
    # Ensure data directories
    print("\n4. Ensuring data directories exist...")
    try:
        ensure_data_directories()
        print("✓ Data directories created/verified")
    except Exception as e:
        print(f"✗ Data directory creation failed: {e}")
        return False
    
    # Display configuration
    print("\n5. Current Configuration:")
    print("-" * 40)
    
    print(f"API Server: {config.api.api_server_host}:{config.api.api_server_port}")
    print(f"Dashboard API: {config.api.dashboard_api_port}")
    print(f"MCP Server: {config.api.mcp_server_port}")
    print(f"Log Level: {config.logging.level}")
    print(f"Kubernetes Namespace: {config.kubernetes.namespace}")
    print(f"Test Mode: {config.kubernetes.test_mode}")
    print(f"CORS Origins: {config.security.cors_origins}")
    
    # API Keys (masked for security)
    print("\nAPI Keys:")
    nvidia_key = config.api.nvidia_api_key
    print(f"NVIDIA API Key: {'✓ Set' if nvidia_key else '✗ Not set'}")
    if nvidia_key:
        print(f"  Key preview: {nvidia_key[:10]}...{nvidia_key[-4:]}")
    
    llama_key = config.api.llama_api_key
    print(f"Llama API Key: {'✓ Set' if llama_key else '✗ Not set'}")
    
    openai_key = config.api.openai_api_key
    print(f"OpenAI API Key: {'✓ Set' if openai_key else '✗ Not set'}")
    
    # Database paths
    print("\nDatabase Paths:")
    print(f"ChromaDB: {config.database.chroma_db_path}")
    print(f"Metrics CSV: {config.database.metrics_csv_path}")
    print(f"Insights JSON: {config.database.insights_json_path}")
    print(f"Knowledge Base: {config.database.knowledge_base_path}")
    
    # Check if paths exist
    for name, path in [
        ("ChromaDB", config.database.chroma_db_path),
        ("Metrics CSV", config.database.metrics_csv_path),
        ("Insights JSON", config.database.insights_json_path),
        ("Knowledge Base", config.database.knowledge_base_path)
    ]:
        path_obj = Path(path)
        if path_obj.exists():
            print(f"  {name}: ✓ Exists")
        else:
            parent_exists = path_obj.parent.exists()
            print(f"  {name}: ✗ Not found (parent {'exists' if parent_exists else 'missing'})")
    
    print("\n" + "=" * 60)
    print("Configuration test completed successfully!")
    print("=" * 60)
    
    return True


def test_backward_compatibility():
    """Test backward compatibility functions."""
    print("\n" + "=" * 60)
    print("Testing Backward Compatibility Functions")
    print("=" * 60)
    
    try:
        from config.loader import (
            get_nvidia_api_key, get_llama_api_key, get_openai_api_key,
            get_prometheus_url, is_test_mode, is_debug_mode
        )
        
        print(f"get_nvidia_api_key(): {'✓ Set' if get_nvidia_api_key() else '✗ Not set'}")
        print(f"get_llama_api_key(): {'✓ Set' if get_llama_api_key() else '✗ Not set'}")
        print(f"get_openai_api_key(): {'✓ Set' if get_openai_api_key() else '✗ Not set'}")
        print(f"get_prometheus_url(): {get_prometheus_url() or 'Not set'}")
        print(f"is_test_mode(): {is_test_mode()}")
        print(f"is_debug_mode(): {is_debug_mode()}")
        
        print("✓ All backward compatibility functions work")
        return True
        
    except Exception as e:
        print(f"✗ Backward compatibility test failed: {e}")
        return False


if __name__ == "__main__":
    print("Starting configuration system tests...\n")
    
    # Test main configuration
    config_success = test_configuration()
    
    # Test backward compatibility
    compat_success = test_backward_compatibility()
    
    if config_success and compat_success:
        print("\n🎉 All tests passed! Configuration system is working correctly.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please check the configuration.")
        sys.exit(1)