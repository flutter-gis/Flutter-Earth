#!/usr/bin/env python3
"""
Basic test script to verify crawling functionality
"""

import os
import sys
from bs4 import BeautifulSoup
import re

def test_html_loading():
    """Test HTML file loading and link extraction"""
    print("🧪 Testing HTML file loading...")
    
    # Check if test HTML exists
    test_html = "test_debug.html"
    if os.path.exists(test_html):
        print(f"✅ Found test HTML file: {test_html}")
        
        # Read the file
        try:
            with open(test_html, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"✅ HTML file loaded: {len(content)} characters")
            print(f"📄 First 200 chars: {content[:200]}...")
        except Exception as e:
            print(f"❌ Failed to read HTML file: {e}")
            return False
        
        # Parse with BeautifulSoup
        try:
            soup = BeautifulSoup(content, 'html.parser')
            print("✅ BeautifulSoup parsing completed")
        except Exception as e:
            print(f"❌ Failed to parse HTML: {e}")
            return False
        
        # Extract all links
        try:
            all_links = soup.find_all('a', href=True)
            print(f"🔗 Found {len(all_links)} total links in HTML")
            
            # Show first few links
            for i, link in enumerate(all_links[:5]):
                url = link.get('href')
                text = link.get_text().strip()
                print(f"🔗 Link {i+1}: {url} -> '{text}'")
        except Exception as e:
            print(f"❌ Failed to extract links: {e}")
            return False
        
        # Test link filtering
        try:
            links = []
            filtered_count = 0
            for link in soup.find_all('a', href=True):
                url = link.get('href')
                if url and url.startswith('http'):
                    # Accept any catalog link that doesn't end with /catalog
                    if '/datasets/catalog/' in url and not url.endswith('/catalog'):
                        links.append(url)
                        print(f"✅ Added catalog link: {url}")
                    # Also accept any link with dataset-like patterns
                    elif re.search(r'[A-Z_]{3,}', url):  # Any uppercase with underscores
                        links.append(url)
                        print(f"✅ Added pattern link: {url}")
                    else:
                        filtered_count += 1
                        print(f"❌ Filtered out: {url}")
                else:
                    filtered_count += 1
                    print(f"❌ Not HTTP link: {url}")
            
            print(f"📊 Link filtering: {len(links)} accepted, {filtered_count} filtered out")
            
            # Show first few accepted links
            for i, url in enumerate(links[:5]):
                print(f"✅ Accepted link {i+1}: {url}")
                
        except Exception as e:
            print(f"❌ Failed to filter links: {e}")
            return False
        
        return True
    else:
        print(f"❌ Test HTML file not found: {test_html}")
        return False

def test_simple_html():
    """Create a simple HTML file for testing"""
    print("🧪 Creating simple test HTML...")
    
    simple_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Earth Engine Catalog</title>
    </head>
    <body>
        <h1>Earth Engine Data Catalog</h1>
        <div>
            <a href="https://developers.google.com/earth-engine/datasets/catalog/landsat-8-collection-2-tier-1">Landsat 8 Collection 2</a>
            <a href="https://developers.google.com/earth-engine/datasets/catalog/sentinel-2">Sentinel-2</a>
            <a href="https://developers.google.com/earth-engine/datasets/catalog/modis">MODIS</a>
            <a href="https://developers.google.com/earth-engine/datasets/catalog/aster">ASTER</a>
            <a href="https://developers.google.com/earth-engine/datasets/catalog/spot">SPOT</a>
        </div>
    </body>
    </html>
    """
    
    try:
        with open("test_debug.html", 'w', encoding='utf-8') as f:
            f.write(simple_html)
        print("✅ Created test HTML file")
        return True
    except Exception as e:
        print(f"❌ Failed to create test HTML: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting basic crawler test...")
    
    # Create test HTML if it doesn't exist
    if not os.path.exists("test_debug.html"):
        if not test_simple_html():
            sys.exit(1)
    
    # Test HTML loading
    if test_html_loading():
        print("✅ All tests passed!")
    else:
        print("❌ Tests failed!")
        sys.exit(1) 