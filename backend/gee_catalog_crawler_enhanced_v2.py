#!/usr/bin/env python3
"""
Enhanced Google Earth Engine Data Catalog Crawler v2.0
Modern implementation with improved architecture, async support, and better data processing
"""

import asyncio
import aiohttp
import json
import time
import logging
from pathlib import Path
from datetime import datetime
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup, Tag
import re
from typing import Dict, List, Optional, Any, Set
import sys
import gzip
import argparse
import shutil
import threading
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor
import itertools
from collections import defaultdict
import hashlib

# Enhanced progress tracking
@dataclass
class CrawlerProgress:
    """Structured crawler progress tracking"""
    total_pages: int = 0
    current_page: int = 0
    total_datasets: int = 0
    processed_datasets: int = 0
    current_status: str = "initializing"
    start_time: str = ""
    estimated_completion: str = ""
    errors: List[str] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []

PROGRESS_FILE = 'backend/crawler_data/crawler_progress_enhanced.json'

def write_progress(progress: CrawlerProgress):
    """Write progress to file with enhanced structure"""
    try:
        Path(PROGRESS_FILE).parent.mkdir(parents=True, exist_ok=True)
        with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
            json.dump(asdict(progress), f, ensure_ascii=False, indent=2)
    except Exception as e:
        logging.warning(f"Failed to write progress: {e}")

