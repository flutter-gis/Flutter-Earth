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
from bs4 import BeautifulSoup, Tag
import re
from typing import Dict, List, Optional, Any
import sys
import gzip
import argparse
import shutil
import threading
import itertools
import os
from logging.handlers import RotatingFileHandler
from glob import glob
import urllib3

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

PROGRESS_FILE = 'backend/crawler_data/crawler_progress.json'

SPINNER_STATES = ['.', '..', '...', '....']

CRAWLER_DATA_DIR = os.path.join(os.path.dirname(__file__), 'crawler_data')

LOG_DIR = os.path.join(os.path.dirname(__file__), 'logs')
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)
LOG_FILE = os.path.join(LOG_DIR, 'gee_catalog_crawler.log')

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('gee_catalog_crawler')

# Set up rotating file handler for crawler logs
file_handler = RotatingFileHandler(LOG_FILE, maxBytes=2*1024*1024, backupCount=3)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

def write_progress(progress):
    try:
        Path(PROGRESS_FILE).parent.mkdir(parents=True, exist_ok=True)
        with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
            json.dump(progress, f, ensure_ascii=False, indent=2)
    except Exception as e:
        pass  # Don't crash on progress write error

def get_local_html_path():
    html_dir = Path(os.path.dirname(os.path.dirname(__file__))) / "gee cat"
    html_files = list(html_dir.glob("*.html"))
    if not html_files:
        print(f"[ERROR] No HTML files found in {html_dir}")
        return None
    print(f"[INFO] Using HTML file: {html_files[0]}")
    return str(html_files[0])

