import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import threading
import time
import os
import json
import re
import requests
from pathlib import Path
from datetime import datetime
from urllib.parse import urljoin, urlparse
import gzip
from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class EarthEngineCrawler:
    """Enhanced Earth Engine crawler with satellite link following"""
    
    def __init__(self, gui_callback=None):
        self.gui_callback = gui_callback
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Data storage
        self.datasets = []
        self.categories = {}
        self.tags = set()
        self.publishers = set()
        self.visited_urls = set()
        
        # Known dataset patterns
        self.known_datasets = self.load_known_datasets()
        
        # Satellite-related keywords to identify relevant links
        self.satellite_keywords = [
            'landsat', 'sentinel', 'modis', 'goes', 'srtm', 'era5', 'gfs', 'ncep',
            'seawifs', 'nasa', 'usgs', 'noaa', 'ecmwf', 'copernicus', 'esa',
            'satellite', 'dataset', 'catalog', 'earth-engine', 'geospatial',
            'remote-sensing', 'imagery', 'radar', 'optical', 'multispectral'
        ]
        
        # Keywords to avoid (social media, navigation, etc.)
        self.avoid_keywords = [
            'facebook', 'twitter', 'linkedin', 'instagram', 'youtube', 'github',
            'stackoverflow', 'reddit', 'discord', 'slack', 'telegram',
            'privacy', 'terms', 'contact', 'about', 'help', 'support',
            'login', 'signup', 'register', 'account', 'profile'
        ]
        
    def log_message(self, message):
        """Send message to GUI log"""
        if self.gui_callback:
            self.gui_callback(message)
    
    def load_known_datasets(self) -> List[Dict[str, Any]]:
        """Load known datasets from various sources"""
        known_datasets = [
            # Landsat datasets
            {"name": "LANDSAT/LC08/C02/T1_L2", "satellite": "Landsat 8", "description": "Landsat 8 Collection 2 Tier 1 TOA Reflectance"},
            {"name": "LANDSAT/LC09/C02/T1_L2", "satellite": "Landsat 9", "description": "Landsat 9 Collection 2 Tier 1 TOA Reflectance"},
            {"name": "LANDSAT/LE07/C02/T1_L2", "satellite": "Landsat 7", "description": "Landsat 7 Collection 2 Tier 1 TOA Reflectance"},
            {"name": "LANDSAT/LT05/C02/T1_L2", "satellite": "Landsat 5", "description": "Landsat 5 Collection 2 Tier 1 TOA Reflectance"},
            
            # Sentinel datasets
            {"name": "COPERNICUS/S2_SR_HARMONIZED", "satellite": "Sentinel-2", "description": "Sentinel-2 MSI: MultiSpectral Instrument, Level-2A"},
            {"name": "COPERNICUS/S2", "satellite": "Sentinel-2", "description": "Sentinel-2 MSI: MultiSpectral Instrument, Level-1C"},
            {"name": "COPERNICUS/S1_GRD", "satellite": "Sentinel-1", "description": "Sentinel-1 SAR GRD: C-band Synthetic Aperture Radar Ground Range Detected"},
            
            # MODIS datasets
            {"name": "MODIS/006/MOD13Q1", "satellite": "MODIS", "description": "MODIS/Terra Vegetation Indices 16-Day L3 Global 250m SIN Grid V006"},
            {"name": "MODIS/006/MYD13Q1", "satellite": "MODIS", "description": "MODIS/Aqua Vegetation Indices 16-Day L3 Global 250m SIN Grid V006"},
            {"name": "MODIS/006/MOD09A1", "satellite": "MODIS", "description": "MODIS/Terra Surface Reflectance 8-Day L3 Global 500m SIN Grid V006"},
            
            # GOES datasets
            {"name": "NOAA/GOES/16/MCMIPF", "satellite": "GOES-16", "description": "GOES-16 ABI L2 Cloud and Moisture Imagery"},
            {"name": "NOAA/GOES/17/MCMIPF", "satellite": "GOES-17", "description": "GOES-17 ABI L2 Cloud and Moisture Imagery"},
            
            # Climate datasets
            {"name": "ECMWF/ERA5/DAILY", "satellite": "ERA5", "description": "ERA5 Daily Aggregates - Latest Climate Reanalysis"},
            {"name": "NASA/NEX-DCP30", "satellite": "NASA", "description": "NASA NEX-DCP30 Climate Projections"},
            
            # Elevation datasets
            {"name": "USGS/SRTMGL1_003", "satellite": "SRTM", "description": "SRTM Digital Elevation Data Version 3"},
            {"name": "USGS/GMTED2010", "satellite": "GMTED", "description": "Global Multi-resolution Terrain Elevation Data 2010"},
            
            # Weather datasets
            {"name": "NOAA/GFS0P25", "satellite": "GFS", "description": "Global Forecast System 384-Hour Predicted Atmosphere Data"},
            {"name": "NOAA/NCEP_DOE_RE2", "satellite": "NCEP", "description": "NCEP-DOE Reanalysis 2"},
            
            # Ocean datasets
            {"name": "NASA/OCEANDATA/MODIS-Aqua/L3SMI", "satellite": "MODIS Aqua", "description": "MODIS Aqua Sea Surface Temperature"},
            {"name": "NASA/OCEANDATA/SeaWiFS/L3SMI", "satellite": "SeaWiFS", "description": "SeaWiFS Sea Surface Temperature"},
            
            # Atmospheric datasets
            {"name": "MODIS/006/MOD08_M3", "satellite": "MODIS", "description": "MODIS/Terra Aerosol Cloud Water Vapor Ozone Monthly L3 Global 1Deg CMG V006"},
            {"name": "MODIS/006/MYD08_M3", "satellite": "MODIS", "description": "MODIS/Aqua Aerosol Cloud Water Vapor Ozone Monthly L3 Global 1Deg CMG V006"},
        ]
        
        return known_datasets
    
    def is_satellite_related_url(self, url: str, link_text: str = "") -> bool:
        url_lower = url.lower()
        text_lower = link_text.lower()

        # Skip non-English catalog language variants
        if "catalog?hl=" in url_lower and "catalog?hl=en" not in url_lower:
            return False

        # Check for avoid keywords
        for avoid in self.avoid_keywords:
            if avoid in url_lower or avoid in text_lower:
                return False

        # Check for satellite keywords
        for keyword in self.satellite_keywords:
            if keyword in url_lower or keyword in text_lower:
                return True

        # Check for Earth Engine specific patterns
        if any(pattern in url_lower for pattern in ['earth-engine', 'datasets/catalog', 'developers.google.com/earth-engine']):
            return True

        return False
    
    def extract_satellite_links_from_html(self, html_content: str, base_url: str = "") -> List[Dict[str, str]]:
        """Extract satellite-related links from HTML content"""
        links = []
        
        try:
            # Use BeautifulSoup for better HTML parsing
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find all links
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                link_text = link.get_text(strip=True)
                
                # Skip empty or very short links
                if not href or len(href) < 5:
                    continue
                
                # Make URL absolute if it's relative
                if base_url and not href.startswith(('http://', 'https://')):
                    href = urljoin(base_url, href)
                
                # Check if this is a satellite-related link
                if self.is_satellite_related_url(href, link_text):
                    links.append({
                        'url': href,
                        'text': link_text,
                        'title': link.get('title', '')
                    })
                    
        except Exception as e:
            self.log_message(f"Error parsing HTML with BeautifulSoup: {e}")
            # Fallback to regex parsing
            links = self.extract_links_with_regex(html_content, base_url)
        
        return links
    
    def extract_links_with_regex(self, html_content: str, base_url: str = "") -> List[Dict[str, str]]:
        """Fallback method to extract links using regex"""
        links = []
        
        # Pattern to find links
        link_pattern = r'<a[^>]*href=["\']([^"\']+)["\'][^>]*>([^<]+)</a>'
        
        for match in re.finditer(link_pattern, html_content, re.IGNORECASE):
            href = match.group(1)
            link_text = match.group(2).strip()
            
            # Skip empty or very short links
            if not href or len(href) < 5:
                continue
            
            # Make URL absolute if it's relative
            if base_url and not href.startswith(('http://', 'https://')):
                href = urljoin(base_url, href)
            
            # Check if this is a satellite-related link
            if self.is_satellite_related_url(href, link_text):
                links.append({
                    'url': href,
                    'text': link_text,
                    'title': ''
                })
        
        return links
    
    def fetch_satellite_page(self, url: str) -> Optional[str]:
        try:
            if url in self.visited_urls:
                return None
            self.log_message(f"Fetching satellite page: {url}")
            self.visited_urls.add(url)
            # Track download speed
            start_time = time.time()
            response = self.session.get(url, timeout=30, verify=False, stream=True)
            response.raise_for_status()
            content = b''
            chunk_size = 8192
            total_bytes = 0
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    content += chunk
                    total_bytes += len(chunk)
                    elapsed = time.time() - start_time
                    speed = (total_bytes / 1024 / 1024) / elapsed if elapsed > 0 else 0
                    if hasattr(self, 'gui_callback') and callable(self.gui_callback):
                        # If called from GUI, update speed bar
                        try:
                            self.gui_callback(f"__UPDATE_SPEED__:{speed}")
                        except Exception:
                            pass
            html_text = content.decode(response.encoding or 'utf-8', errors='ignore')
            self.log_message(f"Successfully fetched page: {url} ({len(html_text)} characters)")
            return html_text
        except Exception as e:
            self.log_message(f"Error fetching {url}: {e}")
            return None
    
    def extract_satellite_details(self, html_content: str, url: str) -> Dict[str, Any]:
        details = {
            'url': url,
            'title': '',
            'availability': '',
            'tags': [],
            'provider': '',
            'snippet': '',
            'thumbnail_url': '',
            'description': '',
            'code_example': '',
            'bands': [],  # Will be a list of dicts
            'terms_of_use': '',
            'citations': '',
            'dois': [],
            'metadata': {},
            'last_updated': datetime.now().isoformat()
        }
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            # Title
            title_el = soup.find(['h1', 'h2'])
            if title_el:
                details['title'] = title_el.get_text(strip=True)
            # Dataset Availability
            avail_el = soup.find(string=lambda t: t and 'Dataset Availability' in t)
            if avail_el:
                avail_parent = avail_el.find_parent()
                if avail_parent:
                    details['availability'] = avail_parent.get_text(strip=True).replace('Dataset Availability', '').strip()
            # Tags
            tag_els = soup.find_all('span', class_='devsite-chip-label')
            details['tags'] = [t.get_text(strip=True) for t in tag_els]
            # Provider
            provider_el = soup.find(string=lambda t: t and 'Dataset Provider' in t)
            if provider_el:
                provider_parent = provider_el.find_parent()
                if provider_parent:
                    details['provider'] = provider_parent.get_text(strip=True).replace('Dataset Provider', '').strip()
            # Snippet
            snippet_el = soup.find('code', string=lambda t: t and 'ee.ImageCollection' in t)
            if snippet_el:
                details['snippet'] = snippet_el.get_text(strip=True)
            # Thumbnail
            img_el = soup.find('img')
            if img_el and img_el.get('src'):
                details['thumbnail_url'] = img_el['src']
            # Description tab
            desc_tab = soup.find('div', {'id': 'description'})
            if desc_tab:
                details['description'] = desc_tab.get_text(strip=True)
            else:
                # fallback: first p
                p = soup.find('p')
                if p:
                    details['description'] = p.get_text(strip=True)
            # Code Editor Example
            code_block = soup.find('pre')
            if code_block:
                details['code_example'] = code_block.get_text(strip=True)
            # Bands tab (parse as table)
            bands_tab = soup.find('div', {'id': 'bands'})
            bands_list = []
            if bands_tab:
                table = bands_tab.find('table')
                if table:
                    headers = [th.get_text(strip=True) for th in table.find_all('th')]
                    for row in table.find_all('tr')[1:]:
                        cells = [td.get_text(strip=True) for td in row.find_all(['td', 'th'])]
                        if len(cells) == len(headers):
                            band_info = dict(zip(headers, cells))
                            bands_list.append(band_info)
                else:
                    # fallback: just get all text
                    bands_list = [b.get_text(strip=True) for b in bands_tab.find_all(['tr', 'td', 'th'])]
            details['bands'] = bands_list
            # Terms of Use tab
            terms_tab = soup.find('div', {'id': 'terms-of-use'})
            if terms_tab:
                details['terms_of_use'] = terms_tab.get_text(strip=True)
            # Citations tab
            citations_tab = soup.find('div', {'id': 'citations'})
            if citations_tab:
                details['citations'] = citations_tab.get_text(strip=True)
                # Extract DOIs from citations
                dois = re.findall(r'10\.\d{4,9}/[-._;()/:A-Z0-9]+', details['citations'], re.I)
                details['dois'] = dois
            # fallback: search for DOIs anywhere
            if not details['dois']:
                all_text = soup.get_text()
                dois = re.findall(r'10\.\d{4,9}/[-._;()/:A-Z0-9]+', all_text, re.I)
                details['dois'] = dois
        except Exception as e:
            self.log_message(f"Error extracting details from {url}: {e}")
        return details
    
    def process_html_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Process HTML file and extract Earth Engine datasets with link following"""
        try:
            self.log_message(f"Reading HTML file: {os.path.basename(file_path)}")
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                html_content = f.read()
            
            self.log_message(f"HTML file size: {len(html_content)} characters")
            
            # Extract satellite links from HTML
            base_url = "https://developers.google.com/earth-engine"
            satellite_links = self.extract_satellite_links_from_html(html_content, base_url)
            
            self.log_message(f"Found {len(satellite_links)} satellite-related links")
            
            datasets = []
            
            # Process each satellite link
            for i, link_info in enumerate(satellite_links):
                self.log_message(f"Processing satellite link {i+1}/{len(satellite_links)}: {link_info['text']}")
                
                # Fetch the satellite page
                page_content = self.fetch_satellite_page(link_info['url'])
                
                if page_content:
                    # Extract detailed information
                    details = self.extract_satellite_details(page_content, link_info['url'])
                    
                    # Create dataset info
                    dataset_info = self.create_dataset_info(link_info['text'], link_info['url'])
                    
                    if dataset_info:
                        # Merge with detailed information
                        dataset_info.update(details)
                        datasets.append(dataset_info)
                        
                        self.log_message(f"Extracted detailed info for: {link_info['text']}")
                
                # Add delay to be respectful
                time.sleep(0.5)
            
            self.log_message(f"Extracted {len(datasets)} datasets from HTML file with link following")
            
            return datasets
            
        except Exception as e:
            self.log_message(f"Error processing HTML file {file_path}: {e}")
            return []
    
    def create_dataset_info(self, name: str, url: str) -> Optional[Dict[str, Any]]:
        """Create dataset information from name and URL"""
        try:
            # Extract satellite/mission from name
            satellite = self.extract_satellite_from_name(name)
            
            # Create basic dataset info
            dataset_info = {
                "name": name,
                "url": url,
                "satellite": satellite,
                "description": self.generate_description(name, satellite),
                "tags": self.generate_tags(name, satellite),
                "applications": self.generate_applications(name, satellite),
                "resolution": self.extract_resolution(name),
                "temporal_coverage": self.extract_temporal_coverage(name),
                "publisher": self.extract_publisher(name, satellite),
                "bands": self.generate_bands(name, satellite),
                "last_updated": datetime.now().isoformat(),
                "metadata": {}
            }
            
            return dataset_info
            
        except Exception as e:
            self.log_message(f"Error creating dataset info for {name}: {e}")
            return None
    
    def extract_satellite_from_name(self, name: str) -> str:
        """Extract satellite/mission name from dataset name"""
        name_upper = name.upper()
        
        satellite_patterns = {
            'Landsat': ['LANDSAT', 'LC08', 'LC09', 'LE07', 'LT05'],
            'Sentinel': ['SENTINEL', 'S2', 'S1', 'COPERNICUS'],
            'MODIS': ['MODIS', 'MOD', 'MYD'],
            'GOES': ['GOES', 'NOAA/GOES'],
            'SRTM': ['SRTM'],
            'ERA5': ['ERA5', 'ECMWF'],
            'GFS': ['GFS', 'NOAA/GFS'],
            'NCEP': ['NCEP'],
            'SeaWiFS': ['SEAWIFS'],
            'NASA': ['NASA'],
            'USGS': ['USGS']
        }
        
        for satellite, patterns in satellite_patterns.items():
            for pattern in patterns:
                if pattern in name_upper:
                    return satellite
        
        return "Other"
    
    def generate_description(self, name: str, satellite: str) -> str:
        """Generate description based on dataset name and satellite"""
        descriptions = {
            'Landsat': f"{satellite} satellite imagery dataset",
            'Sentinel': f"{satellite} satellite radar/optical imagery",
            'MODIS': f"{satellite} moderate resolution imaging spectroradiometer data",
            'GOES': f"{satellite} geostationary operational environmental satellite data",
            'SRTM': "Shuttle Radar Topography Mission elevation data",
            'ERA5': "ERA5 climate reanalysis data",
            'GFS': "Global Forecast System weather data",
            'NCEP': "NCEP-DOE Reanalysis atmospheric data",
            'SeaWiFS': "Sea-viewing Wide Field-of-view Sensor ocean data",
            'NASA': f"{satellite} satellite data",
            'USGS': f"{satellite} geological survey data"
        }
        
        return descriptions.get(satellite, f"{satellite} satellite dataset")
    
    def generate_tags(self, name: str, satellite: str) -> List[str]:
        """Generate tags based on dataset name and satellite"""
        tags = [satellite]
        
        name_upper = name.upper()
        
        # Add tags based on satellite type
        if satellite == 'Landsat':
            tags.extend(['optical', 'multispectral', 'land-cover', 'vegetation'])
        elif satellite == 'Sentinel':
            if 'S1' in name_upper:
                tags.extend(['radar', 'SAR', 'backscatter'])
            elif 'S2' in name_upper:
                tags.extend(['optical', 'multispectral', 'vegetation', 'land-cover'])
        elif satellite == 'MODIS':
            tags.extend(['vegetation', 'climate', 'atmosphere', 'ocean'])
        elif satellite == 'GOES':
            tags.extend(['weather', 'atmosphere', 'clouds', 'geostationary'])
        elif satellite == 'SRTM':
            tags.extend(['elevation', 'topography', 'DEM'])
        elif satellite == 'ERA5':
            tags.extend(['climate', 'reanalysis', 'atmosphere', 'weather'])
        elif satellite == 'GFS':
            tags.extend(['weather', 'forecast', 'atmosphere'])
        
        # Add resolution tags
        if '250M' in name_upper or '250m' in name_upper:
            tags.append('250m-resolution')
        elif '500M' in name_upper or '500m' in name_upper:
            tags.append('500m-resolution')
        elif '1KM' in name_upper or '1km' in name_upper:
            tags.append('1km-resolution')
        
        return tags
    
    def generate_applications(self, name: str, satellite: str) -> List[str]:
        """Generate applications based on dataset type"""
        applications = []
        
        if satellite == 'Landsat':
            applications.extend(['land-cover-mapping', 'vegetation-monitoring', 'urban-development'])
        elif satellite == 'Sentinel':
            applications.extend(['agriculture', 'forestry', 'disaster-monitoring'])
        elif satellite == 'MODIS':
            applications.extend(['climate-monitoring', 'vegetation-analysis', 'atmospheric-studies'])
        elif satellite == 'GOES':
            applications.extend(['weather-forecasting', 'storm-tracking', 'climate-monitoring'])
        elif satellite == 'SRTM':
            applications.extend(['terrain-analysis', 'flood-modeling', 'infrastructure-planning'])
        elif satellite == 'ERA5':
            applications.extend(['climate-research', 'weather-analysis', 'atmospheric-modeling'])
        
        return applications
    
    def extract_resolution(self, name: str) -> str:
        """Extract resolution from dataset name"""
        name_upper = name.upper()
        
        if '250M' in name_upper or '250m' in name_upper:
            return "250m"
        elif '500M' in name_upper or '500m' in name_upper:
            return "500m"
        elif '1KM' in name_upper or '1km' in name_upper:
            return "1km"
        elif '30M' in name_upper or '30m' in name_upper:
            return "30m"
        elif '10M' in name_upper or '10m' in name_upper:
            return "10m"
        
        return "Variable"
    
    def extract_temporal_coverage(self, name: str) -> str:
        """Extract temporal coverage from dataset name"""
        name_upper = name.upper()
        
        if 'DAILY' in name_upper:
            return "Daily"
        elif '8DAY' in name_upper or '8-DAY' in name_upper:
            return "8-day"
        elif '16DAY' in name_upper or '16-DAY' in name_upper:
            return "16-day"
        elif 'MONTHLY' in name_upper or 'MONTH' in name_upper:
            return "Monthly"
        elif 'YEARLY' in name_upper or 'YEAR' in name_upper:
            return "Yearly"
        
        return "Variable"
    
    def extract_publisher(self, name: str, satellite: str) -> str:
        """Extract publisher from dataset name"""
        name_upper = name.upper()
        
        if 'USGS' in name_upper:
            return "USGS"
        elif 'NASA' in name_upper:
            return "NASA"
        elif 'NOAA' in name_upper:
            return "NOAA"
        elif 'ECMWF' in name_upper:
            return "ECMWF"
        elif 'COPERNICUS' in name_upper:
            return "ESA"
        
        return "Google Earth Engine"
    
    def generate_bands(self, name: str, satellite: str) -> List[str]:
        """Generate band information based on satellite type"""
        band_sets = {
            'Landsat': ['Blue', 'Green', 'Red', 'NIR', 'SWIR1', 'SWIR2', 'Thermal'],
            'Sentinel': ['Blue', 'Green', 'Red', 'NIR', 'SWIR1', 'SWIR2'],
            'MODIS': ['Red', 'NIR', 'Blue', 'Green', 'SWIR', 'Thermal'],
            'GOES': ['Visible', 'IR1', 'IR2', 'IR3', 'IR4'],
            'SRTM': ['Elevation'],
            'ERA5': ['Temperature', 'Humidity', 'Pressure', 'Wind'],
            'GFS': ['Temperature', 'Humidity', 'Pressure', 'Wind', 'Precipitation']
        }
        
        return band_sets.get(satellite, [])
    
    def crawl_known_datasets(self) -> List[Dict[str, Any]]:
        """Crawl known datasets and enhance with additional information"""
        self.log_message("Processing known Earth Engine datasets...")
        
        enhanced_datasets = []
        
        for dataset in self.known_datasets:
            try:
                self.log_message(f"Processing known dataset: {dataset['name']}")
                
                # Enhance with additional information
                enhanced_dataset = self.create_dataset_info(dataset['name'], "")
                
                if enhanced_dataset:
                    # Override with known information
                    enhanced_dataset.update(dataset)
                    enhanced_datasets.append(enhanced_dataset)
                    
                    # Add delay to be respectful
                    time.sleep(0.1)
                    
            except Exception as e:
                self.log_message(f"Error processing known dataset {dataset['name']}: {e}")
                continue
        
        return enhanced_datasets
    
    def organize_data(self):
        """Organize datasets by categories"""
        self.log_message("Organizing datasets by categories...")
        
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
            
            # Categorize by tags
            for tag in dataset.get('tags', []):
                if tag not in categories:
                    categories[tag] = []
                categories[tag].append(dataset)
        
        self.categories = categories
        
        # Extract unique tags and publishers
        for dataset in self.datasets:
            self.tags.update(dataset.get('tags', []))
            if dataset.get('publisher'):
                self.publishers.add(dataset['publisher'])
        
        self.log_message(f"Organized {len(self.datasets)} datasets into {len(categories)} categories")
    
    # In save_results, ensure output is a single JSON file with a list of all datasets
    def save_results(self, output_dir: str) -> Dict[str, Any]:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        # Prepare results as a list of datasets
        results = [d for d in self.datasets]
        json_file = output_path / f"earth_engine_catalog_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        gz_file = output_path / f"earth_engine_catalog_{timestamp}.json.gz"
        with gzip.open(gz_file, 'wt', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        self.log_message(f"Results saved to {json_file}")
        self.log_message(f"Compressed results saved to {gz_file}")
        return {'datasets': results, 'json_file': str(json_file), 'gz_file': str(gz_file)}
    
    def generate_summary_report(self) -> str:
        """Generate a summary report of the crawl"""
        report = f"""