class EnhancedGEECatalogCrawlerV2:
    """Enhanced GEE Catalog Crawler with modern architecture"""
    
    def __init__(self, base_url: str = "https://developers.google.com/earth-engine/datasets/catalog"):
        self.base_url = base_url
        self.session = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Setup enhanced logging
        self.setup_enhanced_logging()
        
        # Enhanced data storage
        self.datasets: List[Dict[str, Any]] = []
        self.categories: Dict[str, List[str]] = defaultdict(list)
        self.satellites: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.publishers: Dict[str, List[str]] = defaultdict(list)
        self.tags: Set[str] = set()
        
        # Progress tracking
        self.progress = CrawlerProgress()
        self.progress.start_time = datetime.now().isoformat()
        
        # Setup directories
        self.setup_directories()
        
        # Rate limiting
        self.request_delay = 1.0  # seconds between requests
        self.last_request_time = 0
        
    def setup_enhanced_logging(self):
        """Setup enhanced logging with structured output"""
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        log_file = logs_dir / f"gee_catalog_crawler_v2_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        # Enhanced formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
        )
        
        # File handler
        file_handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.INFO)
        
        # Setup logging
        logging.basicConfig(
            level=logging.DEBUG,
            handlers=[file_handler, console_handler],
            force=True
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("Enhanced GEE Catalog Crawler v2.0 initialized")
    
    def setup_directories(self):
        """Setup enhanced directory structure"""
        self.data_dir = Path("backend/crawler_data")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Enhanced directory structure
        self.thumbnail_dir = self.data_dir / "thumbnails"
        self.thumbnail_dir.mkdir(parents=True, exist_ok=True)
        
        self.metadata_dir = self.data_dir / "metadata"
        self.metadata_dir.mkdir(parents=True, exist_ok=True)
        
        self.cache_dir = self.data_dir / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    async def create_session(self):
        """Create async HTTP session"""
        if self.session is None:
            timeout = aiohttp.ClientTimeout(total=30)
            connector = aiohttp.TCPConnector(limit=10, limit_per_host=5)
            self.session = aiohttp.ClientSession(
                headers=self.headers,
                timeout=timeout,
                connector=connector
            )
    
    async def close_session(self):
        """Close async HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None
    
    def print_enhanced_progress_bar(self, current: int, total: int, prefix: str = 'Progress', 
                                  suffix: str = 'Complete', length: int = 50, fill: str = '█'):
        """Enhanced progress bar with additional information"""
        percent = f"{100 * (current / float(total)):.1f}"
        filled_length = int(length * current // total)
        bar = fill * filled_length + '-' * (length - filled_length)
        
        # Calculate ETA
        if current > 0:
            elapsed = time.time() - datetime.fromisoformat(self.progress.start_time).timestamp()
            rate = current / elapsed
            eta = (total - current) / rate if rate > 0 else 0
            eta_str = f"ETA: {eta:.0f}s"
        else:
            eta_str = "ETA: calculating..."
        
        print(f'\r{prefix} |{bar}| {percent}% {suffix} | {eta_str}', end='', flush=True)
        if current == total:
            print()  # New line when complete
    
    async def get_page_content_async(self, url: str, retries: int = 3, backoff: float = 2.0) -> Optional[BeautifulSoup]:
        """Get page content with async HTTP requests"""
        await self.create_session()
        
        for attempt in range(retries):
            try:
                # Rate limiting
                current_time = time.time()
                time_since_last = current_time - self.last_request_time
                if time_since_last < self.request_delay:
                    await asyncio.sleep(self.request_delay - time_since_last)
                
                self.logger.debug(f"Fetching: {url} (attempt {attempt + 1}/{retries})")
                async with self.session.get(url) as response:
                    response.raise_for_status()
                    content = await response.text()
                    self.last_request_time = time.time()
                    return BeautifulSoup(content, 'html.parser')
                    
            except Exception as e:
                self.logger.warning(f"Error fetching {url} (attempt {attempt + 1}/{retries}): {e}")
                if attempt < retries - 1:
                    await asyncio.sleep(backoff * (2 ** attempt))
                else:
                    self.progress.errors.append(f"Failed to fetch {url}: {e}")
                    return None
    
    def extract_enhanced_thumbnail_url(self, card_element) -> str:
        """Enhanced thumbnail extraction with multiple fallback methods"""
        if not isinstance(card_element, Tag):
            return ''
        
        # Method 1: Direct img tag
        img = card_element.find('img')
        if img and isinstance(img, Tag):
            src = img.get('src')
            if isinstance(src, str) and src.strip():
                return src
        
        # Method 2: Background image in CSS
        style = card_element.get('style', '')
        bg_match = re.search(r'background-image:\s*url\(["\']?([^"\']+)["\']?\)', style)
        if bg_match:
            return bg_match.group(1)
        
        # Method 3: Data attributes
        data_src = card_element.get('data-thumbnail') or card_element.get('data-image')
        if data_src:
            return data_src
        
        # Method 4: Preview links
        preview_links = card_element.find_all('a', href=True)
        for link in preview_links:
            href = link.get('href', '')
            if any(ext in href.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                return href
        
        return ''
    
    async def download_thumbnail_async(self, url: str, dataset_id: str) -> str:
        """Download thumbnail with async HTTP"""
        if not url or not dataset_id:
            return ''
        
        try:
            await self.create_session()
            
            # Normalize URL
            if url.startswith('//'):
                url = 'https:' + url
            elif url.startswith('/'):
                url = 'https://developers.google.com' + url
            
            # Generate filename with hash for uniqueness
            url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
            ext = url.split('.')[-1].split('?')[0]
            if ext not in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                ext = 'jpg'  # Default extension
            
            local_path = self.thumbnail_dir / f"{dataset_id}_{url_hash}.{ext}"
            
            # Check if already downloaded
            if local_path.exists():
                return str(local_path)
            
            # Download with async
            async with self.session.get(url) as response:
                response.raise_for_status()
                content = await response.read()
                
                with open(local_path, 'wb') as f:
                    f.write(content)
                
                return str(local_path)
                
        except Exception as e:
            self.logger.warning(f"Failed to download thumbnail for {dataset_id}: {e}")
            self.progress.warnings.append(f"Thumbnail download failed for {dataset_id}: {e}")
            return ''
    
    def extract_enhanced_dataset_info(self, card_element) -> Dict[str, Any]:
        """Extract enhanced dataset information with improved parsing"""
        dataset_info = {
            # Core fields
            'name': '',
            'description': '',
            'dataset_id': '',
            'collection_id': '',
            'url': '',
            
            # Technical specifications
            'resolution': '',
            'satellites': [],
            'data_type': '',
            'dates': '',
            'frequency': '',
            'coverage': '',
            'bands': [],
            
            # Metadata
            'publisher': '',
            'tags': [],
            'applications': [],
            'limitations': '',
            'thumbnail': '',
            
            # Enhanced fields
            'cloud_cover': True,
            'start_date': '',
            'end_date': '',
            'spatial_resolution': '',
            'temporal_resolution': '',
            'data_format': '',
            'license': '',
            'citation': '',
            'documentation': '',
            'examples': [],
            'code_snippet': '',
            
            # Processing metadata
            'extraction_timestamp': datetime.now().isoformat(),
            'source_url': '',
            'confidence_score': 0.0
        }
        
        try:
            if not isinstance(card_element, Tag):
                return dataset_info
            
            # Extract name and link
            name_link = card_element.find('a')
            if name_link and isinstance(name_link, Tag):
                dataset_info['name'] = name_link.get_text(strip=True)
                href = name_link.get('href')
                if href:
                    dataset_info['url'] = urljoin(self.base_url, href)
                    # Extract dataset ID from URL
                    parsed_url = urlparse(dataset_info['url'])
                    path_parts = parsed_url.path.split('/')
                    if path_parts:
                        dataset_info['dataset_id'] = path_parts[-1]
                        dataset_info['collection_id'] = dataset_info['dataset_id']
            
            # Extract description with multiple fallback methods
            description_selectors = [
                'p',
                'div.description',
                'div[class*="description"]',
                'div[class*="summary"]',
                'div[class*="content"]'
            ]
            
            for selector in description_selectors:
                desc_elem = card_element.select_one(selector)
                if desc_elem and isinstance(desc_elem, Tag):
                    description = desc_elem.get_text(strip=True)
                    if description and len(description) > 10:
                        dataset_info['description'] = description
                        break
            
            # Extract enhanced tags and categorize
            tags_section = card_element.find_all('a', href=re.compile(r'/earth-engine/datasets/tags/'))
            if tags_section:
                dataset_info['tags'] = [tag.get_text(strip=True) for tag in tags_section if isinstance(tag, Tag)]
                
                # Enhanced categorization
                for tag in dataset_info['tags']:
                    tag_lower = tag.lower()
                    
                    # Satellite categorization
                    satellite_keywords = [
                        'landsat', 'modis', 'sentinel', 'aster', 'alos', 'srtm', 'gpm', 
                        'grace', 'jason', 'cryosat', 'icesat', 'quikscat', 'seawinds',
                        'terra', 'aqua', 'spot', 'rapideye', 'planet', 'worldview'
                    ]
                    
                    for keyword in satellite_keywords:
                        if keyword in tag_lower:
                            dataset_info['satellites'].append(tag)
                            break
                    
                    # Publisher categorization
                    publisher_keywords = [
                        'nasa', 'usgs', 'esa', 'jaxa', 'cnes', 'noaa', 'usda',
                        'google', 'planet', 'digitalglobe', 'maxar'
                    ]
                    
                    for keyword in publisher_keywords:
                        if keyword in tag_lower:
                            dataset_info['publisher'] = tag
                            break
                    
                    # Data type categorization
                    data_type_keywords = [
                        'optical', 'radar', 'lidar', 'thermal', 'multispectral',
                        'hyperspectral', 'elevation', 'atmospheric', 'oceanic'
                    ]
                    
                    for keyword in data_type_keywords:
                        if keyword in tag_lower:
                            dataset_info['data_type'] = tag
                            break
            
            # Generate enhanced code snippet
            dataset_info['code_snippet'] = self.generate_enhanced_code_snippet(dataset_info)
            
            # Calculate confidence score
            dataset_info['confidence_score'] = self.calculate_confidence_score(dataset_info)
            
            return dataset_info
            
        except Exception as e:
            self.logger.error(f"Error extracting dataset info: {e}")
            self.progress.errors.append(f"Dataset extraction error: {e}")
            return dataset_info
    
    def generate_enhanced_code_snippet(self, dataset_info: Dict[str, Any]) -> str:
        """Generate enhanced code snippet with better structure"""
        if not dataset_info.get('dataset_id'):
            return ''
        
        dataset_id = dataset_info['dataset_id']
        
        # Enhanced code snippet template
        code_snippet = f"""// {dataset_info.get('name', 'Dataset')}
// {dataset_info.get('description', 'No description available')}

// Load the dataset
var dataset = ee.ImageCollection('{dataset_id}');

// Filter by date range (modify as needed)
var filtered = dataset.filterDate('2020-01-01', '2020-12-31');

// Filter by region (modify as needed)
var region = ee.Geometry.Rectangle([-180, -90, 180, 90]);

// Apply additional filters
var filtered = filtered.filterBounds(region);

// Get the first image for visualization
var firstImage = filtered.first();

// Display the image
Map.addLayer(firstImage, {{}}, '{dataset_info.get('name', 'Dataset')}');

// Export options (uncomment and modify as needed)
/*
Export.image.toDrive({{
  image: firstImage,
  description: '{dataset_id}_export',
  folder: 'EarthEngine_Exports',
  scale: 30,
  region: region
}});
*/"""
        
        return code_snippet
    
    def calculate_confidence_score(self, dataset_info: Dict[str, Any]) -> float:
        """Calculate confidence score for dataset information quality"""
        score = 0.0
        
        # Basic information
        if dataset_info.get('name'):
            score += 0.2
        if dataset_info.get('description'):
            score += 0.2
        if dataset_info.get('dataset_id'):
            score += 0.2
        if dataset_info.get('url'):
            score += 0.1
        
        # Enhanced information
        if dataset_info.get('tags'):
            score += 0.1
        if dataset_info.get('satellites'):
            score += 0.1
        if dataset_info.get('publisher'):
            score += 0.05
        if dataset_info.get('data_type'):
            score += 0.05
        
        return min(score, 1.0)
    
    async def crawl_catalog_page_async(self, page_url: str) -> List[Dict[str, Any]]:
        """Crawl a single catalog page with async processing"""
        try:
            self.logger.info(f"Crawling page: {page_url}")
            self.progress.current_status = f"Crawling page: {page_url}"
            
            soup = await self.get_page_content_async(page_url)
            if not soup:
                return []
            
            # Find dataset cards
            dataset_cards = soup.find_all('div', class_=re.compile(r'card|dataset|item'))
            if not dataset_cards:
                # Fallback: look for any div with links
                dataset_cards = soup.find_all('div')
                dataset_cards = [card for card in dataset_cards if card.find('a', href=re.compile(r'/earth-engine/datasets/'))]
            
            self.logger.info(f"Found {len(dataset_cards)} dataset cards on page")
            
            datasets = []
            for i, card in enumerate(dataset_cards):
                try:
                    dataset_info = self.extract_enhanced_dataset_info(card)
                    
                    if dataset_info.get('dataset_id'):
                        # Download thumbnail asynchronously
                        if dataset_info.get('thumbnail'):
                            thumbnail_path = await self.download_thumbnail_async(
                                dataset_info['thumbnail'], 
                                dataset_info['dataset_id']
                            )
                            dataset_info['thumbnail_local'] = thumbnail_path
                        
                        datasets.append(dataset_info)
                        self.progress.processed_datasets += 1
                        
                        # Update progress
                        if self.progress.total_datasets > 0:
                            progress_percent = (self.progress.processed_datasets / self.progress.total_datasets) * 100
                            self.print_enhanced_progress_bar(
                                self.progress.processed_datasets, 
                                self.progress.total_datasets,
                                prefix=f"Page {self.progress.current_page}/{self.progress.total_pages}"
                            )
                
                except Exception as e:
                    self.logger.error(f"Error processing dataset card {i}: {e}")
                    self.progress.errors.append(f"Dataset card {i} error: {e}")
            
            return datasets
            
        except Exception as e:
            self.logger.error(f"Error crawling page {page_url}: {e}")
            self.progress.errors.append(f"Page crawl error for {page_url}: {e}")
            return []
    
    async def crawl_all_pages_async(self) -> List[Dict[str, Any]]:
        """Crawl all catalog pages with async processing"""
        try:
            self.logger.info("Starting enhanced async catalog crawl")
            self.progress.current_status = "Starting catalog crawl"
            
            # Get the main catalog page
            main_soup = await self.get_page_content_async(self.base_url)
            if not main_soup:
                raise Exception("Failed to load main catalog page")
            
            # Find pagination or category links
            page_links = []
            
            # Look for pagination links
            pagination = main_soup.find_all('a', href=re.compile(r'page=|offset='))
            if pagination:
                page_links = [urljoin(self.base_url, link.get('href')) for link in pagination if link.get('href')]
            
            # If no pagination, look for category links
            if not page_links:
                category_links = main_soup.find_all('a', href=re.compile(r'/earth-engine/datasets/catalog/'))
                page_links = [urljoin(self.base_url, link.get('href')) for link in category_links if link.get('href')]
            
            # Add main page
            page_links.insert(0, self.base_url)
            
            self.progress.total_pages = len(page_links)
            self.logger.info(f"Found {self.progress.total_pages} pages to crawl")
            
            all_datasets = []
            
            # Process pages with concurrency control
            semaphore = asyncio.Semaphore(3)  # Limit concurrent requests
            
            async def crawl_page_with_semaphore(url):
                async with semaphore:
                    return await self.crawl_catalog_page_async(url)
            
            # Create tasks for all pages
            tasks = [crawl_page_with_semaphore(url) for url in page_links]
            
            # Process results as they complete
            for i, task in enumerate(asyncio.as_completed(tasks)):
                self.progress.current_page = i + 1
                datasets = await task
                all_datasets.extend(datasets)
                
                # Update progress
                write_progress(self.progress)
                
                self.logger.info(f"Completed page {self.progress.current_page}/{self.progress.total_pages} - {len(datasets)} datasets")
            
            self.progress.total_datasets = len(all_datasets)
            self.logger.info(f"Crawl completed: {self.progress.total_datasets} total datasets")
            
            return all_datasets
            
        except Exception as e:
            self.logger.error(f"Error in async crawl: {e}", exc_info=True)
            self.progress.errors.append(f"Async crawl error: {e}")
            return []
    
    def categorize_enhanced_datasets(self, datasets: List[Dict[str, Any]]):
        """Enhanced dataset categorization with better organization"""
        try:
            self.logger.info("Starting enhanced dataset categorization")
            
            for dataset in datasets:
                # Categorize by satellite
                for satellite in dataset.get('satellites', []):
                    self.satellites[satellite].append(dataset)
                
                # Categorize by publisher
                publisher = dataset.get('publisher', 'Unknown')
                self.publishers[publisher].append(dataset['dataset_id'])
                
                # Categorize by tags
                for tag in dataset.get('tags', []):
                    self.categories[tag].append(dataset['dataset_id'])
                    self.tags.add(tag)
                
                # Categorize by data type
                data_type = dataset.get('data_type', 'Unknown')
                self.categories[data_type].append(dataset['dataset_id'])
            
            self.logger.info(f"Categorization complete: {len(self.satellites)} satellites, {len(self.publishers)} publishers, {len(self.tags)} tags")
            
        except Exception as e:
            self.logger.error(f"Error in categorization: {e}")
            self.progress.errors.append(f"Categorization error: {e}")
    
    def save_enhanced_outputs(self, datasets: List[Dict[str, Any]], prefix: str = "gee_catalog_data_enhanced_v2"):
        """Save enhanced outputs with better organization"""
        try:
            self.logger.info("Saving enhanced outputs")
            
            # Prepare enhanced data structure
            enhanced_data = {
                "metadata": {
                    "version": "2.0",
                    "generated_at": datetime.now().isoformat(),
                    "total_datasets": len(datasets),
                    "total_satellites": len(self.satellites),
                    "total_publishers": len(self.publishers),
                    "total_tags": len(self.tags),
                    "crawler_progress": asdict(self.progress)
                },
                "datasets": datasets,
                "satellites": dict(self.satellites),
                "publishers": dict(self.publishers),
                "categories": dict(self.categories),
                "tags": list(self.tags)
            }
            
            # Save compressed JSON
            compressed_file = self.data_dir / f"{prefix}.json.gz"
            with gzip.open(compressed_file, 'wt', encoding='utf-8') as f:
                json.dump(enhanced_data, f, ensure_ascii=False, indent=2)
            
            # Save metadata separately
            metadata_file = self.metadata_dir / f"{prefix}_metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(enhanced_data["metadata"], f, ensure_ascii=False, indent=2)
            
            # Save summary statistics
            summary_file = self.metadata_dir / f"{prefix}_summary.json"
            summary = {
                "total_datasets": len(datasets),
                "satellites": {k: len(v) for k, v in self.satellites.items()},
                "publishers": {k: len(v) for k, v in self.publishers.items()},
                "top_tags": sorted(self.categories.items(), key=lambda x: len(x[1]), reverse=True)[:20],
                "generated_at": datetime.now().isoformat()
            }
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"Enhanced outputs saved: {compressed_file}")
            return str(compressed_file)
            
        except Exception as e:
            self.logger.error(f"Error saving outputs: {e}")
            self.progress.errors.append(f"Save error: {e}")
            return None

async def run_enhanced_crawler():
    """Run the enhanced crawler with async processing"""
    crawler = EnhancedGEECatalogCrawlerV2()
    
    try:
        # Crawl all pages
        datasets = await crawler.crawl_all_pages_async()
        
        if datasets:
            # Categorize datasets
            crawler.categorize_enhanced_datasets(datasets)
            
            # Save outputs
            output_file = crawler.save_enhanced_outputs(datasets)
            
            # Final progress update
            crawler.progress.current_status = "Completed successfully"
            crawler.progress.processed_datasets = len(datasets)
            write_progress(crawler.progress)
            
            return {
                "status": "success",
                "message": f"Enhanced crawler completed successfully",
                "total_datasets": len(datasets),
                "output_file": output_file,
                "progress": asdict(crawler.progress)
            }
        else:
            return {
                "status": "error",
                "message": "No datasets found",
                "progress": asdict(crawler.progress)
            }
    
    except Exception as e:
        crawler.logger.error(f"Enhanced crawler failed: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "progress": asdict(crawler.progress)
        }
    finally:
        await crawler.close_session()

def main():
    """Main function for command line usage"""
    parser = argparse.ArgumentParser(description="Enhanced GEE Catalog Crawler v2.0")
    parser.add_argument("--async", action="store_true", help="Use async processing")
    parser.add_argument("--output", type=str, help="Output file prefix")
    
    args = parser.parse_args()
    
    if args.async:
        result = asyncio.run(run_enhanced_crawler())
    else:
        # Fallback to synchronous version
        crawler = EnhancedGEECatalogCrawlerV2()
        # Implement synchronous version if needed
        result = {"status": "error", "message": "Synchronous version not implemented"}
    
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main() 