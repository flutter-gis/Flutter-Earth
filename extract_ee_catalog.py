#!/usr/bin/env python3
"""
Extract just the core Earth Engine catalog data without following links
"""

import os
import sys
import glob
import json
from datetime import datetime

# Add the web_crawler directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'web_crawler'))

from lightweight_crawler import LocalHTMLDataExtractor
from bs4 import BeautifulSoup

def extract_ee_catalog():
    print("=== EARTH ENGINE CATALOG EXTRACTION ===")

    # Find the HTML file
    html_files = glob.glob('./gee cat/*.html')
    if not html_files:
        print("No HTML files found")
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

    # Extract Earth Engine catalog data
    print("Extracting Earth Engine catalog datasets...")
    datasets = extractor.extract_earth_engine_catalog(soup)

    if not datasets:
        print("No datasets extracted")
        return False

    # Classify datasets
    classifications = extractor.classify_earth_engine_datasets(datasets)

    # Create comprehensive data structure
    catalog_data = {
        'extraction_info': {
            'timestamp': datetime.now().isoformat(),
            'source_file': html_file,
            'extractor_version': 'enhanced_v3.0',
            'total_datasets': len(datasets)
        },
        'datasets': datasets,
        'classifications': classifications,
        'statistics': {
            'by_category': {k: len(v) for k, v in classifications.items() if v},
            'quality_distribution': {
                'high_quality': len([d for d in datasets if d.get('confidence_score', 0) >= 70]),
                'medium_quality': len([d for d in datasets if 50 <= d.get('confidence_score', 0) < 70]),
                'low_quality': len([d for d in datasets if d.get('confidence_score', 0) < 50])
            },
            'completeness': {
                'with_titles': len([d for d in datasets if d.get('title')]),
                'with_descriptions': len([d for d in datasets if d.get('description')]),
                'with_tags': len([d for d in datasets if d.get('tags')]),
                'with_urls': len([d for d in datasets if d.get('url')]),
                'with_thumbnails': len([d for d in datasets if d.get('thumbnail')])
            }
        }
    }

    print(f"\n=== EXTRACTION RESULTS ===")
    print(f"Total datasets: {len(datasets)}")

    print(f"\nCATEGORY BREAKDOWN:")
    for category, items in classifications.items():
        if items:
            print(f"  {category.title()}: {len(items)}")

    stats = catalog_data['statistics']
    print(f"\nQUALITY DISTRIBUTION:")
    print(f"  High quality (70%+): {stats['quality_distribution']['high_quality']}")
    print(f"  Medium quality (50-69%): {stats['quality_distribution']['medium_quality']}")
    print(f"  Low quality (<50%): {stats['quality_distribution']['low_quality']}")

    print(f"\nCOMPLETENESS:")
    print(f"  With titles: {stats['completeness']['with_titles']}")
    print(f"  With descriptions: {stats['completeness']['with_descriptions']}")
    print(f"  With tags: {stats['completeness']['with_tags']}")
    print(f"  With URLs: {stats['completeness']['with_urls']}")
    print(f"  With thumbnails: {stats['completeness']['with_thumbnails']}")

    # Save to JSON
    output_file = os.path.join(extractor.output_dir, 'earth_engine_catalog.json')
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(catalog_data, f, indent=2, ensure_ascii=False)

    print(f"\nData saved to: {output_file}")

    # Show sample datasets
    print(f"\nSAMPLE DATASETS:")
    for i, dataset in enumerate(datasets[:10]):
        print(f"{i+1}. {dataset.get('title', 'Unknown')}")
        print(f"   ID: {dataset.get('dataset_id', 'N/A')}")
        print(f"   Category: {extractor.classify_single_dataset(dataset)}")
        print(f"   Quality: {dataset.get('confidence_score', 0)}%")
        print(f"   Tags: {', '.join(dataset.get('tags', [])[:3])}")
        if dataset.get('description'):
            print(f"   Description: {dataset.get('description')[:80]}...")
        print()

    if len(datasets) > 10:
        print(f"... and {len(datasets) - 10} more datasets")

    print(f"\n=== SUCCESS: {len(datasets)} datasets extracted! ===")
    return True

if __name__ == "__main__":
    success = extract_ee_catalog()
    if success:
        print("\nExtraction completed successfully!")
        print("You can now view the data in earth_engine_catalog.json")
    else:
        print("\nExtraction failed!")