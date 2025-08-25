#!/usr/bin/env python3
"""
Test script to verify crawler functionality
"""

import os
import sys
import tempfile
from web_crawler.lightweight_crawler import LocalHTMLDataExtractor

def create_test_html():
    """Create a simple test HTML file"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Earth Engine Catalog</title>
    </head>
    <body>
        <h1>Earth Engine Data Catalog</h1>
        <div class="catalog-grid">
            <div class="dataset-item">
                <a href="/datasets/LANDSAT/LC08/C01/T1_SR">
                    <img src="landsat8_thumb.jpg" alt="Landsat 8 Surface Reflectance">
                    <h3>Landsat 8 Surface Reflectance</h3>
                </a>
                <p>Landsat 8 Collection 1 Tier 1 calibrated top-of-atmosphere reflectance</p>
                <span class="provider">USGS</span>
                <span class="temporal">2013-present</span>
            </div>
            <div class="dataset-item">
                <a href="/datasets/MODIS/006/MOD13Q1">
                    <img src="modis_thumb.jpg" alt="MODIS Vegetation Indices">
                    <h3>MODIS Vegetation Indices</h3>
                </a>
                <p>MODIS Terra Vegetation Indices 16-Day Global 250m</p>
                <span class="provider">NASA</span>
                <span class="temporal">2000-present</span>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
        f.write(html_content)
        return f.name

def test_crawler():
    """Test the crawler functionality"""
    print("🧪 Testing crawler functionality...")
    
    try:
        # Create test HTML file
        test_file = create_test_html()
        print(f"✅ Created test HTML file: {test_file}")
        
        # Initialize extractor
        extractor = LocalHTMLDataExtractor()
        print("✅ Initialized LocalHTMLDataExtractor")
        
        # Read and parse HTML
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(content, 'html.parser')
        print("✅ Parsed HTML with BeautifulSoup")
        
        # Test extraction
        def test_progress(progress):
            print(f"   Progress: {progress:.1f}%")
        
        def test_log(message):
            print(f"   Log: {message}")
        
        print("🔍 Starting extraction test...")
        data = extractor.extract_all_data(soup, test_file, test_progress, test_log)
        
        # Verify results
        if data:
            print("✅ Extraction completed successfully")
            print(f"   Title: {data.get('title', 'N/A')}")
            print(f"   Catalog links found: {len(data.get('catalog_links', []))}")
            print(f"   Satellite catalog entries: {len(data.get('satellite_catalog', {}))}")
            
            # Show some catalog links
            if data.get('catalog_links'):
                print("   Sample catalog links:")
                for i, link in enumerate(data['catalog_links'][:3]):
                    print(f"     {i+1}. {link.get('text', 'N/A')[:50]}...")
            
            return True
        else:
            print("❌ Extraction returned no data")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        return False
    
    finally:
        # Clean up
        try:
            if 'test_file' in locals():
                os.unlink(test_file)
                print("✅ Cleaned up test file")
        except:
            pass

if __name__ == "__main__":
    success = test_crawler()
    if success:
        print("🎉 Crawler functionality test PASSED")
        sys.exit(0)
    else:
        print("💥 Crawler functionality test FAILED")
        sys.exit(1)