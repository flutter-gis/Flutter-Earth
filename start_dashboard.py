#!/usr/bin/env python3
"""
Simple script to start the analytics dashboard
"""

import webbrowser
import time
from analytics_dashboard import get_dashboard

def main():
    print("Starting Earth Engine Crawler Analytics Dashboard...")
    
    # Get dashboard instance
    dashboard = get_dashboard()
    
    # Start dashboard in background
    print("Starting dashboard server...")
    dashboard.start_background()
    
    # Wait a moment for server to start
    time.sleep(3)
    
    # Open in browser
    url = "http://127.0.0.1:8080"
    print(f"Opening dashboard in browser: {url}")
    webbrowser.open(url)
    
    print("Dashboard started successfully!")
    print("Press Ctrl+C to stop...")
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping dashboard...")
        dashboard.stop_monitoring()

if __name__ == "__main__":
    main() 