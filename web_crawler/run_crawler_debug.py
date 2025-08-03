#!/usr/bin/env python3
"""
Debug runner for the lightweight crawler
"""

import sys
import os
from PySide6.QtWidgets import QApplication
from lightweight_crawler import LightweightCrawlerUI

def run_crawler_debug():
    """Run the crawler with debug output"""
    print("🚀 Starting lightweight crawler with debug output...")
    
    try:
        print("📱 Creating QApplication...")
        app = QApplication(sys.argv)
        print("✅ QApplication created")
        
        print("🔧 Setting application style...")
        app.setStyle('Fusion')
        print("✅ Application style set")
        
        print("🏗️ Creating LightweightCrawlerUI...")
        window = LightweightCrawlerUI()
        print("✅ LightweightCrawlerUI created")
        
        print("👁️ Showing window...")
        window.show()
        print("✅ Window shown")
        
        print("🔄 Starting event loop...")
        print("💡 The crawler window should now be visible!")
        print("💡 If you don't see it, check your taskbar or alt+tab")
        
        result = app.exec()
        print(f"✅ Event loop finished with result: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Crawler debug failed: {e}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    print("🚀 Starting crawler debug...")
    if run_crawler_debug():
        print("✅ Crawler debug completed!")
    else:
        print("❌ Crawler debug failed!")
        sys.exit(1) 