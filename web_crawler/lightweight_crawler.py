#!/usr/bin/env python3
"""
Lightweight Web Crawler - Enhanced Earth Engine Data Extraction
Focuses on extracting comprehensive satellite data including thumbnails
"""

import os
import sys
import json
import time
import threading
import requests
import warnings
import re
from datetime import datetime
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

# Suppress SSL warnings
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

class EarthEngineDataExtractor:
    """Enhanced Earth Engine data extractor with comprehensive parameter extraction"""
    
    def __init__(self):
        # Enhanced satellite patterns with better categorization
        self.satellite_patterns = {
            # Landsat series (separate categories)
            'landsat_1_3': r'\b(Landsat\s*[123])\b',
            'landsat_4_5': r'\b(Landsat\s*[45])\b',
            'landsat_7': r'\b(Landsat\s*7)\b',
            'landsat_8_9': r'\b(Landsat\s*[89])\b',
            
            # Sentinel series (separate categories)
            'sentinel_1': r'\b(Sentinel\s*1)\b',
            'sentinel_2': r'\b(Sentinel\s*2)\b',
            'sentinel_3': r'\b(Sentinel\s*3)\b',
            'sentinel_4': r'\b(Sentinel\s*4)\b',
            'sentinel_5': r'\b(Sentinel\s*5)\b',
            'sentinel_6': r'\b(Sentinel\s*6)\b',
            
            # MODIS satellites
            'modis_terra': r'\b(Terra\s*MODIS|MODIS\s*Terra)\b',
            'modis_aqua': r'\b(Aqua\s*MODIS|MODIS\s*Aqua)\b',
            'modis_general': r'\b(MODIS)\b',
            
            # Other optical satellites
            'aster': r'\b(ASTER)\b',
            'spot': r'\b(SPOT\s*\d+)\b',
            'pleiades': r'\b(Pleiades)\b',
            'quickbird': r'\b(QuickBird)\b',
            'worldview': r'\b(WorldView\s*[1234])\b',
            'planet': r'\b(Planet|PlanetScope|RapidEye)\b',
            
            # Radar satellites
            'radarsat': r'\b(RadarSat\s*\d*)\b',
            'ers': r'\b(ERS\s*[12])\b',
            'envisat': r'\b(Envisat)\b',
            
            # Weather satellites
            'goes': r'\b(GOES\s*\d*)\b',
            'noaa': r'\b(NOAA\s*\d*)\b',
            'meteosat': r'\b(Meteosat)\b',
            
            # Commercial satellites
            'ikonos': r'\b(IKONOS)\b',
            'geoeye': r'\b(GeoEye)\b',
            'digitalglobe': r'\b(DigitalGlobe)\b',
            
            # Other important satellites
            'gfs': r'\b(GFS|Global\s+Forecast\s+System)\b',
            'ecmwf': r'\b(ECMWF|European\s+Centre\s+for\s+Medium-Range\s+Weather\s+Forecasts)\b'
        }
        
        # Resolution patterns
        self.resolution_patterns = [
            r'(\d+(?:\.\d+)?)\s*(m|meters?|km|kilometers?)\s*resolution',
            r'resolution\s*of\s*(\d+(?:\.\d+)?)\s*(m|meters?|km|kilometers?)',
            r'(\d+(?:\.\d+)?)\s*(m|meters?|km|kilometers?)\s*pixel',
            r'(\d+(?:\.\d+)?)\s*(m|meters?|km|kilometers?)\s*spatial'
        ]
        
        # Band patterns
        self.band_patterns = [
            r'\b(B\d+|Band\s*\d+)\b',
            r'\b([RGB]|Red|Green|Blue|NIR|SWIR|TIR)\b',
            r'\b(\d+)\s*bands?\b'
        ]
        
        # Enhanced temporal coverage patterns with better filtering
        self.temporal_patterns = [
            # Specific date ranges (preferred)
            r'(\d{4})\s*[-–]\s*(present|\d{4})',
            r'from\s*(\d{4})\s*to\s*(present|\d{4})',
            r'coverage\s*(\d{4})\s*[-–]\s*(present|\d{4})',
            r'period\s*(\d{4})\s*[-–]\s*(present|\d{4})',
            r'temporal\s*coverage\s*(\d{4})\s*[-–]\s*(present|\d{4})',
            r'data\s*available\s*(\d{4})\s*[-–]\s*(present|\d{4})',
            r'collection\s*period\s*(\d{4})\s*[-–]\s*(present|\d{4})'
        ]
        
        # Date filtering patterns to avoid listing all dates
        self.date_filter_patterns = [
            r'\b(19[7-9]\d|20[0-2]\d)\s*[-–]\s*(present|20[0-2]\d)\b',  # Valid year ranges
            r'\b(19[7-9]\d|20[0-2]\d)\s*to\s*(present|20[0-2]\d)\b',
            r'\b(19[7-9]\d|20[0-2]\d)\s*through\s*(present|20[0-2]\d)\b'
        ]
        
        # Spatial coverage patterns
        self.spatial_patterns = [
            r'global\s*coverage',
            r'worldwide',
            r'(\d+(?:\.\d+)?)\s*(km|miles?)\s*coverage'
        ]
        
        # Processing level patterns
        self.processing_patterns = [
            r'level\s*(\d+[A-Z]?)',
            r'processing\s*level\s*(\d+[A-Z]?)',
            r'tier\s*(\d+)'
        ]
        
        # Additional backend parameters for comprehensive extraction
        self.frequency_patterns = [
            r'(\d+)\s*(hour|day|week|month|year)s?\s*frequency',
            r'frequency\s*of\s*(\d+)\s*(hour|day|week|month|year)s?',
            r'(\d+)\s*(hour|day|week|month|year)s?\s*revisit',
            r'revisit\s*time\s*(\d+)\s*(hour|day|week|month|year)s?'
        ]
        
        self.orbit_patterns = [
            r'(\d+(?:\.\d+)?)\s*(km|miles?)\s*altitude',
            r'altitude\s*of\s*(\d+(?:\.\d+)?)\s*(km|miles?)',
            r'(\d+(?:\.\d+)?)\s*(km|miles?)\s*orbit',
            r'orbital\s*height\s*(\d+(?:\.\d+)?)\s*(km|miles?)'
        ]
        
        self.swath_patterns = [
            r'(\d+(?:\.\d+)?)\s*(km|miles?)\s*swath',
            r'swath\s*width\s*(\d+(?:\.\d+)?)\s*(km|miles?)',
            r'(\d+(?:\.\d+)?)\s*(km|miles?)\s*coverage\s*width'
        ]
        
        self.radiometric_patterns = [
            r'(\d+)\s*bit\s*radiometric',
            r'radiometric\s*resolution\s*(\d+)\s*bit',
            r'(\d+)\s*bit\s*quantization',
            r'quantization\s*(\d+)\s*bit'
        ]
        
        self.atmospheric_patterns = [
            r'atmospheric\s*correction',
            r'radiometric\s*correction',
            r'geometric\s*correction',
            r'orthorectification',
            r'terrain\s*correction'
        ]
        
        self.quality_patterns = [
            r'(\d+(?:\.\d+)?)\s*%\s*quality',
            r'quality\s*(\d+(?:\.\d+)?)\s*%',
            r'(\d+(?:\.\d+)?)\s*%\s*accuracy',
            r'accuracy\s*(\d+(?:\.\d+)?)\s*%'
        ]
    
    def extract_satellite_info(self, text):
        """Extract satellite and sensor information"""
        satellites = {}
        for sat_type, pattern in self.satellite_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                satellites[sat_type] = list(set(matches))
        return satellites if satellites else None
    
    def extract_resolution(self, text):
        """Extract resolution information"""
        for pattern in self.resolution_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                return [f"{value} {unit}" for value, unit in matches]
        return None
    
    def extract_bands(self, text):
        """Extract band information"""
        bands = []
        for pattern in self.band_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            bands.extend(matches)
        return list(set(bands)) if bands else None
    
    def extract_temporal_coverage(self, text):
        """Extract temporal coverage with better filtering and validation"""
        # First try to extract explicit date ranges with context
        for pattern in self.temporal_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # Validate the date ranges
                valid_ranges = []
                for start, end in matches:
                    # Check if it's a reasonable date range
                    if self.is_valid_date_range(start, end):
                        valid_ranges.append(f"{start} to {end}")
                if valid_ranges:
                    return valid_ranges
        
        # Try to extract from satellite information (more specific)
        satellite_dates = self.get_satellite_date_ranges(text)
        if satellite_dates:
            return satellite_dates
        
        # Try to extract any valid date ranges
        for pattern in self.date_filter_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                return [f"{start} to {end}" for start, end in matches]
        
        return []
    
    def is_valid_date_range(self, start_date, end_date):
        """Validate if a date range is reasonable for satellite data"""
        try:
            # Check if dates are reasonable years
            if start_date.isdigit() and end_date.isdigit():
                start_year = int(start_date)
                end_year = int(end_date)
                
                # Valid year ranges for satellite data
                if 1970 <= start_year <= 2030 and 1970 <= end_year <= 2030:
                    # Check if range is reasonable (not too short, not too long)
                    if 1 <= (end_year - start_year) <= 60:
                        return True
            
            # Check if end_date is "present"
            if start_date.isdigit() and end_date.lower() == "present":
                start_year = int(start_date)
                if 1970 <= start_year <= 2030:
                    return True
                    
        except (ValueError, AttributeError):
            pass
        
        return False
    
    def get_satellite_date_ranges(self, text):
        """Get date ranges based on satellite operational periods"""
        satellite_ranges = {
            # Landsat satellites
            'landsat 1': ('1972-07-23', '1978-01-06'),
            'landsat 2': ('1975-01-22', '1982-02-25'),
            'landsat 3': ('1978-03-05', '1983-03-31'),
            'landsat 4': ('1982-07-16', '1993-12-14'),
            'landsat 5': ('1984-03-01', '2013-06-05'),
            'landsat 6': ('1993-10-05', '1993-10-05'),  # Failed launch
            'landsat 7': ('1999-04-15', '2022-04-06'),
            'landsat 8': ('2013-04-11', 'present'),
            'landsat 9': ('2021-10-31', 'present'),
            
            # Sentinel satellites
            'sentinel 1': ('2014-04-03', 'present'),
            'sentinel 2': ('2015-06-23', 'present'),
            'sentinel 3': ('2016-02-16', 'present'),
            'sentinel 4': ('2024-01-01', 'present'),  # Planned
            'sentinel 5': ('2017-10-13', '2022-12-31'),  # Ended
            'sentinel 5p': ('2017-10-13', 'present'),
            'sentinel 6': ('2020-11-21', 'present'),
            
            # MODIS satellites
            'terra modis': ('1999-12-18', 'present'),
            'aqua modis': ('2002-05-04', 'present'),
            
            # Other important satellites
            'spot 1': ('1986-02-22', '1990-12-31'),
            'spot 2': ('1990-01-22', '2009-07-31'),
            'spot 3': ('1993-09-26', '1996-11-14'),
            'spot 4': ('1998-03-24', '2013-07-29'),
            'spot 5': ('2002-05-04', '2015-03-31'),
            'spot 6': ('2012-09-09', 'present'),
            'spot 7': ('2014-06-30', 'present'),
            
            # Commercial satellites
            'worldview 1': ('2007-09-18', 'present'),
            'worldview 2': ('2009-10-08', 'present'),
            'worldview 3': ('2014-08-13', 'present'),
            'worldview 4': ('2016-11-11', '2019-10-29'),
            'quickbird': ('2001-10-18', '2015-01-27'),
            'ikonos': ('1999-09-24', '2015-03-31'),
            
            # Radar satellites
            'ers 1': ('1991-07-17', '2000-03-10'),
            'ers 2': ('1995-04-21', '2011-09-05'),
            'envisat': ('2002-03-01', '2012-04-08'),
            'radarsat 1': ('1995-11-04', '2013-03-29'),
            'radarsat 2': ('2007-12-14', 'present'),
        }
        
        # Look for satellite mentions in text
        text_lower = text.lower()
        found_ranges = []
        
        for satellite, (start_date, end_date) in satellite_ranges.items():
            if satellite in text_lower:
                if end_date == 'present':
                    found_ranges.append(f"{start_date} to present")
                else:
                    found_ranges.append(f"{start_date} to {end_date}")
        
        return found_ranges
    
    def extract_spatial_coverage(self, text):
        """Extract spatial coverage"""
        for pattern in self.spatial_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                return matches
        return None
    
    def extract_processing_level(self, text):
        """Extract processing level"""
        for pattern in self.processing_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                return matches
        return None
    
    def extract_frequency(self, text):
        """Extract frequency/revisit time information"""
        for pattern in self.frequency_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                return [f"{value} {unit}" for value, unit in matches]
        return None
    
    def extract_orbit_info(self, text):
        """Extract orbital altitude information"""
        for pattern in self.orbit_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                return [f"{value} {unit}" for value, unit in matches]
        return None
    
    def extract_swath_info(self, text):
        """Extract swath width information"""
        for pattern in self.swath_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                return [f"{value} {unit}" for value, unit in matches]
        return None
    
    def extract_radiometric_info(self, text):
        """Extract radiometric resolution information"""
        for pattern in self.radiometric_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                return matches
        return None
    
    def extract_atmospheric_corrections(self, text):
        """Extract atmospheric correction information"""
        corrections = []
        for pattern in self.atmospheric_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                corrections.append(pattern.replace('_', ' ').title())
        return corrections if corrections else None
    
    def extract_quality_info(self, text):
        """Extract quality/accuracy information"""
        for pattern in self.quality_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                return [f"{value}%" for value in matches]
        return None

