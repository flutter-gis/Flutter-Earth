#!/usr/bin/env python3
"""
Minimal UI test for the crawler
"""

import sys
from PySide6.QtWidgets import QApplication
from lightweight_crawler import LightweightCrawlerUI

def test_ui():
    """Test UI initialization"""
    print("🧪 Testing UI initialization...")
    
    try:
        app = QApplication(sys.argv)
        print("✅ QApplication created")
        
        crawler = LightweightCrawlerUI()
        print("✅ LightweightCrawlerUI created")
        
        crawler.show()
        print("✅ UI window shown")
        
        print("✅ UI test passed!")
        return True
        
    except Exception as e:
        print(f"❌ UI test failed: {e}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    print("🚀 Starting UI test...")
    if test_ui():
        print("✅ All UI tests passed!")
    else:
        print("❌ UI tests failed!")
        sys.exit(1) 