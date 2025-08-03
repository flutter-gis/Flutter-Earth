#!/usr/bin/env python3
"""
Debug test script to check crawler functionality step by step
"""

import sys
import os
import time

# Add web_crawler to path
sys.path.append('web_crawler')

print("🔍 Starting debug test...")

try:
    # Test 1: Import the crawler
    print("📦 Test 1: Importing crawler...")
    from lightweight_crawler import LightweightCrawlerUI
    print("✅ Import successful")
    
    # Test 2: Create UI
    print("📦 Test 2: Creating UI...")
    from PySide6.QtWidgets import QApplication
    app = QApplication([])
    crawler = LightweightCrawlerUI()
    print("✅ UI created")
    
    # Test 3: Load config
    print("📦 Test 3: Loading config...")
    crawler.load_config()
    print(f"✅ Config loaded: {crawler.config}")
    
    # Test 4: Create test HTML file
    print("📦 Test 4: Creating test HTML...")
    test_html = """
    <html>
    <head><title>Test Earth Engine Datasets</title></head>
    <body>
    <h1>Earth Engine Data Catalog</h1>
    <a href="https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_LC08_C02_T1_L2">Landsat 8 Collection 2</a>
    <a href="https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S2_SR">Sentinel-2 Surface Reflectance</a>
    <a href="https://developers.google.com/earth-engine/datasets/catalog/MODIS_006_MOD13Q1">MODIS Vegetation Indices</a>
    </body>
    </html>
    """
    
    test_file = "test_debug.html"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_html)
    print(f"✅ Test HTML created: {test_file}")
    
    # Test 5: Test file reading
    print("📦 Test 5: Testing file reading...")
    with open(test_file, 'r', encoding='utf-8') as f:
        content = f.read()
    print(f"✅ File read: {len(content)} characters")
    
    # Test 6: Test BeautifulSoup
    print("📦 Test 6: Testing BeautifulSoup...")
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(content, 'html.parser')
    links = soup.find_all('a', href=True)
    print(f"✅ BeautifulSoup: Found {len(links)} links")
    
    for i, link in enumerate(links):
        url = link.get('href')
        text = link.get_text().strip()
        print(f"  Link {i+1}: {url} -> '{text}'")
    
    # Test 7: Test link filtering
    print("📦 Test 7: Testing link filtering...")
    filtered_links = []
    for link in links:
        url = link.get('href')
        if url and url.startswith('http'):
            if '/datasets/catalog/' in url and not url.endswith('/catalog'):
                filtered_links.append(url)
                print(f"✅ Accepted: {url}")
            else:
                print(f"❌ Filtered: {url}")
    
    print(f"✅ Filtering: {len(filtered_links)} links accepted")
    
    # Test 8: Test crawler with test file
    print("📦 Test 8: Testing crawler with test file...")
    crawler.file_path_edit.setText(test_file)
    print(f"✅ File path set: {crawler.file_path_edit.text()}")
    
    # Test 9: Test crawl function
    print("📦 Test 9: Testing crawl function...")
    try:
        crawler.crawl_html_file(test_file)
        print("✅ Crawl function completed")
    except Exception as e:
        print(f"❌ Crawl function failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("🏁 Debug test completed")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc() 