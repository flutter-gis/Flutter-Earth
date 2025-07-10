#!/usr/bin/env python3
"""
Test script for Earth Engine Catalog Crawler
"""

import sys
import os
from pathlib import Path

def test_crawler_import():
    """Test if the crawler can be imported"""
    try:
        from advanced_earth_engine_crawler import AdvancedEarthEngineCrawler
        print("✓ Advanced Earth Engine Crawler imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Failed to import Advanced Earth Engine Crawler: {e}")
        return False

def test_crawler_creation():
    """Test if crawler can be created"""
    try:
        from advanced_earth_engine_crawler import AdvancedEarthEngineCrawler
        crawler = AdvancedEarthEngineCrawler()
        print("✓ Crawler instance created successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to create crawler instance: {e}")
        return False

def test_known_datasets():
    """Test known datasets functionality"""
    try:
        from advanced_earth_engine_crawler import AdvancedEarthEngineCrawler
        crawler = AdvancedEarthEngineCrawler()
        
        # Test known datasets
        known_datasets = crawler.crawl_known_datasets()
        print(f"✓ Found {len(known_datasets)} known datasets")
        
        if len(known_datasets) > 0:
            print(f"  Sample dataset: {known_datasets[0]['name']}")
            return True
        else:
            print("✗ No known datasets found")
            return False
            
    except Exception as e:
        print(f"✗ Error testing known datasets: {e}")
        return False

def test_full_crawl():
    """Test full crawl functionality"""
    try:
        from advanced_earth_engine_crawler import AdvancedEarthEngineCrawler
        crawler = AdvancedEarthEngineCrawler()
        
        print("Starting full crawl test...")
        results = crawler.crawl_all_datasets()
        
        if results and 'datasets' in results:
            print(f"✓ Full crawl completed successfully")
            print(f"  Total datasets: {len(results['datasets'])}")
            print(f"  Total tags: {len(results.get('tags', []))}")
            print(f"  Total publishers: {len(results.get('publishers', []))}")
            return True
        else:
            print("✗ Full crawl failed - no results")
            return False
            
    except Exception as e:
        print(f"✗ Error during full crawl: {e}")
        return False

def main():
    """Run all tests"""
    print("Testing Earth Engine Catalog Crawler...")
    print("=" * 50)
    
    # Test imports
    print("\n1. Testing imports:")
    import_ok = test_crawler_import()
    
    # Test crawler creation
    print("\n2. Testing crawler creation:")
    creation_ok = test_crawler_creation()
    
    # Test known datasets
    print("\n3. Testing known datasets:")
    known_ok = test_known_datasets()
    
    # Test full crawl (optional - can be slow)
    print("\n4. Testing full crawl:")
    full_ok = test_full_crawl()
    
    print("\n" + "=" * 50)
    print("Test Results:")
    print(f"Imports: {'✓ PASS' if import_ok else '✗ FAIL'}")
    print(f"Creation: {'✓ PASS' if creation_ok else '✗ FAIL'}")
    print(f"Known Datasets: {'✓ PASS' if known_ok else '✗ FAIL'}")
    print(f"Full Crawl: {'✓ PASS' if full_ok else '✗ FAIL'}")
    
    if all([import_ok, creation_ok, known_ok, full_ok]):
        print("\n🎉 All tests passed! Earth Engine crawler is ready to use.")
        return True
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 