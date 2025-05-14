#!/usr/bin/env python3
"""
Kubernetes Anomaly Visualization Dashboard Launcher

This script launches the Streamlit-based visualization dashboard for the Kubernetes multi-agent system.
"""

import os
import sys
import subprocess
import argparse
import time

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import streamlit
        import plotly
        import pandas
        import numpy
        import networkx
        return True
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Please install required dependencies with: pip install -r requirements-dashboard.txt")
        return False

def launch_dashboard(port=8501, debug=False):
    """Launch the Streamlit dashboard"""
    # Find the dashboard script path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Look for the dashboard in the src directory first (preferred location)
    dashboard_path = os.path.join(script_dir, "src", "k8s_visualization_dashboard.py")
    
    if not os.path.exists(dashboard_path):
        # Fall back to the agents directory as an alternative location
        dashboard_path = os.path.join(script_dir, "agents", "k8s_visualization_dashboard.py")
        
        # If still not found, create a symbolic link or copy from src to agents
        if not os.path.exists(dashboard_path):
            src_path = os.path.join(script_dir, "src", "k8s_visualization_dashboard.py")
            if os.path.exists(src_path):
                # Ensure the agents directory exists
                agents_dir = os.path.join(script_dir, "agents")
                os.makedirs(agents_dir, exist_ok=True)
                
                # Copy the file from src to agents
                import shutil
                shutil.copy2(src_path, dashboard_path)
                print(f"Copied dashboard from {src_path} to {dashboard_path}")
            else:
                print(f"Dashboard file not found at: {src_path} or {dashboard_path}")
                return False
    
    # Set environment variables
    env = os.environ.copy()
    if debug:
        env["STREAMLIT_LOGGER_LEVEL"] = "debug"
        
    # Launch Streamlit
    cmd = [
        "streamlit", "run", dashboard_path,
        "--server.port", str(port),
        "--server.address", "0.0.0.0",
        "--browser.serverAddress", "localhost"
    ]
    
    print(f"Launching dashboard on http://localhost:{port}")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        # Start the Streamlit process
        process = subprocess.Popen(cmd, env=env)
        
        # Keep the script running while the dashboard is active
        while process.poll() is None:
            time.sleep(1)
            
        return process.returncode == 0
    except KeyboardInterrupt:
        print("Dashboard stopped by user")
        return True
    except Exception as e:
        print(f"Error launching dashboard: {e}")
        return False

def main():
    """Main function to parse arguments and launch the dashboard"""
    parser = argparse.ArgumentParser(description='Kubernetes Anomaly Visualization Dashboard')
    parser.add_argument('--port', type=int, default=8501, help='Port to run the dashboard on')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    # Check dependencies
    if not check_dependencies():
        return 1
    
    # Launch the dashboard
    success = launch_dashboard(port=args.port, debug=args.debug)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())