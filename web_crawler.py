#!/usr/bin/env python3
"""
Google Earth Engine Data Catalog Web Crawler
Extracts comprehensive dataset information from the Earth Engine catalog
"""

import requests
import json
import time
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
from urllib.parse import urljoin, urlparse
import gzip

class EarthEngineCatalogCrawler:
    """Crawler for Google Earth Engine Data Catalog"""
    
    def __init__(self):
        self.base_url = "https://developers.google.com/earth-engine/datasets/catalog"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/earth_engine_crawler.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Data storage
        self.datasets = []
        self.categories = []
        self.tags = set()
        self.publishers = set()
        
        # Create output directory
        self.output_dir = Path("crawler_data")
        self.output_dir.mkdir(exist_ok=True)
        
    def get_catalog_page(self, url: str) -> Optional[str]:
        """Get the content of a catalog page"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            self.logger.error(f"Error fetching {url}: {e}")
            return None
    
    def extract_dataset_info(self, html_content: str) -> List[Dict[str, Any]]:
        """Extract dataset information from HTML content"""
        datasets = []
        
        # Pattern to match dataset entries
        # Looking for the table structure with dataset information
        dataset_pattern = r'<tr[^>]*>\s*<td[^>]*>\s*<a[^>]*href="([^"]*)"[^>]*>\s*([^<]+)</a>\s*</td>\s*<td[^>]*>\s*([^<]+(?:<[^>]+>[^<]*</[^>]+>[^<]*)*)</td>\s*<td[^>]*>\s*([^<]+)</td>\s*</tr>'
        
        matches = re.finditer(dataset_pattern, html_content, re.DOTALL)
        
        for match in matches:
            try:
                dataset_url = match.group(1)
                dataset_name = match.group(2).strip()
                description = self.clean_html(match.group(3))
                tags_text = match.group(4).strip()
                
                # Extract tags
                tags = self.extract_tags(tags_text)
                
                # Get detailed dataset information
                dataset_info = self.get_dataset_details(dataset_url, dataset_name, description, tags)
                if dataset_info:
                    datasets.append(dataset_info)
                    
            except Exception as e:
                self.logger.error(f"Error parsing dataset entry: {e}")
                continue
        
        return datasets
    
    def clean_html(self, html_text: str) -> str:
        """Clean HTML tags from text"""
        # Remove HTML tags
        clean_text = re.sub(r'<[^>]+>', '', html_text)
        # Remove extra whitespace
        clean_text = re.sub(r'\s+', ' ', clean_text)
        return clean_text.strip()
    
    def extract_tags(self, tags_text: str) -> List[str]:
        """Extract tags from the tags column"""
        tags = []
        # Look for tag links
        tag_pattern = r'<a[^>]*href="[^"]*tags/[^"]*"[^>]*>([^<]+)</a>'
        tag_matches = re.findall(tag_pattern, tags_text)
        tags.extend(tag_matches)
        return tags
    
    def get_dataset_details(self, dataset_url: str, name: str, description: str, tags: List[str]) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific dataset"""
        try:
            full_url = urljoin(self.base_url, dataset_url)
            self.logger.info(f"Fetching details for: {name}")
            
            # Add delay to be respectful
            time.sleep(1)
            
            page_content = self.get_catalog_page(full_url)
            if not page_content:
                return None
            
            # Extract additional information from the dataset page
            details = self.extract_dataset_page_info(page_content, name, description, tags)
            
            return details
            
        except Exception as e:
            self.logger.error(f"Error getting details for {name}: {e}")
            return None
    
    def extract_dataset_page_info(self, html_content: str, name: str, description: str, tags: List[str]) -> Dict[str, Any]:
        """Extract detailed information from a dataset page"""
        dataset_info = {
            "name": name,
            "description": description,
            "tags": tags,
            "url": "",
            "satellite": "",
            "resolution": "",
            "temporal_coverage": "",
            "spatial_coverage": "",
            "bands": [],
            "applications": [],
            "publisher": "",
            "last_updated": "",
            "code_snippet": "",
            "metadata": {}
        }
        
        # Extract satellite information
        satellite_pattern = r'(Landsat|Sentinel|MODIS|GOES|NOAA|NASA|USGS|ESA|JAXA|Copernicus)'
        satellite_match = re.search(satellite_pattern, name, re.IGNORECASE)
        if satellite_match:
            dataset_info["satellite"] = satellite_match.group(1)
        
        # Extract resolution information
        resolution_pattern = r'(\d+(?:\.\d+)?)\s*(?:m|meter|meters|km|kilometer|kilometers)'
        resolution_match = re.search(resolution_pattern, description, re.IGNORECASE)
        if resolution_match:
            dataset_info["resolution"] = f"{resolution_match.group(1)}m"
        
        # Extract temporal coverage
        temporal_pattern = r'(\d{4}(?:-\d{4})?|present|ongoing)'
        temporal_matches = re.findall(temporal_pattern, description)
        if temporal_matches:
            dataset_info["temporal_coverage"] = " - ".join(temporal_matches)
        
        # Extract applications from description
        applications = []
        app_keywords = ["agriculture", "forestry", "urban", "water", "climate", "disaster", "marine", "atmospheric", "vegetation", "soil", "elevation"]
        for keyword in app_keywords:
            if keyword.lower() in description.lower():
                applications.append(keyword.title())
        dataset_info["applications"] = applications
        
        # Extract publisher
        publisher_pattern = r'(NASA|NOAA|USGS|ESA|JAXA|Copernicus|Google|University|Institute)'
        publisher_match = re.search(publisher_pattern, description, re.IGNORECASE)
        if publisher_match:
            dataset_info["publisher"] = publisher_match.group(1)
        
        # Extract bands information
        bands_pattern = r'(B\d+|band|bands|spectral|wavelength)'
        bands_matches = re.findall(bands_pattern, description, re.IGNORECASE)
        if bands_matches:
            dataset_info["bands"] = list(set(bands_matches))
        
        return dataset_info
    
    def crawl_all_datasets(self) -> Dict[str, Any]:
        """Crawl all datasets from the Earth Engine catalog"""
        self.logger.info("Starting Earth Engine catalog crawl")
        
        # Get the main catalog page
        main_page = self.get_catalog_page(self.base_url)
        if not main_page:
            self.logger.error("Failed to fetch main catalog page")
            return {}
        
        # Extract datasets from the main page
        self.logger.info("Extracting datasets from main page")
        datasets = self.extract_dataset_info(main_page)
        
        # Process each dataset
        for i, dataset in enumerate(datasets):
            self.logger.info(f"Processing dataset {i+1}/{len(datasets)}: {dataset['name']}")
            
            # Add to collections
            self.datasets.append(dataset)
            
            # Extract tags and publishers
            self.tags.update(dataset.get('tags', []))
            if dataset.get('publisher'):
                self.publishers.add(dataset['publisher'])
        
        # Organize data by categories
        self.organize_by_categories()
        
        # Save results
        results = self.save_results()
        
        self.logger.info(f"Crawl completed. Found {len(self.datasets)} datasets")
        return results
    
    def organize_by_categories(self):
        """Organize datasets by categories"""
        categories = {}
        
        for dataset in self.datasets:
            # Categorize by satellite/mission
            satellite = dataset.get('satellite', 'Other')
            if satellite not in categories:
                categories[satellite] = []
            categories[satellite].append(dataset)
            
            # Categorize by applications
            for app in dataset.get('applications', []):
                if app not in categories:
                    categories[app] = []
                categories[app].append(dataset)
        
        self.categories = categories
    
    def save_results(self) -> Dict[str, Any]:
        """Save crawl results to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Prepare results
        results = {
            "metadata": {
                "crawl_date": datetime.now().isoformat(),
                "total_datasets": len(self.datasets),
                "total_tags": len(self.tags),
                "total_publishers": len(self.publishers),
                "categories": list(self.categories.keys())
            },
            "datasets": self.datasets,
            "categories": self.categories,
            "tags": list(self.tags),
            "publishers": list(self.publishers)
        }
        
        # Save as JSON
        json_file = self.output_dir / f"earth_engine_catalog_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # Save as compressed JSON
        gz_file = self.output_dir / f"earth_engine_catalog_{timestamp}.json.gz"
        with gzip.open(gz_file, 'wt', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Results saved to {json_file} and {gz_file}")
        
        return results
    
    def generate_summary_report(self) -> str:
        """Generate a summary report of the crawl"""
        report = f"""