Enhanced Earth Engine Catalog Crawl Summary
===========================================

Crawl Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Total Datasets: {len(self.datasets)}
Total Tags: {len(self.tags)}
Total Publishers: {len(self.publishers)}
Visited URLs: {len(self.visited_urls)}

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

class CrawlerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Enhanced Earth Engine Data Catalog Crawler")
        self.root.geometry("800x600")
        
        # Variables
        self.selected_folder = tk.StringVar()
        self.progress_var = tk.DoubleVar()
        self.status_var = tk.StringVar(value="Ready to start")
        
        # Initialize crawler
        self.crawler = EarthEngineCrawler(gui_callback=self.log_message)
        
        # Create GUI elements
        self.create_widgets()
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Enhanced Earth Engine Data Catalog Crawler", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Folder selection section
        folder_frame = ttk.LabelFrame(main_frame, text="Select Folder", padding="10")
        folder_frame.pack(fill=tk.X, pady=(0, 20))
        
        folder_inner = ttk.Frame(folder_frame)
        folder_inner.pack(fill=tk.X)
        
        ttk.Label(folder_inner, text="Folder Path:").pack(side=tk.LEFT, padx=(0, 10))
        
        folder_entry = ttk.Entry(folder_inner, textvariable=self.selected_folder, width=60)
        folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        browse_btn = ttk.Button(folder_inner, text="Browse", command=self.browse_folder)
        browse_btn.pack(side=tk.RIGHT)
        
        # Progress section
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="10")
        progress_frame.pack(fill=tk.X, pady=(0, 20))

        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                           maximum=100, length=400)
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))

        # ETA label
        self.eta_var = tk.StringVar(value="ETA: --")
        eta_label = ttk.Label(progress_frame, textvariable=self.eta_var)
        eta_label.pack(anchor=tk.W)

        # Download speed bar (Task Manager style)
        speed_frame = ttk.Frame(progress_frame)
        speed_frame.pack(fill=tk.X, pady=(5, 0))
        ttk.Label(speed_frame, text="Download Speed:").pack(side=tk.LEFT)
        self.speed_canvas = tk.Canvas(speed_frame, width=200, height=20, bg="#222")
        self.speed_canvas.pack(side=tk.LEFT, padx=(10, 0))
        self.speed_var = tk.DoubleVar(value=0.0)
        self.speed_label = ttk.Label(speed_frame, text="0.00 MB/s")
        self.speed_label.pack(side=tk.LEFT, padx=(10, 0))
        self.speed_history = [0.0] * 50  # For graphing
        
        status_label = ttk.Label(progress_frame, textvariable=self.status_var)
        status_label.pack(anchor=tk.W)
        
        # Buttons section
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=(20, 0))
        
        self.start_btn = ttk.Button(button_frame, text="Start Enhanced Crawling", 
                                   command=self.start_crawling)
        self.start_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_btn = ttk.Button(button_frame, text="Stop", 
                                  command=self.stop_crawling, state="disabled")
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        clear_btn = ttk.Button(button_frame, text="Clear", command=self.clear_all)
        clear_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        save_btn = ttk.Button(button_frame, text="Save Results", command=self.save_results)
        save_btn.pack(side=tk.LEFT)

        # Add Clear Saved Files button
        clear_files_btn = ttk.Button(button_frame, text="Clear Saved Files", command=self.clear_saved_files)
        clear_files_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # Log section
        log_frame = ttk.LabelFrame(main_frame, text="Log", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(20, 0))
        
        # Log text area with scrollbar
        log_container = ttk.Frame(log_frame)
        log_container.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = tk.Text(log_container, height=12, wrap=tk.WORD)
        log_scrollbar = ttk.Scrollbar(log_container, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def browse_folder(self):
        """Open folder browser dialog"""
        folder_path = filedialog.askdirectory(
            title="Select Earth Engine Data Folder",
            initialdir=os.getcwd()
        )
        if folder_path:
            self.selected_folder.set(folder_path)
            self.log_message(f"Selected folder: {folder_path}")
            
    def start_crawling(self):
        """Start the crawling process in a separate thread"""
        if not self.selected_folder.get():
            messagebox.showerror("Error", "Please select a folder first!")
            return
            
        if not os.path.exists(self.selected_folder.get()):
            messagebox.showerror("Error", "Selected folder does not exist!")
            return
            
        # Disable start button and enable stop button
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        
        # Reset progress
        self.progress_var.set(0)
        self.status_var.set("Starting enhanced Earth Engine crawler...")
        
        # Start crawling in separate thread
        self.crawling_thread = threading.Thread(target=self.crawl_folder)
        self.crawling_thread.daemon = True
        self.crawling_thread.start()
        
    def stop_crawling(self):
        """Stop the crawling process"""
        self.status_var.set("Stopping crawler...")
        self.log_message("Crawler stopped by user")
        
        # Re-enable start button and disable stop button
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        
    def clear_all(self):
        """Clear all fields and reset progress"""
        self.selected_folder.set("")
        self.progress_var.set(0)
        self.status_var.set("Ready to start")
        self.log_text.delete(1.0, tk.END)
        
    def save_results(self):
        """Save current results"""
        if not hasattr(self, 'crawler') or not self.crawler.datasets:
            messagebox.showwarning("Warning", "No data to save. Run the crawler first.")
            return
            
        save_dir = filedialog.askdirectory(
            title="Select Directory to Save Results",
            initialdir=os.getcwd()
        )
        
        if save_dir:
            try:
                results = self.crawler.save_results(save_dir)
                
                # Generate and save summary report
                report = self.crawler.generate_summary_report()
                report_file = Path(save_dir) / "enhanced_crawl_summary.txt"
                with open(report_file, 'w', encoding='utf-8') as f:
                    f.write(report)
                
                self.log_message(f"Results saved to: {save_dir}")
                messagebox.showinfo("Success", f"Results saved to:\n{save_dir}")
                
            except Exception as e:
                self.log_message(f"Error saving results: {e}")
                messagebox.showerror("Error", f"Failed to save results: {e}")
        
    def log_message(self, message):
        if message.startswith("__UPDATE_SPEED__:"):
            try:
                speed = float(message.split(":", 1)[1])
                self.update_speed_bar(speed)
            except Exception:
                pass
            return
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def update_speed_bar(self, speed_mb_s):
        self.speed_history.append(speed_mb_s)
        if len(self.speed_history) > 50:
            self.speed_history.pop(0)
        self.speed_canvas.delete("all")
        max_speed = max(self.speed_history) if self.speed_history else 1
        for i, val in enumerate(self.speed_history):
            x0 = i * 4
            y0 = 20 - int((val / (max_speed or 1)) * 18)
            x1 = x0 + 3
            y1 = 20
            color = "#4caf50" if val > 0 else "#333"
            self.speed_canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="")
        self.speed_label.config(text=f"{speed_mb_s:.2f} MB/s")

    def crawl_folder(self):
        try:
            folder_path = self.selected_folder.get()
            self.log_message(f"Starting enhanced Earth Engine catalog crawl for folder: {folder_path}")
            all_files = []
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    all_files.append(os.path.join(root, file))
            total_files = len(all_files)
            self.log_message(f"Found {total_files} files to process")
            if total_files == 0:
                self.status_var.set("No files found")
                self.log_message("No files found in selected folder")
                return
            self.log_message("Processing known Earth Engine datasets...")
            known_datasets = self.crawler.crawl_known_datasets()
            self.crawler.datasets.extend(known_datasets)
            html_files = [f for f in all_files if f.lower().endswith('.html')]
            other_files = [f for f in all_files if not f.lower().endswith('.html')]
            # Timing for ETA
            start_time = time.time()
            processed = 0
            total_to_process = len(html_files) + len(other_files)
            last_bytes = 0
            last_time = start_time
            for i, file_path in enumerate(html_files):
                if not hasattr(self, 'crawling_thread') or not self.crawling_thread.is_alive():
                    break
                progress = (i + 1) / total_to_process * 100
                self.progress_var.set(progress)
                self.status_var.set(f"Processing HTML file {i+1} of {len(html_files)}: {os.path.basename(file_path)}")
                # Track download speed
                file_bytes = os.path.getsize(file_path)
                now = time.time()
                elapsed = now - last_time
                speed = (file_bytes - last_bytes) / 1024 / 1024 / elapsed if elapsed > 0 else 0
                self.update_speed_bar(speed)
                last_bytes = file_bytes
                last_time = now
                # ETA
                processed += 1
                avg_time = (now - start_time) / processed if processed else 0
                eta = avg_time * (total_to_process - processed)
                self.eta_var.set(f"ETA: {int(eta//60):02d}:{int(eta%60):02d}")
                datasets = self.crawler.process_html_file(file_path)
                self.crawler.datasets.extend(datasets)
                time.sleep(0.1)
            for i, file_path in enumerate(other_files):
                if not hasattr(self, 'crawling_thread') or not self.crawling_thread.is_alive():
                    break
                progress = (len(html_files) + i + 1) / total_to_process * 100
                self.progress_var.set(progress)
                self.status_var.set(f"Processing file {len(html_files) + i + 1} of {total_to_process}: {os.path.basename(file_path)}")
                file_bytes = os.path.getsize(file_path)
                now = time.time()
                elapsed = now - last_time
                speed = (file_bytes - last_bytes) / 1024 / 1024 / elapsed if elapsed > 0 else 0
                self.update_speed_bar(speed)
                last_bytes = file_bytes
                last_time = now
                processed += 1
                avg_time = (now - start_time) / processed if processed else 0
                eta = avg_time * (total_to_process - processed)
                self.eta_var.set(f"ETA: {int(eta//60):02d}:{int(eta%60):02d}")
                file_ext = os.path.splitext(file_path)[1].lower()
                self.log_message(f"Processing {file_ext} file: {os.path.basename(file_path)}")
                time.sleep(0.05)
            unique_datasets = []
            seen_names = set()
            for dataset in self.crawler.datasets:
                if dataset['name'] not in seen_names:
                    unique_datasets.append(dataset)
                    seen_names.add(dataset['name'])
            self.crawler.datasets = unique_datasets
            self.crawler.organize_data()
            self.progress_var.set(100)
            self.status_var.set("Enhanced crawling completed!")
            self.log_message(f"Enhanced Earth Engine crawler completed successfully!")
            self.log_message(f"Found {len(self.crawler.datasets)} unique datasets")
            self.log_message(f"Organized into {len(self.crawler.categories)} categories")
            self.log_message(f"Extracted {len(self.crawler.tags)} unique tags")
            self.log_message(f"Found {len(self.crawler.publishers)} publishers")
            self.log_message(f"Visited {len(self.crawler.visited_urls)} satellite pages")
        except Exception as e:
            self.log_message(f"Error during crawling: {str(e)}")
            self.status_var.set("Error occurred")
        finally:
            self.root.after(0, lambda: self.start_btn.config(state="normal"))
            self.root.after(0, lambda: self.stop_btn.config(state="disabled"))

    def clear_saved_files(self):
        """Delete all saved crawler output files and show confirmation"""
        import glob
        import shutil
        deleted_files = []
        dirs_to_clear = ["output", "crawler_data", "logs"]
        patterns = ["*.json", "*.json.gz", "*.txt", "*.log"]
        for d in dirs_to_clear:
            if os.path.exists(d):
                for pattern in patterns:
                    for f in glob.glob(os.path.join(d, pattern)):
                        try:
                            os.remove(f)
                            deleted_files.append(f)
                        except Exception as e:
                            self.log_message(f"Error deleting {f}: {e}")
        if deleted_files:
            self.log_message(f"Deleted {len(deleted_files)} files from output, crawler_data, and logs.")
            messagebox.showinfo("Files Deleted", f"Deleted {len(deleted_files)} files from output, crawler_data, and logs.")
        else:
            self.log_message("No files found to delete.")
            messagebox.showinfo("Files Deleted", "No files found to delete.")

def main():
    """Main function to run the GUI"""
    root = tk.Tk()
    
    # Set theme if available
    try:
        style = ttk.Style()
        style.theme_use('clam')  # or 'vista', 'xpnative', 'winnative'
    except:
        pass
    
    app = CrawlerGUI(root)
    
    # Center the window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main() 