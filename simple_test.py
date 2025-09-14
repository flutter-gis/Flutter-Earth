#!/usr/bin/env python3
"""
Simple test to extract data from gee cat folder
"""

import os
import sys

# Add the web_crawler directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'web_crawler'))

try:
    from lightweight_crawler import LocalHTMLDataExtractor
    from bs4 import BeautifulSoup

    def simple_test():
        print("Starting Earth Engine extraction test...")

        # Initialize extractor
        extractor = LocalHTMLDataExtractor()

        # Path to the gee cat folder
        gee_cat_path = os.path.join(os.path.dirname(__file__), 'gee cat')
        html_file = os.path.join(gee_cat_path, 'Earth Engine Data Catalog  _  Google for Developers.html')

        if not os.path.exists(html_file):
            print(f"HTML file not found: {html_file}")
            return False

        print(f"Processing: {os.path.basename(html_file)}")
        print(f"Size: {os.path.getsize(html_file):,} bytes")

        # Read and parse HTML
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()

        soup = BeautifulSoup(content, 'html.parser')
        print("HTML parsed successfully")

        # Test Earth Engine specific extraction
        datasets = extractor.extract_earth_engine_catalog(soup)

        if datasets:
            print(f"\nSUCCESS: Found {len(datasets)} datasets!")

            # Show first few datasets
            for i, dataset in enumerate(datasets[:3]):
                print(f"\n{i+1}. {dataset.get('title', 'Unknown')}")
                print(f"   ID: {dataset.get('dataset_id', 'N/A')}")
                print(f"   Confidence: {dataset.get('confidence_score', 0)}%")
                print(f"   Tags: {', '.join(dataset.get('tags', [])[:3])}")

            return True
        else:
            print("No datasets found with Earth Engine extraction")

            # Try generic extraction as fallback
            print("Trying generic extraction...")
            data = extractor.extract_all_data(soup, html_file)

            if data:
                print("Generic extraction succeeded")
                return True
            else:
                print("No data extracted")
                return False

    if __name__ == "__main__":
        success = simple_test()
        if success:
            print("\nTest completed successfully!")
        else:
            print("\nTest failed!")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()