#!/usr/bin/env python3
"""
Test script to verify that all services can import and use the new configuration system.

This script tests that the configuration management system is properly integrated
across all backend services.
"""

import sys
import os
from pathlib import Path

# Add the project root directory to the path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def test_service_imports():
    """Test that all services can import with the new configuration system."""
    print("=" * 60)
    print("Testing Service Imports with Configuration System")
    print("=" * 60)
    
    services = [
        ("API Server", "backend.src.api.api_server"),
        ("MCP Server", "backend.src.api.mcp_server"),
        ("Dashboard API", "backend.src.api.dashboard_api"),
        ("NVIDIA LLM", "backend.src.agents.nvidia_llm"),
        ("Configuration System", "backend.src.config.settings"),
        ("Configuration Loader", "backend.src.config.loader"),
    ]
    
    results = []
    
    for service_name, module_name in services:
        print(f"\nTesting {service_name}...")
        try:
            __import__(module_name)
            print(f"✓ {service_name} imported successfully")
            results.append((service_name, True, None))
        except Exception as e:
            print(f"✗ {service_name} failed to import: {e}")
            results.append((service_name, False, str(e)))
    
    # Summary
    print("\n" + "=" * 60)
    print("Import Test Results")
    print("=" * 60)
    
    successful = 0
    for service_name, success, error in results:
        if success:
            print(f"✓ {service_name}")
            successful += 1
        else:
            print(f"✗ {service_name}: {error}")
    
    print(f"\nResults: {successful}/{len(services)} services imported successfully")
    
    return successful == len(services)


def test_configuration_functions():
    """Test configuration functions work correctly."""
    print("\n" + "=" * 60)
    print("Testing Configuration Functions")
    print("=" * 60)
    
    try:
        from config.loader import (
            get_config, get_api_config, get_kubernetes_config,
            get_database_paths, validate_environment, ensure_data_directories
        )
        
        # Test get_config
        print("\n1. Testing get_config()...")
        config = get_config()
        print(f"✓ Configuration loaded: {type(config).__name__}")
        
        # Test get_api_config
        print("\n2. Testing get_api_config()...")
        api_config = get_api_config()
        print(f"✓ API config loaded: {len(api_config)} keys")
        
        # Test get_kubernetes_config
        print("\n3. Testing get_kubernetes_config()...")
        k8s_config = get_kubernetes_config()
        print(f"✓ Kubernetes config loaded: namespace={k8s_config['namespace']}")
        
        # Test get_database_paths
        print("\n4. Testing get_database_paths()...")
        db_paths = get_database_paths()
        print(f"✓ Database paths loaded: {len(db_paths)} paths")
        
        # Test validate_environment
        print("\n5. Testing validate_environment()...")
        is_valid = validate_environment()
        print(f"✓ Environment validation: {'Valid' if is_valid else 'Has warnings'}")
        
        # Test ensure_data_directories
        print("\n6. Testing ensure_data_directories()...")
        ensure_data_directories()
        print("✓ Data directories ensured")
        
        return True
        
    except Exception as e:
        print(f"✗ Configuration function test failed: {e}")
        return False


def test_backward_compatibility():
    """Test backward compatibility functions."""
    print("\n" + "=" * 60)
    print("Testing Backward Compatibility")
    print("=" * 60)
    
    try:
        from config.loader import (
            get_nvidia_api_key, get_llama_api_key, get_openai_api_key,
            get_prometheus_url, is_test_mode, is_debug_mode
        )
        
        functions = [
            ("get_nvidia_api_key", get_nvidia_api_key),
            ("get_llama_api_key", get_llama_api_key),
            ("get_openai_api_key", get_openai_api_key),
            ("get_prometheus_url", get_prometheus_url),
            ("is_test_mode", is_test_mode),
            ("is_debug_mode", is_debug_mode),
        ]
        
        for func_name, func in functions:
            try:
                result = func()
                print(f"✓ {func_name}(): {type(result).__name__}")
            except Exception as e:
                print(f"✗ {func_name}() failed: {e}")
                return False
        
        return True
        
    except Exception as e:
        print(f"✗ Backward compatibility test failed: {e}")
        return False


def main():
    """Main test function."""
    print("Starting configuration system integration tests...\n")
    
    # Test service imports
    imports_ok = test_service_imports()
    
    # Test configuration functions
    functions_ok = test_configuration_functions()
    
    # Test backward compatibility
    compat_ok = test_backward_compatibility()
    
    # Final results
    print("\n" + "=" * 60)
    print("Final Test Results")
    print("=" * 60)
    
    tests = [
        ("Service Imports", imports_ok),
        ("Configuration Functions", functions_ok),
        ("Backward Compatibility", compat_ok),
    ]
    
    all_passed = True
    for test_name, passed in tests:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status} {test_name}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All tests passed! Configuration system is fully integrated.")
        return 0
    else:
        print("\n❌ Some tests failed. Please check the configuration system.")
        return 1


if __name__ == "__main__":
    sys.exit(main())