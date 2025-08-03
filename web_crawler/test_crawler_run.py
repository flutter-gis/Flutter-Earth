#!/usr/bin/env python3
"""
Test running the crawler with a test HTML file
"""

import sys
import os
from PySide6.QtWidgets import QApplication
from lightweight_crawler import LightweightCrawlerUI

def test_crawler_run():
    """Test running the crawler"""
    print("🧪 Testing crawler run...")
    
    try:
        app = QApplication(sys.argv)
        print("✅ QApplication created")
        
        crawler = LightweightCrawlerUI()
        print("✅ LightweightCrawlerUI created")
        
        # Set the test HTML file
        test_html = "test_debug.html"
        if os.path.exists(test_html):
            crawler.file_path_edit.setText(test_html)
            print(f"✅ Set HTML file: {test_html}")
            
            # Show the UI
            crawler.show()
            print("✅ UI window shown")
            
            # Start crawling
            print("🚀 Starting crawl...")
            crawler.start_crawl()
            print("✅ Crawl started")
            
            return True
        else:
            print(f"❌ Test HTML file not found: {test_html}")
            return False
        
    except Exception as e:
        print(f"❌ Crawler test failed: {e}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    print("🚀 Starting crawler run test...")
    if test_crawler_run():
        print("✅ Crawler run test passed!")
        # Keep the app running
        sys.exit(app.exec())
    else:
        print("❌ Crawler run test failed!")
        sys.exit(1) 