import sys
import subprocess
import random
import importlib.util

def check_package_installed(package_name):
    """Check if a package is actually installed and importable"""
    # Handle package name variations
    module_name = package_name.replace('-', '_')
    
    # First try direct import
    try:
        __import__(module_name)
        return True
    except ImportError:
        pass
    
    # Check if it's installed but has a different import name
    try:
        spec = importlib.util.find_spec(module_name)
        if spec is not None:
            return True
    except:
        pass
    
    # Special cases for packages with different import names
    package_import_map = {
        'scikit-learn': 'sklearn',
        'pyyaml': 'yaml',
        'dateparser': 'dateparser'
    }
    
    if package_name in package_import_map:
        try:
            __import__(package_import_map[package_name])
            return True
        except ImportError:
            pass
    
    return False

REQUIRED_PACKAGES = [
    'spacy',
    'transformers', 
    'scikit-learn',
    'geopy',
    'pyyaml',
    'dash',
    'dateparser'
]

missing = []
for pkg in REQUIRED_PACKAGES:
    if not check_package_installed(pkg):
        missing.append(pkg)

if missing:
    print(f"Missing required packages: {', '.join(missing)}. Attempting to install...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade'] + missing)
        print("All required packages installed. Please restart the program.")
        sys.exit(0)
    except Exception as e:
        print("Automatic installation failed.")
        print("Error:", e)
        print("Please install the missing packages manually:")
        print(f"    {sys.executable} -m pip install {' '.join(missing)}")
        sys.exit(1)

# Ensure spaCy English model is downloaded
try:
    import spacy
    spacy.load('en_core_web_sm')
except OSError:
    print("Downloading spaCy English model (en_core_web_sm)...")
    try:
        subprocess.check_call([sys.executable, '-m', 'spacy', 'download', 'en_core_web_sm'])
        print("spaCy English model installed. Please restart the program.")
        sys.exit(0)
    except Exception as e:
        print("Failed to download spaCy English model.")
        print("Error:", e)
        print(f"Please run: {sys.executable} -m spacy download en_core_web_sm")
        sys.exit(1)

import os
import threading
import json
import time
import requests
from queue import Queue
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import re
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, 
    QProgressBar, QLabel, QFileDialog, QLineEdit, QGroupBox, QCheckBox, QTabWidget
)
from PySide6.QtCore import QTimer, Qt, QThread
import csv
from collections import defaultdict
from datetime import datetime

# Advanced imports with fallbacks - only import once
spacy = None
transformers = None
geopy = None
dash = None
plotly = None
sklearn = None
yaml_module = None
dateparser = None

# Import all available packages at startup
try:
    import spacy
    print("✓ spaCy loaded successfully")
except ImportError:
    print("⚠ spaCy not available - ML/NLP features disabled")

try:
    import transformers
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    print("✓ Transformers loaded successfully")
except ImportError:
    print("⚠ Transformers not available - BERT features disabled")

try:
    import sklearn
    from sklearn.ensemble import VotingClassifier
    from sklearn.feature_extraction.text import TfidfVectorizer
    import numpy as np
    print("✓ Scikit-learn loaded successfully")
except ImportError:
    print("⚠ Scikit-learn not available - some ML features disabled")

try:
    from geopy.geocoders import Nominatim
    from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
    geopy = True
    print("✓ Geopy loaded successfully")
except ImportError:
    print("⚠ Geopy not available - geospatial validation disabled")

try:
    import yaml as yaml_module
    from config_utils import load_config, load_plugins
    print("✓ YAML/config_utils loaded successfully")
except ImportError:
    print("⚠ YAML/config_utils not available - config features disabled")

try:
    from analytics_dashboard import get_dashboard
    dash = True
    print("✓ Analytics dashboard loaded successfully")
except ImportError:
    print("⚠ Dash not available - analytics dashboard disabled")

try:
    import dateparser
    print("✓ Dateparser loaded successfully")
except ImportError:
    print("⚠ Dateparser not available - fuzzy date parsing disabled")

from datetime import datetime

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0',
]

class EnhancedCrawlerUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Earth Engine Catalog Web Crawler - Enhanced")
        self.resize(1000, 700)
        self.setup_ui()
        self.log_queue = Queue()
        self.progress_queue = Queue()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_ui)
        self.thread = None  # type: threading.Thread | None
        self.output_dir = "extracted_data"
        self.images_dir = "thumbnails"
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.images_dir, exist_ok=True)
        # Load spaCy model for ML/NLP-based classification
        self.nlp = None
        if spacy:
            try:
                self.nlp = spacy.load("en_core_web_sm")
                print("spaCy model loaded successfully")
            except Exception as e:
                print(f"spaCy model not loaded: {e}")
        # Load advanced ML models for ensemble classification
        self.bert_classifier = None
        self.tfidf_vectorizer = None
        if transformers:
            try:
                # Load BERT model for text classification
                self.bert_tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
                self.bert_model = AutoModelForSequenceClassification.from_pretrained("bert-base-uncased")
                self.bert_classifier = pipeline("text-classification", model=self.bert_model, tokenizer=self.bert_tokenizer)
                # Initialize TF-IDF vectorizer for traditional ML
                self.tfidf_vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
                print("Advanced ML models loaded successfully.")
            except Exception as e:
                print(f"Advanced ML models not loaded: {e}")
        # Load config and plugins
        self.config = None
        self.plugins = {}
        try:
            if yaml_module and 'load_config' in globals():
                self.config = load_config()
                self.plugins = load_plugins(self.config.get('plugins', []))
                print("Config and plugins loaded.")
        except Exception as e:
            print(f"Config/plugins not loaded: {e}")
        # Initialize validation components
        self.geocoder = None
        if geopy:
            try:
                self.geocoder = Nominatim(user_agent="earth_engine_crawler")
                print("Geocoder initialized successfully")
            except Exception as e:
                print(f"Geocoder not initialized: {e}")
        # Validation settings from config
        self.validation_config = self.config.get('validation', {}) if self.config else {}
        # Initialize analytics dashboard
        self.dashboard = None
        if dash:
            try:
                self.dashboard = get_dashboard()
                self.dashboard.start_background()
                print("Analytics dashboard started on http://127.0.0.1:8080")
            except Exception as e:
                print(f"Analytics dashboard not started: {e}")
        # Error handling and retry configuration
        self.error_tracker = {
            'total_errors': 0,
            'retry_attempts': 0,
            'recovered_results': 0,
            'error_categories': defaultdict(int)
        }
        self.max_retries = 3
        self.retry_delay = 2  # seconds
        # Now safe to call status indicators
        self.update_status_indicators()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Enhanced title with version
        title_label = QLabel("Earth Engine Catalog Web Crawler - Ultra Enhanced v2.0")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; margin: 10px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Status indicators for advanced features
        status_group = QGroupBox("Advanced Features Status")
        status_layout = QHBoxLayout()
        
        self.spacy_status = QLabel("spaCy: ❌")
        self.bert_status = QLabel("BERT: ❌")
        self.geo_status = QLabel("Geospatial: ❌")
        self.dashboard_status = QLabel("Dashboard: ❌")
        self.config_status = QLabel("Config: ❌")
        
        for status in [self.spacy_status, self.bert_status, self.geo_status, self.dashboard_status, self.config_status]:
            status.setStyleSheet("padding: 5px; border: 1px solid #bdc3c7; border-radius: 3px;")
            status_layout.addWidget(status)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # File selection group
        file_group = QGroupBox("HTML File Selection")
        file_layout = QHBoxLayout()
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setPlaceholderText("Select local HTML file to crawl...")
        self.browse_btn = QPushButton("Browse")
        self.browse_btn.clicked.connect(self.browse_file)
        file_layout.addWidget(self.file_path_edit, 1)
        file_layout.addWidget(self.browse_btn)
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # Advanced options group
        options_group = QGroupBox("Advanced Crawling Options")
        options_layout = QVBoxLayout()
        
        # Basic options
        basic_options = QHBoxLayout()
        self.download_thumbs = QCheckBox("Download thumbnails")
        self.download_thumbs.setChecked(True)
        self.extract_details = QCheckBox("Extract detailed information")
        self.extract_details.setChecked(True)
        self.save_individual = QCheckBox("Save as individual JSON files")
        self.save_individual.setChecked(True)
        basic_options.addWidget(self.download_thumbs)
        basic_options.addWidget(self.extract_details)
        basic_options.addWidget(self.save_individual)
        options_layout.addLayout(basic_options)
        
        # Advanced ML options
        ml_options = QHBoxLayout()
        self.use_ml_classification = QCheckBox("Use ML/NLP Classification")
        self.use_ml_classification.setChecked(True)
        self.use_ensemble = QCheckBox("Use Ensemble ML Models")
        self.use_ensemble.setChecked(True)
        self.use_validation = QCheckBox("Use Data Validation")
        self.use_validation.setChecked(True)
        ml_options.addWidget(self.use_ml_classification)
        ml_options.addWidget(self.use_ensemble)
        ml_options.addWidget(self.use_validation)
        options_layout.addLayout(ml_options)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # Dashboard and config controls
        controls_group = QGroupBox("Advanced Controls")
        controls_layout = QHBoxLayout()
        
        self.dashboard_btn = QPushButton("Open Analytics Dashboard")
        self.dashboard_btn.clicked.connect(self.open_dashboard)
        self.dashboard_btn.setEnabled(False)
        
        self.config_btn = QPushButton("Edit Configuration")
        self.config_btn.clicked.connect(self.edit_config)
        
        self.test_btn = QPushButton("Test Features")
        self.test_btn.clicked.connect(self.test_features)
        
        controls_layout.addWidget(self.dashboard_btn)
        controls_layout.addWidget(self.config_btn)
        controls_layout.addWidget(self.test_btn)
        controls_group.setLayout(controls_layout)
        layout.addWidget(controls_group)
        
        # Status and progress
        self.status = QLabel("Ready. Select an HTML file to begin.")
        layout.addWidget(self.status)
        
        self.progress = QProgressBar()
        self.progress.setMaximum(100)
        self.progress.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress.setStyleSheet("QProgressBar {height: 30px; font-size: 16px;} QProgressBar::chunk {background: #3a6ea5;}")
        layout.addWidget(self.progress)
        
        # Enhanced console with tabs
        console_group = QGroupBox("Real-Time Output")
        console_layout = QVBoxLayout()
        
        # Tab widget for different views
        self.tab_widget = QTabWidget()
        
        # Main console tab
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setStyleSheet("background: #181818; color: #e0e0e0; font-family: Consolas; font-size: 12px;")
        self.tab_widget.addTab(self.console, "Console Log")
        
        # ML Classification tab
        self.ml_console = QTextEdit()
        self.ml_console.setReadOnly(True)
        self.ml_console.setStyleSheet("background: #1a1a2e; color: #00d4ff; font-family: Consolas; font-size: 12px;")
        self.tab_widget.addTab(self.ml_console, "ML Classification")
        
        # Validation tab
        self.validation_console = QTextEdit()
        self.validation_console.setReadOnly(True)
        self.validation_console.setStyleSheet("background: #1a2e1a; color: #00ff88; font-family: Consolas; font-size: 12px;")
        self.tab_widget.addTab(self.validation_console, "Validation Results")
        
        # Error log tab
        self.error_console = QTextEdit()
        self.error_console.setReadOnly(True)
        self.error_console.setStyleSheet("background: #2e1a1a; color: #ff6b6b; font-family: Consolas; font-size: 12px;")
        self.tab_widget.addTab(self.error_console, "Error Log")
        
        # Add summary tab
        self.summary_console = QTextEdit()
        self.summary_console.setReadOnly(True)
        self.summary_console.setStyleSheet("background: #222; color: #ffe066; font-family: Consolas; font-size: 12px;")
        self.tab_widget.addTab(self.summary_console, "Summary")

        console_layout.addWidget(self.tab_widget)
        console_group.setLayout(console_layout)
        layout.addWidget(console_group, 1)
        
        # Control buttons
        button_layout = QHBoxLayout()
        self.crawl_btn = QPushButton("Start Advanced Crawling")
        self.crawl_btn.clicked.connect(self.start_crawl)
        self.crawl_btn.setEnabled(False)
        self.crawl_btn.setStyleSheet("QPushButton {background: #27ae60; color: white; padding: 10px; font-weight: bold;}")
        
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.clicked.connect(self.stop_crawl)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet("QPushButton {background: #e74c3c; color: white; padding: 10px;}")
        
        self.clear_btn = QPushButton("Clear All")
        self.clear_btn.clicked.connect(self.clear_all_consoles)
        self.clear_btn.setStyleSheet("QPushButton {background: #f39c12; color: white; padding: 10px;}")
        
        button_layout.addWidget(self.crawl_btn)
        button_layout.addWidget(self.stop_btn)
        button_layout.addWidget(self.clear_btn)
        layout.addLayout(button_layout)
        
        # Update status indicators
        # self.update_status_indicators()

    def update_status_indicators(self):
        """Update the status indicators for advanced features."""
        print(f"DEBUG: Updating status indicators...")
        print(f"DEBUG: self.nlp = {self.nlp}")
        print(f"DEBUG: self.bert_classifier = {self.bert_classifier}")
        print(f"DEBUG: self.geocoder = {self.geocoder}")
        print(f"DEBUG: self.dashboard = {self.dashboard}")
        print(f"DEBUG: self.config = {self.config}")
        
        if self.nlp:
            self.spacy_status.setText("spaCy: ✅")
            self.spacy_status.setStyleSheet("padding: 5px; border: 1px solid #27ae60; border-radius: 3px; color: #27ae60;")
        else:
            self.spacy_status.setText("spaCy: ❌")
            self.spacy_status.setStyleSheet("padding: 5px; border: 1px solid #e74c3c; border-radius: 3px; color: #e74c3c;")
        
        if self.bert_classifier:
            self.bert_status.setText("BERT: ✅")
            self.bert_status.setStyleSheet("padding: 5px; border: 1px solid #27ae60; border-radius: 3px; color: #27ae60;")
        else:
            self.bert_status.setText("BERT: ❌")
            self.bert_status.setStyleSheet("padding: 5px; border: 1px solid #e74c3c; border-radius: 3px; color: #e74c3c;")
        
        if self.geocoder:
            self.geo_status.setText("Geospatial: ✅")
            self.geo_status.setStyleSheet("padding: 5px; border: 1px solid #27ae60; border-radius: 3px; color: #27ae60;")
        else:
            self.geo_status.setText("Geospatial: ❌")
            self.geo_status.setStyleSheet("padding: 5px; border: 1px solid #e74c3c; border-radius: 3px; color: #e74c3c;")
        
        if self.dashboard:
            self.dashboard_status.setText("Dashboard: ✅")
            self.dashboard_status.setStyleSheet("padding: 5px; border: 1px solid #27ae60; border-radius: 3px; color: #27ae60;")
            self.dashboard_btn.setEnabled(True)
        else:
            self.dashboard_status.setText("Dashboard: ❌")
            self.dashboard_status.setStyleSheet("padding: 5px; border: 1px solid #e74c3c; border-radius: 3px; color: #e74c3c;")
        
        if self.config:
            self.config_status.setText("Config: ✅")
            self.config_status.setStyleSheet("padding: 5px; border: 1px solid #27ae60; border-radius: 3px; color: #27ae60;")
        else:
            self.config_status.setText("Config: ❌")
            self.config_status.setStyleSheet("padding: 5px; border: 1px solid #e74c3c; border-radius: 3px; color: #e74c3c;")
        
        print(f"DEBUG: Status indicators updated")

    def update_ui(self):
        """Update UI elements."""
        # Process progress updates
        while not self.progress_queue.empty():
            progress = self.progress_queue.get()
            self.progress.setValue(progress)
        
        # Process log messages
        while not self.log_queue.empty():
            message = self.log_queue.get()
            self.console.append(message)
            self.console.ensureCursorVisible()
        
        # Check if crawl thread is finished
        if hasattr(self, 'crawl_thread') and not self.crawl_thread.is_alive():
            self.crawl_finished()

    def open_dashboard(self):
        """Open the analytics dashboard in default browser."""
        if self.dashboard:
            import webbrowser
            webbrowser.open("http://127.0.0.1:8080")
            self.log_message("[DASHBOARD] Opening analytics dashboard in browser...")
        else:
            self.log_message("[ERROR] Analytics dashboard not available")

    def edit_config(self):
        """Open the configuration file for editing."""
        config_path = os.path.join(os.path.dirname(__file__), 'crawler_config.yaml')
        if os.path.exists(config_path):
            import subprocess
            try:
                subprocess.Popen(['notepad', config_path])
                self.log_message("[CONFIG] Opening configuration file for editing...")
            except:
                self.log_message("[CONFIG] Could not open config file. Edit manually: " + config_path)
        else:
            self.log_message("[ERROR] Configuration file not found")

    def test_features(self):
        """Test all advanced features."""
        self.log_message("[TEST] Testing advanced features...")
        
        # Test ML classification
        if self.nlp:
            test_text = "NASA Landsat 8 satellite data from 2020"
            doc = self.nlp(test_text)
            entities = [(ent.text, ent.label_) for ent in doc.ents]
            self.ml_console.append(f"[ML TEST] spaCy NER: {entities}")
        
        # Test geospatial validation
        if self.geocoder:
            self.validation_console.append("[VALIDATION TEST] Geocoder available")
        
        # Test config
        if self.config:
            self.console.append(f"[CONFIG TEST] Loaded {len(self.config.get('fields', []))} field definitions")
        
        # Test plugins
        if self.plugins:
            self.console.append(f"[PLUGIN TEST] Loaded {len(self.plugins)} plugins")
        
        self.log_message("[TEST] Feature testing completed!")

    def clear_all_consoles(self):
        """Clear all console tabs."""
        self.console.clear()
        self.ml_console.clear()
        self.validation_console.clear()
        self.error_console.clear()
        self.log_message("[CLEAR] All consoles cleared")

    def log_ml_classification(self, message):
        """Log ML classification results to the ML console."""
        self.ml_console.append(f"[{time.strftime('%H:%M:%S')}] {message}")

    def log_validation(self, message):
        """Log validation results to the validation console."""
        self.validation_console.append(f"[{time.strftime('%H:%M:%S')}] {message}")

    def log_error(self, message):
        """Log errors to the error console."""
        self.error_console.append(f"[{time.strftime('%H:%M:%S')}] {message}")

    def log_message(self, message):
        """Log messages to the main console."""
        self.log_queue.put(f"[{time.strftime('%H:%M:%S')}] {message}")

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select HTML File", "", "HTML Files (*.html *.htm);;All Files (*)"
        )
        if file_path:
            self.file_path_edit.setText(file_path)
            self.crawl_btn.setEnabled(True)
            self.log_message(f"Selected file: {file_path}")

    def start_crawl(self):
        """Start the advanced crawling process with all features enabled."""
        file_path = self.file_path_edit.text()
        if not file_path:
            self.log_message("No HTML file selected.")
            return
        
        if not os.path.exists(file_path):
            self.log_message(f"File not found: {file_path}")
            return
        
        # Update UI state
        self.crawl_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.browse_btn.setEnabled(False)
        self.progress.setValue(0)
        self.status.setText("Crawling in progress...")
        # Clear consoles
        self.clear_all_consoles()
        
        # Start crawling in a separate thread
        self.crawl_thread = threading.Thread(
            target=self.crawl_html_file,
            args=(file_path,),
            daemon=True
        )
        self.crawl_thread.start()
        
        # Start UI update timer
        self.timer.start(100)  # Update every 100ms
        
        self.log_message(f"Starting advanced crawl for: {file_path}")
        self.log_message("Advanced features enabled:")
        if self.nlp:
            self.log_message("  - spaCy NLP for text analysis")
        if self.bert_classifier:
            self.log_message("  - BERT for advanced text classification")
        if self.geocoder:
            self.log_message("  - Geospatial validation and enrichment")
        if self.dashboard:
            self.log_message("  - Analytics dashboard integration")

    def stop_crawl(self):
        """Stop the crawling process."""
        if hasattr(self, 'crawl_thread') and self.crawl_thread.is_alive():
            self.stop_requested = True
            self.log_message("Stopping crawler... Please wait for current operation to complete.")
            self.status.setText("Stopping...")

    def crawl_html_file(self, html_file):
        """Main crawling method with all advanced features."""
        try:
            self.stop_requested = False
            self.log_message("Reading HTML file...")
            
            # Read the HTML file
            with open(html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            self.log_message("Parsing HTML content...")
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find all dataset links
            links = soup.find_all('a', href=True)
            dataset_links = []
            
            for link in links:
                if self.stop_requested:
                    break
                
                href = link.get('href')
                if href and ('catalog' in href or 'datasets' in href):
                    # Convert relative URLs to absolute
                    if href.startswith('/'):
                        href = f"https://developers.google.com{href}"
                    elif not href.startswith('http'):
                        href = urljoin("https://developers.google.com/earth-engine/datasets/", href)
                    dataset_links.append(href)
            
            self.log_message(f"Found {len(dataset_links)} potential dataset links")
            
            # Remove duplicates
            dataset_links = list(set(dataset_links))
            self.log_message(f"Unique links to process: {len(dataset_links)}")
            
            if not dataset_links:
                self.log_message("No dataset links found. Processing as single page...")
                # Process the current page as a single dataset
                result = self.advanced_extract(soup, html_file)
                if result:
                    self.save_results([result])
                return
            
            # Setup webdriver for detailed crawling
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            options.add_argument('--window-size=1920,1080')
            # User-agent randomization
            user_agent = random.choice(USER_AGENTS)
            options.add_argument(f'user-agent={user_agent}')
            driver = webdriver.Edge(options=options)
            
            processed_count = 0
            total_links = len(dataset_links)
            results = []
            
            for i, link in enumerate(dataset_links):
                if self.stop_requested:
                    self.log_message("Crawling stopped by user")
                    break
                retry_count = 0
                max_retries = 3
                while retry_count <= max_retries:
                    try:
                        # Update progress
                        progress = int((i / total_links) * 100)
                        self.progress_queue.put(progress)
                        self.log_message(f"Processing link {i+1}/{total_links}: {link}")
                        driver.get(link)
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.TAG_NAME, "body"))
                        )
                        page_source = driver.page_source
                        page_soup = BeautifulSoup(page_source, 'html.parser')
                        dataset_info = self.advanced_extract(page_soup, link)
                        if dataset_info:
                            results.append(dataset_info)
                            processed_count += 1
                            self.log_message(f"Extracted: {dataset_info.get('title', 'Unknown')}")
                            if dataset_info.get('ml_classification'):
                                for field, ml_data in dataset_info['ml_classification'].items():
                                    if isinstance(ml_data, dict):
                                        self.log_ml_classification(f"{field}: {ml_data.get('label', 'Unknown')} (confidence: {ml_data.get('confidence', 0):.2f})")
                            if dataset_info.get('validation_results'):
                                for validation_type, result in dataset_info['validation_results'].items():
                                    status = "✅" if result.get('valid') else "❌"
                                    self.log_validation(f"{validation_type}: {status} {result.get('errors', [])}")
                        time.sleep(1)
                        break  # Success, break retry loop
                    except Exception as e:
                        retry_count += 1
                        delay = 2 ** retry_count
                        self.log_error(f"Error processing {link} (attempt {retry_count}): {str(e)}. Retrying in {delay}s...")
                        time.sleep(delay)
                        if retry_count > max_retries:
                            self.error_tracker['total_errors'] += 1
                            self.error_tracker['error_categories'][type(e).__name__] += 1
                            break

            driver.quit()
            
            # Save results
            if results:
                self.save_results(results)
                self.log_message(f"Crawling completed! Processed {processed_count} datasets successfully.")
                self.status.setText(f"Crawl completed - {processed_count} datasets extracted")
            else:
                self.log_message("No datasets were successfully extracted.")
                self.status.setText("Crawl completed - No data extracted")
            
            # Log error summary
            if self.error_tracker['total_errors'] > 0:
                self.log_error_summary()
            
        except Exception as e:
            error_msg = f"Crawling error: {str(e)}"
            self.log_error(error_msg)
            self.status.setText("Crawl failed")
        finally:
            # Reset UI state
            self.progress_queue.put(100)
            self.crawl_finished()

    def advanced_extract(self, soup, url):
        """Advanced extraction with ML classification and validation."""
        result = {
            'title': '', 'provider': '', 'tags': [], 'date_range': '', 'description': '',
            'bands': [], 'terms_of_use': '', 'snippet': '', 'spatial_coverage': '',
            'temporal_coverage': '', 'citation': '', 'type': '', 'region': '', 'source_url': url,
            'extraction_report': {}, 'confidence': {}, 'ml_classification': {}, 'validation_results': {}
        }
        
        # Extract basic information
        result = self.extract_basic_info(soup, result)
        
        # Apply ML classification
        if hasattr(self, 'use_ml_classification') and self.use_ml_classification.isChecked():
            result = self.apply_ml_classification(soup, result)
        
        # Apply validation
        if hasattr(self, 'use_validation') and self.use_validation.isChecked():
            result = self.apply_validation(result)
        
        # Apply ensemble methods
        if hasattr(self, 'use_ensemble') and self.use_ensemble.isChecked():
            result = self.apply_ensemble_methods(result)
        
        return result

    def extract_basic_info(self, soup, result):
        """Extract basic dataset information."""
        # Title
        title_elem = soup.find(['h1', 'title'])
        if title_elem:
            result['title'] = title_elem.get_text(strip=True)
            result['confidence']['title'] = 1.0
        else:
            meta_title = soup.find('meta', attrs={'property': 'og:title'})
            if meta_title and meta_title.get('content'):
                result['title'] = meta_title['content']
                result['confidence']['title'] = 0.9
        
        # Description
        desc_elem = soup.find('div', class_=re.compile(r'description|body|content|summary', re.IGNORECASE))
        if desc_elem:
            result['description'] = desc_elem.get_text(strip=True)[:500] + "..."
            result['confidence']['description'] = 1.0
        else:
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc and meta_desc.get('content'):
                result['description'] = meta_desc['content']
                result['confidence']['description'] = 0.8
        
        # Tags
        tags = set()
        tag_elems = soup.find_all(['span', 'div', 'a'], class_=re.compile(r'tag|chip|label|badge', re.IGNORECASE))
        for elem in tag_elems:
            tags.update([t.strip().title() for t in elem.get_text().split(',') if t.strip()])
        result['tags'] = list(tags)
        if result['tags']:
            result['confidence']['tags'] = 0.9
        
        # Provider
        provider_patterns = [r'Provider[:\s]+([^\n]+)', r'Source[:\s]+([^\n]+)', r'Organization[:\s]+([^\n]+)']
        for pattern in provider_patterns:
            match = re.search(pattern, soup.get_text(), re.IGNORECASE)
            if match:
                result['provider'] = match.group(1).strip()
                result['confidence']['provider'] = 0.8
                break
        
        return result

    def apply_ml_classification(self, soup, result):
        """Apply ML classification to extracted data."""
        ml_results = {}
        
        # spaCy NER
        if self.nlp:
            text = soup.get_text()[:1000]  # Limit text length
            doc = self.nlp(text)
            
            # Extract entities
            entities = {}
            for ent in doc.ents:
                if ent.label_ not in entities:
                    entities[ent.label_] = []
                entities[ent.label_].append(ent.text)
            
            ml_results['spacy_entities'] = entities
            
            # Classify title if available
            if result['title']:
                title_doc = self.nlp(result['title'])
                title_entities = [(ent.text, ent.label_) for ent in title_doc.ents]
                ml_results['title_entities'] = title_entities
        
        # BERT classification
        if self.bert_classifier:
            try:
                if result['title']:
                    bert_result = self.bert_classifier(result['title'])
                    ml_results['bert_classification'] = bert_result
            except Exception as e:
                self.log_error(f"BERT classification error: {e}")
        
        # Fallback keyword extraction if spaCy/BERT unavailable
        if not self.nlp and not self.bert_classifier:
            text = soup.get_text()[:1000]
            keywords = set(re.findall(r'\b[A-Za-z]{5,}\b', text))
            ml_results['keywords'] = list(keywords)[:20]

        result['ml_classification'] = ml_results
        return result

    def apply_validation(self, result):
        """Apply data validation."""
        validation_results = {}
        
        # Spatial validation
        if self.geocoder:
            spatial_result = self.validate_spatial_data(result)
            validation_results['spatial'] = spatial_result
        
        # Temporal validation
        temporal_result = self.validate_temporal_data(result)
        validation_results['temporal'] = temporal_result
        
        # Data quality validation
        quality_result = self.validate_data_quality(result)
        validation_results['quality'] = quality_result
        
        result['validation_results'] = validation_results
        return result

    def apply_ensemble_methods(self, result):
        """Apply ensemble ML methods."""
        if self.tfidf_vectorizer and result['title']:
            try:
                # TF-IDF analysis
                tfidf_result = self.tfidf_vectorizer.fit_transform([result['title']])
                if hasattr(tfidf_result, 'shape') and len(tfidf_result.shape) > 1:
                    result['ensemble_features'] = {
                        'tfidf_features': tfidf_result.shape[1],
                        'text_length': len(result['title'])
                    }
                else:
                    result['ensemble_features'] = {
                        'tfidf_features': 0,
                        'text_length': len(result['title'])
                    }
            except Exception as e:
                self.log_error(f"Ensemble method error: {e}")
        
        return result

    def validate_spatial_data(self, data):
        """Validate spatial information."""
        result = {'valid': False, 'errors': [], 'enriched': {}}
        
        try:
            # Look for geographic references
            text = data.get('title', '') + ' ' + data.get('description', '')
            geographic_terms = ['global', 'worldwide', 'continental', 'regional', 'local']
            
            for term in geographic_terms:
                if term.lower() in text.lower():
                    result['enriched']['spatial_scope'] = term
                    result['valid'] = True
                    break
            
            # Try geocoding if specific location mentioned
            if self.geocoder:
                # Look for country names, cities, etc.
                location_patterns = [
                    r'\b[A-Z][a-z]+(?:[-\s][A-Z][a-z]+)*\b',  # Capitalized words
                ]
                
                for pattern in location_patterns:
                    matches = re.findall(pattern, text)
                    for match in matches:
                        if len(match) > 3:  # Avoid short words
                            try:
                                location = self.geocoder.geocode(match, timeout=5)
                                if location:
                                    result['enriched']['geocoded_location'] = {
                                        'name': match,
                                        'coordinates': (location.latitude, location.longitude)
                                    }
                                    result['valid'] = True
                                    break
                            except:
                                continue
                
        except Exception as e:
            result['errors'].append(f"Spatial validation error: {e}")
        
        return result

    def validate_temporal_data(self, data):
        """Validate temporal information."""
        result = {'valid': False, 'errors': [], 'enriched': {}}
        
        try:
            text = data.get('title', '') + ' ' + data.get('description', '')
            
            # Look for date patterns
            date_patterns = [
                r'\b\d{4}-\d{2}-\d{2}\b',  # YYYY-MM-DD
                r'\b\d{4}\b',  # Year
                r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\b',  # Month Year
            ]
            
            for pattern in date_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    result['enriched']['temporal_references'] = matches
                    result['valid'] = True
                    break
            
            # Look for temporal keywords
            temporal_keywords = ['historical', 'current', 'recent', 'archived', 'ongoing', 'continuous']
            for keyword in temporal_keywords:
                if keyword.lower() in text.lower():
                    result['enriched']['temporal_keyword'] = keyword
                    result['valid'] = True
                    break
                
            # Fuzzy date parsing if dateparser is available
            if dateparser:
                fuzzy_dates = []
                for match in re.findall(r'\b\d{4}-\d{2}-\d{2}\b|\b\d{4}\b', text):
                    dt = dateparser.parse(match)
                    if dt:
                        fuzzy_dates.append(str(dt.date()))
                if fuzzy_dates:
                    result['enriched']['fuzzy_dates'] = fuzzy_dates
                    result['valid'] = True

        except Exception as e:
            result['errors'].append(f"Temporal validation error: {e}")
        
        return result

    def validate_data_quality(self, data):
        """Validate overall data quality."""
        result = {'valid': False, 'score': 0, 'errors': [], 'enriched': {}}
        
        try:
            score = 0
            max_score = 100
            
            # Title quality
            if data.get('title'):
                score += 20
                if len(data['title']) > 10:
                    score += 10
            
            # Description quality
            if data.get('description'):
                score += 20
                if len(data['description']) > 50:
                    score += 10
            
            # Tags quality
            if data.get('tags'):
                score += 15
                if len(data['tags']) > 2:
                    score += 5
            
            # Provider quality
            if data.get('provider'):
                score += 10
            
            # ML classification quality
            if data.get('ml_classification'):
                score += 10
            
            result['score'] = min(score, max_score)
            result['valid'] = score >= 50
            result['enriched']['quality_score'] = score
            
        except Exception as e:
            result['errors'].append(f"Quality validation error: {e}")
        
        return result

    def save_results(self, results):
        """Save crawling results to files."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Create output directory
            os.makedirs(self.output_dir, exist_ok=True)
            
            # Save as JSON
            json_file = os.path.join(self.output_dir, f"enhanced_crawl_results_{timestamp}.json")
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            # Save individual files if requested
            if hasattr(self, 'save_individual') and self.save_individual.isChecked():
                for i, result in enumerate(results):
                    individual_file = os.path.join(self.output_dir, f"dataset_{i+1}_{timestamp}.json")
                    with open(individual_file, 'w', encoding='utf-8') as f:
                        json.dump(result, f, indent=2, ensure_ascii=False)
            
            # CSV export
            try:
                csv_file = os.path.join(self.output_dir, f"enhanced_crawl_results_{timestamp}.csv")
                with open(csv_file, 'w', encoding='utf-8', newline='') as f:
                    if results:
                        fieldnames = list(results[0].keys())
                        writer = csv.DictWriter(f, fieldnames=fieldnames)
                        writer.writeheader()
                        for row in results:
                            writer.writerow(row)
                self.log_message(f"Results also saved to: {csv_file}")
            except Exception as e:
                self.log_error(f"Error saving CSV: {e}")
            
            self.log_message(f"Results saved to: {json_file}")
            
            # Update dashboard
            if self.dashboard:
                try:
                    for result in results:
                        self.dashboard.add_data(result)
                except Exception as e:
                    self.log_error(f"Dashboard update error: {e}")
            
        except Exception as e:
            self.log_error(f"Error saving results: {e}")

    def log_error_summary(self):
        """Log a summary of all errors encountered."""
        if self.error_tracker['total_errors'] == 0:
            self.log_message("No errors encountered during crawling!")
            return
        
        self.log_error(f"Error Summary:")
        self.log_error(f"  Total errors: {self.error_tracker['total_errors']}")
        self.log_error(f"  Retry attempts: {self.error_tracker['retry_attempts']}")
        self.log_error(f"  Recovered results: {self.error_tracker['recovered_results']}")
        
        if self.error_tracker['error_categories']:
            self.log_error("  Error categories:")
            for category, count in self.error_tracker['error_categories'].items():
                self.log_error(f"    - {category}: {count}")

    def crawl_finished(self):
        """Handle crawl completion."""
        # Reset UI state
        self.crawl_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.browse_btn.setEnabled(True)
        self.timer.stop()
        
        # Update status indicators
        self.update_status_indicators()

        # Update summary tab
        summary = f"Total datasets: {len(getattr(self, 'results', []))}\n"
        summary += f"Total errors: {self.error_tracker['total_errors']}\n"
        summary += f"Error categories: {dict(self.error_tracker['error_categories'])}\n"
        self.summary_console.setPlainText(summary)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = EnhancedCrawlerUI()
    win.show()
    sys.exit(app.exec()) 