#!/usr/bin/env python3
"""Basic test script for Flutter Earth application."""

import os
import sys
import logging
from datetime import datetime, timedelta

# Add the dead_the_third package to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'dead_the_third'))

def setup_logging():
    """Setup basic logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def test_earth_engine_auth():
    """Test Earth Engine authentication."""
    print("Testing Earth Engine authentication...")
    
    try:
        import ee
        from ee import data as ee_data
        
        # Try to initialize Earth Engine
        print("Attempting to initialize Earth Engine...")
        ee.Initialize()
        
        # Test basic functionality
        print("Testing basic Earth Engine functionality...")
        test_image = ee.Image('USGS/SRTMGL1_003')
        bounds = test_image.geometry().bounds().getInfo()
        print(f"Successfully loaded test image with bounds: {bounds}")
        
        print("✅ Earth Engine authentication successful!")
        return True
        
    except Exception as e:
        print(f"❌ Earth Engine authentication failed: {e}")
        print("\nTo fix this issue:")
        print("1. Install the Earth Engine Python API: pip install earthengine-api")
        print("2. Authenticate with Earth Engine: earthengine authenticate")
        print("3. Make sure you have a Google Cloud project with Earth Engine enabled")
        print("4. Visit https://developers.google.com/earth-engine/guides/access to sign up")
        return False

def test_basic_imports():
    """Test basic imports."""
    print("Testing basic imports...")
    
    try:
        from dead_the_third.types import AppConfig, SatelliteDetails
        from dead_the_third.config import ConfigManager
        from dead_the_third.errors import EarthEngineError
        print("✅ Basic imports successful!")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_config_manager():
    """Test configuration manager."""
    print("Testing configuration manager...")
    
    try:
        from dead_the_third.config import ConfigManager
        
        config_manager = ConfigManager()
        config = config_manager.config
        
        print(f"✅ Configuration loaded successfully!")
        print(f"   Output directory: {config.get('output_dir', 'Not set')}")
        print(f"   Tile size: {config.get('tile_size', 'Not set')}")
        print(f"   Max workers: {config.get('max_workers', 'Not set')}")
        
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_download_manager():
    """Test download manager initialization."""
    print("Testing download manager...")
    
    try:
        from dead_the_third.download_manager import DownloadManager
        from dead_the_third.config import ConfigManager
        
        config_manager = ConfigManager()
        download_manager = DownloadManager()
        
        # Convert config to dict for compatibility
        config_dict = dict(config_manager.config)
        download_manager.initialize(config_dict)
        
        print("✅ Download manager initialized successfully!")
        return True
    except Exception as e:
        print(f"❌ Download manager error: {e}")
        return False

def main():
    """Run all tests."""
    setup_logging()
    
    print("=" * 50)
    print("Flutter Earth Basic Test Suite")
    print("=" * 50)
    
    tests = [
        ("Basic Imports", test_basic_imports),
        ("Configuration Manager", test_config_manager),
        ("Download Manager", test_download_manager),
        ("Earth Engine Authentication", test_earth_engine_auth),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("Test Results Summary:")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All tests passed! Your Flutter Earth setup is ready.")
        print("You can now run: python flutter_earth_6-19.py")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above before running the main application.")
        
        if not any(name == "Earth Engine Authentication" and result for name, result in results):
            print("\n🔧 To fix Earth Engine authentication:")
            print("1. Run: pip install earthengine-api")
            print("2. Run: earthengine authenticate")
            print("3. Follow the authentication prompts")
            print("4. Make sure you have Earth Engine access enabled")

if __name__ == "__main__":
    main() 