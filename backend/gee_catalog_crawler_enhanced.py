#!/usr/bin/env python3
"""
Enhanced Google Earth Engine Data Catalog Crawler
Extracts essential dataset information and download code snippets
"""

import requests
import json
import time
import logging
from pathlib import Path
from datetime import datetime
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import re
from typing import Dict, List, Optional, Any
import sys

class EnhancedGEECatalogCrawler:
    def __init__(self, base_url: str = "https://developers.google.com/earth-engine/datasets/catalog"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Setup logging
        self.setup_logging()
        
        # Storage for extracted data
        self.datasets = []
        self.categories = {}
        self.satellites = {}
        self.publishers = {}
        
        # Progress tracking
        self.total_pages = 0
        self.current_page = 0
        self.total_datasets = 0
        
    def setup_logging(self):
        """Setup logging configuration"""
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        log_file = logs_dir / f"gee_catalog_crawler_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, mode='w', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def print_progress_bar(self, current, total, prefix='Progress', suffix='Complete', length=50, fill='█'):
        """Print a progress bar to the console"""
        percent = f"{100 * (current / float(total)):.1f}"
        filled_length = int(length * current // total)
        bar = fill * filled_length + '-' * (length - filled_length)
        print(f'\r{prefix} |{bar}| {percent}% {suffix}', end='', flush=True)
        if current == total:
            print()  # New line when complete
        
    def get_page_content(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch and parse a web page"""
        try:
            self.logger.info(f"Fetching: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            self.logger.error(f"Error fetching {url}: {e}")
            return None
    
    def extract_dataset_from_card(self, card_element) -> Dict[str, Any]:
        """Extract essential dataset information from a dataset card element"""
        dataset_info = {
            # Essential fields for frontend
            'name': '',
            'description': '',
            'dataset_id': '',
            'collection_id': '',
            'resolution': '',
            'satellites': [],
            'data_type': '',
            'dates': '',
            'frequency': '',
            'publisher': '',
            'coverage': '',
            'download_link': '',
            'code_snippet': '',
            'bands': [],
            'tags': [],
            'cloud_cover': True,
            'start_date': '',
            'end_date': '',
            'applications': [],
            'limitations': ''
        }
        
        try:
            # Extract name and link from the main heading
            name_link = card_element.find('a')
            if name_link:
                dataset_info['name'] = name_link.get_text(strip=True)
                link = urljoin(self.base_url, name_link.get('href', ''))
                
                # Extract dataset ID from URL
                if link:
                    parsed_url = urlparse(link)
                    path_parts = parsed_url.path.split('/')
                    if len(path_parts) > 0:
                        dataset_info['dataset_id'] = path_parts[-1]
                        dataset_info['collection_id'] = dataset_info['dataset_id']
            
            # Extract description
            description_elem = card_element.find('p') or card_element.find('div', class_='description')
            if description_elem:
                dataset_info['description'] = description_elem.get_text(strip=True)
            
            # Extract tags and categorize
            tags_section = card_element.find_all('a', href=re.compile(r'/earth-engine/datasets/tags/'))
            if tags_section:
                dataset_info['tags'] = [tag.get_text(strip=True) for tag in tags_section]
                
                # Categorize tags and extract satellites
                for tag in dataset_info['tags']:
                    tag_lower = tag.lower()
                    
                    # Satellite detection
                    satellite_keywords = [
                        'landsat', 'modis', 'sentinel', 'aster', 'alos', 'srtm', 'gpm', 
                        'grace', 'jason', 'cryosat', 'icesat', 'quikscat', 'seawinds',
                        'avhrr', 'viirs', 'meris', 'envisat', 'ers', 'radarsat', 'terrasar',
                        'rapideye', 'planet', 'worldview', 'ikonos', 'quickbird', 'geoeye',
                        'pleiades', 'spot', 'formosat', 'kompsat', 'cartosat', 'resourcesat',
                        'irs', 'risat', 'oceansat', 'scatsat', 'smos', 'swarm', 'goce',
                        'aeolus', 'biomass', 'flex', 'earthcare', 'metop', 'goes', 'himawari',
                        'meteosat', 'fy', 'fengyun', 'gaofen', 'zy', 'tianhui', 'superview',
                        'jilin', 'changguang'
                    ]
                    
                    for keyword in satellite_keywords:
                        if keyword in tag_lower:
                            dataset_info['satellites'].append(tag)
                            break
                    
                    # Data type categorization
                    if any(keyword in tag_lower for keyword in ['elevation', 'dem', 'topography', 'srtm']):
                        dataset_info['data_type'] = 'Elevation/Topography'
                    elif any(keyword in tag_lower for keyword in ['imagery', 'satellite', 'optical']):
                        dataset_info['data_type'] = 'Satellite Imagery'
                    elif any(keyword in tag_lower for keyword in ['climate', 'weather', 'temperature', 'precipitation']):
                        dataset_info['data_type'] = 'Climate/Weather'
                    elif any(keyword in tag_lower for keyword in ['vegetation', 'ndvi', 'evi', 'lai']):
                        dataset_info['data_type'] = 'Vegetation'
                    elif any(keyword in tag_lower for keyword in ['water', 'ocean', 'hydrology', 'flood']):
                        dataset_info['data_type'] = 'Water/Hydrology'
                    elif any(keyword in tag_lower for keyword in ['soil', 'geology', 'mineral']):
                        dataset_info['data_type'] = 'Soil/Geology'
                    elif any(keyword in tag_lower for keyword in ['population', 'demographics', 'settlement']):
                        dataset_info['data_type'] = 'Population/Demographics'
                    elif any(keyword in tag_lower for keyword in ['fire', 'burn', 'wildfire']):
                        dataset_info['data_type'] = 'Fire/Burn'
                    elif any(keyword in tag_lower for keyword in ['administrative', 'boundaries', 'political']):
                        dataset_info['data_type'] = 'Administrative'
                    elif any(keyword in tag_lower for keyword in ['agriculture', 'crop', 'farming']):
                        dataset_info['data_type'] = 'Agriculture'
                    elif any(keyword in tag_lower for keyword in ['atmospheric', 'aerosol', 'air']):
                        dataset_info['data_type'] = 'Atmospheric'
                    elif any(keyword in tag_lower for keyword in ['cryosphere', 'ice', 'snow', 'glacier']):
                        dataset_info['data_type'] = 'Cryosphere'
            
            # Extract resolution information from description
            description_text = dataset_info['description'].lower()
            resolution_patterns = [
                r'(\d+(?:\.\d+)?)\s*(?:m|meter|meters)\s*resolution',
                r'(\d+(?:\.\d+)?)\s*(?:km|kilometer|kilometers)\s*resolution',
                r'(\d+(?:\.\d+)?)\s*(?:arcsec|arcsecond)\s*resolution',
                r'(\d+(?:\.\d+)?)\s*(?:degree|degrees)\s*resolution',
                r'(\d+(?:\.\d+)?)\s*(?:m|meter|meters)',
                r'(\d+(?:\.\d+)?)\s*(?:km|kilometer|kilometers)',
                r'(\d+(?:\.\d+)?)\s*(?:arcsec|arcsecond)',
                r'(\d+(?:\.\d+)?)\s*(?:degree|degrees)'
            ]
            
            for pattern in resolution_patterns:
                match = re.search(pattern, description_text, re.IGNORECASE)
                if match:
                    dataset_info['resolution'] = match.group(0)
                    break
            
            # Extract temporal frequency
            frequency_patterns = [
                r'daily',
                r'weekly',
                r'monthly',
                r'yearly',
                r'annual',
                r'seasonal',
                r'real-time',
                r'near real-time',
                r'every\s+\d+\s+(?:day|week|month|year)s?'
            ]
            
            for pattern in frequency_patterns:
                match = re.search(pattern, description_text, re.IGNORECASE)
                if match:
                    dataset_info['frequency'] = match.group(0)
                    break
            
            # Extract date ranges
            date_patterns = [
                r'(\d{4})\s*-\s*(\d{4})',  # Year range
                r'(\d{4})',                # Single year
                r'(\d{4}-\d{2}-\d{2})',    # Full date
                r'(\d{2}/\d{2}/\d{4})'     # Date with slashes
            ]
            
            for pattern in date_patterns:
                match = re.search(pattern, description_text)
                if match:
                    dataset_info['dates'] = match.group(0)
                    # Extract start and end dates
                    if '-' in match.group(0) and len(match.group(0)) == 9:  # Year range
                        years = match.group(0).split('-')
                        dataset_info['start_date'] = f"{years[0]}-01-01"
                        dataset_info['end_date'] = f"{years[1]}-12-31"
                    break
            
            # Extract coverage information
            coverage_patterns = [
                r'global',
                r'worldwide',
                r'continental',
                r'regional',
                r'local'
            ]
            
            for pattern in coverage_patterns:
                if re.search(pattern, description_text, re.IGNORECASE):
                    dataset_info['coverage'] = pattern
                    break
            
            # Generate download link and code snippet
            if dataset_info['dataset_id']:
                dataset_info['download_link'] = f"https://developers.google.com/earth-engine/datasets/catalog/{dataset_info['dataset_id']}"
                dataset_info['code_snippet'] = self.generate_code_snippet(dataset_info)
            
            # Extract publisher information
            publisher_keywords = ['nasa', 'noaa', 'usgs', 'esa', 'jaxa', 'copernicus', 'usda']
            for keyword in publisher_keywords:
                if keyword in description_text:
                    dataset_info['publisher'] = keyword.upper()
                    break
            
            # Extract bands information
            bands_patterns = [
                r'bands?\s*:\s*\[([^\]]+)\]',
                r'bands?\s*=\s*\[([^\]]+)\]',
                r'(\w+)\s*band',
                r'red|green|blue|nir|swir|thermal|pan'
            ]
            
            for pattern in bands_patterns:
                matches = re.findall(pattern, description_text, re.IGNORECASE)
                if matches:
                    dataset_info['bands'] = [band.strip() for band in matches if len(band.strip()) > 2]
                    break
            
            # Extract applications from description
            application_keywords = [
                'agriculture', 'forestry', 'urban planning', 'disaster management',
                'climate monitoring', 'water resources', 'biodiversity', 'conservation',
                'mapping', 'surveying', 'environmental monitoring', 'research'
            ]
            
            for keyword in application_keywords:
                if keyword in description_text:
                    dataset_info['applications'].append(keyword)
            
        except Exception as e:
            self.logger.error(f"Error extracting dataset info: {e}")
            
        return dataset_info
    
    def generate_code_snippet(self, dataset_info: Dict[str, Any]) -> str:
        """Generate Earth Engine code snippet for dataset access"""
        dataset_id = dataset_info['dataset_id']
        if not dataset_id:
            return ""
        
        # Basic code snippet
        code = f"""// Earth Engine Code Snippet for {dataset_info['name']}
// Dataset ID: {dataset_id}

// Load the dataset
var dataset = ee.ImageCollection('{dataset_id}');

// Filter by date range (example)
var filtered = dataset.filterDate('2020-01-01', '2020-12-31');

// Get the first image
var image = filtered.first();

// Display the image (adjust bands as needed)
Map.addLayer(image, {{}}, '{dataset_info['name']}');

// Export options (uncomment to use)
/*
Export.image.toDrive({{
  image: image,
  description: '{dataset_info['name']}_export',
  folder: 'EarthEngine_Exports',
  scale: 30,  // Adjust resolution as needed
  region: geometry  // Define your area of interest
}});
*/"""
        
        return code
    
    def crawl_catalog_page(self, page_url: str) -> List[Dict[str, Any]]:
        """Crawl a single catalog page"""
        soup = self.get_page_content(page_url)
        if not soup:
            return []
        
        datasets = []
        
        # Look for dataset cards or table rows
        # Method 1: Look for table rows (traditional catalog layout)
        table_rows = soup.find_all('tr')
        if table_rows:
            for row in table_rows:
                if row.find('th'):  # Skip header rows
                    continue
                    
                cells = row.find_all('td')
                if len(cells) >= 2:
                    dataset_info = self.extract_dataset_from_card(row)
                    if dataset_info['name']:
                        datasets.append(dataset_info)
                        self.logger.info(f"Extracted dataset (table): {dataset_info['name']}")
        
        # Method 2: Look for dataset cards (modern layout)
        if not datasets:
            cards = soup.find_all(['div', 'article'], class_=re.compile(r'(card|dataset|item)'))
            if not cards:
                cards = soup.find_all('div', recursive=True)
                cards = [card for card in cards if card.find('a') and len(card.get_text(strip=True)) > 50]
            
            for card in cards[:50]:  # Limit to avoid too many false positives
                dataset_info = self.extract_dataset_from_card(card)
                if dataset_info['name'] and len(dataset_info['name']) > 5:
                    datasets.append(dataset_info)
                    self.logger.info(f"Extracted dataset (card): {dataset_info['name']}")
        
        # Method 3: Look for any links that might be datasets
        if not datasets:
            links = soup.find_all('a', href=re.compile(r'/earth-engine/datasets/catalog/'))
            for link in links:
                parent = link.parent
                if parent:
                    dataset_info = self.extract_dataset_from_card(parent)
                    if dataset_info['name'] and len(dataset_info['name']) > 5:
                        datasets.append(dataset_info)
                        self.logger.info(f"Extracted dataset (link): {dataset_info['name']}")
        
        # Update progress
        self.total_datasets += len(datasets)
        
        return datasets
    
    def crawl_all_pages(self) -> List[Dict[str, Any]]:
        """Crawl all catalog pages until no more datasets are found"""
        all_datasets = []
        page_num = 1
        consecutive_empty_pages = 0
        max_consecutive_empty = 5  # Stop after 5 consecutive empty pages
        
        print(f"\n🌍 Starting to crawl all available pages...")
        print("=" * 60)
        print("The crawler will continue until no more datasets are found.")
        print("=" * 60)
        
        while True:
            if page_num == 1:
                page_url = self.base_url
            else:
                page_url = f"{self.base_url}?page={page_num}"
            
            # Update progress
            self.current_page = page_num
            print(f'\r🌍 Crawling Page {page_num} | Datasets found: {self.total_datasets} | Empty pages: {consecutive_empty_pages}', end='', flush=True)
            
            self.logger.info(f"Crawling page {page_num}: {page_url}")
            page_datasets = self.crawl_catalog_page(page_url)
            
            if not page_datasets:
                consecutive_empty_pages += 1
                self.logger.info(f"No datasets found on page {page_num} (empty page #{consecutive_empty_pages})")
                
                # Stop if we've had too many consecutive empty pages
                if consecutive_empty_pages >= max_consecutive_empty:
                    print(f"\n✅ No more datasets found after {consecutive_empty_pages} consecutive empty pages.")
                    break
            else:
                consecutive_empty_pages = 0  # Reset counter when we find data
                all_datasets.extend(page_datasets)
                self.logger.info(f"Found {len(page_datasets)} datasets on page {page_num}")
            
            # Be respectful with rate limiting
            time.sleep(1)
            page_num += 1
            
            # Safety check - don't go forever (but much higher limit)
            if page_num > 10000:
                print(f"\n⚠️ Safety limit reached (10000 pages). Stopping to prevent infinite loop.")
                break
        
        print(f"\n✅ Crawling completed! Found {len(all_datasets)} total datasets across {page_num-1} pages.")
        print("=" * 60)
        
        self.datasets = all_datasets
        return all_datasets
    
    def categorize_datasets(self):
        """Categorize datasets by various criteria"""
        print("\n📊 Categorizing datasets...")
        
        total_datasets = len(self.datasets)
        for i, dataset in enumerate(self.datasets):
            # Show categorization progress
            if i % 10 == 0 or i == total_datasets - 1:
                self.print_progress_bar(
                    current=i + 1,
                    total=total_datasets,
                    prefix='Categorizing',
                    suffix=f'Dataset {i+1}/{total_datasets}'
                )
            
            # Categorize by satellite
            for satellite in dataset['satellites']:
                if satellite not in self.satellites:
                    self.satellites[satellite] = []
                self.satellites[satellite].append(dataset)
            
            # Categorize by data type
            if dataset['data_type']:
                if dataset['data_type'] not in self.categories:
                    self.categories[dataset['data_type']] = []
                self.categories[dataset['data_type']].append(dataset)
            
            # Categorize by publisher
            if dataset['publisher']:
                if dataset['publisher'] not in self.publishers:
                    self.publishers[dataset['publisher']] = []
                self.publishers[dataset['publisher']].append(dataset)
        
        print(f"\n✅ Categorization completed!")
        print(f"   📁 Categories: {len(self.categories)}")
        print(f"   🛰️ Satellites: {len(self.satellites)}")
        print(f"   🏢 Publishers: {len(self.publishers)}")
    
    def save_to_json(self, filename: str = "gee_catalog_data_enhanced.json"):
        """Save extracted data to JSON file"""
        print(f"\n💾 Saving data to {filename}...")
        
        output_data = {
            'metadata': {
                'crawl_date': datetime.now().isoformat(),
                'total_datasets': len(self.datasets),
                'source_url': self.base_url,
                'crawler_version': 'enhanced_v2'
            },
            'datasets': self.datasets,
            'categories': self.categories,
            'satellites': self.satellites,
            'publishers': self.publishers,
            'summary': {
                'total_datasets': len(self.datasets),
                'unique_satellites': len(self.satellites),
                'unique_categories': len(self.categories),
                'unique_publishers': len(self.publishers),
                'datasets_with_resolution': len([d for d in self.datasets if d['resolution']]),
                'datasets_with_dates': len([d for d in self.datasets if d['dates']]),
                'datasets_with_frequency': len([d for d in self.datasets if d['frequency']]),
                'datasets_with_code_snippets': len([d for d in self.datasets if d['code_snippet']])
            }
        }
        
        output_path = Path(filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Data saved successfully to: {output_path}")
        self.logger.info(f"Enhanced data saved to {output_path}")
        return output_path

def main():
    """Main function to run the enhanced crawler"""
    crawler = EnhancedGEECatalogCrawler()
    
    print("🚀 Starting Enhanced Google Earth Engine Data Catalog Crawler")
    print("=" * 60)
    print("This crawler will extract essential dataset information")
    print("from the Earth Engine Data Catalog with code snippets.")
    print("=" * 60)
    
    # Crawl all pages (no limit - goes until nothing left)
    datasets = crawler.crawl_all_pages()
    
    # Categorize the datasets
    crawler.categorize_datasets()
    
    # Save to JSON
    json_file = crawler.save_to_json()
    
    # Print final summary
    print("\n" + "=" * 60)
    print("🎉 CRAWLER COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print(f"📊 Total datasets extracted: {len(datasets)}")
    print(f"🛰️ Satellites found: {len(crawler.satellites)}")
    print(f"📁 Categories found: {len(crawler.categories)}")
    print(f"🏢 Publishers found: {len(crawler.publishers)}")
    
    if crawler.satellites:
        print(f"\n🛰️ Top satellites:")
        for satellite, datasets_list in sorted(crawler.satellites.items(), key=lambda x: len(x[1]), reverse=True)[:5]:
            print(f"   {satellite}: {len(datasets_list)} datasets")
    
    if crawler.categories:
        print(f"\n📁 Top categories:")
        for category, datasets_list in sorted(crawler.categories.items(), key=lambda x: len(x[1]), reverse=True)[:5]:
            print(f"   {category}: {len(datasets_list)} datasets")
    
    if crawler.publishers:
        print(f"\n🏢 Top publishers:")
        for publisher, datasets_list in sorted(crawler.publishers.items(), key=lambda x: len(x[1]), reverse=True)[:5]:
            print(f"   {publisher}: {len(datasets_list)} datasets")
    
    if crawler.datasets:
        print(f"\n📋 Sample dataset:")
        sample = crawler.datasets[0]
        print(f"   Name: {sample['name']}")
        print(f"   Type: {sample['data_type']}")
        print(f"   Satellites: {', '.join(sample['satellites'][:3])}")
        print(f"   Resolution: {sample['resolution']}")
        print(f"   Code snippet: {'Yes' if sample['code_snippet'] else 'No'}")
    
    print(f"\n💾 Data saved to: {json_file}")
    print("🌐 Open catalog_viewer.html to browse the data")
    print("=" * 60)
    
    return crawler

if __name__ == "__main__":
    main() 