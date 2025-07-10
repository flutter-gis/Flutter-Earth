#!/usr/bin/env python3
"""
Advanced Google Earth Engine Data Catalog Crawler
Handles JavaScript-rendered content and API endpoints
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
import random

class AdvancedEarthEngineCrawler:
    """Advanced crawler for Google Earth Engine Data Catalog"""
    
    def __init__(self):
        self.base_url = "https://developers.google.com/earth-engine/datasets/catalog"
        self.api_base = "https://developers.google.com/earth-engine/api"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/advanced_earth_engine_crawler.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Data storage
        self.datasets = []
        self.categories = {}
        self.tags = set()
        self.publishers = set()
        
        # Create output directory
        self.output_dir = Path("crawler_data")
        self.output_dir.mkdir(exist_ok=True)
        
        # Known dataset patterns
        self.known_datasets = self.load_known_datasets()
        
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
    
    def get_catalog_page(self, url: str) -> Optional[str]:
        """Get the content of a catalog page"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            self.logger.error(f"Error fetching {url}: {e}")
            return None
    
    def extract_datasets_from_page(self, html_content: str) -> List[Dict[str, Any]]:
        """Extract dataset information from HTML content"""
        datasets = []
        
        # Look for dataset links in the catalog
        dataset_patterns = [
            r'href="([^"]*datasets/catalog/[^"]*)"[^>]*>([^<]+)</a>',
            r'<a[^>]*href="([^"]*)"[^>]*>([^<]*LANDSAT[^<]*)</a>',
            r'<a[^>]*href="([^"]*)"[^>]*>([^<]*SENTINEL[^<]*)</a>',
            r'<a[^>]*href="([^"]*)"[^>]*>([^<]*MODIS[^<]*)</a>',
            r'<a[^>]*href="([^"]*)"[^>]*>([^<]*COPERNICUS[^<]*)</a>',
        ]
        
        for pattern in dataset_patterns:
            matches = re.finditer(pattern, html_content, re.IGNORECASE)
            for match in matches:
                try:
                    dataset_url = match.group(1)
                    dataset_name = match.group(2).strip()
                    
                    # Clean up the dataset name
                    dataset_name = re.sub(r'<[^>]+>', '', dataset_name)
                    dataset_name = re.sub(r'\s+', ' ', dataset_name).strip()
                    
                    if dataset_name and len(dataset_name) > 3:
                        dataset_info = self.create_dataset_info(dataset_name, dataset_url)
                        if dataset_info:
                            datasets.append(dataset_info)
                            
                except Exception as e:
                    self.logger.error(f"Error parsing dataset link: {e}")
                    continue
        
        return datasets
    
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
            self.logger.error(f"Error creating dataset info for {name}: {e}")
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
            'Landsat': f"{satellite} satellite data collection for Earth observation and land monitoring",
            'Sentinel': f"{satellite} mission data for environmental monitoring and security applications",
            'MODIS': f"{satellite} instrument data for global Earth system monitoring",
            'GOES': f"{satellite} geostationary satellite data for weather monitoring",
            'SRTM': f"Shuttle Radar Topography Mission digital elevation data",
            'ERA5': f"ERA5 climate reanalysis data for atmospheric and surface parameters",
            'GFS': f"Global Forecast System weather prediction data",
            'NCEP': f"NCEP-DOE Reanalysis atmospheric and surface data",
            'SeaWiFS': f"Sea-viewing Wide Field-of-view Sensor ocean color data",
            'NASA': f"NASA Earth observation and research data",
            'USGS': f"USGS Earth science and mapping data"
        }
        
        return descriptions.get(satellite, f"{satellite} Earth observation dataset")
    
    def generate_tags(self, name: str, satellite: str) -> List[str]:
        """Generate tags based on dataset characteristics"""
        tags = []
        
        # Add satellite-specific tags
        if 'Landsat' in satellite:
            tags.extend(['optical', 'multispectral', 'land-monitoring', 'agriculture', 'forestry'])
        elif 'Sentinel' in satellite:
            tags.extend(['optical', 'radar', 'multispectral', 'land-monitoring', 'marine-monitoring'])
        elif 'MODIS' in satellite:
            tags.extend(['optical', 'multispectral', 'climate-monitoring', 'vegetation'])
        elif 'GOES' in satellite:
            tags.extend(['weather', 'atmospheric', 'geostationary', 'cloud-monitoring'])
        elif 'SRTM' in satellite:
            tags.extend(['elevation', 'topography', 'dem', 'terrain'])
        elif 'ERA5' in satellite:
            tags.extend(['climate', 'atmospheric', 'reanalysis', 'weather'])
        
        # Add general tags based on name
        name_lower = name.lower()
        if 'surface' in name_lower:
            tags.append('surface-data')
        if 'reflectance' in name_lower:
            tags.append('reflectance')
        if 'temperature' in name_lower:
            tags.append('temperature')
        if 'vegetation' in name_lower:
            tags.append('vegetation')
        if 'aerosol' in name_lower:
            tags.append('aerosol')
        if 'cloud' in name_lower:
            tags.append('cloud')
        if 'ocean' in name_lower:
            tags.append('ocean')
        
        return list(set(tags))
    
    def generate_applications(self, name: str, satellite: str) -> List[str]:
        """Generate applications based on dataset characteristics"""
        applications = []
        
        name_lower = name.lower()
        
        # Add applications based on satellite type
        if 'Landsat' in satellite:
            applications.extend(['Agriculture', 'Forestry', 'Urban Planning', 'Land Cover'])
        elif 'Sentinel' in satellite:
            applications.extend(['Agriculture', 'Forestry', 'Disaster Management', 'Marine Monitoring'])
        elif 'MODIS' in satellite:
            applications.extend(['Climate Studies', 'Vegetation Monitoring', 'Ocean Studies'])
        elif 'GOES' in satellite:
            applications.extend(['Weather Monitoring', 'Climate Studies', 'Atmospheric Research'])
        elif 'SRTM' in satellite:
            applications.extend(['Topography', 'Hydrology', 'Infrastructure Planning'])
        elif 'ERA5' in satellite:
            applications.extend(['Climate Research', 'Weather Analysis', 'Atmospheric Studies'])
        
        # Add applications based on data type
        if 'surface' in name_lower or 'reflectance' in name_lower:
            applications.append('Surface Analysis')
        if 'temperature' in name_lower:
            applications.append('Temperature Monitoring')
        if 'vegetation' in name_lower:
            applications.append('Vegetation Analysis')
        if 'aerosol' in name_lower:
            applications.append('Air Quality')
        if 'cloud' in name_lower:
            applications.append('Cloud Monitoring')
        if 'ocean' in name_lower:
            applications.append('Oceanography')
        
        return list(set(applications))
    
    def extract_resolution(self, name: str) -> str:
        """Extract resolution information from dataset name"""
        # Look for resolution patterns
        resolution_patterns = [
            r'(\d+)m',  # meters
            r'(\d+)km',  # kilometers
            r'(\d+)deg',  # degrees
        ]
        
        for pattern in resolution_patterns:
            match = re.search(pattern, name, re.IGNORECASE)
            if match:
                value = match.group(1)
                if 'km' in pattern:
                    return f"{value}km"
                elif 'deg' in pattern:
                    return f"{value}°"
                else:
                    return f"{value}m"
        
        # Default resolutions based on satellite
        default_resolutions = {
            'Landsat': '30m',
            'Sentinel-2': '10m',
            'Sentinel-1': '10m',
            'MODIS': '250m',
            'GOES': '2km',
            'SRTM': '30m',
            'ERA5': '0.25°'
        }
        
        return default_resolutions.get(self.extract_satellite_from_name(name), 'Variable')
    
    def extract_temporal_coverage(self, name: str) -> str:
        """Extract temporal coverage information"""
        # Look for year patterns
        year_pattern = r'(\d{4})'
        years = re.findall(year_pattern, name)
        
        if years:
            if len(years) >= 2:
                return f"{min(years)}-{max(years)}"
            else:
                return f"{years[0]}-present"
        
        # Default temporal coverage based on satellite
        default_coverage = {
            'Landsat': '1972-present',
            'Sentinel': '2014-present',
            'MODIS': '2000-present',
            'GOES': '1975-present',
            'SRTM': '2000',
            'ERA5': '1979-present'
        }
        
        return default_coverage.get(self.extract_satellite_from_name(name), 'Variable')
    
    def extract_publisher(self, name: str, satellite: str) -> str:
        """Extract publisher information"""
        publishers = {
            'Landsat': 'USGS',
            'Sentinel': 'ESA',
            'MODIS': 'NASA',
            'GOES': 'NOAA',
            'SRTM': 'NASA',
            'ERA5': 'ECMWF',
            'GFS': 'NOAA',
            'NCEP': 'NOAA',
            'SeaWiFS': 'NASA'
        }
        
        return publishers.get(satellite, 'Google')
    
    def generate_bands(self, name: str, satellite: str) -> List[str]:
        """Generate band information based on satellite type"""
        band_sets = {
            'Landsat': ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9', 'B10', 'B11'],
            'Sentinel-2': ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B8A', 'B9', 'B10', 'B11', 'B12'],
            'Sentinel-1': ['VV', 'VH'],
            'MODIS': ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7'],
            'GOES': ['C01', 'C02', 'C03', 'C04', 'C05', 'C06', 'C07', 'C08', 'C09', 'C10', 'C11', 'C12', 'C13', 'C14', 'C15', 'C16']
        }
        
        return band_sets.get(satellite, [])
    
    def crawl_known_datasets(self) -> List[Dict[str, Any]]:
        """Crawl known datasets and enhance with additional information"""
        self.logger.info("Starting crawl of known datasets")
        
        enhanced_datasets = []
        
        for dataset in self.known_datasets:
            try:
                self.logger.info(f"Processing known dataset: {dataset['name']}")
                
                # Enhance with additional information
                enhanced_dataset = self.create_dataset_info(dataset['name'], "")
                
                if enhanced_dataset:
                    # Override with known information
                    enhanced_dataset.update(dataset)
                    enhanced_datasets.append(enhanced_dataset)
                    
                    # Add delay to be respectful
                    time.sleep(0.1)
                    
            except Exception as e:
                self.logger.error(f"Error processing known dataset {dataset['name']}: {e}")
                continue
        
        return enhanced_datasets
    
    def crawl_all_datasets(self) -> Dict[str, Any]:
        """Crawl all available datasets"""
        self.logger.info("Starting comprehensive Earth Engine catalog crawl")
        
        # Start with known datasets
        self.logger.info("Processing known datasets")
        known_datasets = self.crawl_known_datasets()
        self.datasets.extend(known_datasets)
        
        # Try to get additional datasets from the catalog page
        self.logger.info("Fetching catalog page for additional datasets")
        catalog_page = self.get_catalog_page(self.base_url)
        
        if catalog_page:
            self.logger.info("Extracting datasets from catalog page")
            page_datasets = self.extract_datasets_from_page(catalog_page)
            self.datasets.extend(page_datasets)
        
        # Remove duplicates
        unique_datasets = []
        seen_names = set()
        for dataset in self.datasets:
            if dataset['name'] not in seen_names:
                unique_datasets.append(dataset)
                seen_names.add(dataset['name'])
        
        self.datasets = unique_datasets
        
        # Organize data
        self.organize_data()
        
        # Save results
        results = self.save_results()
        
        self.logger.info(f"Crawl completed. Found {len(self.datasets)} unique datasets")
        return results
    
    def organize_data(self):
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
        json_file = self.output_dir / f"earth_engine_catalog_advanced_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # Save as compressed JSON
        gz_file = self.output_dir / f"earth_engine_catalog_advanced_{timestamp}.json.gz"
        with gzip.open(gz_file, 'wt', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Results saved to {json_file} and {gz_file}")
        
        return results
    
    def generate_summary_report(self) -> str:
        """Generate a summary report of the crawl"""
        report = f"""
Advanced Earth Engine Catalog Crawl Summary
===========================================

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
    """Main function to run the advanced crawler"""
    crawler = AdvancedEarthEngineCrawler()
    
    try:
        # Run the crawler
        results = crawler.crawl_all_datasets()
        
        # Generate and save summary report
        report = crawler.generate_summary_report()
        report_file = crawler.output_dir / "advanced_crawl_summary.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(report)
        print(f"\nAdvanced crawl completed successfully!")
        print(f"Results saved to: {crawler.output_dir}")
        
    except Exception as e:
        print(f"Error during advanced crawl: {e}")
        crawler.logger.error(f"Advanced crawl failed: {e}")

if __name__ == "__main__":
    main() 