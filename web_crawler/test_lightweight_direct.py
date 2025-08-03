#!/usr/bin/env python3
"""
Direct test of lightweight crawler functionality
"""

import sys
import os
from PySide6.QtWidgets import QApplication
from lightweight_crawler import LightweightCrawlerUI

def test_direct():
    """Test the crawler directly"""
    print("🧪 Testing lightweight crawler directly...")
    
    try:
        app = QApplication(sys.argv)
        print("✅ QApplication created")
        
        crawler = LightweightCrawlerUI()
        print("✅ LightweightCrawlerUI created")
        
        # Test with the test HTML file
        test_html = "test_debug.html"
        if os.path.exists(test_html):
            print(f"✅ Test HTML file exists: {test_html}")
            
            # Set the file path
            crawler.file_path_edit.setText(test_html)
            print("✅ File path set")
            
            # Show the UI
            crawler.show()
            print("✅ UI shown")
            
            # Test the crawl_html_file method directly
            print("🚀 Testing crawl_html_file method directly...")
            crawler.crawl_html_file(test_html)
            print("✅ crawl_html_file completed")
            
            return True
        else:
            print(f"❌ Test HTML file not found: {test_html}")
            return False
        
    except Exception as e:
        print(f"❌ Direct test failed: {e}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    print("🚀 Starting direct lightweight crawler test...")
    if test_direct():
        print("✅ Direct test passed!")
    else:
        print("❌ Direct test failed!")
        sys.exit(1) 