Earth Engine Catalog Crawl Summary
==================================

Crawl Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Total Datasets: {len(self.datasets)}
Total Tags: {len(self.tags)}
Total Publishers: {len(self.publishers)}

Top Satellites/Missions:
"""
        
        # Count satellites
        satellite_counts = {}
        for dataset in self.datasets:
            satellite = dataset.get('satellite', 'Other')
            satellite_counts[satellite] = satellite_counts.get(satellite, 0) + 1
        
        for satellite, count in sorted(satellite_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            report += f"  {satellite}: {count} datasets\n"
        
        report += "\nTop Applications:\n"
        
        # Count applications
        app_counts = {}
        for dataset in self.datasets:
            for app in dataset.get('applications', []):
                app_counts[app] = app_counts.get(app, 0) + 1
        
        for app, count in sorted(app_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            report += f"  {app}: {count} datasets\n"
        
        report += f"\nTop Tags:\n"
        tag_counts = {}
        for dataset in self.datasets:
            for tag in dataset.get('tags', []):
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        for tag, count in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:15]:
            report += f"  {tag}: {count} datasets\n"
        
        return report

def main():
    """Main function to run the crawler"""
    crawler = EarthEngineCatalogCrawler()
    
    try:
        # Run the crawler
        results = crawler.crawl_all_datasets()
        
        # Generate and save summary report
        report = crawler.generate_summary_report()
        report_file = crawler.output_dir / "crawl_summary.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(report)
        print(f"\nCrawl completed successfully!")
        print(f"Results saved to: {crawler.output_dir}")
        
    except Exception as e:
        print(f"Error during crawl: {e}")
        crawler.logger.error(f"Crawl failed: {e}")

if __name__ == "__main__":
    main() 