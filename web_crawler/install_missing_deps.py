#!/usr/bin/env python3
"""
Install missing dependencies for the web crawler
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ Successfully installed {package}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package}: {e}")
        return False

def main():
    """Install missing dependencies"""
    print("🔧 Installing missing dependencies...")
    
    # List of missing packages
    missing_packages = [
        "aiohttp",
        "websockets", 
        "schedule",
        "sentencepiece"
    ]
    
    success_count = 0
    total_count = len(missing_packages)
    
    for package in missing_packages:
        print(f"📦 Installing {package}...")
        if install_package(package):
            success_count += 1
    
    print(f"\n📊 Installation Summary:")
    print(f"✅ Successfully installed: {success_count}/{total_count}")
    print(f"❌ Failed installations: {total_count - success_count}")
    
    if success_count == total_count:
        print("🎉 All dependencies installed successfully!")
    else:
        print("⚠️ Some dependencies failed to install. The crawler will work with reduced functionality.")

if __name__ == "__main__":
    main() 