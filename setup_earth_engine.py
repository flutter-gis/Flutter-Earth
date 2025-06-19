#!/usr/bin/env python3
"""Setup script for Flutter Earth Earth Engine authentication."""

import os
import sys
import subprocess
import platform

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python version {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_package(package):
    """Install a Python package."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def check_package(package):
    """Check if a package is installed."""
    try:
        __import__(package)
        return True
    except ImportError:
        return False

def setup_earth_engine():
    """Setup Earth Engine authentication."""
    print("Setting up Earth Engine for Flutter Earth...")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Check/install required packages
    required_packages = [
        ('earthengine-api', 'earthengine'),
        ('numpy', 'numpy'),
        ('rasterio', 'rasterio'),
        ('folium', 'folium'),
        ('requests', 'requests')
    ]
    
    print("\nChecking required packages...")
    for package_name, import_name in required_packages:
        if check_package(import_name):
            print(f"✅ {package_name} is already installed")
        else:
            print(f"📦 Installing {package_name}...")
            if install_package(package_name):
                print(f"✅ {package_name} installed successfully")
            else:
                print(f"❌ Failed to install {package_name}")
                return False
    
    # Authenticate with Earth Engine
    print("\n🔐 Setting up Earth Engine authentication...")
    print("This will open a browser window for authentication.")
    print("If no browser opens, you'll need to manually copy the URL.")
    
    try:
        # Try to authenticate
        result = subprocess.run(['earthengine', 'authenticate'], 
                              capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ Earth Engine authentication successful!")
            return True
        else:
            print(f"❌ Earth Engine authentication failed:")
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Authentication timed out. Please try again.")
        return False
    except FileNotFoundError:
        print("❌ 'earthengine' command not found.")
        print("   This usually means the earthengine-api package wasn't installed correctly.")
        return False
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return False

def test_earth_engine():
    """Test Earth Engine functionality."""
    print("\n🧪 Testing Earth Engine functionality...")
    
    try:
        import ee
        from ee import data as ee_data
        
        # Initialize Earth Engine
        ee.Initialize()
        
        # Test basic functionality
        test_image = ee.Image('USGS/SRTMGL1_003')
        bounds = test_image.geometry().bounds().getInfo()
        
        print("✅ Earth Engine test successful!")
        print(f"   Test image bounds: {bounds}")
        return True
        
    except Exception as e:
        print(f"❌ Earth Engine test failed: {e}")
        return False

def main():
    """Main setup function."""
    print("Flutter Earth - Earth Engine Setup")
    print("=" * 50)
    
    # Setup Earth Engine
    if not setup_earth_engine():
        print("\n❌ Setup failed. Please check the errors above.")
        print("\nManual setup instructions:")
        print("1. Install Earth Engine API: pip install earthengine-api")
        print("2. Authenticate: earthengine authenticate")
        print("3. Visit https://developers.google.com/earth-engine/guides/access to sign up")
        return False
    
    # Test Earth Engine
    if not test_earth_engine():
        print("\n❌ Earth Engine test failed. Please check your authentication.")
        return False
    
    print("\n🎉 Earth Engine setup completed successfully!")
    print("You can now run: python test_basic.py")
    print("Or run the main application: python flutter_earth_6-19.py")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 