class LightweightCrawlerUI(QWidget):
    """Lightweight crawler with enhanced Earth Engine data extraction"""
    
    # Define signals for thread-safe UI updates
    progress_updated = Signal(int, int)
    status_updated = Signal(str)
    data_updated = Signal()
    log_updated = Signal(str)
    error_updated = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lightweight Earth Engine Crawler")
        self.setGeometry(100, 100, 1400, 900)
        
        # Initialize components
        self.extractor = EarthEngineDataExtractor()
        
        # Create session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
        # Data storage
        self.extracted_data = []
        self.is_crawling = False
        self.stop_requested = False
        self.is_paused = False
        self.pause_requested = False
        self.current_crawl_state = {}  # Store current crawl state for resume
        self.processed_urls = set()
        self.thumbnail_cache = {}
        
        # Statistics
        self.total_processed = 0
        self.successful_extractions = 0
        self.failed_extractions = 0
        self.thumbnail_failures = 0
        self.request_failures = 0
        self.parsing_failures = 0
        self.start_time = None
        
        self.setup_ui()
        self.load_config()
        
        # Connect signals
        self.progress_updated.connect(self.update_progress)
        self.status_updated.connect(self.update_status)
        self.data_updated.connect(self.update_results_table)
        self.log_updated.connect(self.log_message)
        self.error_updated.connect(self.log_error)
    
    def load_config(self):
        """Load configuration"""
        self.config = {
            'performance': {
                'max_concurrent_requests': 2,
                'request_delay': 2.0,
                'timeout': 15
            },
            'processing': {
                'min_confidence': 0.1,
                'max_links_per_run': 999999  # No limit
            }
        }
        self.log_message("✅ Configuration loaded")
    
    def setup_ui(self):
        """Setup the user interface with enhanced viewing mechanisms"""
        layout = QVBoxLayout()
        
        # File selection group
        file_group = QGroupBox("Data Source")
        file_layout = QHBoxLayout()
        
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setPlaceholderText("Select HTML file or enter URL...")
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_file)
        
        # URL input
        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText("Enter URL to crawl...")
        download_btn = QPushButton("Download & Crawl")
        download_btn.clicked.connect(self.download_and_crawl)
        
        file_layout.addWidget(QLabel("HTML File:"))
        file_layout.addWidget(self.file_path_edit)
        file_layout.addWidget(browse_btn)
        file_layout.addWidget(QLabel("OR URL:"))
        file_layout.addWidget(self.url_edit)
        file_layout.addWidget(download_btn)
        file_group.setLayout(file_layout)
        
        # Control buttons
        control_layout = QHBoxLayout()
        self.start_btn = QPushButton("Start Crawling")
        self.start_btn.clicked.connect(self.start_crawl)
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.clicked.connect(self.stop_crawl)
        self.stop_btn.setEnabled(False)
        
        # Pause button
        self.pause_btn = QPushButton("Pause")
        self.pause_btn.clicked.connect(self.toggle_pause)
        self.pause_btn.setEnabled(False)
        
        # Overwrite checkbox
        self.overwrite_checkbox = QCheckBox("Overwrite existing data")
        self.overwrite_checkbox.setChecked(True)  # Default to True
        self.overwrite_checkbox.setToolTip("When enabled, will overwrite existing data instead of skipping")
        
        # Clear state button
        self.clear_state_btn = QPushButton("Clear State")
        self.clear_state_btn.clicked.connect(self.clear_crawl_state)
        self.clear_state_btn.setToolTip("Clear saved crawl state and start fresh")
        
        # Export buttons
        self.export_json_btn = QPushButton("Export JSON")
        self.export_json_btn.clicked.connect(self.export_results)
        self.export_csv_btn = QPushButton("Export CSV")
        self.export_csv_btn.clicked.connect(self.export_results_csv)
        
        # View options
        self.detailed_view_btn = QPushButton("Detailed View")
        self.detailed_view_btn.clicked.connect(self.show_detailed_view)
        
        control_layout.addWidget(self.start_btn)
        control_layout.addWidget(self.stop_btn)
        control_layout.addWidget(self.pause_btn)
        control_layout.addWidget(self.overwrite_checkbox)
        control_layout.addWidget(self.clear_state_btn)
        control_layout.addWidget(self.export_json_btn)
        control_layout.addWidget(self.export_csv_btn)
        control_layout.addWidget(self.detailed_view_btn)
        
        # Search and filter group
        filter_group = QGroupBox("Search & Filter")
        filter_layout = QHBoxLayout()
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search in results...")
        self.search_edit.textChanged.connect(self.filter_results)
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All", "High Confidence (>0.7)", "Medium Confidence (0.4-0.7)", "Low Confidence (<0.4)"])
        self.filter_combo.currentTextChanged.connect(self.filter_results)
        
        self.clear_filter_btn = QPushButton("Clear Filters")
        self.clear_filter_btn.clicked.connect(self.clear_filters)
        
        filter_layout.addWidget(QLabel("Search:"))
        filter_layout.addWidget(self.search_edit)
        filter_layout.addWidget(QLabel("Filter:"))
        filter_layout.addWidget(self.filter_combo)
        filter_layout.addWidget(self.clear_filter_btn)
        filter_group.setLayout(filter_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("font-weight: bold; color: #007acc;")
        
        # Results table with enhanced viewing
        results_group = QGroupBox("Extracted Data")
        results_layout = QVBoxLayout()
        
        # Table controls
        table_controls = QHBoxLayout()
        self.refresh_btn = QPushButton("Refresh Table")
        self.refresh_btn.clicked.connect(self.update_results_table)
        self.sort_btn = QPushButton("Sort by Confidence")
        self.sort_btn.clicked.connect(self.sort_by_confidence)
        self.stats_btn = QPushButton("Show Statistics")
        self.stats_btn.clicked.connect(self.show_statistics)
        
        table_controls.addWidget(self.refresh_btn)
        table_controls.addWidget(self.sort_btn)
        table_controls.addWidget(self.stats_btn)
        table_controls.addStretch()
        
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(20)
        self.results_table.setHorizontalHeaderLabels([
            "Thumbnail", "Title", "Description", "Satellite", "Resolution", "Bands", 
            "Temporal Coverage", "Spatial Coverage", "Processing Level", 
            "Provider", "Data Type", "License", "File Format", "Cloud Cover", 
            "Frequency", "Orbit Altitude", "Swath Width", "Radiometric", "Corrections", "Confidence"
        ])
        
        # Set column widths with larger thumbnails
        self.results_table.setColumnWidth(0, 120)  # Thumbnail (larger)
        self.results_table.setColumnWidth(1, 200)  # Title
        self.results_table.setColumnWidth(2, 250)  # Description
        self.results_table.setColumnWidth(3, 120)  # Satellite
        self.results_table.setColumnWidth(4, 100)  # Resolution
        self.results_table.setColumnWidth(5, 150)  # Bands
        self.results_table.setColumnWidth(6, 120)  # Temporal Coverage
        self.results_table.setColumnWidth(7, 120)  # Spatial Coverage
        self.results_table.setColumnWidth(8, 100)  # Processing Level
        self.results_table.setColumnWidth(9, 100)  # Provider
        self.results_table.setColumnWidth(10, 100) # Data Type
        self.results_table.setColumnWidth(11, 100) # License
        self.results_table.setColumnWidth(12, 80)  # File Format
        self.results_table.setColumnWidth(13, 80)  # Cloud Cover
        self.results_table.setColumnWidth(14, 100) # Frequency
        self.results_table.setColumnWidth(15, 100) # Orbit Altitude
        self.results_table.setColumnWidth(16, 100) # Swath Width
        self.results_table.setColumnWidth(17, 100) # Radiometric
        self.results_table.setColumnWidth(18, 120) # Corrections
        self.results_table.setColumnWidth(19, 80)  # Confidence
        
        # Apply dark theme styling
        self.apply_dark_theme()
        
        # Enable sorting
        self.results_table.setSortingEnabled(True)
        
        # Enable context menu
        self.results_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.results_table.customContextMenuRequested.connect(self.show_context_menu)
        
        results_layout.addLayout(table_controls)
        results_layout.addWidget(self.results_table)
        results_group.setLayout(results_layout)
        
        # Console for logging
        console_group = QGroupBox("Logs")
        console_layout = QVBoxLayout()
        self.console = QTextEdit()
        self.console.setMaximumHeight(150)
        console_layout.addWidget(self.console)
        console_group.setLayout(console_layout)
        
        # Add all components to main layout
        layout.addWidget(file_group)
        layout.addLayout(control_layout)
        layout.addWidget(filter_group)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.status_label)
        layout.addWidget(results_group)
        layout.addWidget(console_group)
        
        self.setLayout(layout)
    
    def browse_file(self):
        """Browse for HTML file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select HTML file", "", "HTML files (*.html *.htm)"
        )
        if file_path:
            self.file_path_edit.setText(file_path)
            self.log_message(f"📁 Selected file: {file_path}")
    
    def download_and_crawl(self):
        """Download HTML from URL and start crawling"""
        url = self.url_edit.text().strip()
        if not url:
            QMessageBox.warning(self, "Warning", "Please enter a URL first!")
            return
        
        if not url.startswith('http'):
            url = 'https://' + url
        
        self.log_message(f"🌐 Downloading HTML from: {url}")
        
        try:
            # Download the HTML
            response = self.session.get(url, timeout=30, verify=False)
            response.raise_for_status()
            
            # Save to temporary file
            temp_file = "downloaded_page.html"
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            self.log_message(f"✅ Downloaded and saved to: {temp_file}")
            self.file_path_edit.setText(temp_file)
            
            # Start crawling
            self.start_crawl()
            
        except Exception as e:
            self.log_error(f"❌ Failed to download from URL: {e}")
            QMessageBox.critical(self, "Error", f"Failed to download from URL: {e}")
    
    def start_crawl(self):
        """Start crawling process"""
        # Check if we have a file path or URL
        file_path = self.file_path_edit.text().strip()
        url = self.url_edit.text().strip()
        
        if not file_path and not url:
            QMessageBox.warning(self, "Warning", "Please select an HTML file or enter a URL first!")
            return
        
        self.is_crawling = True
        self.stop_requested = False
        self.is_paused = False
        self.pause_requested = False
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.pause_btn.setEnabled(True)
        self.pause_btn.setText("Pause")
        
        # Reset statistics (unless resuming)
        if not self.current_crawl_state:
            self.total_processed = 0
            self.successful_extractions = 0
            self.failed_extractions = 0
            self.thumbnail_failures = 0
            self.request_failures = 0
            self.parsing_failures = 0
            self.extracted_data = []
            self.processed_urls.clear()
        else:
            # Load previous state when resuming
            self.load_crawl_state()
        
        # Start comprehensive logging
        self.start_crawl_logging()
        
        # Start crawling in background
        if file_path:
            self.crawl_thread = threading.Thread(
                target=self.crawl_html_file, 
                args=(file_path, None)
            )
        else:
            # Use URL directly
            self.crawl_thread = threading.Thread(
                target=self.crawl_from_url, 
                args=(url,)
            )
        
        # If resuming from pause, log the state
        if self.current_crawl_state:
            state = self.current_crawl_state
            self.log_message(f"🔄 Resuming from: {state.get('current_url', 'Unknown')}")
            self.log_message(f"📊 Progress: {state.get('current_index', 0)}/{state.get('total_links', 0)} links")
            self.log_message(f"📈 Data extracted: {state.get('extracted_data', 0)} items")
        
        self.crawl_thread.daemon = True
        self.crawl_thread.start()
    
    def stop_crawl(self):
        """Stop crawling process"""
        self.stop_requested = True
        self.is_crawling = False
        self.is_paused = False
        self.pause_requested = False
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.pause_btn.setEnabled(False)
        self.pause_btn.setText("Pause")
        self.log_message("🛑 Crawling stopped by user")
    
    def toggle_pause(self):
        """Toggle pause/resume crawling"""
        if self.is_paused:
            # Resume crawling
            self.is_paused = False
            self.pause_requested = False
            self.pause_btn.setText("Pause")
            self.log_message("▶️ Crawling resumed")
        else:
            # Pause crawling
            self.is_paused = True
            self.pause_requested = True
            self.pause_btn.setText("Resume")
            self.log_message("⏸️ Crawling paused")
    
    def check_pause(self):
        """Check if crawling should be paused"""
        while self.is_paused and not self.stop_requested:
            time.sleep(0.1)  # Small delay to prevent high CPU usage
        return self.stop_requested
    
    def save_crawl_state(self, url, index, total):
        """Save current crawl state for resume functionality"""
        self.current_crawl_state = {
            'current_url': url,
            'current_index': index,
            'total_links': total,
            'processed_urls': list(self.processed_urls),
            'extracted_data': len(self.extracted_data),
            'successful_extractions': self.successful_extractions,
            'failed_extractions': self.failed_extractions,
            'total_processed': self.total_processed
        }
    
    def load_crawl_state(self):
        """Load saved crawl state"""
        if self.current_crawl_state:
            # Restore processed URLs
            self.processed_urls = set(self.current_crawl_state.get('processed_urls', []))
            
            # Restore statistics
            self.successful_extractions = self.current_crawl_state.get('successful_extractions', 0)
            self.failed_extractions = self.current_crawl_state.get('failed_extractions', 0)
            self.total_processed = self.current_crawl_state.get('total_processed', 0)
            
            return True
        return False
    
    def clear_crawl_state(self):
        """Clear saved crawl state"""
        self.current_crawl_state = {}
        self.log_message("🗑️ Crawl state cleared")
    
    def crawl_from_url(self, url):
        """Crawl directly from URL"""
        try:
            self.log_message("🚀 Starting Earth Engine data extraction from URL...")
            self.log_message(f"🌐 URL: {url}")
            
            # Download the HTML
            try:
                response = self.session.get(url, timeout=30, verify=False)
                response.raise_for_status()
                content = response.text
                self.log_message(f"📄 HTML downloaded: {len(content)} characters")
            except Exception as e:
                self.log_error(f"❌ Failed to download from URL: {e}")
                return
            
            # Parse HTML
            try:
                soup = BeautifulSoup(content, 'html.parser')
                self.log_message("✅ HTML parsed successfully")
            except Exception as e:
                self.log_error(f"❌ Failed to parse HTML: {e}")
                return
            
            # Extract and process links
            self.process_links_from_soup(soup, url)
            
        except Exception as e:
            self.log_error(f"❌ Crawling from URL failed: {e}")
        finally:
            self.crawl_finished()
    
    def crawl_html_file(self, html_file, url=None):
        """Main crawling function"""
        try:
            self.log_message("🚀 Starting Earth Engine data extraction...")
            self.log_message(f"📁 HTML file: {html_file}")
            
            # Validate file
            if not os.path.exists(html_file):
                self.log_error(f"❌ File not found: {html_file}")
                return
            
            # Read HTML file
            try:
                with open(html_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.log_message(f"📄 HTML loaded: {len(content)} characters")
            except Exception as e:
                self.log_error(f"❌ Failed to read HTML: {e}")
                return
            
            # Parse HTML
            try:
                soup = BeautifulSoup(content, 'html.parser')
                self.log_message("✅ HTML parsed successfully")
            except Exception as e:
                self.log_error(f"❌ Failed to parse HTML: {e}")
                return
            
            # Extract and process links
            self.process_links_from_soup(soup, url or html_file)
            
        except Exception as e:
            self.log_error(f"❌ Crawling failed: {e}")
        finally:
            self.crawl_finished()
    
    def process_links_from_soup(self, soup, base_url):
        """Process links from parsed HTML soup"""
        # Extract links
        links = []
        for link in soup.find_all('a', href=True):
            url = link.get('href')
            if url and url.startswith('http'):
                if '/datasets/catalog/' in url and not url.endswith('/catalog'):
                    links.append(url)
        
        self.log_message(f"🔗 Found {len(links)} catalog links")
        
        # Process all links (no limiting)
        self.log_message(f"📊 Processing ALL {len(links)} links")
        
        if not links:
            self.log_message("⚠️ No valid links found")
            return
        
        # Process links
        for i, url in enumerate(links):
            if self.stop_requested:
                break
            
            # Check for pause
            if self.check_pause():
                break
            
            # Store current state for resume
            self.save_crawl_state(url, i, len(links))
            
            self.log_message(f"🔍 Processing {i+1}/{len(links)}: {url}")
            success = self.process_link(url, i+1, len(links))
            
            if success:
                time.sleep(self.config['performance']['request_delay'])
            else:
                time.sleep(5)  # Longer delay on failure
        
        self.log_message("✅ Crawling completed!")
        self.show_summary()
    
    def process_link(self, url, current, total):
        """Process individual link with enhanced error handling"""
        try:
            # Check if URL already processed (unless overwrite is enabled)
            if url in self.processed_urls and not self.overwrite_checkbox.isChecked():
                self.log_message(f"⏭️ Skipping already processed: {url}")
                return True
            
            self.total_processed += 1
            self.progress_updated.emit(current, total)
            self.status_updated.emit(f"Processing: {current}/{total}")
            
            # Enhanced request with retry mechanism
            max_retries = 3
            retry_delay = 2
            
            for attempt in range(max_retries):
                try:
                    # Enhanced headers for better compatibility
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1',
                        'Cache-Control': 'no-cache',
                        'Pragma': 'no-cache'
                    }
                    
                    response = self.session.get(
                        url, 
                        timeout=self.config['performance']['timeout'],
                        verify=False,
                        headers=headers,
                        allow_redirects=True
                    )
                    response.raise_for_status()
                    
                    # Check if response is HTML
                    content_type = response.headers.get('content-type', '').lower()
                    if not content_type.startswith('text/html'):
                        self.log_error(f"❌ URL does not return HTML: {content_type} - {url}")
                        return False
                    
                    break  # Success, exit retry loop
                    
                except requests.exceptions.Timeout:
                    self.log_error(f"⏰ Timeout (attempt {attempt + 1}/{max_retries}): {url}")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        retry_delay *= 2
                    else:
                        self.request_failures += 1
                        return False
                        
                except requests.exceptions.ConnectionError:
                    self.log_error(f"🌐 Connection error (attempt {attempt + 1}/{max_retries}): {url}")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        retry_delay *= 2
                    else:
                        self.request_failures += 1
                        return False
                        
                except requests.exceptions.HTTPError as e:
                    self.log_error(f"📡 HTTP error {e.response.status_code} (attempt {attempt + 1}/{max_retries}): {url}")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        retry_delay *= 2
                    else:
                        self.request_failures += 1
                        return False
                        
                except Exception as e:
                    self.log_error(f"❌ Request failed (attempt {attempt + 1}/{max_retries}): {e} - {url}")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        retry_delay *= 2
                    else:
                        self.request_failures += 1
                        return False
            
            # Parse response
            try:
                soup = BeautifulSoup(response.content, 'html.parser')
            except Exception as e:
                self.log_error(f"❌ Failed to parse response: {e}")
                self.parsing_failures += 1
                return False
            
            # Extract data
            result = self.extract_comprehensive_data(soup, url)
            
            # Check confidence
            min_confidence = self.config['processing']['min_confidence']
            if result.get('confidence_score', 0) >= min_confidence:
                self.extracted_data.append(result)
                self.successful_extractions += 1
                self.processed_urls.add(url)
                self.data_updated.emit()
                
                self.log_updated.emit(
                    f"✅ {result.get('title', 'Unknown')[:50]}... "
                    f"(Confidence: {result.get('confidence_score', 0):.2f})"
                )
            else:
                self.failed_extractions += 1
                self.log_updated.emit(
                    f"⚠️ Low confidence: {result.get('title', 'Unknown')[:50]}... "
                    f"(Confidence: {result.get('confidence_score', 0):.2f})"
                )
            
            return True
            
        except Exception as e:
            self.failed_extractions += 1
            self.error_updated.emit(f"❌ Failed to process {url}: {e}")
            return False
    
    def extract_comprehensive_data(self, soup, url):
        """Extract ALL information from the page for later parsing"""
        result = {
            'url': url,
            'title': '',
            'description': '',
            'raw_html': str(soup),  # Complete HTML
            'raw_text': soup.get_text(),  # Complete text
            'all_links': [],  # All links on page
            'all_images': [],  # All images on page
            'all_tables': [],  # All tables on page
            'all_metadata': {},  # All meta tags
            'all_scripts': [],  # All script content
            'all_styles': [],  # All style content
            'all_forms': [],  # All form data
            'satellite_info': {},
            'resolution': '',
            'bands': [],
            'temporal_coverage': '',
            'spatial_coverage': '',
            'processing_level': '',
            'provider': '',
            'data_type': '',
            'license': '',
            'file_format': '',
            'cloud_cover': '',
            'thumbnail_url': '',
            'thumbnail_data': None,
            'confidence_score': 0.0,
            'timestamp': datetime.now().isoformat()
        }
        
        # Smart text extraction - prioritize meaningful content
        content_parts = []
        
        # Extract title and clean it up
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text().strip()
            # Clean up Google Developer parts
            title = re.sub(r'Google\s+for\s+Developers?', '', title, flags=re.IGNORECASE)
            title = re.sub(r'Google\s+Developers?', '', title, flags=re.IGNORECASE)
            title = re.sub(r'Developers?\.google\.com', '', title, flags=re.IGNORECASE)
            title = re.sub(r'\|.*$', '', title)  # Remove everything after |
            title = re.sub(r'-.*$', '', title)   # Remove everything after -
            title = title.strip(' -|')  # Remove leading/trailing spaces, dashes, pipes
            result['title'] = title
        
        # Capture ALL raw data from the page
        # All links
        for link in soup.find_all('a', href=True):
            result['all_links'].append({
                'text': link.get_text().strip(),
                'href': link.get('href'),
                'title': link.get('title', ''),
                'class': link.get('class', [])
            })
        
        # All images
        for img in soup.find_all('img'):
            result['all_images'].append({
                'src': img.get('src', ''),
                'alt': img.get('alt', ''),
                'title': img.get('title', ''),
                'class': img.get('class', [])
            })
        
        # All tables
        for table in soup.find_all('table'):
            table_data = []
            for row in table.find_all('tr'):
                row_data = []
                for cell in row.find_all(['td', 'th']):
                    row_data.append(cell.get_text().strip())
                if row_data:
                    table_data.append(row_data)
            result['all_tables'].append(table_data)
        
        # All metadata
        for meta in soup.find_all('meta'):
            name = meta.get('name', meta.get('property', ''))
            content = meta.get('content', '')
            if name and content:
                result['all_metadata'][name] = content
        
        # All scripts
        for script in soup.find_all('script'):
            result['all_scripts'].append({
                'src': script.get('src', ''),
                'type': script.get('type', ''),
                'content': script.get_text()
            })
        
        # All styles
        for style in soup.find_all('style'):
            result['all_styles'].append(style.get_text())
        
        # All forms
        for form in soup.find_all('form'):
            form_data = {
                'action': form.get('action', ''),
                'method': form.get('method', ''),
                'inputs': []
            }
            for input_tag in form.find_all('input'):
                form_data['inputs'].append({
                    'name': input_tag.get('name', ''),
                    'type': input_tag.get('type', ''),
                    'value': input_tag.get('value', '')
                })
            result['all_forms'].append(form_data)
        
        # Get basic description (raw text from main content areas)
        main_content = []
        for tag in ['p', 'div', 'span', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            for element in soup.find_all(tag):
                text = element.get_text().strip()
                if len(text) > 20:
                    main_content.append(text)
        
        result['description'] = ' '.join(main_content[:10])  # First 10 content blocks
        
        # Extract basic thumbnail info
        thumbnail_url = self.extract_thumbnail(soup, url)
        if thumbnail_url:
            result['thumbnail_url'] = thumbnail_url
        
        # Extract basic GEE code snippet
        gee_code_snippet = self.extract_gee_code_snippet(soup, url)
        if gee_code_snippet:
            result['gee_code_snippet'] = gee_code_snippet
            result['dataset_id'] = self.extract_dataset_id_from_url(url)
        
        # Set basic confidence score
        result['confidence_score'] = 1.0  # Default confidence for raw data
        
        return result
        
        for pattern in license_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                result['license'] = ', '.join(set(matches))
                break
        
        # Extract file format
        format_patterns = [
            r'\b(GeoTIFF|TIFF|JPEG|PNG|HDF|NetCDF|Shapefile|GeoJSON)\b',
            r'\b(Geographic\s+Tagged\s+Image\s+File\s+Format)\b',
            r'\b(Hierarchical\s+Data\s+Format)\b',
            r'\b(Network\s+Common\s+Data\s+Form)\b',
        ]
        
        for pattern in format_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                result['file_format'] = ', '.join(set(matches))
                break
        
        # Extract cloud cover information
        cloud_patterns = [
            r'\b(\d+(?:\.\d+)?)\s*%\s*cloud\s*cover\b',
            r'\bcloud\s*cover[:\s]*(\d+(?:\.\d+)?)\s*%\b',
            r'\b(\d+(?:\.\d+)?)\s*%\s*cloud\b',
            r'\bcloud\s*free\b',
            r'\bno\s*cloud\s*cover\b',
        ]
        
        for pattern in cloud_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                if 'cloud free' in content.lower() or 'no cloud cover' in content.lower():
                    result['cloud_cover'] = '0%'
                else:
                    result['cloud_cover'] = ', '.join(set(matches)) + '%'
                break
        
        # Calculate confidence score
        result['confidence_score'] = self.calculate_confidence(result)
        
        return result
    
    def extract_comprehensive_description(self, soup):
        """Extract clean, comprehensive description from multiple sources"""
        description = ""
        
        # Strategy 1: Look for specific Earth Engine dataset descriptions
        ee_selectors = [
            '[class*="dataset-description"]',
            '[class*="product-description"]',
            '[class*="data-description"]',
            '[class*="earth-engine"]',
            '[class*="catalog-description"]',
            '[class*="dataset-info"]',
            '[class*="product-info"]',
            '[class*="description"]',
            '[class*="content"]',
            '[class*="summary"]',
            '[class*="overview"]',
            '[class*="details"]',
            '[class*="specification"]',
            '[class*="documentation"]',
            '[class*="information"]'
        ]
        
        # Try to get the most complete description first
        best_description = ""
        for selector in ee_selectors:
            elements = soup.select(selector)
            for element in elements:
                text = self.clean_text_content(element.get_text().strip())
                if len(text) > 200 and self.is_earth_engine_description(text):
                    # Always prefer the longest, most complete description
                    if len(text) > len(best_description):
                        best_description = text
                
            if best_description:
                description = best_description
                break
        
        # Strategy 2: Look for main content areas with comprehensive filtering
        if not description:
            content_selectors = [
                'main', 'article', 'section',
                '[class*="description"]', '[class*="content"]', '[class*="summary"]',
                '[class*="dataset"]', '[class*="catalog"]', '[class*="info"]',
                '[class*="overview"]', '[class*="details"]', '[class*="specification"]',
                '[class*="documentation"]', '[class*="information"]',
                '.content', '.main-content', '.description', '.summary',
                '.dataset-info', '.catalog-info', '.product-info',
                'div[role="main"]', 'div[role="contentinfo"]',
                'div[class*="main"]', 'div[class*="body"]',
                'div[class*="content"]', 'div[class*="text"]'
            ]
            
            # Try to get the most complete content
            best_description = ""
            for selector in content_selectors:
                elements = soup.select(selector)
                for element in elements:
                    text = self.clean_text_content(element.get_text().strip())
                    if len(text) > 300 and self.is_likely_description(text):
                        # Always prefer the longest, most complete description
                        if len(text) > len(best_description):
                            best_description = text
                
                if best_description:
                    description = best_description
                    break
        
        # Strategy 2: If no substantial content found, try meta descriptions
        if not description:
            # Try meta description first
            desc_tag = soup.find('meta', attrs={'name': 'description'})
            if desc_tag:
                description = desc_tag.get('content', '')
            
            # Try Open Graph description
            og_desc_tag = soup.find('meta', attrs={'property': 'og:description'})
            if og_desc_tag and not description:
                description = og_desc_tag.get('content', '')
        
        # Strategy 3: Extract from paragraphs if still no description
        if not description:
            paragraphs = soup.find_all('p')
            paragraph_texts = []
            
            for p in paragraphs:
                text = p.get_text().strip()
                if len(text) > 100:  # Increased minimum length for better quality
                    if self.is_likely_description(text):
                        paragraph_texts.append(text)
            
            # Combine multiple paragraphs if they seem related
            if paragraph_texts:
                description = ' '.join(paragraph_texts)
        
        # Strategy 4: Look for content in divs and spans
        if not description:
            content_elements = soup.find_all(['div', 'span'])
            best_content = ""
            for element in content_elements:
                text = element.get_text().strip()
                if len(text) > 300:  # Increased minimum length for better quality
                    if self.is_likely_description(text):
                        # Always prefer the longest content
                        if len(text) > len(best_content):
                            best_content = text
            
            if best_content:
                description = best_content
        
        # Strategy 5: Extract from list items (often contain detailed descriptions)
        if not description:
            list_items = soup.find_all(['li', 'dd', 'dt'])
            item_texts = []
            
            for item in list_items:
                text = item.get_text().strip()
                if len(text) > 80:  # Increased minimum length for better quality
                    if self.is_likely_description(text):
                        item_texts.append(text)
            
            if item_texts:
                description = ' '.join(item_texts)
        
        # Clean up the description
        if description:
            description = self.clean_description(description)
            return {
                'full': description
            }
        
        return {'full': ''}
    

    
    def clean_text_content(self, text):
        """Clean and filter text content to remove junk and noise"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        # Remove common junk patterns
        junk_patterns = [
            r'cookie|privacy|terms|conditions|legal|disclaimer',
            r'menu|navigation|header|footer|sidebar',
            r'search|filter|sort|browse',
            r'copyright|©|all rights reserved',
            r'skip to|jump to|go to',
            r'loading|please wait|processing',
            r'javascript|script|function',
            r'css|style|stylesheet',
            r'xmlns|xml|html|doctype',
            r'charset|encoding|utf-8',
            r'viewport|meta|link',
            r'button|click|submit|form',
            r'login|sign|register|account',
            r'help|support|contact|feedback',
            r'news|blog|article|post',
            r'social|share|like|follow',
            r'advertisement|ad|sponsored',
            r'analytics|tracking|pixel',
            r'iframe|embed|object',
            r'noscript|comment|<!--.*?-->',
            r'close|×|✕|✖',
            r'expand|collapse|show|hide',
            r'previous|next|back|forward',
            r'home|about|contact|help',
            r'breadcrumb|bread-crumb',
            r'tab|accordion|collapse',
            r'modal|dialog|popup',
            r'tooltip|tool-tip',
            r'notification|alert|message',
            r'progress|loading|spinner',
            r'pagination|page|pages',
            r'rating|star|review',
            r'comment|reply|response',
            r'author|writer|contributor',
            r'date|time|timestamp',
            r'category|tag|label',
            r'related|similar|recommended',
            r'popular|trending|featured',
            r'new|latest|recent',
            r'hot|trending|viral'
        ]
        
        # Remove lines containing junk patterns
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if line contains junk patterns
            is_junk = False
            for pattern in junk_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    is_junk = True
                    break
            
            # Additional checks for junk content
            if not is_junk:
                # Check for very short lines that are likely navigation
                if len(line) < 20:
                    continue
                # Check for lines that are mostly punctuation or numbers
                if re.match(r'^[\d\s\-_\.]+$', line):
                    continue
                # Check for lines that are just repeated characters
                if len(set(line)) < 3:
                    continue
                
                cleaned_lines.append(line)
        
        # Rejoin lines and clean up
        cleaned_text = ' '.join(cleaned_lines)
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
        
        # Additional cleaning for better content
        # Remove very short paragraphs that are likely navigation
        paragraphs = cleaned_text.split('. ')
        good_paragraphs = []
        for para in paragraphs:
            para = para.strip()
            if len(para) > 30:  # Reduced minimum length to preserve more content
                # Additional quality checks
                if not re.match(r'^[\d\s\-_\.]+$', para):  # Not just numbers/punctuation
                    if len(set(para)) > 5:  # Reduced character variety requirement
                        good_paragraphs.append(para)
        
        cleaned_text = '. '.join(good_paragraphs)
        
        # Final cleanup
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
        cleaned_text = cleaned_text.strip()
        
        return cleaned_text
    
    def is_earth_engine_description(self, text):
        """Check if text is specifically about Earth Engine datasets"""
        if not text or len(text) < 50:
            return False
        
        # Earth Engine specific indicators
        ee_indicators = [
            'earth engine', 'google earth engine', 'gee',
            'dataset', 'satellite', 'remote sensing',
            'landsat', 'sentinel', 'modis', 'aster',
            'resolution', 'coverage', 'temporal',
            'spatial', 'bands', 'processing',
            'imagery', 'data', 'collection',
            'catalog', 'product', 'mission'
        ]
        
        text_lower = text.lower()
        indicator_count = sum(1 for indicator in ee_indicators if indicator in text_lower)
        
        # Must have at least 3 Earth Engine indicators
        return indicator_count >= 3
    
    def is_likely_description(self, text):
        """Check if text looks like a real description rather than navigation or metadata"""
        # Skip if too short (NO UPPER LIMIT)
        if len(text) < 50:
            return False
        
        # Skip if it's mostly navigation or metadata
        navigation_indicators = [
            'menu', 'navigation', 'header', 'footer', 'sidebar',
            'copyright', 'privacy', 'terms', 'contact', 'about',
            'home', 'back', 'next', 'previous', 'search'
        ]
        
        text_lower = text.lower()
        for indicator in navigation_indicators:
            if indicator in text_lower and len(text) < 200:
                return False
        
        # Look for description indicators
        description_indicators = [
            'dataset', 'satellite', 'resolution', 'coverage', 'temporal',
            'spatial', 'bands', 'processing', 'provider', 'license',
            'description', 'summary', 'overview', 'details', 'information',
            'data', 'imagery', 'sensor', 'mission', 'product'
        ]
        
        indicator_count = 0
        for indicator in description_indicators:
            if indicator in text_lower:
                indicator_count += 1
        
        # If we find multiple description indicators, it's likely a real description
        return indicator_count >= 2
    
    def clean_description(self, description):
        """Clean and format the description"""
        if not description:
            return ""
        
        # Remove excessive whitespace
        import re
        description = re.sub(r'\s+', ' ', description)
        description = description.strip()
        
        # Remove common unwanted prefixes/suffixes
        unwanted_prefixes = [
            'description:', 'summary:', 'overview:', 'details:',
            'information:', 'data:', 'dataset:', 'product:'
        ]
        
        for prefix in unwanted_prefixes:
            if description.lower().startswith(prefix.lower()):
                description = description[len(prefix):].strip()
        
        # Handle incomplete endings like "Please see ..." or "See ..."
        incomplete_patterns = [
            r'please see\s*\.{3,}.*$',
            r'see\s*\.{3,}.*$',
            r'\.{3,}.*$',
            r'\.{2,}\s*$',
            r'…\s*$',
            r'\.\.\.\s*$',
            r'please see\s*….*$',
            r'see\s*….*$',
            r'more details are available.*$',
            r'documentation\s*\.\s*\.\s*$',
            r'documentation\s*\.\s*$',
            r'\.\s*\.\s*$',
            r'\s*\.\s*\.\s*$'
        ]
        
        for pattern in incomplete_patterns:
            description = re.sub(pattern, '', description, flags=re.IGNORECASE)
        
        # Ensure proper sentence structure
        if description and not description.endswith(('.', '!', '?')):
            description += '.'
        
        return description
    
    def extract_from_description(self, result, description):
        """Extract ALL missing parameters from the complete description"""
        # Use full description for parameter extraction
        full_description = result.get('description_full', description)
        if not full_description:
            return
        
        # Extract resolution from description (if not already found)
        if not result.get('resolution'):
            resolution_patterns = [
                r'(\d+(?:\.\d+)?)\s*(m|meters?|km|kilometers?)\s*resolution',
                r'resolution\s*of\s*(\d+(?:\.\d+)?)\s*(m|meters?|km|kilometers?)',
                r'(\d+(?:\.\d+)?)\s*(m|meters?|km|kilometers?)\s*pixel',
                r'(\d+(?:\.\d+)?)\s*(m|meters?|km|kilometers?)\s*spatial',
                r'(\d+(?:\.\d+)?)\s*(m|meters?|km|kilometers?)',
                r'(\d+(?:\.\d+)?)\s*(m|meters?|km|kilometers?)\s*ground\s*sample',
                r'(\d+(?:\.\d+)?)\s*(m|meters?|km|kilometers?)\s*nadir',
                r'(\d+(?:\.\d+)?)\s*(m|meters?|km|kilometers?)\s*at\s*nadir',
            ]
            
            for pattern in resolution_patterns:
                matches = re.findall(pattern, full_description, re.IGNORECASE)
                if matches:
                    result['resolution'] = ', '.join([f"{value} {unit}" for value, unit in matches])
                    break
        
        # Extract temporal information from description (if not already found)
        if not result.get('temporal_coverage'):
            temporal_patterns = [
                r'(\d{4})\s*[-–]\s*(present|\d{4})',
                r'from\s*(\d{4})\s*to\s*(present|\d{4})',
                r'coverage\s*(\d{4})\s*[-–]\s*(present|\d{4})',
                r'(\d{4})\s*through\s*(present|\d{4})',
                r'(\d{4})\s*until\s*(present|\d{4})',
                r'(\d{4})\s*present\b',
                r'(\d{4})\s*ongoing\b',
                r'(\d{4})\s*to\s*present\b',
                r'(\d{4})\s*-\s*present\b',
                r'(\d{4})\s*to\s*(\d{4})',
                r'(\d{4})\s*through\s*(\d{4})',
                r'(\d{4})\s*until\s*(\d{4})',
                r'(\d{4})\s*[-–]\s*(\d{4})',
                r'(\d{4})\s*to\s*(\d{4})',
                r'(\d{4})\s*through\s*(\d{4})',
                r'(\d{4})\s*until\s*(\d{4})',
            ]
            
            all_matches = []
            for pattern in temporal_patterns:
                matches = re.findall(pattern, full_description, re.IGNORECASE)
                all_matches.extend(matches)
            
            if all_matches:
                # Remove duplicates and format properly
                unique_matches = []
                for match in all_matches:
                    if isinstance(match, tuple):
                        start, end = match
                        formatted = f"{start} to {end}"
                    else:
                        formatted = f"{match} to Present"
                    
                    if formatted not in unique_matches:
                        unique_matches.append(formatted)
                
                result['temporal_coverage'] = ', '.join(unique_matches)
        
        # Extract satellite mentions from description (if not already found)
        if not result.get('satellite_info'):
            satellite_patterns = [
                r'\b(ALOS|Advanced\s+Land\s+Observing\s+Satellite)\b',
                r'\b(Landsat\s*\d+[A-Z]?)\b',
                r'\b(Sentinel\s*[12AB])\b',
                r'\b(MODIS|Terra|Aqua)\b',
                r'\b(ASTER)\b',
                r'\b(SPOT\s*\d+)\b',
                r'\b(Pleiades)\b',
                r'\b(QuickBird)\b',
                r'\b(WorldView\s*[1234])\b',
                r'\b(Planet|PlanetScope|RapidEye)\b',
                r'\b(GFS|Global\s+Forecast\s+System)\b',
                r'\b(ECMWF|European\s+Centre\s+for\s+Medium-Range\s+Weather\s+Forecasts)\b',
                r'\b(ERS\s*[12])\b',
                r'\b(Envisat)\b',
                r'\b(Radarsat\s*[12])\b',
                r'\b(IKONOS)\b',
                r'\b(GeoEye\s*[12])\b',
                r'\b(DigitalGlobe)\b',
                r'\b(JAXA|Japan\s+Aerospace\s+Exploration\s+Agency)\b',
            ]
            
            satellites_found = []
            for pattern in satellite_patterns:
                matches = re.findall(pattern, full_description, re.IGNORECASE)
                satellites_found.extend(matches)
            
            if satellites_found:
                result['satellite_info'] = {'detected': list(set(satellites_found))}
        
        # Extract bands from description (if not already found)
        if not result.get('bands'):
            band_patterns = [
                r'\b(B\d+|Band\s*\d+)\b',
                r'\b([RGB]|Red|Green|Blue|NIR|SWIR|TIR)\b',
                r'\b(\d+)\s*bands?\b',
                r'\b(visible|infrared|thermal|microwave)\s*bands?\b',
                r'\b(panchromatic|multispectral|hyperspectral)\b',
            ]
            
            bands_found = []
            for pattern in band_patterns:
                matches = re.findall(pattern, full_description, re.IGNORECASE)
                bands_found.extend(matches)
            
            if bands_found:
                result['bands'] = list(set(bands_found))
        
        # Extract processing level from description (if not already found)
        if not result.get('processing_level'):
            processing_patterns = [
                r'level\s*(\d+[A-Z]?)',
                r'processing\s*level\s*(\d+[A-Z]?)',
                r'tier\s*(\d+)',
                r'(\d+[A-Z]?)\s*processing',
                r'processing\s*(\d+[A-Z]?)',
            ]
            
            for pattern in processing_patterns:
                matches = re.findall(pattern, full_description, re.IGNORECASE)
                if matches:
                    result['processing_level'] = ', '.join(matches)
                    break
        
        # Extract provider from description (if not already found)
        if not result.get('provider'):
            provider_patterns = [
                r'\b(USGS|NASA|ESA|NOAA|USDA|EPA|NCEP|NWS)\b',
                r'\b(United\s+States\s+Geological\s+Survey)\b',
                r'\b(National\s+Aeronautics\s+and\s+Space\s+Administration)\b',
                r'\b(European\s+Space\s+Agency)\b',
                r'\b(National\s+Oceanic\s+and\s+Atmospheric\s+Administration)\b',
                r'\b(United\s+States\s+Department\s+of\s+Agriculture)\b',
                r'\b(Environmental\s+Protection\s+Agency)\b',
                r'\b(National\s+Centers?\s+for\s+Environmental\s+Prediction)\b',
                r'\b(National\s+Weather\s+Service)\b',
                r'\b(European\s+Centre\s+for\s+Medium-Range\s+Weather\s+Forecasts)\b',
                r'\b(European\s+Organization\s+for\s+the\s+Exploitation\s+of\s+Meteorological\s+Satellites)\b',
            ]
            
            for pattern in provider_patterns:
                matches = re.findall(pattern, full_description, re.IGNORECASE)
                if matches:
                    result['provider'] = ', '.join(set(matches))
                    break
        
        # Extract data type from description (if not already found)
        if not result.get('data_type'):
            data_type_patterns = [
                r'\b(optical|radar|thermal|multispectral|hyperspectral)\b',
                r'\b(satellite|aerial|drone|UAV)\s+imagery\b',
                r'\b(DEM|DSM|DTM|elevation|terrain)\b',
                r'\b(land\s+cover|land\s+use|vegetation)\b',
                r'\b(atmospheric|climate|weather|forecast|meteorological)\b',
                r'\b(ocean|marine|sea)\s+(surface|temperature|current)\b',
                r'\b(soil|moisture|precipitation|rainfall)\b',
                r'\b(air\s+quality|pollution|aerosol)\b',
                r'\b(urban|built-up|infrastructure)\b',
                r'\b(forest|vegetation|biomass)\b',
                r'\b(water|hydrology|flood)\b',
                r'\b(ice|snow|glacier)\b',
                r'\b(fire|burn|wildfire)\b',
            ]
            
            for pattern in data_type_patterns:
                matches = re.findall(pattern, full_description, re.IGNORECASE)
                if matches:
                    result['data_type'] = ', '.join(set(matches))
                    break
        
        # Extract license from description (if not already found)
        if not result.get('license'):
            license_patterns = [
                r'\b(public\s+domain|open\s+access|free)\b',
                r'\b(CC\s*[A-Z-]+|Creative\s+Commons)\b',
                r'\b(commercial\s+use|non-commercial)\b',
                r'\b(restricted|proprietary|licensed)\b',
                r'\b(open\s+source|open\s+data)\b',
                r'\b(government\s+data|public\s+data)\b',
            ]
            
            for pattern in license_patterns:
                matches = re.findall(pattern, full_description, re.IGNORECASE)
                if matches:
                    result['license'] = ', '.join(set(matches))
                    break
        
        # Extract file format from description (if not already found)
        if not result.get('file_format'):
            format_patterns = [
                r'\b(GeoTIFF|TIFF|JPEG|PNG|HDF|NetCDF|Shapefile|GeoJSON)\b',
                r'\b(Geographic\s+Tagged\s+Image\s+File\s+Format)\b',
                r'\b(Hierarchical\s+Data\s+Format)\b',
                r'\b(Network\s+Common\s+Data\s+Form)\b',
                r'\b(ESRI\s+Shapefile)\b',
                r'\b(GeoPackage|GPKG)\b',
                r'\b(KML|KMZ)\b',
            ]
            
            for pattern in format_patterns:
                matches = re.findall(pattern, full_description, re.IGNORECASE)
                if matches:
                    result['file_format'] = ', '.join(set(matches))
                    break
        
        # Extract cloud cover from description (if not already found)
        if not result.get('cloud_cover'):
            cloud_patterns = [
                r'\b(\d+(?:\.\d+)?)\s*%\s*cloud\s*cover\b',
                r'\bcloud\s*cover[:\s]*(\d+(?:\.\d+)?)\s*%\b',
                r'\b(\d+(?:\.\d+)?)\s*%\s*cloud\b',
                r'\bcloud\s*free\b',
                r'\bno\s*cloud\s*cover\b',
                r'\bcloud\s*cover\s*<=\s*(\d+(?:\.\d+)?)\s*%\b',
                r'\bcloud\s*cover\s*less\s*than\s*(\d+(?:\.\d+)?)\s*%\b',
            ]
            
            for pattern in cloud_patterns:
                matches = re.findall(pattern, full_description, re.IGNORECASE)
                if matches:
                    if 'cloud free' in full_description.lower() or 'no cloud cover' in full_description.lower():
                        result['cloud_cover'] = '0%'
                    else:
                        result['cloud_cover'] = ', '.join(set(matches)) + '%'
                    break
        
        # Extract spatial coverage from description (if not already found)
        if not result.get('spatial_coverage'):
            spatial_patterns = [
                r'\bglobal\s*coverage\b',
                r'\bworldwide\b',
                r'\b(\d+(?:\.\d+)?)\s*(km|miles?)\s*coverage\b',
                r'\b(coverage|extent)\s*of\s*(\d+(?:\.\d+)?)\s*(km|miles?)\b',
                r'\b(continental|national|regional|local)\s*coverage\b',
                r'\b(coverage|extent)\s*:\s*([^.]*?)\b',
            ]
            
            for pattern in spatial_patterns:
                matches = re.findall(pattern, full_description, re.IGNORECASE)
                if matches:
                    result['spatial_coverage'] = ', '.join(set(matches))
                    break
    
    def extract_thumbnail(self, soup, base_url):
        """Extract thumbnail URL"""
        # Look for images in various locations
        img_selectors = [
            'img[src*="thumb"]',
            'img[src*="preview"]',
            'img[src*="image"]',
            '.thumbnail img',
            '.preview img',
            'img[width="200"]',
            'img[width="300"]',
            'img[height="200"]'
        ]
        
        for selector in img_selectors:
            img = soup.select_one(selector)
            if img and img.get('src'):
                src = img.get('src')
                if src.startswith('http'):
                    return src
                elif src.startswith('/'):
                    # Make relative URL absolute
                    parsed = urlparse(base_url)
                    return f"{parsed.scheme}://{parsed.netloc}{src}"
        
        # Fallback to first reasonable image
        for img in soup.find_all('img'):
            src = img.get('src')
            if src and (src.startswith('http') or src.startswith('/')):
                if src.startswith('/'):
                    parsed = urlparse(base_url)
                    return f"{parsed.scheme}://{parsed.netloc}{src}"
                return src
        
        return None
    
    def download_thumbnail(self, thumbnail_url):
        """Download and cache thumbnail with retry mechanism"""
        if not thumbnail_url or thumbnail_url in self.thumbnail_cache:
            return self.thumbnail_cache.get(thumbnail_url)
        
        # Retry mechanism for failed downloads
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                # Add headers to mimic browser request
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                }
                
                response = self.session.get(
                    thumbnail_url, 
                    timeout=15, 
                    verify=False,
                    headers=headers,
                    allow_redirects=True
                )
                response.raise_for_status()
                
                # Check if response is actually an image
                content_type = response.headers.get('content-type', '').lower()
                if not content_type.startswith('image/'):
                    self.log_error(f"❌ URL does not return an image: {content_type}")
                    return None
                
                # Convert to QPixmap
                pixmap = QPixmap()
                if not pixmap.loadFromData(response.content):
                    self.log_error(f"❌ Failed to load image data from {thumbnail_url}")
                    return None
                
                # Scale to larger size for better visibility
                scaled_pixmap = pixmap.scaled(100, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                
                self.thumbnail_cache[thumbnail_url] = scaled_pixmap
                self.log_message(f"✅ Thumbnail downloaded successfully: {thumbnail_url}")
                return scaled_pixmap
                
            except requests.exceptions.Timeout:
                self.log_error(f"⏰ Timeout downloading thumbnail (attempt {attempt + 1}/{max_retries}): {thumbnail_url}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                    
            except requests.exceptions.ConnectionError:
                self.log_error(f"🌐 Connection error downloading thumbnail (attempt {attempt + 1}/{max_retries}): {thumbnail_url}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2
                    
            except requests.exceptions.HTTPError as e:
                self.log_error(f"📡 HTTP error downloading thumbnail (attempt {attempt + 1}/{max_retries}): {e} - {thumbnail_url}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2
                    
            except Exception as e:
                self.log_error(f"❌ Failed to download thumbnail (attempt {attempt + 1}/{max_retries}): {e} - {thumbnail_url}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2
        
        # If all retries failed, log the failure
        self.log_error(f"💥 All retries failed for thumbnail: {thumbnail_url}")
        self.thumbnail_failures += 1
        return None
    
    def calculate_confidence(self, result):
        """Calculate confidence score based on extracted data"""
        score = 0.0
        
        # Base score for having a title
        if result.get('title'):
            score += 0.1
        
        # Score for comprehensive description (weighted heavily)
        if result.get('description'):
            desc_length = len(result['description'])
            if desc_length > 500:  # Very comprehensive description
                score += 0.25
            elif desc_length > 200:  # Good description
                score += 0.2
            elif desc_length > 100:  # Basic description
                score += 0.15
            else:  # Short description
                score += 0.1
        
        # Score for satellite info
        if result.get('satellite_info'):
            score += 0.15
        
        # Score for technical data
        if result.get('resolution') or result.get('bands'):
            score += 0.15
        
        # Score for coverage info
        if result.get('temporal_coverage') or result.get('spatial_coverage'):
            score += 0.1
        
        # Score for processing level
        if result.get('processing_level'):
            score += 0.1
        
        # Score for provider info
        if result.get('provider'):
            score += 0.1
        
        # Score for data type
        if result.get('data_type'):
            score += 0.1
        
        # Score for license info
        if result.get('license'):
            score += 0.05
        
        # Score for file format
        if result.get('file_format'):
            score += 0.05
        
        # Score for cloud cover
        if result.get('cloud_cover'):
            score += 0.05
        
        # Score for thumbnail
        if result.get('thumbnail_url'):
            score += 0.05
        
        # Score for GEE code snippet (CRITICAL for data download)
        if result.get('gee_code_snippet'):
            score += 0.15
        
        # Score for dataset ID
        if result.get('dataset_id'):
            score += 0.1
        
        # Score for additional backend parameters
        if result.get('frequency') or result.get('orbit_altitude') or result.get('swath_width'):
            score += 0.1
        
        # Score for radiometric and correction info
        if result.get('radiometric_resolution') or result.get('atmospheric_corrections'):
            score += 0.05
        
        # Score for quality information
        if result.get('quality_accuracy'):
            score += 0.05
        
        return min(score, 1.0)
    
    def extract_gee_code_snippet(self, soup, url):
        """Extract GEE code snippet from the page (CRITICAL for data download)"""
        # Look for code blocks with GEE code
        code_selectors = [
            'pre code',
            'code',
            'pre',
            '[class*="code"]',
            '[class*="snippet"]',
            '[class*="javascript"]',
            '[class*="ee"]'
        ]
        
        for selector in code_selectors:
            code_elements = soup.select(selector)
            for element in code_elements:
                code_text = element.get_text().strip()
                # Check if this looks like GEE code
                if self.is_gee_code(code_text):
                    return self.clean_gee_code(code_text)
        
        # If no code found, generate a basic snippet based on dataset info
        return self.generate_basic_gee_snippet(url)
    
    def is_gee_code(self, code_text):
        """Check if text looks like GEE code"""
        gee_indicators = [
            'ee.ImageCollection',
            'ee.Image',
            'ee.FeatureCollection',
            'ee.Geometry',
            'Map.addLayer',
            'Export.image',
            'Export.table',
            'filterDate',
            'filterBounds',
            'filter',
            'select',
            'clip',
            'reproject'
        ]
        
        code_lower = code_text.lower()
        indicator_count = sum(1 for indicator in gee_indicators if indicator.lower() in code_lower)
        return indicator_count >= 2  # At least 2 GEE indicators
    
    def clean_gee_code(self, code_text):
        """Clean and format GEE code snippet"""
        # Remove excessive whitespace
        code_text = re.sub(r'\s+', ' ', code_text)
        code_text = code_text.strip()
        
        # Ensure proper formatting
        lines = code_text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if line:
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def generate_basic_gee_snippet(self, url):
        """Generate basic GEE code snippet when none is found"""
        dataset_id = self.extract_dataset_id_from_url(url)
        if not dataset_id:
            return ""
        
        # Generate a comprehensive GEE code snippet
        snippet = f"""// Earth Engine Code Snippet
// Dataset: {dataset_id}
// URL: {url}

// Load the dataset
var dataset = ee.ImageCollection('{dataset_id}');

// Filter by date range (modify as needed)
var startDate = '2020-01-01';
var endDate = '2020-12-31';
var filtered = dataset.filterDate(startDate, endDate);

// Filter by region (modify as needed)
var region = ee.Geometry.Rectangle([-180, -90, 180, 90]); // Global
var filtered = filtered.filterBounds(region);

// Get the first image for visualization
var firstImage = filtered.first();

// Display the image
Map.addLayer(firstImage, {{}}, 'Dataset');

// Export options (uncomment and modify as needed)
/*
Export.image.toDrive({{
  image: firstImage,
  description: '{dataset_id}_export',
  folder: 'EarthEngine_Exports',
  scale: 30,  // Adjust resolution as needed
  region: region,
  maxPixels: 1e13
}});

// Export as table if needed
Export.table.toDrive({{
  collection: filtered,
  description: '{dataset_id}_table_export',
  folder: 'EarthEngine_Exports',
  fileFormat: 'CSV'
}});
*/"""
        
        return snippet
    
    def extract_dataset_id_from_url(self, url):
        """Extract dataset ID from URL"""
        # Common patterns for dataset IDs in URLs
        patterns = [
            r'/catalog/([^/]+)$',
            r'/datasets/([^/]+)$',
            r'/dataset/([^/]+)$',
            r'catalog/([^/]+)',
            r'datasets/([^/]+)',
            r'dataset/([^/]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def extract_additional_parameters(self, result, content):
        """Extract additional backend parameters"""
        additional_data = {}
        
        # Extract frequency information
        frequency = self.extractor.extract_frequency(content)
        if frequency:
            additional_data['frequency'] = ', '.join(frequency)
        
        # Extract orbit information
        orbit_info = self.extractor.extract_orbit_info(content)
        if orbit_info:
            additional_data['orbit_altitude'] = ', '.join(orbit_info)
        
        # Extract swath information
        swath_info = self.extractor.extract_swath_info(content)
        if swath_info:
            additional_data['swath_width'] = ', '.join(swath_info)
        
        # Extract radiometric information
        radiometric = self.extractor.extract_radiometric_info(content)
        if radiometric:
            additional_data['radiometric_resolution'] = ', '.join(radiometric)
        
        # Extract atmospheric corrections
        corrections = self.extractor.extract_atmospheric_corrections(content)
        if corrections:
            additional_data['atmospheric_corrections'] = ', '.join(corrections)
        
        # Extract quality information
        quality = self.extractor.extract_quality_info(content)
        if quality:
            additional_data['quality_accuracy'] = ', '.join(quality)
        
        # Extract file format if not already found
        if not result.get('file_format'):
            format_patterns = [
                r'\b(GeoTIFF|TIFF|JPEG|PNG|HDF|NetCDF|Shapefile|GeoJSON|KML|KMZ)\b',
                r'\b(Geographic\s+Tagged\s+Image\s+File\s+Format)\b',
                r'\b(Joint\s+Photographic\s+Experts\s+Group)\b',
                r'\b(Portable\s+Network\s+Graphics)\b',
                r'\b(Hierarchical\s+Data\s+Format)\b',
                r'\b(Network\s+Common\s+Data\s+Form)\b'
            ]
            
            for pattern in format_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    additional_data['file_format'] = ', '.join(set(matches))
                    break
        
        # Extract cloud cover if not already found
        if not result.get('cloud_cover'):
            cloud_patterns = [
                r'(\d+(?:\.\d+)?)\s*%\s*cloud\s*cover',
                r'cloud\s*cover\s*(\d+(?:\.\d+)?)\s*%',
                r'(\d+(?:\.\d+)?)\s*%\s*cloud',
                r'cloud\s*(\d+(?:\.\d+)?)\s*%'
            ]
            
            for pattern in cloud_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    additional_data['cloud_cover'] = ', '.join([f"{match}%" for match in matches])
                    break
        
        # Extract license information if not already found
        if not result.get('license'):
            license_patterns = [
                r'\b(Public\s+Domain|Creative\s+Commons|GPL|MIT|Apache|BSD)\b',
                r'\b(Open\s+Data|Open\s+Source|Free\s+to\s+use|Open\s+Access)\b',
                r'\b(USGS\s+license|NASA\s+license|ESA\s+license|JAXA\s+license)\b',
                r'\b(commercial\s+use|non-commercial|educational)\b',
                r'\b(free|free\s+to\s+use|open\s+access)\b'
            ]
            
            for pattern in license_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    additional_data['license'] = ', '.join(set(matches))
                    break
        
        return additional_data
    
    def update_progress(self, current, total):
        """Update progress bar"""
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
    
    def update_status(self, status):
        """Update status label"""
        if self.is_paused:
            self.status_label.setText(f"⏸️ PAUSED - {status}")
            self.status_label.setStyleSheet("font-weight: bold; color: #ffa500;")  # Orange for paused
        else:
            self.status_label.setText(status)
            self.status_label.setStyleSheet("font-weight: bold; color: #007acc;")  # Blue for normal
    
    def update_results_table(self):
        """Update results table with all extracted data"""
        self.results_table.setRowCount(len(self.extracted_data))
        
        for row, data in enumerate(self.extracted_data):
            # Thumbnail
            if data.get('thumbnail_data'):
                label = QLabel()
                label.setPixmap(data['thumbnail_data'])
                label.setAlignment(Qt.AlignCenter)
                self.results_table.setCellWidget(row, 0, label)
            else:
                self.results_table.setItem(row, 0, QTableWidgetItem("❌"))
            
            # Title (cleaned)
            self.results_table.setItem(row, 1, QTableWidgetItem(data.get('title', 'Unknown')))
            
            # Description (summary for table display)
            # Get description data
            description = data.get('description', '')
            
            # Use complete description in table
            description_item = QTableWidgetItem(description)
            if len(description) > 500:  # Only show tooltip for very long descriptions
                description_item.setToolTip(f"Complete Description:\n{description}")
            self.results_table.setItem(row, 2, description_item)
            
            # Satellite (with better categorization)
            satellite_text = ""
            if data.get('satellite_info'):
                # Group satellites by type for better display
                satellite_groups = {}
                for sat_type, satellites in data['satellite_info'].items():
                    # Clean up satellite type names
                    clean_type = sat_type.replace('_', ' ').title()
                    if clean_type not in satellite_groups:
                        satellite_groups[clean_type] = []
                    satellite_groups[clean_type].extend(satellites)
                
                # Create formatted satellite text
                for sat_type, satellites in satellite_groups.items():
                    unique_sats = list(set(satellites))  # Remove duplicates
                    satellite_text += f"{sat_type}: {', '.join(unique_sats)}\n"
            
            self.results_table.setItem(row, 3, QTableWidgetItem(satellite_text.strip()))
            
            # Resolution
            self.results_table.setItem(row, 4, QTableWidgetItem(data.get('resolution', '')))
            
            # Bands
            bands_text = ', '.join(data.get('bands', [])) if data.get('bands') else ''
            self.results_table.setItem(row, 5, QTableWidgetItem(bands_text))
            
            # Temporal Coverage
            self.results_table.setItem(row, 6, QTableWidgetItem(data.get('temporal_coverage', '')))
            
            # Spatial Coverage
            self.results_table.setItem(row, 7, QTableWidgetItem(data.get('spatial_coverage', '')))
            
            # Processing Level
            self.results_table.setItem(row, 8, QTableWidgetItem(data.get('processing_level', '')))
            
            # Provider
            self.results_table.setItem(row, 9, QTableWidgetItem(data.get('provider', '')))
            
            # Data Type
            self.results_table.setItem(row, 10, QTableWidgetItem(data.get('data_type', '')))
            
            # License
            self.results_table.setItem(row, 11, QTableWidgetItem(data.get('license', '')))
            
            # File Format
            self.results_table.setItem(row, 12, QTableWidgetItem(data.get('file_format', '')))
            
            # Cloud Cover
            self.results_table.setItem(row, 13, QTableWidgetItem(data.get('cloud_cover', '')))
            
            # Frequency
            self.results_table.setItem(row, 14, QTableWidgetItem(data.get('frequency', '')))
            
            # Orbit Altitude
            self.results_table.setItem(row, 15, QTableWidgetItem(data.get('orbit_altitude', '')))
            
            # Swath Width
            self.results_table.setItem(row, 16, QTableWidgetItem(data.get('swath_width', '')))
            
            # Radiometric Resolution
            self.results_table.setItem(row, 17, QTableWidgetItem(data.get('radiometric_resolution', '')))
            
            # Atmospheric Corrections
            self.results_table.setItem(row, 18, QTableWidgetItem(data.get('atmospheric_corrections', '')))
            
            # Confidence
            confidence = f"{data.get('confidence_score', 0):.2f}"
            self.results_table.setItem(row, 19, QTableWidgetItem(confidence))
    
    def show_summary(self):
        """Show crawling summary"""
        summary = f"""
📊 Crawling Summary:
   Total processed: {self.total_processed}
   Successful extractions: {self.successful_extractions}
   Failed extractions: {self.failed_extractions}
   Data items: {len(self.extracted_data)}
        """
        self.log_message(summary)
    
    def export_results(self):
        """Export results to JSON"""
        if not self.extracted_data:
            QMessageBox.warning(self, "Warning", "No data to export!")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save JSON file", "", "JSON files (*.json)"
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.extracted_data, f, indent=2, ensure_ascii=False)
                self.log_message(f"✅ Results exported to: {file_path}")
            except Exception as e:
                self.log_error(f"❌ Export failed: {e}")
    
    def export_results_csv(self):
        """Export results to CSV"""
        if not self.extracted_data:
            QMessageBox.warning(self, "Warning", "No data to export!")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save CSV file", "", "CSV files (*.csv)"
        )
        if file_path:
            try:
                import csv
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    if self.extracted_data:
                        writer = csv.DictWriter(f, fieldnames=self.extracted_data[0].keys())
                        writer.writeheader()
                        writer.writerows(self.extracted_data)
                self.log_message(f"✅ Results exported to: {file_path}")
            except Exception as e:
                self.log_error(f"❌ Export failed: {e}")
    
    def apply_dark_theme(self):
        """Apply dark theme styling to the application"""
        # Dark theme colors
        dark_bg = "#2b2b2b"
        dark_text = "#ffffff"
        dark_alt_bg = "#3c3c3c"
        dark_border = "#555555"
        dark_highlight = "#007acc"
        
        # Main application styling
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {dark_bg};
                color: {dark_text};
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 12px;
            }}
            
            QGroupBox {{
                border: 2px solid {dark_border};
                border-radius: 8px;
                margin-top: 1ex;
                font-weight: bold;
                color: {dark_text};
                background-color: {dark_alt_bg};
                padding: 10px;
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: {dark_highlight};
            }}
            
            QLineEdit, QTextEdit, QTextBrowser {{
                background-color: {dark_alt_bg};
                border: 2px solid {dark_border};
                border-radius: 5px;
                padding: 8px;
                color: {dark_text};
                selection-background-color: {dark_highlight};
            }}
            
            QLineEdit:focus, QTextEdit:focus, QTextBrowser:focus {{
                border-color: {dark_highlight};
            }}
            
            QPushButton {{
                background-color: {dark_highlight};
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                color: white;
                font-weight: bold;
                min-width: 80px;
            }}
            
            QPushButton:hover {{
                background-color: #005a9e;
            }}
            
            QPushButton:pressed {{
                background-color: #004080;
            }}
            
            QPushButton:disabled {{
                background-color: {dark_border};
                color: #888888;
            }}
            
            QComboBox {{
                background-color: {dark_alt_bg};
                border: 2px solid {dark_border};
                border-radius: 5px;
                padding: 5px;
                color: {dark_text};
                min-width: 100px;
            }}
            
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {dark_text};
                margin-right: 5px;
            }}
            
            QProgressBar {{
                border: 2px solid {dark_border};
                border-radius: 5px;
                text-align: center;
                background-color: {dark_alt_bg};
                color: {dark_text};
            }}
            
            QProgressBar::chunk {{
                background-color: {dark_highlight};
                border-radius: 3px;
            }}
            
            QTableWidget {{
                background-color: {dark_alt_bg};
                alternate-background-color: {dark_bg};
                gridline-color: {dark_border};
                border: 2px solid {dark_border};
                border-radius: 5px;
                color: {dark_text};
                selection-background-color: {dark_highlight};
                selection-color: white;
            }}
            
            QTableWidget::item {{
                padding: 5px;
                border: none;
            }}
            
            QTableWidget::item:selected {{
                background-color: {dark_highlight};
                color: white;
            }}
            
            QHeaderView::section {{
                background-color: {dark_border};
                color: {dark_text};
                padding: 8px;
                border: 1px solid {dark_alt_bg};
                font-weight: bold;
            }}
            
            QHeaderView::section:hover {{
                background-color: {dark_highlight};
            }}
            
            QLabel {{
                color: {dark_text};
                background-color: transparent;
            }}
            
            QScrollBar:vertical {{
                background-color: {dark_alt_bg};
                width: 12px;
                border-radius: 6px;
            }}
            
            QScrollBar::handle:vertical {{
                background-color: {dark_border};
                border-radius: 6px;
                min-height: 20px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background-color: {dark_highlight};
            }}
        """)
    
    def crawl_finished(self):
        """Cleanup after crawling"""
        self.is_crawling = False
        self.is_paused = False
        self.pause_requested = False
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.pause_btn.setEnabled(False)
        self.pause_btn.setText("Pause")
        self.status_label.setText("Ready")
        
        # End comprehensive logging
        self.end_crawl_logging()
        
        # Clear crawl state when crawling is complete
        if self.current_crawl_state:
            self.log_message("✅ Crawling completed - state cleared")
            self.current_crawl_state = {}
    
    def log_message(self, message):
        """Log message to console"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.console.append(f"[{timestamp}] {message}")
        self.console.ensureCursorVisible()
        
        # Also log to file
        self.log_to_file(f"INFO: {message}")
    
    def log_error(self, message):
        """Log error to console"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.console.append(f"[{timestamp}] ERROR: {message}")
        self.console.ensureCursorVisible()
        
        # Also log to file
        self.log_to_file(f"ERROR: {message}")
    
    def log_to_file(self, message):
        """Log message to file"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_file = f"lightweight_crawler_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"[{timestamp}] {message}\n")
        except Exception as e:
            # Fallback to console if file logging fails
            print(f"Failed to log to file: {e}")
    
    def save_failure_report(self):
        """Save detailed failure report"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = f"failure_report_{timestamp}.json"
            
            report = {
                'timestamp': datetime.now().isoformat(),
                'session_duration': str(datetime.now() - self.start_time) if self.start_time else None,
                'statistics': {
                    'total_processed': self.total_processed,
                    'successful_extractions': self.successful_extractions,
                    'failed_extractions': self.failed_extractions,
                    'thumbnail_failures': self.thumbnail_failures,
                    'request_failures': self.request_failures,
                    'parsing_failures': self.parsing_failures
                },
                'success_rate': (self.successful_extractions / self.total_processed * 100) if self.total_processed > 0 else 0,
                'failure_rates': {
                    'thumbnail_failure_rate': (self.thumbnail_failures / self.total_processed * 100) if self.total_processed > 0 else 0,
                    'request_failure_rate': (self.request_failures / self.total_processed * 100) if self.total_processed > 0 else 0,
                    'parsing_failure_rate': (self.parsing_failures / self.total_processed * 100) if self.total_processed > 0 else 0
                },
                'configuration': self.config,
                'overwrite_enabled': self.overwrite_checkbox.isChecked() if hasattr(self, 'overwrite_checkbox') else False
            }
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            self.log_message(f"📊 Failure report saved: {report_file}")
            
        except Exception as e:
            self.log_error(f"❌ Failed to save failure report: {e}")
    
    def start_crawl_logging(self):
        """Start comprehensive logging for crawl session"""
        self.start_time = datetime.now()
        session_id = self.start_time.strftime('%Y%m%d_%H%M%S')
        
        self.log_message(f"🚀 Starting crawl session: {session_id}")
        self.log_message(f"📊 Initial statistics: Processed={self.total_processed}, Success={self.successful_extractions}, Failed={self.failed_extractions}")
        self.log_message(f"⚙️ Configuration: Max concurrent={self.config['performance']['max_concurrent_requests']}, Delay={self.config['performance']['request_delay']}s, Timeout={self.config['performance']['timeout']}s")
        self.log_message(f"🔄 Overwrite mode: {'Enabled' if self.overwrite_checkbox.isChecked() else 'Disabled'}")
    
    def end_crawl_logging(self):
        """End crawl session with comprehensive statistics"""
        if self.start_time:
            duration = datetime.now() - self.start_time
            self.log_message(f"⏱️ Crawl session duration: {duration}")
        
        self.log_message(f"📊 Final statistics:")
        self.log_message(f"   Total processed: {self.total_processed}")
        self.log_message(f"   Successful extractions: {self.successful_extractions}")
        self.log_message(f"   Failed extractions: {self.failed_extractions}")
        self.log_message(f"   Thumbnail failures: {self.thumbnail_failures}")
        self.log_message(f"   Request failures: {self.request_failures}")
        self.log_message(f"   Parsing failures: {self.parsing_failures}")
        
        if self.total_processed > 0:
            success_rate = (self.successful_extractions / self.total_processed) * 100
            self.log_message(f"   Success rate: {success_rate:.1f}%")
        
        self.log_message(f"💾 Data extracted: {len(self.extracted_data)} items")
        self.log_message(f"🖼️ Thumbnails cached: {len(self.thumbnail_cache)} images")
        
        # Show failure analysis
        if self.thumbnail_failures > 0 or self.request_failures > 0 or self.parsing_failures > 0:
            self.log_message(f"🔍 FAILURE ANALYSIS:")
            if self.thumbnail_failures > 0:
                self.log_message(f"   📸 Thumbnail failures: {self.thumbnail_failures} ({(self.thumbnail_failures/self.total_processed)*100:.1f}%)")
            if self.request_failures > 0:
                self.log_message(f"   🌐 Request failures: {self.request_failures} ({(self.request_failures/self.total_processed)*100:.1f}%)")
            if self.parsing_failures > 0:
                self.log_message(f"   📄 Parsing failures: {self.parsing_failures} ({(self.parsing_failures/self.total_processed)*100:.1f}%)")
            
            # Save detailed failure report
            self.save_failure_report()

    def filter_results(self):
        """Filter results based on search text and confidence level"""
        search_text = self.search_edit.text().lower()
        filter_type = self.filter_combo.currentText()
        
        for row in range(self.results_table.rowCount()):
            show_row = True
            
            # Search filter
            if search_text:
                row_text = ""
                for col in range(self.results_table.columnCount()):
                    item = self.results_table.item(row, col)
                    if item:
                        row_text += item.text().lower() + " "
                
                if search_text not in row_text:
                    show_row = False
            
            # Confidence filter
            if filter_type != "All":
                confidence_item = self.results_table.item(row, 14)  # Confidence column
                if confidence_item:
                    try:
                        confidence = float(confidence_item.text())
                        if filter_type == "High Confidence (>0.7)" and confidence <= 0.7:
                            show_row = False
                        elif filter_type == "Medium Confidence (0.4-0.7)" and (confidence < 0.4 or confidence > 0.7):
                            show_row = False
                        elif filter_type == "Low Confidence (<0.4)" and confidence >= 0.4:
                            show_row = False
                    except ValueError:
                        show_row = False
            
            self.results_table.setRowHidden(row, not show_row)
    
    def clear_filters(self):
        """Clear all filters and show all results"""
        self.search_edit.clear()
        self.filter_combo.setCurrentText("All")
        for row in range(self.results_table.rowCount()):
            self.results_table.setRowHidden(row, False)
    
    def sort_by_confidence(self):
        """Sort results by confidence score (highest first)"""
        self.results_table.sortItems(14, Qt.DescendingOrder)  # Confidence column
    
    def show_statistics(self):
        """Show statistics about the extracted data"""
        if not self.extracted_data:
            QMessageBox.information(self, "Statistics", "No data available for statistics.")
            return
        
        # Show crawl state if available
        if self.current_crawl_state:
            state = self.current_crawl_state
            state_info = f"""
            📊 CRAWL STATE:
            Current URL: {state.get('current_url', 'Unknown')}
            Progress: {state.get('current_index', 0)}/{state.get('total_links', 0)} links
            Processed URLs: {len(state.get('processed_urls', []))}
            Extracted Data: {state.get('extracted_data', 0)} items
            Successful: {state.get('successful_extractions', 0)}
            Failed: {state.get('failed_extractions', 0)}
            """
            QMessageBox.information(self, "Crawl State", state_info)
        
        total_items = len(self.extracted_data)
        confidence_scores = [data.get('confidence_score', 0) for data in self.extracted_data]
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        
        # Count providers
        providers = {}
        for data in self.extracted_data:
            provider = data.get('provider', 'Unknown')
            providers[provider] = providers.get(provider, 0) + 1
        
        # Count data types
        data_types = {}
        for data in self.extracted_data:
            data_type = data.get('data_type', 'Unknown')
            data_types[data_type] = data_types.get(data_type, 0) + 1
        
        # Count satellites
        satellites = {}
        for data in self.extracted_data:
            if data.get('satellite_info'):
                for sat_type, sat_list in data['satellite_info'].items():
                    for sat in sat_list:
                        satellites[sat] = satellites.get(sat, 0) + 1
        
        stats_text = f"""
        📊 EXTRACTION STATISTICS
        
        Total Items: {total_items}
        Average Confidence: {avg_confidence:.2f}
        
        📡 TOP PROVIDERS:
        """
        for provider, count in sorted(providers.items(), key=lambda x: x[1], reverse=True)[:5]:
            stats_text += f"  {provider}: {count}\n"
        
        stats_text += "\n🔍 TOP DATA TYPES:\n"
        for data_type, count in sorted(data_types.items(), key=lambda x: x[1], reverse=True)[:5]:
            stats_text += f"  {data_type}: {count}\n"
        
        stats_text += "\n🛰️ TOP SATELLITES:\n"
        for satellite, count in sorted(satellites.items(), key=lambda x: x[1], reverse=True)[:5]:
            stats_text += f"  {satellite}: {count}\n"
        
        QMessageBox.information(self, "Extraction Statistics", stats_text)
    
    def show_detailed_view(self):
        """Show detailed view of selected item with navigation and enhanced features"""
        current_row = self.results_table.currentRow()
        if current_row < 0 or current_row >= len(self.extracted_data):
            QMessageBox.warning(self, "Selection", "Please select an item to view details.")
            return
        
        # Create detailed view dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Detailed Dataset View")
        dialog.setModal(True)
        dialog.resize(1000, 700)
        
        # Enable keyboard navigation
        dialog.setFocusPolicy(Qt.StrongFocus)
        
        layout = QVBoxLayout()
        
        # Navigation controls
        nav_layout = QHBoxLayout()
        
        self.prev_btn = QPushButton("← Previous (Ctrl+Left)")
        self.prev_btn.clicked.connect(lambda: self.navigate_detail(dialog, -1))
        
        self.next_btn = QPushButton("Next → (Ctrl+Right)")
        self.next_btn.clicked.connect(lambda: self.navigate_detail(dialog, 1))
        
        self.current_index_label = QLabel(f"Item {current_row + 1} of {len(self.extracted_data)}")
        self.current_index_label.setAlignment(Qt.AlignCenter)
        
        nav_layout.addWidget(self.prev_btn)
        nav_layout.addWidget(self.current_index_label)
        nav_layout.addWidget(self.next_btn)
        
        # Search and filter controls
        filter_layout = QHBoxLayout()
        
        self.detail_search = QLineEdit()
        self.detail_search.setPlaceholderText("Search in current item... (Ctrl+F)")
        self.detail_search.textChanged.connect(lambda: self.filter_detail_content(dialog.text_browser))
        
        self.detail_filter_combo = QComboBox()
        self.detail_filter_combo.addItems(["All Sections", "Basic Info", "Complete Description", "Satellite Info", "Technical Specs", "Coverage", "Provider Info"])
        self.detail_filter_combo.currentTextChanged.connect(lambda: self.filter_detail_content(dialog.text_browser))
        
        filter_layout.addWidget(QLabel("Search:"))
        filter_layout.addWidget(self.detail_search)
        filter_layout.addWidget(QLabel("Filter:"))
        filter_layout.addWidget(self.detail_filter_combo)
        
        # Main content area with splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Thumbnail and basic info
        left_panel = QVBoxLayout()
        
        # Thumbnail display with click-to-expand
        thumbnail_group = QGroupBox("Thumbnail (Click to expand)")
        thumbnail_layout = QVBoxLayout()
        
        self.thumbnail_label = QLabel()
        self.thumbnail_label.setAlignment(Qt.AlignCenter)
        self.thumbnail_label.setMinimumSize(250, 180)
        self.thumbnail_label.setMaximumSize(350, 250)
        self.thumbnail_label.setStyleSheet("border: 2px solid #ccc; background-color: #f5f5f5; cursor: pointer; border-radius: 5px;")
        self.thumbnail_label.mousePressEvent = lambda event: self.expand_thumbnail(dialog)
        
        thumbnail_layout.addWidget(self.thumbnail_label)
        thumbnail_group.setLayout(thumbnail_layout)
        left_panel.addWidget(thumbnail_group)
        
        # Quick info panel
        quick_info_group = QGroupBox("Quick Info")
        quick_info_layout = QVBoxLayout()
        
        self.quick_info_text = QTextEdit()
        self.quick_info_text.setMaximumHeight(200)
        self.quick_info_text.setReadOnly(True)
        self.quick_info_text.setStyleSheet("font-size: 12px; line-height: 1.4;")
        
        quick_info_layout.addWidget(self.quick_info_text)
        quick_info_group.setLayout(quick_info_layout)
        left_panel.addWidget(quick_info_group)
        
        # Action buttons
        action_layout = QHBoxLayout()
        
        self.open_url_btn = QPushButton("Open URL")
        self.open_url_btn.clicked.connect(lambda: self.open_url_in_browser(current_row))
        
        self.copy_url_btn = QPushButton("Copy URL")
        self.copy_url_btn.clicked.connect(lambda: self.copy_url_to_clipboard(current_row))
        
        self.export_item_btn = QPushButton("Export Item")
        self.export_item_btn.clicked.connect(lambda: self.export_single_item(current_row))
        
        action_layout.addWidget(self.open_url_btn)
        action_layout.addWidget(self.copy_url_btn)
        action_layout.addWidget(self.export_item_btn)
        
        left_panel.addLayout(action_layout)
        
        # Create left panel widget
        left_widget = QWidget()
        left_widget.setLayout(left_panel)
        left_widget.setMaximumWidth(350)
        
        # Right panel - Detailed information
        right_panel = QVBoxLayout()
        
        # Create text browser for detailed view
        text_browser = QTextBrowser()
        text_browser.setOpenExternalLinks(True)
        
        right_panel.addWidget(text_browser)
        
        # Create right panel widget
        right_widget = QWidget()
        right_widget.setLayout(right_panel)
        
        # Add panels to splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([300, 700])  # Set initial split sizes
        
        # Store current data for navigation
        dialog.current_data = self.extracted_data
        dialog.current_index = current_row
        dialog.text_browser = text_browser
        dialog.thumbnail_label = self.thumbnail_label
        dialog.quick_info_text = self.quick_info_text
        dialog.current_index_label = self.current_index_label
        
        # Load initial data
        self.load_detail_data(dialog, current_row)
        
        # Add keyboard shortcuts
        self.setup_keyboard_shortcuts(dialog)
        
        # Add all components to main layout
        layout.addLayout(nav_layout)
        layout.addLayout(filter_layout)
        layout.addWidget(splitter)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def setup_keyboard_shortcuts(self, dialog):
        """Setup keyboard shortcuts for navigation"""
        # Previous item
        prev_shortcut = QShortcut(QKeySequence("Ctrl+Left"), dialog)
        prev_shortcut.activated.connect(lambda: self.navigate_detail(dialog, -1))
        
        # Next item
        next_shortcut = QShortcut(QKeySequence("Ctrl+Right"), dialog)
        next_shortcut.activated.connect(lambda: self.navigate_detail(dialog, 1))
        
        # Search
        search_shortcut = QShortcut(QKeySequence("Ctrl+F"), dialog)
        search_shortcut.activated.connect(lambda: self.detail_search.setFocus())
        
        # Escape to close
        close_shortcut = QShortcut(QKeySequence("Escape"), dialog)
        close_shortcut.activated.connect(dialog.accept)
    
    def expand_thumbnail(self, dialog):
        """Expand thumbnail to full size in a new window"""
        current_data = dialog.current_data[dialog.current_index]
        
        if not current_data.get('thumbnail_data'):
            QMessageBox.information(dialog, "Thumbnail", "No thumbnail available for this item.")
            return
        
        # Create thumbnail viewer dialog
        thumb_dialog = QDialog(dialog)
        thumb_dialog.setWindowTitle(f"Thumbnail - {current_data.get('title', 'Unknown')}")
        thumb_dialog.setModal(True)
        thumb_dialog.resize(600, 500)
        
        layout = QVBoxLayout()
        
        # Create larger thumbnail display
        thumb_label = QLabel()
        thumb_label.setPixmap(current_data['thumbnail_data'])
        thumb_label.setAlignment(Qt.AlignCenter)
        thumb_label.setMinimumSize(500, 400)
        thumb_label.setStyleSheet("border: 2px solid #ccc; background-color: #f5f5f5; border-radius: 5px;")
        
        # Add close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(thumb_dialog.accept)
        close_btn.setStyleSheet("QPushButton { padding: 8px 16px; font-size: 12px; }")
        
        layout.addWidget(thumb_label)
        layout.addWidget(close_btn)
        
        thumb_dialog.setLayout(layout)
        thumb_dialog.exec()
    
    def load_detail_data(self, dialog, row_index):
        """Load detailed data for the specified row"""
        if row_index < 0 or row_index >= len(dialog.current_data):
            return
        
        data = dialog.current_data[row_index]
        
        # Update navigation
        dialog.current_index = row_index
        dialog.current_index_label.setText(f"Item {row_index + 1} of {len(dialog.current_data)}")
        
        # Update thumbnail
        if data.get('thumbnail_data'):
            dialog.thumbnail_label.setPixmap(data['thumbnail_data'])
            dialog.thumbnail_label.setToolTip("Click to view full size")
        else:
            dialog.thumbnail_label.setText("No thumbnail available")
            dialog.thumbnail_label.setToolTip("")
        
        # Update quick info with better formatting
        quick_info = f"""
        <div style="font-family: Arial, sans-serif; line-height: 1.4;">
            <p><strong>Title:</strong> {data.get('title', 'N/A')}</p>
            <p><strong>Confidence:</strong> {data.get('confidence_score', 0):.2f}</p>
            <p><strong>Provider:</strong> {data.get('provider', 'N/A')}</p>
            <p><strong>Data Type:</strong> {data.get('data_type', 'N/A')}</p>
            <p><strong>Resolution:</strong> {data.get('resolution', 'N/A')}</p>
            <p><strong>Temporal:</strong> {data.get('temporal_coverage', 'N/A')}</p>
            <p><strong>License:</strong> {data.get('license', 'N/A')}</p>
                            <p><strong>Description:</strong> {data.get('description', 'N/A')}</p>
        </div>
        """
        dialog.quick_info_text.setHtml(quick_info)
        
        # Update detailed view
        details = self.format_detailed_content(data)
        dialog.text_browser.setHtml(details)
    
    def format_detailed_content(self, data):
        """Format detailed content with sections and styling"""
        details = f"""
        <style>
            .section {{ margin: 15px 0; padding: 15px; border-left: 4px solid #007acc; background-color: #2b2b2b; color: #ffffff; }}
            .section-title {{ color: #007acc; font-size: 18px; font-weight: bold; margin-bottom: 15px; }}
            .field {{ margin: 8px 0; font-size: 14px; }}
            .field-label {{ font-weight: bold; color: #ffffff; }}
            .field-value {{ color: #cccccc; }}
            .url {{ color: #007acc; text-decoration: none; }}
            .url:hover {{ text-decoration: underline; }}
            .description-text {{ 
                background-color: #3c3c3c; 
                padding: 15px; 
                border-left: 4px solid #28a745; 
                margin: 15px 0; 
                line-height: 1.6;
                font-size: 14px;
                word-wrap: break-word;
                overflow-wrap: break-word;
                color: #ffffff;
            }}
            .section-icon {{ 
                font-size: 24px; 
                margin-right: 10px; 
                vertical-align: middle;
            }}
            .missing-value {{ color: #999; font-style: italic; }}
            .code-snippet {{
                background-color: #1e1e1e;
                border: 2px solid #555555;
                border-radius: 5px;
                padding: 15px;
                margin: 15px 0;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 12px;
                color: #ffffff;
                overflow-x: auto;
                white-space: pre-wrap;
                word-wrap: break-word;
            }}
            .code-header {{
                color: #007acc;
                font-weight: bold;
                margin-bottom: 10px;
                font-size: 14px;
            }}
        </style>
        
        <h1 style="color: #007acc; border-bottom: 2px solid #007acc; padding-bottom: 15px; font-size: 24px;">
            📋 DETAILED DATASET INFORMATION
        </h1>
        
        <div class="section" id="basic-info">
            <div class="section-title"><span class="section-icon">📝</span>Basic Information</div>
            <div class="field"><span class="field-label">Title:</span> <span class="field-value">{data.get('title', 'N/A')}</span></div>
            <div class="field"><span class="field-label">URL:</span> <a href="{data.get('url', '')}" class="url">{data.get('url', 'N/A')}</a></div>
            <div class="field"><span class="field-label">Confidence Score:</span> <span class="field-value">{data.get('confidence_score', 0):.2f}</span></div>
            <div class="field"><span class="field-label">Timestamp:</span> <span class="field-value">{data.get('timestamp', 'N/A')}</span></div>
        </div>
        
        <div class="section" id="description-section">
            <div class="section-title"><span class="section-icon">📄</span>Complete Description</div>
            <div class="description-text">{data.get('description_full', data.get('description', 'No description available.'))}</div>
        </div>
        

        
        <div class="section" id="satellite-info">
            <div class="section-title"><span class="section-icon">🛰️</span>Satellite Information</div>
        """
        
        if data.get('satellite_info'):
            for sat_type, satellites in data['satellite_info'].items():
                details += f'<div class="field"><span class="field-label">{sat_type.title()}:</span> <span class="field-value">{", ".join(satellites)}</span></div>'
        else:
            details += '<div class="field"><span class="field-value missing-value">No satellite information found</span></div>'
        
        details += f"""
        </div>
        
        <div class="section" id="technical-specs">
            <div class="section-title"><span class="section-icon">🔬</span>Technical Specifications</div>
            <div class="field"><span class="field-label">Resolution:</span> <span class="field-value">{data.get('resolution', 'N/A')}</span></div>
            <div class="field"><span class="field-label">Bands:</span> <span class="field-value">{", ".join(data.get('bands', [])) if data.get('bands') else 'N/A'}</span></div>
            <div class="field"><span class="field-label">Processing Level:</span> <span class="field-value">{data.get('processing_level', 'N/A')}</span></div>
            <div class="field"><span class="field-label">File Format:</span> <span class="field-value">{data.get('file_format', 'N/A')}</span></div>
            <div class="field"><span class="field-label">Cloud Cover:</span> <span class="field-value">{data.get('cloud_cover', 'N/A')}</span></div>
        </div>
        
        <div class="section" id="coverage-info">
            <div class="section-title"><span class="section-icon">🌍</span>Coverage Information</div>
            <div class="field"><span class="field-label">Temporal Coverage:</span> <span class="field-value">{data.get('temporal_coverage', 'N/A')}</span></div>
            <div class="field"><span class="field-label">Spatial Coverage:</span> <span class="field-value">{data.get('spatial_coverage', 'N/A')}</span></div>
        </div>
        
        <div class="section" id="provider-info">
            <div class="section-title"><span class="section-icon">🏢</span>Provider Information</div>
            <div class="field"><span class="field-label">Provider:</span> <span class="field-value">{data.get('provider', 'N/A')}</span></div>
            <div class="field"><span class="field-label">Data Type:</span> <span class="field-value">{data.get('data_type', 'N/A')}</span></div>
            <div class="field"><span class="field-label">License:</span> <span class="field-value">{data.get('license', 'N/A')}</span></div>
        </div>
        
        <div class="section" id="advanced-specs">
            <div class="section-title"><span class="section-icon">🔬</span>Advanced Specifications</div>
            <div class="field"><span class="field-label">Frequency/Revisit:</span> <span class="field-value">{data.get('frequency', 'N/A')}</span></div>
            <div class="field"><span class="field-label">Orbit Altitude:</span> <span class="field-value">{data.get('orbit_altitude', 'N/A')}</span></div>
            <div class="field"><span class="field-label">Swath Width:</span> <span class="field-value">{data.get('swath_width', 'N/A')}</span></div>
            <div class="field"><span class="field-label">Radiometric Resolution:</span> <span class="field-value">{data.get('radiometric_resolution', 'N/A')}</span></div>
            <div class="field"><span class="field-label">Atmospheric Corrections:</span> <span class="field-value">{data.get('atmospheric_corrections', 'N/A')}</span></div>
            <div class="field"><span class="field-label">Quality/Accuracy:</span> <span class="field-value">{data.get('quality_accuracy', 'N/A')}</span></div>
        </div>
        """
        
        # Add GEE code snippet section if available
        if data.get('gee_code_snippet'):
            details += f"""
        <div class="section" id="gee-code">
            <div class="section-title"><span class="section-icon">💻</span>Earth Engine Code Snippet</div>
            <div class="code-header">Copy this code to download the dataset:</div>
            <div class="code-snippet">{data.get('gee_code_snippet', 'No code snippet available')}</div>
        </div>
        """
        
        if data.get('thumbnail_url'):
            details += f"""
        <div class="section" id="thumbnail-info">
            <div class="section-title"><span class="section-icon">🖼️</span>Thumbnail</div>
            <div class="field"><span class="field-label">Thumbnail URL:</span> <a href="{data.get('thumbnail_url', '')}" class="url">{data.get('thumbnail_url', 'N/A')}</a></div>
        </div>
        """
        
        return details
    
    def navigate_detail(self, dialog, direction):
        """Navigate to next/previous item in detailed view"""
        new_index = dialog.current_index + direction
        
        if 0 <= new_index < len(dialog.current_data):
            self.load_detail_data(dialog, new_index)
    
    def filter_detail_content(self, text_browser):
        """Filter content in detailed view based on search and filter"""
        search_text = self.detail_search.text().lower()
        filter_section = self.detail_filter_combo.currentText()
        
        # Get the current data - use the current row from the table
        current_row = self.results_table.currentRow()
        if current_row >= 0 and current_row < len(self.extracted_data):
            current_data = self.extracted_data[current_row]
        else:
            return
        details = self.format_detailed_content(current_data)
        
        # Apply section filtering
        if filter_section != "All Sections":
            # Extract only the relevant section
            section_mapping = {
                "Basic Info": "basic-info",
                "Complete Description": "description-section",
                "Satellite Info": "satellite-info", 
                "Technical Specs": "technical-specs",
                "Coverage": "coverage-info",
                "Provider Info": "provider-info"
            }
            
            section_id = section_mapping.get(filter_section, "")
            if section_id:
                # Simple section extraction (in a real implementation, you'd use proper HTML parsing)
                start_tag = f'<div class="section" id="{section_id}">'
                end_tag = '</div>'
                
                start_pos = details.find(start_tag)
                if start_pos != -1:
                    end_pos = details.find(end_tag, start_pos)
                    if end_pos != -1:
                        # Extract just this section
                        section_content = details[start_pos:end_pos + len(end_tag)]
                        details = f"""
                        <style>
                            .section {{ margin: 10px 0; padding: 10px; border-left: 3px solid #007acc; background-color: #f8f9fa; }}
                            .section-title {{ color: #007acc; font-size: 16px; font-weight: bold; margin-bottom: 10px; }}
                            .field {{ margin: 5px 0; }}
                            .field-label {{ font-weight: bold; color: #333; }}
                            .field-value {{ color: #666; }}
                            .url {{ color: #007acc; text-decoration: none; }}
                            .url:hover {{ text-decoration: underline; }}
                            .highlight {{ background-color: yellow; font-weight: bold; }}
                        </style>
                        <h1 style="color: #007acc; border-bottom: 2px solid #007acc; padding-bottom: 10px;">
                            📋 {filter_section}
                        </h1>
                        {section_content}
                        """
        
        # Apply search highlighting
        if search_text:
            # Highlight search terms in the content (case-insensitive)
            import re
            pattern = re.compile(re.escape(search_text), re.IGNORECASE)
            details = pattern.sub(f'<span class="highlight">{search_text}</span>', details)
        
        text_browser.setHtml(details)
    
    def show_context_menu(self, position):
        """Show context menu for table items"""
        menu = QMenu()
        
        # Get the item under the cursor
        item = self.results_table.itemAt(position)
        if item:
            row = item.row()
            
            # Add context menu actions
            view_details = menu.addAction("View Details")
            copy_url = menu.addAction("Copy URL")
            open_url = menu.addAction("Open URL")
            menu.addSeparator()
            export_item = menu.addAction("Export This Item")
            
            # Connect actions
            view_details.triggered.connect(lambda: self.show_detailed_view())
            copy_url.triggered.connect(lambda: self.copy_url_to_clipboard(row))
            open_url.triggered.connect(lambda: self.open_url_in_browser(row))
            export_item.triggered.connect(lambda: self.export_single_item(row))
            
            menu.exec(self.results_table.mapToGlobal(position))
    
    def copy_url_to_clipboard(self, row):
        """Copy URL to clipboard"""
        if row < len(self.extracted_data):
            url = self.extracted_data[row].get('url', '')
            clipboard = QApplication.clipboard()
            clipboard.setText(url)
            self.log_message(f"📋 Copied URL to clipboard: {url}")
    
    def open_url_in_browser(self, row):
        """Open URL in default browser"""
        if row < len(self.extracted_data):
            url = self.extracted_data[row].get('url', '')
            if url:
                QDesktopServices.openUrl(QUrl(url))
                self.log_message(f"🌐 Opening URL in browser: {url}")
    
    def export_single_item(self, row):
        """Export single item to JSON file"""
        if row < len(self.extracted_data):
            data = self.extracted_data[row]
            filename, _ = QFileDialog.getSaveFileName(
                self, "Export Item", f"dataset_{row}.json", "JSON Files (*.json)"
            )
            if filename:
                # Create enhanced export with GEE code snippet
                export_data = data.copy()
                if data.get('gee_code_snippet'):
                    # Also create a separate .js file for the GEE code
                    js_filename = filename.replace('.json', '.js')
                    with open(js_filename, 'w', encoding='utf-8') as f:
                        f.write(f"// Earth Engine Code for {data.get('title', 'Dataset')}\n")
                        f.write(f"// Dataset ID: {data.get('dataset_id', 'Unknown')}\n")
                        f.write(f"// URL: {data.get('url', 'Unknown')}\n\n")
                        f.write(data['gee_code_snippet'])
                    self.log_message(f"💾 Exported GEE code to: {js_filename}")
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
                self.log_message(f"💾 Exported item to: {filename}")

def main():
    """Main function"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Set application properties
    app.setApplicationName("Lightweight Earth Engine Crawler")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("Flutter Earth")
    
    window = LightweightCrawlerUI()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 