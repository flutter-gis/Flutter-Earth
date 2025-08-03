#!/usr/bin/env python3
"""
Test lightweight crawler without HTTP requests
"""

import sys
import os
import re
from PySide6.QtWidgets import QApplication
from lightweight_crawler import LightweightCrawlerUI
from bs4 import BeautifulSoup

def test_no_http():
    """Test the crawler without making HTTP requests"""
    print("🧪 Testing lightweight crawler without HTTP requests...")
    
    try:
        app = QApplication(sys.argv)
        print("✅ QApplication created")
        
        crawler = LightweightCrawlerUI()
        print("✅ LightweightCrawlerUI created")
        
        # Test with the test HTML file
        test_html = "test_debug.html"
        if os.path.exists(test_html):
            print(f"✅ Test HTML file exists: {test_html}")
            
            # Read the HTML file
            with open(test_html, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"✅ HTML file loaded: {len(content)} characters")
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(content, 'html.parser')
            print("✅ BeautifulSoup parsing completed")
            
            # Extract links
            all_links = soup.find_all('a', href=True)
            print(f"🔗 Found {len(all_links)} total links in HTML")
            
            # Test link filtering
            links = []
            for link in soup.find_all('a', href=True):
                url = link.get('href')
                if url and url.startswith('http'):
                    if '/datasets/catalog/' in url and not url.endswith('/catalog'):
                        links.append(url)
                        print(f"✅ Added catalog link: {url}")
                    elif re.search(r'[A-Z_]{3,}', url):
                        links.append(url)
                        print(f"✅ Added pattern link: {url}")
            
            print(f"📊 Found {len(links)} links to process")
            
            # Test the extract_comprehensive_data method with a mock soup
            if links:
                test_url = links[0]
                print(f"🧪 Testing extract_comprehensive_data with: {test_url}")
                
                # Create a mock response soup
                mock_html = f"""
                <html>
                <head><title>Test Dataset - Landsat 8 Collection 2</title></head>
                <body>
                    <h1>Landsat 8 Collection 2 Tier 1</h1>
                    <p>This dataset contains Landsat 8 Collection 2 Tier 1 data with 30m resolution.</p>
                    <p>Bands: B1, B2, B3, B4, B5, B6, B7</p>
                    <p>Resolution: 30 meters</p>
                    <p>Temporal coverage: 2013-present</p>
                    <p>Provider: USGS</p>
                </body>
                </html>
                """
                mock_soup = BeautifulSoup(mock_html, 'html.parser')
                
                # Test extraction
                result = crawler.extract_comprehensive_data(mock_soup, test_url)
                print(f"✅ Extraction completed")
                print(f"📊 Title: {result.get('title', 'Unknown')}")
                print(f"📊 Confidence: {result.get('confidence_score', 0.0):.3f}")
                print(f"📊 Category: {result.get('category', 'unknown')}")
                print(f"📊 Satellite: {result.get('satellite_info', {})}")
                print(f"📊 Technical specs: {result.get('technical_specs', {})}")
                
                return True
            else:
                print("❌ No valid links found")
                return False
        else:
            print(f"❌ Test HTML file not found: {test_html}")
            return False
        
    except Exception as e:
        print(f"❌ No HTTP test failed: {e}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    print("🚀 Starting no HTTP test...")
    if test_no_http():
        print("✅ No HTTP test passed!")
    else:
        print("❌ No HTTP test failed!")
        sys.exit(1) 