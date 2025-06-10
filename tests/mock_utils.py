#!/usr/bin/env python
"""
Mock utils module for testing remediation_logic.py
"""
import logging

# Create a logger
logger = logging.getLogger("mock-utils")

def setup_k8s_client():
    """Mock setup_k8s_client function"""
    from mock_k8s import CoreV1Api, AppsV1Api
    return CoreV1Api(), AppsV1Api()

def parse_resource_value(resource_str, factor=1.0, return_unit=False, is_memory=False):
    """
    Parse a Kubernetes resource value string into a float.
    
    Args:
        resource_str: Resource value string (e.g., '100m', '1Gi', '0.5')
        factor: Multiplication factor for the parsed value
        return_unit: If True, return the unit along with the value
        is_memory: If True, treat as memory value (for byte units)
        
    Returns:
        Float value representing the resource quantity, or (value, unit) if return_unit=True
    """
    if not resource_str:
        return (0.0, '') if return_unit else 0.0
    
    # Memory units
    memory_multipliers = {
        'Ki': 1024,
        'Mi': 1024**2,
        'Gi': 1024**3,
        'Ti': 1024**4,
        'Pi': 1024**5,
        'Ei': 1024**6,
        'K': 1000,
        'M': 1000**2,
        'G': 1000**3,
        'T': 1000**4,
        'P': 1000**5,
        'E': 1000**6
    }
    
    # CPU units
    if resource_str.endswith('m') and not is_memory:
        value = float(resource_str[:-1]) * factor / 1000.0
        unit = 'm'
    # Memory units
    elif is_memory or any(resource_str.endswith(suffix) for suffix in memory_multipliers):
        for suffix, multiplier in memory_multipliers.items():
            if resource_str.endswith(suffix):
                value = float(resource_str[:-len(suffix)]) * factor * multiplier
                unit = suffix
                break
        else:
            try:
                value = float(resource_str) * factor
                unit = ''
            except ValueError:
                return (0.0, '') if return_unit else 0.0
    # Plain number
    else:
        try:
            value = float(resource_str) * factor
            unit = ''
        except ValueError:
            return (0.0, '') if return_unit else 0.0
    
    return (value, unit) if return_unit else value

def safe_api_call(func, max_retries=3, retry_delay=1):
    """Mock safe_api_call function that just calls the function directly"""
    try:
        return func()
    except Exception as e:
        logger.error(f"Error in API call: {str(e)}")
        raise 