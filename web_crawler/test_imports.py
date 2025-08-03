#!/usr/bin/env python3
"""
Test imports for the crawler
"""

def test_imports():
    """Test all imports"""
    print("🧪 Testing imports...")
    
    try:
        import os
        print("✅ os imported")
        
        import sys
        print("✅ sys imported")
        
        import json
        print("✅ json imported")
        
        import time
        print("✅ time imported")
        
        import threading
        print("✅ threading imported")
        
        import requests
        print("✅ requests imported")
        
        import warnings
        print("✅ warnings imported")
        
        import re
        print("✅ re imported")
        
        from datetime import datetime
        print("✅ datetime imported")
        
        from urllib.parse import urljoin, urlparse
        print("✅ urllib.parse imported")
        
        from bs4 import BeautifulSoup
        print("✅ BeautifulSoup imported")
        
        from PySide6.QtWidgets import QApplication, QWidget
        print("✅ PySide6.QtWidgets imported")
        
        from PySide6.QtCore import Signal
        print("✅ PySide6.QtCore imported")
        
        from PySide6.QtGui import QPixmap
        print("✅ PySide6.QtGui imported")
        
        print("✅ All imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    print("🚀 Starting import test...")
    if test_imports():
        print("✅ All import tests passed!")
    else:
        print("❌ Import tests failed!")
        import sys
        sys.exit(1) 