class EnhancedGEECatalogCrawler:
    def __init__(self, base_url: str = "https://developers.google.com/earth-engine/datasets/catalog"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Disable SSL verification completely for home network
        self.session.verify = False
        
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
        
        self.data_dir = Path("backend/crawler_data")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.thumbnail_dir = self.data_dir / "thumbnails"
        self.thumbnail_dir.mkdir(parents=True, exist_ok=True)
        
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
        
    def get_page_content(self, url: str, retries: int = 3, backoff: float = 2.0) -> Optional[BeautifulSoup]:
        for attempt in range(retries):
            try:
                self.logger.info(f"Fetching: {url}")
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                return BeautifulSoup(response.content, 'html.parser')
            except requests.RequestException as e:
                self.logger.error(f"Error fetching {url} (attempt {attempt+1}/{retries}): {e}")
                if attempt < retries - 1:
                    time.sleep(backoff * (2 ** attempt))
                else:
                    return None
    
    def extract_thumbnail_url(self, card_element) -> str:
        """Try to extract a thumbnail/preview image URL from the card element."""
        from bs4 import Tag
        # Only operate if card_element is a Tag
        if not isinstance(card_element, Tag):
            return ''
        # Try common image tags
        img = card_element.find('img') if hasattr(card_element, 'find') else None
        if img and isinstance(img, Tag):
            src = img.get('src')
            if isinstance(src, str):
                return src
        # Try meta/preview links
        preview = card_element.find('a', href=True) if hasattr(card_element, 'find') else None
        if preview and isinstance(preview, Tag):
            href = preview.get('href')
            if isinstance(href, str) and ('.jpg' in href or '.png' in href):
                return href
        return ''

    def download_thumbnail(self, url: str, dataset_id: str) -> str:
        """Download the thumbnail image and return the local path, or empty string on failure."""
        if not url or not dataset_id:
            return ''
        try:
            # Normalize URL
            if url.startswith('//'):
                url = 'https:' + url
            elif url.startswith('/'):
                url = 'https://developers.google.com' + url
            # Get file extension
            ext = url.split('.')[-1].split('?')[0]
            local_path = self.thumbnail_dir / f"{dataset_id}.{ext}"
            # Download with SSL verification disabled
            resp = self.session.get(url, stream=True, timeout=15, verify=False)
            resp.raise_for_status()
            with open(local_path, 'wb') as f:
                shutil.copyfileobj(resp.raw, f)
            return str(local_path)
        except Exception as e:
            self.logger.warning(f"Failed to download thumbnail for {dataset_id}: {e}")
            return ''

    def extract_dataset_from_card(self, card_element) -> Dict[str, Any]:
        """Extract essential dataset information from a dataset card element"""
        from bs4 import Tag
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
            'limitations': '',
            'thumbnail': '',
        }
        try:
            # Extract name and link from the main heading
            name_link = card_element.find('a') if isinstance(card_element, Tag) else None
            if name_link and isinstance(name_link, Tag):
                dataset_info['name'] = name_link.get_text(strip=True)
                href = name_link.get('href') if isinstance(name_link, Tag) else None
                link = urljoin(self.base_url, href) if isinstance(href, str) else None
                # Extract dataset ID from URL
                if link:
                    parsed_url = urlparse(link)
                    path_parts = parsed_url.path.split('/')
                    if len(path_parts) > 0:
                        dataset_info['dataset_id'] = path_parts[-1]
                        dataset_info['collection_id'] = dataset_info['dataset_id']
            # Extract description
            description_elem = (card_element.find('p') if isinstance(card_element, Tag) else None) or \
                              (card_element.find('div', class_='description') if isinstance(card_element, Tag) else None)
            if description_elem and isinstance(description_elem, Tag):
                dataset_info['description'] = description_elem.get_text(strip=True)
            # Extract tags and categorize
            tags_section = card_element.find_all('a', href=re.compile(r'/earth-engine/datasets/tags/')) if isinstance(card_element, Tag) else []
            if tags_section:
                dataset_info['tags'] = [tag.get_text(strip=True) for tag in tags_section if isinstance(tag, Tag)]
                # Categorize tags and extract satellites
                for tag in dataset_info['tags']:
                    tag_lower = tag.lower()
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
            
            # Extract thumbnail URL and download
            thumb_url = self.extract_thumbnail_url(card_element)
            if thumb_url and dataset_info['dataset_id']:
                dataset_info['thumbnail'] = self.download_thumbnail(thumb_url, dataset_info['dataset_id'])
            
        except Exception as e:
            self.logger.error(f"Error extracting dataset from card: {e}")
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
        from bs4 import Tag
        datasets = []
        soup = self.get_page_content(page_url)
        if not soup:
            self.logger.warning(f"No soup returned for {page_url}")
            return datasets
        # Find all dataset cards
        cards = soup.find_all('div', class_='devsite-article-body') if hasattr(soup, 'find_all') else []
        if not cards:
            # Try alternative selectors if nothing found
            cards = soup.find_all('section', class_='devsite-article-body') if hasattr(soup, 'find_all') else []
        self.logger.info(f"[DEBUG] Found {len(cards)} 'devsite-article-body' cards on {page_url}")
        if len(cards) == 0:
            self.logger.warning(f"[DEBUG] No dataset cards found on {page_url}. HTML snippet: {str(soup)[:500]}")
        for card in cards:
            if isinstance(card, Tag):
                for child in card.find_all('div', recursive=False) if hasattr(card, 'find_all') else []:
                    if isinstance(child, Tag):
                        dataset_info = self.extract_dataset_from_card(child)
                        if dataset_info['name']:
                            # Download thumbnail if available
                            thumb_url = self.extract_thumbnail_url(child)
                            if thumb_url:
                                dataset_info['thumbnail'] = self.download_thumbnail(thumb_url, dataset_info['dataset_id'])
                            datasets.append(dataset_info)
                            self.logger.info(f"Extracted dataset (link): {dataset_info['name']}")
                        else:
                            self.logger.warning(f"[DEBUG] Failed to extract dataset name from card. Card HTML: {str(child)[:300]}")
        if len(datasets) == 0:
            self.logger.warning(f"[DEBUG] No datasets extracted from {page_url}")
        # Update progress
        self.total_datasets += len(datasets)
        return datasets
    
    def extract_dataset_links_from_local_html(self, local_html_path):
        """Parse the local HTML file and extract all dataset links from image elements."""
        from bs4 import BeautifulSoup, Tag
        links = []
        with open(local_html_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
        
        # Extract all <a href=...> links that wrap <img> tags (image links)
        for a in soup.find_all('a', href=True):
            if isinstance(a, Tag) and a.find('img'):
                href = a.get('href')
                if isinstance(href, str):
                    # Convert relative URLs to absolute URLs
                    if href.startswith('/'):
                        links.append('https://developers.google.com' + href)
                    elif href.startswith('http'):
                        links.append(href)
                    else:
                        # Handle relative URLs
                        links.append('https://developers.google.com/earth-engine/datasets/catalog/' + href.lstrip('/'))
        
        self.logger.info(f"[DEBUG] Found {len(links)} image links in local HTML file.")
        return links

    def crawl_all_pages(self) -> List[Dict[str, Any]]:
        """Crawl all dataset pages using links from local HTML if available."""
        local_html_path = get_local_html_path()
        if local_html_path and Path(local_html_path).exists():
            dataset_links = self.extract_dataset_links_from_local_html(local_html_path)
            all_datasets = []
            processed_datasets = 0
            start_time = time.time()
            progress = {
                'status': 'crawling',
                'message': 'Crawling dataset links from local HTML...',
                'current_dataset': 0,
                'total_datasets': len(dataset_links),
                'datasets_found': 0,
                'satellites_found': 0,
                'percent': 0,
                'speed': 0,
                'error': None
            }
            write_progress(progress)
            for i, url in enumerate(dataset_links):
                print(f"[DEBUG] Processing dataset link {i+1}/{len(dataset_links)}: {url}")
                self.logger.info(f"[DEBUG] Processing dataset link {i+1}/{len(dataset_links)}: {url}")
                try:
                    soup = self.get_page_content(url)
                    if not soup:
                        self.logger.warning(f"[DEBUG] Could not fetch {url}")
                        print(f"[WARN] Could not fetch {url}")
                        continue
                    # Try to find the main dataset card on the page
                    main_card = soup.find('div', class_='devsite-article-body')
                    if not main_card:
                        self.logger.warning(f"[DEBUG] No main card found on {url}")
                        print(f"[WARN] No main card found on {url}")
                        continue
                    for child in main_card.find_all('div', recursive=False) if isinstance(main_card, Tag) else []:
                        if isinstance(child, Tag):
                            dataset_info = self.extract_dataset_from_card(child)
                            if dataset_info['name']:
                                all_datasets.append(dataset_info)
                                processed_datasets += 1
                                print(f"[INFO] Extracted dataset: {dataset_info['name']}")
                                # Save as unique JSON file
                                dataset_id = dataset_info.get('dataset_id', f'{processed_datasets}')
                                dataset_path = self.data_dir / f"dataset_{dataset_id}.json"
                                try:
                                    with open(dataset_path, 'w', encoding='utf-8') as f:
                                        json.dump(dataset_info, f, ensure_ascii=False, indent=2)
                                except Exception as e:
                                    self.logger.warning(f"Failed to save dataset {dataset_id}: {e}")
                                # Update progress
                                progress['current_dataset'] = i + 1
                                progress['datasets_found'] = processed_datasets
                                progress['percent'] = int(100 * processed_datasets / max(1, len(dataset_links)))
                                progress['last_saved_dataset'] = str(dataset_path)
                                progress['last_saved_name'] = dataset_info.get('name', '')
                                write_progress(progress)
                            else:
                                print(f"[WARN] Skipped a dataset card with no name at {url}")
                    # Add a small delay to be polite to the server
                    time.sleep(0.2)
                except Exception as e:
                    self.logger.error(f"[ERROR] Exception processing {url}: {e}")
                    print(f"[ERROR] Exception processing {url}: {e}")
            progress['status'] = 'completed'
            progress['message'] = f'Crawling completed! {processed_datasets} datasets.'
            progress['percent'] = 100
            write_progress(progress)
            self.datasets = all_datasets
            return all_datasets
        else:
            print(f"[ERROR] LOCAL_HTML file not found: {local_html_path}")
            return []
    
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
    
    def save_to_json_gz(self, filename: str = "gee_catalog_data_enhanced.json.gz"):
        """Save the extracted catalog data to a compressed .json.gz file"""
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
        out_path = self.data_dir / filename
        with gzip.open(out_path, 'wt', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        self.logger.info(f"Saved compressed catalog data to {out_path}")
        print(f"✅ Data saved successfully to: {out_path}")
        return out_path

    def save_all_outputs(self, prefix: str = "gee_catalog_data"):
        # Only save compressed JSON for frontend
        self.save_to_json_gz(f"{prefix}_enhanced.json.gz")

def safe_filename(name):
    return re.sub(r'[^a-zA-Z0-9_-]', '_', name)[:64]

def crawl_local_html():
    local_html_path = get_local_html_path()
    if not local_html_path:
        logger.error("No HTML file found to parse")
        return
    
    logger.info(f"Parsing local HTML: {local_html_path}")
    with open(local_html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    dataset_cards = soup.find_all('li', class_='ee-sample-image')
    logger.info(f"Found {len(dataset_cards)} dataset cards.")
    for card in dataset_cards:
        try:
            a = card.find('a', href=True) if isinstance(card, Tag) else None
            h3_tag = a.find('h3') if isinstance(a, Tag) else None
            name = h3_tag.get_text(strip=True) if isinstance(h3_tag, Tag) else None
            link = a.get('href') if isinstance(a, Tag) else None
            img_tag = a.find('img') if isinstance(a, Tag) else None
            img = img_tag.get('src') if isinstance(img_tag, Tag) else None
            desc_td = card.find('td', class_='ee-dataset-description-snippet') if isinstance(card, Tag) else None
            description = desc_td.get_text(strip=True) if isinstance(desc_td, Tag) else None
            tags_td = card.find('td', class_='ee-tag-buttons') if isinstance(card, Tag) else None
            tags = [t.get_text(strip=True) for t in tags_td.find_all('a', class_='ee-chip')] if isinstance(tags_td, Tag) else []
            dataset = {
                'name': name,
                'link': link,
                'thumbnail': img,
                'description': description,
                'tags': tags
            }
            fname = f"dataset_{safe_filename(name or 'unknown')}.json"
            out_path = os.path.join(CRAWLER_DATA_DIR, fname)
            with open(out_path, 'w', encoding='utf-8') as out:
                json.dump(dataset, out, indent=2)
            logger.info(f"Saved dataset: {name} -> {fname}")
        except Exception as e:
            logger.error(f"Failed to process a dataset card: {e}")

def run_crawler():
    """Entry point for external scripts to run the crawler and save outputs."""
    try:
        crawler = EnhancedGEECatalogCrawler()
        datasets = crawler.crawl_all_pages()
        crawler.categorize_datasets()
        crawler.save_all_outputs()
        return {
            "status": "success",
            "message": "Web crawler completed successfully",
            "total_datasets": len(datasets),
            "total_satellites": len(crawler.satellites),
            "output_file": str(crawler.data_dir / "gee_catalog_data_enhanced.json.gz")
        }
    except Exception as e:
        progress = {'status': 'error', 'message': str(e), 'error': str(e)}
        write_progress(progress)
        return {
            "status": "error",
            "message": f"Web crawler error: {str(e)}"
        }

def main():
    parser = argparse.ArgumentParser(description="Enhanced GEE Catalog Crawler")
    parser.add_argument('--prefix', type=str, default='gee_catalog_data', help='Output file prefix')
    parser.add_argument('--headless', action='store_true', help='Enable headless browser mode (future)')
    args = parser.parse_args()
    start_time = time.time()
    crawler = EnhancedGEECatalogCrawler()
    print("🚀 Starting Enhanced Google Earth Engine Data Catalog Crawler")
    print("=" * 60)
    print("This crawler will extract essential dataset information\nfrom the Earth Engine Data Catalog with code snippets.")
    print("=" * 60)
    datasets = crawler.crawl_all_pages()
    crawler.categorize_datasets()
    crawler.save_all_outputs(args.prefix)
    elapsed = time.time() - start_time
    print(f"\n⏱️ Total crawl time: {elapsed:.2f} seconds")
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
    print(f"\n💾 Data saved to: backend/{args.prefix}_enhanced.json.gz")
    print("🌐 Open catalog_viewer.html to browse the data")
    print("=" * 60)
    
    return crawler

if __name__ == "__main__":
    main() 