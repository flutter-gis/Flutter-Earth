#!/usr/bin/env python3
"""
Debug script to test the main function
"""

import sys
import traceback

def test_main():
    """Test the main function"""
    print("🧪 Testing main function...")
    
    try:
        # Import the main function
        from lightweight_crawler import main
        print("✅ Main function imported")
        
        # Test if we can create the app
        from PySide6.QtWidgets import QApplication
        app = QApplication(sys.argv)
        print("✅ QApplication created")
        
        # Test if we can create the crawler
        from lightweight_crawler import LightweightCrawlerUI
        crawler = LightweightCrawlerUI()
        print("✅ LightweightCrawlerUI created")
        
        # Test if we can show the UI
        crawler.show()
        print("✅ UI shown")
        
        print("✅ All tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        print(f"❌ Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    print("🚀 Starting main function test...")
    if test_main():
        print("✅ Main function test passed!")
    else:
        print("❌ Main function test failed!")
        sys.exit(1) 