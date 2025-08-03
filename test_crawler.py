#!/usr/bin/env python3
"""
Simple test script to check lightweight crawler functionality
"""

import sys
import os
sys.path.append('web_crawler')

try:
    from lightweight_crawler import LightweightCrawlerUI
    print("✅ LightweightCrawlerUI imported successfully")
    
    # Test basic functionality
    print("🔍 Testing basic crawler functionality...")
    
    # Check if we can create the UI
    try:
        from PySide6.QtWidgets import QApplication
        app = QApplication([])
        crawler = LightweightCrawlerUI()
        print("✅ Crawler UI created successfully")
        
        # Test configuration loading
        print("📋 Testing configuration...")
        crawler.load_config()
        print(f"✅ Configuration loaded: {crawler.config}")
        
        # Test HTML file processing
        print("📄 Testing HTML file processing...")
        
        # Create a simple test HTML file
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
        
        with open('test_data.html', 'w', encoding='utf-8') as f:
            f.write(test_html)
        
        print("✅ Test HTML file created")
        
        # Test link extraction
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(test_html, 'html.parser')
        links = soup.find_all('a', href=True)
        print(f"🔗 Found {len(links)} links in test HTML")
        
        for link in links:
            url = link.get('href')
            print(f"  - {url}")
        
        print("✅ Basic functionality test completed")
        
    except Exception as e:
        print(f"❌ Error creating crawler: {e}")
        import traceback
        traceback.print_exc()
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()

print("�� Test completed") 