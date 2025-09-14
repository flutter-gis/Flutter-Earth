#!/usr/bin/env python3
"""
Test script to extract data from gee cat folder using the enhanced extractor
"""

import os
import sys
import time
from pathlib import Path

# Add the web_crawler directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'web_crawler'))

try:
    from lightweight_crawler import LocalHTMLDataExtractor

    def test_extraction():
        """Test extraction on gee cat folder"""
        print("Starting enhanced Earth Engine extraction test...")

        # Initialize extractor
        extractor = LocalHTMLDataExtractor()

        # Path to the gee cat folder
        gee_cat_path = os.path.join(os.path.dirname(__file__), 'gee cat')
        html_file = os.path.join(gee_cat_path, 'Earth Engine Data Catalog  _  Google for Developers.html')

        if not os.path.exists(html_file):
            print(f"HTML file not found: {html_file}")
            return

        print(f"Processing file: {os.path.basename(html_file)}")
        print(f"File size: {os.path.getsize(html_file):,} bytes")

        # Extract data
        try:
            from bs4 import BeautifulSoup

            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()

            soup = BeautifulSoup(content, 'html.parser')
            print(f"🔍 HTML parsed successfully")

            # Test the enhanced extraction
            def progress_callback(percent):
                print(f"📊 Progress: {percent}%")

            def log_callback(message):
                print(f"📝 {message}")

            # Extract all data using enhanced methods
            data = extractor.extract_all_data(soup, html_file, progress_callback, log_callback)

            if data:
                print(f"✅ Extraction completed!")
                print(f"📊 Results summary:")
                print(f"   🎯 Extraction method: {data.get('satellite_catalog', {}).get('extraction_method', 'unknown')}")
                print(f"   📈 Confidence: {data.get('satellite_catalog', {}).get('extraction_confidence', 'unknown')}")

                datasets = data.get('satellite_catalog', {}).get('datasets', [])
                if datasets:
                    print(f"   🛰️  Total datasets found: {len(datasets)}")

                    # Show sample datasets
                    print(f"\n📋 Sample datasets:")
                    for i, dataset in enumerate(datasets[:5]):
                        title = dataset.get('title', 'Unknown')
                        category = extractor.classify_single_dataset(dataset)
                        confidence = dataset.get('confidence_score', 0)
                        completeness = dataset.get('data_completeness', 0)
                        print(f"   {i+1}. {title[:60]}...")
                        print(f"      Category: {category} | Quality: {confidence}% | Complete: {completeness}%")

                    if len(datasets) > 5:
                        print(f"   ... and {len(datasets) - 5} more datasets")

                classifications = data.get('satellite_catalog', {}).get('classifications', {})
                if classifications:
                    print(f"\n📊 Classifications:")
                    for category, items in classifications.items():
                        if items:
                            print(f"   {category.title()}: {len(items)} datasets")

                # Save the data
                json_file = extractor.save_data_to_json(data, html_file)
                if json_file:
                    print(f"\n💾 Data saved to: {json_file}")

                print(f"\n🎉 Enhanced extraction test completed successfully!")
                return True

            else:
                print("❌ No data extracted")
                return False

        except Exception as e:
            print(f"❌ Extraction failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    if __name__ == "__main__":
        success = test_extraction()
        if success:
            print("\n✅ Test completed successfully!")
        else:
            print("\n❌ Test failed!")

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running this from the correct directory")