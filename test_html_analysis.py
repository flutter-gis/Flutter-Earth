#!/usr/bin/env python3
"""
Test script for HTML analysis functionality
"""

import os
import sys
from pathlib import Path
from bs4 import BeautifulSoup
import re
from datetime import datetime
import json

def test_html_analysis():
    """Test HTML analysis with the existing HTML file"""
    
    # Path to the HTML file
    html_file = Path("gee cat") / "Earth Engine Data Catalog  _  Google for Developers.html"
    
    if not html_file.exists():
        print(f"HTML file not found: {html_file}")
        return
    
    print(f"Testing HTML analysis with: {html_file}")
    print(f"File size: {html_file.stat().st_size / (1024*1024):.2f} MB")
    
    try:
        # Read HTML file
        print("Reading HTML file...")
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        print(f"HTML content length: {len(html_content)} characters")
        
        # Parse HTML
        print("Parsing HTML with BeautifulSoup...")
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Test extraction methods
        print("\nTesting extraction methods...")
        
        # Method 1: Look for dataset containers
        dataset_containers = soup.find_all(['div', 'article', 'section'], 
                                         class_=re.compile(r'dataset|card|item|entry', re.I))
        print(f"Found {len(dataset_containers)} potential dataset containers")
        
        # Method 2: Look for links
        dataset_links = soup.find_all('a', href=re.compile(r'dataset|catalog|earth-engine', re.I))
        print(f"Found {len(dataset_links)} potential dataset links")
        
        # Method 3: Look for Earth Engine patterns
        ee_patterns = soup.find_all(string=re.compile(r'Landsat|Sentinel|MODIS|USGS|NASA', re.I))
        print(f"Found {len(ee_patterns)} Earth Engine text patterns")
        
        # Method 4: Look for table rows
        dataset_tables = soup.find_all('tr')
        print(f"Found {len(dataset_tables)} table rows")
        
        # Extract some sample data
        print("\nExtracting sample data...")
        datasets = []
        
        # Extract from containers
        for container in dataset_containers[:10]:  # Limit to first 10
            name_elem = container.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'strong', 'b'])
            if name_elem:
                name = name_elem.get_text(strip=True)
                if name and len(name) > 3:
                    datasets.append({
                        'name': name,
                        'source': 'container',
                        'extracted_at': datetime.now().isoformat()
                    })
        
        # Extract from links
        for link in dataset_links[:10]:  # Limit to first 10
            name = link.get_text(strip=True)
            if name and len(name) > 3:
                datasets.append({
                    'name': name,
                    'url': link.get('href', ''),
                    'source': 'link',
                    'extracted_at': datetime.now().isoformat()
                })
        
        # Extract from text patterns
        for text_elem in ee_patterns[:10]:  # Limit to first 10
            if text_elem.parent:
                text = text_elem.parent.get_text(strip=True)
                if text and len(text) > 10:
                    datasets.append({
                        'name': text[:100],
                        'description': text,
                        'source': 'text_pattern',
                        'extracted_at': datetime.now().isoformat()
                    })
        
        # Remove duplicates
        unique_datasets = []
        seen_names = set()
        for dataset in datasets:
            name = dataset.get('name', '')
            if name and name not in seen_names:
                unique_datasets.append(dataset)
                seen_names.add(name)
        
        print(f"\nExtracted {len(unique_datasets)} unique datasets:")
        for i, dataset in enumerate(unique_datasets[:5]):  # Show first 5
            print(f"  {i+1}. {dataset['name']} ({dataset['source']})")
        
        if len(unique_datasets) > 5:
            print(f"  ... and {len(unique_datasets) - 5} more")
        
        # Save test results
        test_data = {
            'test_timestamp': datetime.now().isoformat(),
            'source_file': str(html_file),
            'total_datasets': len(unique_datasets),
            'datasets': unique_datasets,
            'extraction_stats': {
                'containers_found': len(dataset_containers),
                'links_found': len(dataset_links),
                'patterns_found': len(ee_patterns),
                'tables_found': len(dataset_tables)
            }
        }
        
        # Create output directory
        output_dir = Path("extracted_data")
        output_dir.mkdir(exist_ok=True)
        
        # Save test results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        test_file = output_dir / f"test_analysis_{timestamp}.json"
        
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, indent=2, ensure_ascii=False)
        
        print(f"\nTest results saved to: {test_file}")
        print("HTML analysis test completed successfully!")
        
    except Exception as e:
        print(f"Error during HTML analysis test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_html_analysis() 