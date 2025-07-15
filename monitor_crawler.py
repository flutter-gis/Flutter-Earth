#!/usr/bin/env python3
"""
Monitor script for the Enhanced Crawler UI
Checks if the UI is responsive and detects potential issues
"""

import psutil
import time
import os
import sys
from datetime import datetime

def find_crawler_process():
    """Find the crawler UI process"""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] == 'python.exe':
                cmdline = proc.info['cmdline']
                if cmdline and any('enhanced_crawler_ui.py' in arg for arg in cmdline):
                    return proc
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return None

def monitor_process(proc):
    """Monitor the crawler process for issues"""
    print(f"Monitoring crawler process (PID: {proc.pid})")
    print("=" * 60)
    
    start_time = time.time()
    last_memory = 0
    memory_increases = 0
    
    try:
        while proc.is_running():
            # Get process info
            cpu_percent = proc.cpu_percent()
            memory_info = proc.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024
            
            # Check for memory leaks
            if last_memory > 0:
                memory_diff = memory_mb - last_memory
                if memory_diff > 50:  # More than 50MB increase
                    memory_increases += 1
                    print(f"⚠ WARNING: Memory increased by {memory_diff:.1f}MB")
            
            # Check if process is responding
            try:
                proc.status()
                status = "Running"
            except psutil.NoSuchProcess:
                status = "Not Found"
                break
            
            # Print status
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] CPU: {cpu_percent:5.1f}% | Memory: {memory_mb:7.1f}MB | Status: {status}")
            
            # Check for potential issues
            if memory_mb > 2000:  # More than 2GB
                print(f"⚠ WARNING: High memory usage ({memory_mb:.1f}MB)")
            
            if cpu_percent > 80:  # High CPU usage
                print(f"⚠ WARNING: High CPU usage ({cpu_percent:.1f}%)")
            
            if memory_increases > 5:
                print("⚠ WARNING: Multiple memory increases detected - potential memory leak")
            
            last_memory = memory_mb
            time.sleep(2)  # Check every 2 seconds
            
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user")
    except Exception as e:
        print(f"Error monitoring process: {e}")
    
    # Final status
    if proc.is_running():
        print(f"\n✅ Process is still running after {time.time() - start_time:.1f} seconds")
    else:
        print(f"\n❌ Process stopped unexpectedly")

def main():
    print("Enhanced Crawler UI Monitor")
    print("=" * 30)
    
    # Find the crawler process
    proc = find_crawler_process()
    
    if proc is None:
        print("❌ Crawler UI process not found")
        print("Make sure enhanced_crawler_ui.py is running")
        return
    
    print(f"✅ Found crawler process (PID: {proc.pid})")
    print(f"Command: {' '.join(proc.cmdline())}")
    print()
    
    # Start monitoring
    monitor_process(proc)

if __name__ == "__main__":
    main() 