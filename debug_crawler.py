#!/usr/bin/env python3
"""
Debug version of the crawler to catch UI initialization errors
"""

import sys
import traceback

try:
    print("🔍 Importing PySide6...")
    from PySide6.QtWidgets import QApplication
    print("✅ PySide6 imported successfully")
    
    print("🔍 Importing the crawler module...")
    from web_crawler.lightweight_crawler import LocalHTMLDataExtractorUI
    print("✅ Crawler module imported successfully")
    
    print("🔍 Creating QApplication...")
    app = QApplication(sys.argv)
    print("✅ QApplication created successfully")
    
    print("🔍 Setting application style...")
    app.setStyle('Fusion')
    print("✅ Application style set successfully")
    
    print("🔍 Creating UI window...")
    try:
        window = LocalHTMLDataExtractorUI()
        print("✅ UI window created successfully")
    except Exception as e:
        print(f"❌ Failed to create UI window: {e}")
        print(f"❌ Traceback: {traceback.format_exc()}")
        sys.exit(1)
    
    print("🔍 Showing window...")
    window.show()
    print("✅ Window shown successfully")
    
    print("🔍 Starting event loop...")
    sys.exit(app.exec())
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print(f"❌ Traceback: {traceback.format_exc()}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    print(f"❌ Traceback: {traceback.format_exc()}")
    sys.exit(1) 