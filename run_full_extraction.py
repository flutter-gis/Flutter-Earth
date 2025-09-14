#!/usr/bin/env python3
"""
Run full extraction on the gee cat Earth Engine catalog
"""

import os
import sys
import glob
import json

# Add the web_crawler directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'web_crawler'))

from lightweight_crawler import LocalHTMLDataExtractor
from bs4 import BeautifulSoup

def run_full_extraction():
    print("=== FLUTTER EARTH - ENHANCED EXTRACTION ===")
    print("Running full extraction on Earth Engine catalog...")

    # Find the HTML file
    html_files = glob.glob('./gee cat/*.html')
    if not html_files:
        print("No HTML files found in gee cat folder")
        return False

    html_file = html_files[0]
    print(f"Processing: {os.path.basename(html_file)}")
    print(f"File size: {os.path.getsize(html_file):,} bytes")

    # Initialize extractor
    extractor = LocalHTMLDataExtractor()

    # Parse HTML
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()

    soup = BeautifulSoup(content, 'html.parser')
    print("HTML parsed successfully")

    # Progress callback
    def progress_callback(percent):
        print(f"Progress: {percent}%")

    def log_callback(message):
        print(f"LOG: {message}")

    # Run full extraction
    print("\nStarting full data extraction...")
    data = extractor.extract_all_data(soup, html_file, progress_callback, log_callback)

    if data:
        print("\n=== EXTRACTION RESULTS ===")

        # Get satellite catalog data
        satellite_catalog = data.get('satellite_catalog', {})

        print(f"Extraction method: {satellite_catalog.get('extraction_method', 'unknown')}")
        print(f"Confidence level: {satellite_catalog.get('extraction_confidence', 'unknown')}")

        # Dataset statistics
        datasets = satellite_catalog.get('datasets', [])
        classifications = satellite_catalog.get('classifications', {})

        print(f"\nDATASET STATISTICS:")
        print(f"Total datasets: {len(datasets)}")

        if classifications:
            print(f"\nCATEGORY BREAKDOWN:")
            for category, items in classifications.items():
                if items:
                    print(f"  {category.title()}: {len(items)} datasets")

        # Quality statistics
        if datasets:
            high_quality = len([d for d in datasets if d.get('confidence_score', 0) >= 70])
            medium_quality = len([d for d in datasets if 50 <= d.get('confidence_score', 0) < 70])
            low_quality = len([d for d in datasets if d.get('confidence_score', 0) < 50])

            print(f"\nQUALITY BREAKDOWN:")
            print(f"  High quality (70%+): {high_quality}")
            print(f"  Medium quality (50-69%): {medium_quality}")
            print(f"  Low quality (<50%): {low_quality}")

            # Data completeness
            avg_completeness = sum(d.get('data_completeness', 0) for d in datasets) / len(datasets)
            print(f"  Average completeness: {avg_completeness:.1f}%")

        # Save the data
        json_file = extractor.save_data_to_json(data, html_file)
        if json_file:
            print(f"\nData saved to: {json_file}")

        # Show sample datasets
        print(f"\nSAMPLE DATASETS:")
        for i, dataset in enumerate(datasets[:5]):
            print(f"{i+1}. {dataset.get('title', 'Unknown')}")
            print(f"   ID: {dataset.get('dataset_id', 'N/A')}")
            print(f"   Provider: {dataset.get('provider', 'N/A')}")
            print(f"   Quality: {dataset.get('confidence_score', 0)}% | Complete: {dataset.get('data_completeness', 0)}%")

            # Show temporal info if available
            temporal = dataset.get('temporal_coverage', {})
            if temporal.get('start_date') or temporal.get('end_date'):
                print(f"   Temporal: {temporal.get('start_date', 'N/A')} to {temporal.get('end_date', 'N/A')}")

            # Show spatial info if available
            spatial = dataset.get('spatial_info', {})
            if spatial.get('resolution'):
                print(f"   Resolution: {spatial.get('resolution', 'N/A')}")

            print()

        if len(datasets) > 5:
            print(f"... and {len(datasets) - 5} more datasets")

        print(f"\n=== EXTRACTION COMPLETED SUCCESSFULLY ===")
        print(f"Total datasets extracted: {len(datasets)}")
        print(f"Output directory: {extractor.output_dir}")
        print(f"Thumbnails directory: {extractor.thumbnails_dir}")

        return True

    else:
        print("No data extracted")
        return False

if __name__ == "__main__":
    success = run_full_extraction()
    if success:
        print("\nFull extraction completed successfully!")
        print("You can now run the UI to view the extracted data with thumbnails.")
    else:
        print("\nExtraction failed!")