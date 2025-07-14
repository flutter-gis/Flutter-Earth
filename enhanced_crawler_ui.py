import sys
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
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, 
    QProgressBar, QLabel, QFileDialog, QLineEdit, QGroupBox, QCheckBox, QTabWidget
)
from PySide6.QtCore import QTimer, Qt, QThread
import csv
from collections import defaultdict

# Advanced imports with fallbacks
spacy = None
transformers = None
geopy = None
dash = None
plotly = None

try:
    import spacy
except ImportError:
    print("spaCy not available - ML/NLP features disabled")

try:
    import transformers
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
except ImportError:
    print("Transformers not available - BERT features disabled")

try:
    from sklearn.ensemble import VotingClassifier
    from sklearn.feature_extraction.text import TfidfVectorizer
    import numpy as np
except ImportError:
    print("Scikit-learn not available - some ML features disabled")

try:
    from geopy.geocoders import Nominatim
    from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
    geopy = True
except ImportError:
    print("Geopy not available - geospatial validation disabled")

try:
    import yaml
    from config_utils import load_config, load_plugins
except ImportError:
    print("YAML/config_utils not available - config features disabled")

try:
    from analytics_dashboard import get_dashboard
    dash = True
except ImportError:
    print("Dash not available - analytics dashboard disabled")

from datetime import datetime

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
            if 'yaml' in globals() and 'load_config' in globals():
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
        self.update_status_indicators()

    def update_status_indicators(self):
        """Update the status indicators for advanced features."""
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
import sys
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
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, 
    QProgressBar, QLabel, QFileDialog, QLineEdit, QGroupBox, QCheckBox
)
from PySide6.QtCore import QTimer, Qt, QThread
import csv
from collections import defaultdict

# Advanced imports with fallbacks
spacy = None
transformers = None
geopy = None
dash = None
plotly = None

try:
    import spacy
except ImportError:
    print("spaCy not available - ML/NLP features disabled")

try:
    import transformers
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
except ImportError:
    print("Transformers not available - BERT features disabled")

try:
    from sklearn.ensemble import VotingClassifier
    from sklearn.feature_extraction.text import TfidfVectorizer
    import numpy as np
except ImportError:
    print("Scikit-learn not available - some ML features disabled")

try:
    from geopy.geocoders import Nominatim
    from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
    geopy = True
except ImportError:
    print("Geopy not available - geospatial validation disabled")

try:
    import yaml
    from config_utils import load_config, load_plugins
except ImportError:
    print("YAML/config_utils not available - config features disabled")

try:
    from analytics_dashboard import get_dashboard
    dash = True
except ImportError:
    print("Dash not available - analytics dashboard disabled")

from datetime import datetime

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
            if 'yaml' in globals() and 'load_config' in globals():
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

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
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
        
        # Options group
        options_group = QGroupBox("Crawling Options")
        options_layout = QVBoxLayout()
        self.download_thumbs = QCheckBox("Download thumbnails")
        self.download_thumbs.setChecked(True)
        self.extract_details = QCheckBox("Extract detailed information")
        self.extract_details.setChecked(True)
        self.save_individual = QCheckBox("Save as individual JSON files")
        self.save_individual.setChecked(True)
        options_layout.addWidget(self.download_thumbs)
        options_layout.addWidget(self.extract_details)
        options_layout.addWidget(self.save_individual)
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # Status and progress
        self.status = QLabel("Ready. Select an HTML file to begin.")
        layout.addWidget(self.status)
        
        self.progress = QProgressBar()
        self.progress.setMaximum(100)
        self.progress.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress.setStyleSheet("QProgressBar {height: 30px; font-size: 16px;} QProgressBar::chunk {background: #3a6ea5;}")
        layout.addWidget(self.progress)
        
        # Console output
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setStyleSheet("background: #181818; color: #e0e0e0; font-family: Consolas; font-size: 12px;")
        layout.addWidget(self.console, 1)
        
        # Control buttons
        button_layout = QHBoxLayout()
        self.crawl_btn = QPushButton("Start Crawling")
        self.crawl_btn.clicked.connect(self.start_crawl)
        self.crawl_btn.setEnabled(False)
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.clicked.connect(self.stop_crawl)
        self.stop_btn.setEnabled(False)
        self.clear_btn = QPushButton("Clear Console")
        self.clear_btn.clicked.connect(self.console.clear)
        button_layout.addWidget(self.crawl_btn)
        button_layout.addWidget(self.stop_btn)
        button_layout.addWidget(self.clear_btn)
        layout.addLayout(button_layout)

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select HTML File", "", "HTML Files (*.html *.htm);;All Files (*)"
        )
        if file_path:
            self.file_path_edit.setText(file_path)
            self.crawl_btn.setEnabled(True)
            self.log_message(f"Selected file: {file_path}")

    def log_message(self, message):
        self.log_queue.put(f"[{time.strftime('%H:%M:%S')}] {message}")

    def log_sectioned(self, info_dict):
        """Log info in clear, separated sections."""
        for key, value in info_dict.items():
            if value:
                self.log_message(f"[{key.upper()}] {value}")
        self.log_message("-")

    def ml_classify_field(self, text):
        """Classify and normalize a field using spaCy NER and text categorization."""
        if not self.nlp or not text or not isinstance(text, str):
            return None, 0.0, None
        doc = self.nlp(text)
        # Try to extract entities and label
        if doc.ents:
            # Use the first entity as the label
            ent = doc.ents[0]
            return ent.label_, 0.9, ent.text
        # Fallback: use textcat if available
        if hasattr(self.nlp, 'textcat') and self.nlp.textcat is not None:
            cats = self.nlp(text).cats
            if cats:
                best = max(cats, key=cats.get)
                return best, cats[best], text
        return None, 0.0, None

    def advanced_extract(self, soup, link):
        """Advanced extraction and classification for a dataset page, with config-driven extraction and plugin support."""
        result = {
            'title': '', 'provider': '', 'tags': [], 'date_range': '', 'description': '',
            'bands': [], 'terms_of_use': '', 'snippet': '', 'spatial_coverage': '',
            'temporal_coverage': '', 'citation': '', 'type': '', 'region': '', 'source_url': link,
            'extraction_report': {}, 'confidence': {}, 'ml_classification': {}
        }
        report = {}
        confidence = {}
        ml_classification = {}
        
        # Use config-driven extraction if available
        if self.config and 'fields' in self.config:
            for field_config in self.config['fields']:
                field_name = field_config['name']
                selectors = field_config.get('selectors', [])
                ml_types = field_config.get('ml_types', [])
                
                # Extract using config selectors
                extracted_value = self.extract_with_selectors(soup, selectors, field_name)
                if extracted_value:
                    result[field_name] = extracted_value
                    report[field_name] = f"config selectors: {', '.join(selectors)}"
                    confidence[field_name] = 0.8
                    
                    # ML classification with config-defined types
                    label, conf, norm = self.ml_classify_field_with_types(extracted_value, ml_types)
                    if label:
                        ml_classification[field_name] = {'label': label, 'confidence': conf, 'normalized': norm}
                
                # Use plugins for specialized processing
                if field_name == 'bands' and self.plugins and 'custom_band_parser' in self.plugins:
                    try:
                        plugin_bands = self.plugins['custom_band_parser'].parse_bands(soup)
                        if plugin_bands:
                            result['bands'] = plugin_bands
                            report['bands'] = 'custom_band_parser plugin'
                            confidence['bands'] = 0.9
                    except Exception as e:
                        self.log_message(f"[PLUGIN ERROR] Band parser failed: {e}")
        else:
            # Fallback to original extraction logic
            result = self.fallback_extraction(soup, link)
            report = result['extraction_report']
            confidence = result['confidence']
            ml_classification = result['ml_classification']
        
        # Apply OCR to thumbnails if plugin available
        if self.plugins and 'thumbnail_ocr' in self.plugins and result.get('thumbnail_url'):
            try:
                ocr_text = self.plugins['thumbnail_ocr'].extract_text_from_thumbnail(result['thumbnail_url'])
                if ocr_text and not ocr_text.startswith('[OCR ERROR]'):
                    result['thumbnail_ocr_text'] = ocr_text
                    report['thumbnail_ocr_text'] = 'thumbnail_ocr plugin'
                    confidence['thumbnail_ocr_text'] = 0.7
            except Exception as e:
                self.log_message(f"[PLUGIN ERROR] OCR failed: {e}")
        
        result['extraction_report'] = report
        result['confidence'] = confidence
        result['ml_classification'] = ml_classification
        
        # Apply validation and enrichment
        result = self.validate_and_enrich_data(result)
        
        # Add to analytics dashboard
        if self.dashboard:
            try:
                self.dashboard.add_data(result)
            except Exception as e:
                self.log_message(f"[DASHBOARD ERROR] {e}")
        
        return result

    def extract_with_selectors(self, soup, selectors, field_name):
        """Extract field value using config-defined selectors."""
        for selector in selectors:
            try:
                if selector.startswith('meta['):
                    # Handle meta tag selectors
                    attr_name = selector.split('[')[1].split('=')[0]
                    attr_value = selector.split('=')[1].rstrip(']').strip('"\'')
                    meta = soup.find('meta', attrs={attr_name: attr_value})
                    if meta and meta.get('content'):
                        return meta['content']
                else:
                    # Handle regular CSS selectors
                    elements = soup.select(selector)
                    if elements:
                        if field_name == 'tags':
                            # Handle multiple tags
                            tags = []
                            for elem in elements:
                                tags.extend([t.strip() for t in elem.get_text().split(',') if t.strip()])
                            return list(set(tags))  # Remove duplicates
                        else:
                            return elements[0].get_text(strip=True)
            except Exception as e:
                continue
        return None

    def ml_classify_field_with_types(self, text, expected_types):
        """Classify field with specific expected ML types from config using ensemble methods."""
        return self.ensemble_ml_classify(text, expected_types)

    def fallback_extraction(self, soup, link):
        """Original extraction logic as fallback when config is not available."""
        # This is the original advanced_extract logic
        result = {
            'title': '', 'provider': '', 'tags': [], 'date_range': '', 'description': '',
            'bands': [], 'terms_of_use': '', 'snippet': '', 'spatial_coverage': '',
            'temporal_coverage': '', 'citation': '', 'type': '', 'region': '', 'source_url': link,
            'extraction_report': {}, 'confidence': {}, 'ml_classification': {}
        }
        report = {}
        confidence = {}
        ml_classification = {}
        
        # Title
        title = ''
        title_elem = soup.find(['h1', 'title'])
        if title_elem:
            title = title_elem.get_text(strip=True)
            report['title'] = 'h1/title tag'
            confidence['title'] = 1.0
        else:
            meta_title = soup.find('meta', attrs={'property': 'og:title'})
            if meta_title and meta_title.get('content'):
                title = meta_title['content']
                report['title'] = 'og:title meta'
                confidence['title'] = 1.0
            else:
                confidence['title'] = 0.7
        result['title'] = title
        label, conf, norm = self.ml_classify_field(title)
        if label:
            ml_classification['title'] = {'label': label, 'confidence': conf, 'normalized': norm}
        
        # Provider
        provider = ''
        prov_elem = soup.find(string=re.compile(r'Provider|Source|Agency|Organization', re.IGNORECASE))
        if prov_elem:
            provider = prov_elem.strip()
            report['provider'] = 'text match'
            confidence['provider'] = 0.7
        else:
            meta_provider = soup.find('meta', attrs={'name': 'provider'})
            if meta_provider and meta_provider.get('content'):
                provider = meta_provider['content']
                report['provider'] = 'meta[name=provider]'
                confidence['provider'] = 1.0
            else:
                confidence['provider'] = 0.5
        result['provider'] = provider
        label, conf, norm = self.ml_classify_field(provider)
        if label:
            ml_classification['provider'] = {'label': label, 'confidence': conf, 'normalized': norm}
        
        # Tags
        tags = set()
        tag_elems = soup.find_all(['span', 'div', 'a'], class_=re.compile(r'tag|chip|label|badge', re.IGNORECASE))
        if tag_elems:
            confidence['tags'] = 1.0
        for elem in tag_elems:
            tags.update([t.strip().title() for t in elem.get_text().split(',') if t.strip()])
        tag_text = soup.find(string=re.compile(r'Tags', re.IGNORECASE))
        if tag_text:
            tags.update([t.strip().title() for t in re.split(r'[^a-z0-9\-]+', tag_text, flags=re.IGNORECASE) if t.strip()])
            confidence['tags'] = 0.7
        if not tags:
            confidence['tags'] = 0.5
        result['tags'] = list(tags)
        report['tags'] = 'class/tag/chip/label/badge or text'
        label, conf, norm = self.ml_classify_field(", ".join(result['tags']))
        if label:
            ml_classification['tags'] = {'label': label, 'confidence': conf, 'normalized': norm}
        
        # Date Range
        date_range = ''
        date_elem = soup.find(string=re.compile(r'\d{4}-\d{2}-\d{2}.*[–-].*\d{4}-\d{2}-\d{2}', re.IGNORECASE))
        if date_elem:
            date_range = date_elem.strip().replace('–', ' to ').replace('-', ' to ', 1)
            report['date_range'] = 'text match'
            confidence['date_range'] = 0.7
        else:
            confidence['date_range'] = 0.5
        result['date_range'] = date_range
        label, conf, norm = self.ml_classify_field(date_range)
        if label:
            ml_classification['date_range'] = {'label': label, 'confidence': conf, 'normalized': norm}
        
        # Description
        desc = ''
        desc_elem = soup.find('div', class_=re.compile(r'description|body|content|summary', re.IGNORECASE))
        if desc_elem:
            desc = desc_elem.get_text(strip=True)
            report['description'] = 'div.description/body/content/summary'
            confidence['description'] = 1.0
        else:
            for p in soup.find_all('p'):
                if len(p.get_text(strip=True)) > 50:
                    desc = p.get_text(strip=True)
                    report['description'] = 'first long <p>'
                    confidence['description'] = 0.7
                    break
            if not desc:
                confidence['description'] = 0.5
        result['description'] = desc
        label, conf, norm = self.ml_classify_field(desc)
        if label:
            ml_classification['description'] = {'label': label, 'confidence': conf, 'normalized': norm}
        
        # Bands
        bands = []
        bands_table = soup.find('table', class_=re.compile(r'band', re.IGNORECASE))
        if bands_table:
            for row in bands_table.find_all('tr'):
                cols = row.find_all(['td', 'th'])
                if len(cols) >= 2:
                    bands.append(f"{cols[0].get_text(strip=True)}: {cols[1].get_text(strip=True)}")
            report['bands'] = 'table.band'
            confidence['bands'] = 1.0
        else:
            bands_text = soup.find(string=re.compile(r'Bands', re.IGNORECASE))
            if bands_text:
                bands.append(bands_text.strip())
                report['bands'] = 'text match'
                confidence['bands'] = 0.7
            else:
                confidence['bands'] = 0.5
        result['bands'] = bands
        label, conf, norm = self.ml_classify_field(", ".join(bands))
        if label:
            ml_classification['bands'] = {'label': label, 'confidence': conf, 'normalized': norm}
        
        # Terms of Use
        terms = ''
        terms_elem = soup.find(string=re.compile(r'Terms of Use|License|Copyright', re.IGNORECASE))
        if terms_elem:
            terms = terms_elem.strip()
            report['terms_of_use'] = 'text match'
            confidence['terms_of_use'] = 0.7
        else:
            confidence['terms_of_use'] = 0.5
        result['terms_of_use'] = terms
        label, conf, norm = self.ml_classify_field(terms)
        if label:
            ml_classification['terms_of_use'] = {'label': label, 'confidence': conf, 'normalized': norm}
        
        # Snippet
        snippet = ''
        snippet_elem = soup.find(string=re.compile(r'ee\.', re.IGNORECASE))
        if snippet_elem:
            snippet = snippet_elem.strip()
            report['snippet'] = 'text match'
            confidence['snippet'] = 0.7
        else:
            confidence['snippet'] = 0.5
        result['snippet'] = snippet
        label, conf, norm = self.ml_classify_field(snippet)
        if label:
            ml_classification['snippet'] = {'label': label, 'confidence': conf, 'normalized': norm}
        
        # Spatial Coverage
        spatial = ''
        spatial_elem = soup.find(string=re.compile(r'Lat:|Lon:|Bounding Box|Extent', re.IGNORECASE))
        if spatial_elem:
            spatial = spatial_elem.strip()
            report['spatial_coverage'] = 'text match'
            confidence['spatial_coverage'] = 0.7
        else:
            confidence['spatial_coverage'] = 0.5
        result['spatial_coverage'] = spatial
        label, conf, norm = self.ml_classify_field(spatial)
        if label:
            ml_classification['spatial_coverage'] = {'label': label, 'confidence': conf, 'normalized': norm}
        
        # Temporal Coverage
        temporal = ''
        temporal_elem = soup.find(string=re.compile(r'Period|Temporal|Time', re.IGNORECASE))
        if temporal_elem:
            temporal = temporal_elem.strip()
            report['temporal_coverage'] = 'text match'
            confidence['temporal_coverage'] = 0.7
        else:
            confidence['temporal_coverage'] = 0.5
        result['temporal_coverage'] = temporal
        label, conf, norm = self.ml_classify_field(temporal)
        if label:
            ml_classification['temporal_coverage'] = {'label': label, 'confidence': conf, 'normalized': norm}
        
        # Citation
        citation = ''
        citation_elem = soup.find(string=re.compile(r'Citation|How to Cite', re.IGNORECASE))
        if citation_elem:
            citation = citation_elem.strip()
            report['citation'] = 'text match'
            confidence['citation'] = 0.7
        else:
            confidence['citation'] = 0.5
        result['citation'] = citation
        label, conf, norm = self.ml_classify_field(citation)
        if label:
            ml_classification['citation'] = {'label': label, 'confidence': conf, 'normalized': norm}
        
        # Type
        dtype = ''
        if any(x in desc.lower() for x in ['raster', 'image', 'pixel']):
            dtype = 'Raster'
            confidence['type'] = 0.7
        elif any(x in desc.lower() for x in ['vector', 'feature', 'polygon', 'point', 'line']):
            dtype = 'Vector'
            confidence['type'] = 0.7
        else:
            confidence['type'] = 0.5
        result['type'] = dtype
        report['type'] = 'inferred from description'
        label, conf, norm = self.ml_classify_field(dtype)
        if label:
            ml_classification['type'] = {'label': label, 'confidence': conf, 'normalized': norm}
        
        # Region
        region = ''
        region_elem = soup.find(string=re.compile(r'Region|Country|Area', re.IGNORECASE))
        if region_elem:
            region = region_elem.strip()
            report['region'] = 'text match'
            confidence['region'] = 0.7
        else:
            confidence['region'] = 0.5
        result['region'] = region
        label, conf, norm = self.ml_classify_field(region)
        if label:
            ml_classification['region'] = {'label': label, 'confidence': conf, 'normalized': norm}
        
        result['extraction_report'] = report
        result['confidence'] = confidence
        result['ml_classification'] = ml_classification
        return result

    def log_advanced_sectioned(self, info_dict):
        """Log info in clear, separated sections with extraction method/confidence and ML classification."""
        for key, value in info_dict.items():
            if key in ('extraction_report', 'confidence', 'ml_classification'):
                continue
            if value:
                method = info_dict['extraction_report'].get(key, '')
                conf_score = info_dict['confidence'].get(key, '')
                ml_info = info_dict.get('ml_classification', {}).get(key, {})
                
                log_msg = f"[{key.upper()}] {value}"
                if method:
                    log_msg += f" (method: {method})"
                if conf_score:
                    log_msg += f" (confidence: {conf_score})"
                if ml_info:
                    log_msg += f" (ML: {ml_info.get('label', 'N/A')} @ {ml_info.get('confidence', 0):.2f})"
                
                self.log_message(log_msg)
        self.log_message("-")

    def pre_scan_link(self, link, driver, summary_table):
        try:
            self.log_message(f"[PRE-SCAN] Analyzing: {link}")
            
            # Use intelligent retry for page loading
            def load_page():
                driver.get(link)
                return driver.page_source
            
            page_html = self.intelligent_retry(load_page)
            if not page_html:
                raise Exception("Failed to load page content")
                
            soup = BeautifulSoup(page_html, 'html.parser')
            
            # Use intelligent retry for extraction
            def extract_data():
                return self.advanced_extract(soup, link)
            
            info = self.intelligent_retry(extract_data)
            self.log_advanced_sectioned(info)
            summary_table.append({
                'url': link,
                'fields_found': [k for k, v in info.items() if v and k not in ('extraction_report', 'confidence', 'ml_classification', 'validation_results')],
                'confidence': info['confidence'],
                'ml_classification': info.get('ml_classification', {})
            })
            self.log_message(f"[PRE-SCAN] Completed analysis for: {link}")
            
        except Exception as e:
            error_category = self.categorize_error(e)
            self.log_message(f"[ERROR] Pre-scan failed for {link}: {error_category} - {str(e)}")
            
            # Attempt partial result recovery
            try:
                # Create a minimal soup for recovery if page_html is available
                recovery_soup = None
                if 'page_html' in locals() and page_html:
                    recovery_soup = BeautifulSoup(page_html, 'html.parser')
                
                partial_result = self.recover_partial_results(recovery_soup, link, e)
                if partial_result and (partial_result.get('title') or partial_result.get('description')):
                    summary_table.append({
                        'url': link,
                        'fields_found': [k for k, v in partial_result.items() if v and k not in ('extraction_report', 'confidence', 'ml_classification', 'validation_results', 'recovery_error')],
                        'confidence': partial_result['confidence'],
                        'ml_classification': partial_result.get('ml_classification', {}),
                        'recovered': True
                    })
                    self.log_message(f"[RECOVERY] Partial results saved for {link}")
            except Exception as recovery_error:
                self.log_message(f"[RECOVERY FAILED] Could not recover partial results for {link}: {str(recovery_error)}")

    def start_crawl(self):
        html_file = self.file_path_edit.text()
        if not html_file or not os.path.exists(html_file):
            self.log_message("ERROR: Please select a valid HTML file")
            return
        
        self.console.clear()
        self.status.setText("Crawling...")
        self.progress.setValue(0)
        self.crawl_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.browse_btn.setEnabled(False)
        
        self.thread = threading.Thread(
            target=self.crawl_html_file, 
            args=(html_file, self.log_queue, self.progress_queue),
            daemon=True
        )
        if hasattr(self.thread, 'start'):
            self.thread.start()
        self.timer.start(100)

    def stop_crawl(self):
        if self.thread and hasattr(self.thread, 'is_alive') and self.thread.is_alive():
            self.log_message("Stopping crawler...")
            self.stop_requested = True

    def update_ui(self):
        # Process log messages
        while not self.log_queue.empty():
            msg = self.log_queue.get()
            self.console.append(msg)
            # Auto-scroll to bottom
            self.console.verticalScrollBar().setValue(self.console.verticalScrollBar().maximum())
            # Force update
            self.console.repaint()
            if "[DONE]" in msg or "[ERROR]" in msg:
                self.status.setText("Done!")
                self.crawl_btn.setEnabled(True)
                self.stop_btn.setEnabled(False)
                self.browse_btn.setEnabled(True)
        
        # Process progress updates
        while not self.progress_queue.empty():
            val = self.progress_queue.get()
            self.progress.setValue(val)
        
        # Check if thread has finished
        if self.thread and hasattr(self.thread, 'is_alive') and not self.thread.is_alive():
            self.timer.stop()
            self.crawl_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.browse_btn.setEnabled(True)
            self.status.setText("Done!")

    def export_summary(self, summary_table):
        # Export as JSON
        with open('summary.json', 'w', encoding='utf-8') as f:
            json.dump(summary_table, f, ensure_ascii=False, indent=2)
        # Export as CSV
        if not summary_table:
            return
        # Collect all possible field names
        all_fields = set()
        all_conf_fields = set()
        all_ml_fields = set()
        for entry in summary_table:
            all_fields.update(entry['fields_found'])
            all_conf_fields.update(entry.get('confidence', {}).keys())
            all_ml_fields.update(entry.get('ml_classification', {}).keys())
        all_fields = sorted(list(all_fields))
        all_conf_fields = sorted(list(all_conf_fields))
        all_ml_fields = sorted(list(all_ml_fields))
        with open('summary.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            header = ['url'] + all_fields + [f'conf_{field}' for field in all_conf_fields] + [f'ml_label_{field}' for field in all_ml_fields] + [f'ml_conf_{field}' for field in all_ml_fields]
            writer.writerow(header)
            for entry in summary_table:
                row = [entry['url']]
                for field in all_fields:
                    row.append('Y' if field in entry['fields_found'] else '')
                for field in all_conf_fields:
                    row.append(entry.get('confidence', {}).get(field, ''))
                for field in all_ml_fields:
                    ml_info = entry.get('ml_classification', {}).get(field, {})
                    row.append(ml_info.get('label', ''))
                for field in all_ml_fields:
                    ml_info = entry.get('ml_classification', {}).get(field, {})
                    row.append(ml_info.get('confidence', ''))
                writer.writerow(row)

    def crawl_html_file(self, html_file, log_queue, progress_queue):
        try:
            log_queue.put(f"Starting crawl of: {html_file}")
            with open(html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            log_queue.put("Parsing HTML content...")
            soup = BeautifulSoup(html_content, 'html.parser')
            links = soup.find_all('a', href=True)
            dataset_links = []
            for link in links:
                # Only call get('href') if link is a Tag (not NavigableString/PageElement)
                from bs4 import Tag
                if isinstance(link, Tag):
                    href = link.get('href')
                    if href and isinstance(href, str) and ('catalog' in href or 'datasets' in href):
                        if href.startswith('/'):
                            href = f"https://developers.google.com{href}"
                        elif not href.startswith('http'):
                            href = urljoin("https://developers.google.com/earth-engine/datasets/", href)
                        dataset_links.append(href)
            log_queue.put(f"Found {len(dataset_links)} potential dataset links")
            dataset_links = list(set(dataset_links))
            log_queue.put(f"Unique links to process: {len(dataset_links)}")
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            options.add_argument('--window-size=1920,1080')
            driver = webdriver.Edge(options=options)
            # --- ADVANCED PRE-SCAN PHASE ---
            log_queue.put("[PRE-SCAN] Advanced analysis of all links for key structures...")
            summary_table = []
            for i, link in enumerate(dataset_links):
                self.pre_scan_link(link, driver, summary_table)
                progress = int((i + 1) / len(dataset_links) * 10)
                progress_queue.put(progress)
            log_queue.put("[PRE-SCAN] Complete. Proceeding to download/extraction phase.")
            # Output summary table
            log_queue.put("[SUMMARY TABLE]")
            for entry in summary_table:
                log_queue.put(f"URL: {entry['url']}")
                log_queue.put(f"Fields found: {', '.join(entry['fields_found'])}")
                log_queue.put(f"Confidence: {entry['confidence']}")
                log_queue.put("-")
            # Export summary
            self.export_summary(summary_table)
            log_queue.put("[SUMMARY TABLE EXPORTED as summary.json and summary.csv]")
            # --- NORMAL CRAWL PHASE (as before) ---
            processed_count = 0
            total_links = len(dataset_links)
            for i, link in enumerate(dataset_links):
                if hasattr(self, 'stop_requested') and self.stop_requested:
                    log_queue.put("Crawling stopped by user")
                    break
                try:
                    log_queue.put(f"Processing {i+1}/{total_links}: {link}")
                    driver.get(link)
                    time.sleep(2)
                    page_html = driver.page_source
                    page_soup = BeautifulSoup(page_html, 'html.parser')
                    dataset_data = self.extract_dataset_info(page_soup, link)
                    if dataset_data:
                        # Download thumbnail if requested
                        if self.download_thumbs.isChecked() and dataset_data.get('thumbnail_url'):
                            thumb_path = self.download_image(dataset_data['thumbnail_url'])
                            dataset_data['thumbnail_path'] = thumb_path
                        
                        # Save as individual JSON file
                        if self.save_individual.isChecked():
                            safe_title = "".join(c for c in dataset_data.get('title', 'dataset') if c.isalnum() or c in (' ', '-', '_')).rstrip()
                            safe_title = safe_title[:50]  # Limit length
                            json_filename = f"{safe_title}_{i}.json"
                            json_path = os.path.join(self.output_dir, json_filename)
                            
                            with open(json_path, 'w', encoding='utf-8') as f:
                                json.dump(dataset_data, f, ensure_ascii=False, indent=2)
                            
                            log_queue.put(f"Saved: {json_filename}")
                            processed_count += 1
                    
                    # Update progress
                    progress = int(10 + (i + 1) / total_links * 90)  # 10-100% for crawl
                    progress_queue.put(progress)
                    
                    # Small delay to be respectful
                    time.sleep(0.5)
                    
                except Exception as e:
                    log_queue.put(f"ERROR processing {link}: {str(e)}")
                    continue
            driver.quit()
            
            # Log error summary
            self.log_error_summary()
            
            log_queue.put(f"[DONE] Crawling complete! Processed {processed_count} datasets.")
            log_queue.put(f"Data saved to: {self.output_dir}")
            if self.download_thumbs.isChecked():
                log_queue.put(f"Thumbnails saved to: {self.images_dir}")
            
        except Exception as e:
            log_queue.put(f"[ERROR] Crawling failed: {str(e)}")
            # Log error summary even on failure
            self.log_error_summary()

    def extract_dataset_info(self, soup, url):
        """Extract dataset information from a page"""
        data = {
            'url': url,
            'title': None,
            'description': None,
            'thumbnail_url': None,
            'metadata': {},
            'tags': [],
            'provider': None
        }
        
        # Extract title
        title_elem = soup.find('h1') or soup.find('title')
        if title_elem:
            data['title'] = title_elem.get_text(strip=True)
        
        # Extract description
        desc_elem = soup.find('div', class_='devsite-article-body') or soup.find('p')
        if desc_elem:
            data['description'] = desc_elem.get_text(strip=True)
        
        # Extract thumbnail
        img_elem = soup.find('img')
        if img_elem and img_elem.get('src'):
            src = img_elem['src']
            if not src.startswith('http'):
                src = urljoin(url, src)
            data['thumbnail_url'] = src
        
        # Extract metadata from tables
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cols = row.find_all(['td', 'th'])
                if len(cols) >= 2:
                    key = cols[0].get_text(strip=True)
                    value = cols[1].get_text(strip=True)
                    if key and value:
                        data['metadata'][key] = value
        
        # Extract tags/chips
        chips = soup.find_all('span', class_='devsite-chip-label')
        data['tags'] = [chip.get_text(strip=True) for chip in chips if chip.get_text(strip=True)]
        
        # Extract provider
        provider_elem = soup.find('a', class_='devsite-link')
        if provider_elem:
            data['provider'] = provider_elem.get_text(strip=True)
        
        return data

    def download_image(self, url):
        """Download an image and return the local path"""
        if not url:
            return None
        
        try:
            parsed = urlparse(url)
            filename = os.path.basename(parsed.path)
            if not filename or '.' not in filename:
                filename = f"thumb_{int(time.time())}.jpg"
            
            filepath = os.path.join(self.images_dir, filename)
            
            headers = {"User-Agent": "Mozilla/5.0 (compatible; EarthEngineCrawler/1.0)"}
            response = requests.get(url, headers=headers, stream=True, timeout=10)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(8192):
                    f.write(chunk)
            
            return filepath
            
        except Exception as e:
            self.log_queue.put(f"Failed to download image {url}: {str(e)}")
            return None

    def ensemble_ml_classify(self, text, expected_types=None):
        """Advanced ensemble classification using multiple ML models."""
        if not text or not isinstance(text, str):
            return None, 0.0, None
        
        results = []
        weights = []
        
        # 1. spaCy NER classification
        if self.nlp:
            try:
                doc = self.nlp(text)
                if doc.ents:
                    ent = doc.ents[0]
                    results.append(ent.label_)
                    weights.append(0.4)  # spaCy weight
            except Exception as e:
                pass
        
        # 2. BERT classification
        if self.bert_classifier:
            try:
                bert_result = self.bert_classifier(text[:512])  # BERT has token limit
                if bert_result:
                    results.append(bert_result[0]['label'])
                    weights.append(0.4)  # BERT weight
            except Exception as e:
                pass
        
        # 3. Rule-based classification
        rule_label = self.rule_based_classify(text)
        if rule_label:
            results.append(rule_label)
            weights.append(0.2)  # Rule-based weight
        
        # Ensemble decision
        if results:
            # Simple weighted voting
            label_counts = {}
            for i, label in enumerate(results):
                if label in label_counts:
                    label_counts[label] += weights[i]
                else:
                    label_counts[label] = weights[i]
            
            best_label = max(label_counts, key=label_counts.get)
            confidence = label_counts[best_label] / sum(weights)
            
            # Filter by expected types if provided
            if expected_types and best_label not in expected_types:
                # Find best matching expected type
                for label in results:
                    if label in expected_types:
                        best_label = label
                        break
            
            return best_label, confidence, text
        
        return None, 0.0, None

    def rule_based_classify(self, text):
        """Rule-based classification using patterns and keywords."""
        text_lower = text.lower()
        
        # Date patterns
        if re.search(r'\d{4}-\d{2}-\d{2}', text):
            return 'DATE'
        
        # Organization patterns
        org_keywords = ['inc', 'corp', 'ltd', 'university', 'institute', 'agency', 'organization']
        if any(keyword in text_lower for keyword in org_keywords):
            return 'ORG'
        
        # Location patterns
        loc_keywords = ['country', 'region', 'area', 'continent', 'ocean', 'sea']
        if any(keyword in text_lower for keyword in loc_keywords):
            return 'GPE'
        
        # Product patterns
        product_keywords = ['satellite', 'sensor', 'instrument', 'band', 'collection']
        if any(keyword in text_lower for keyword in product_keywords):
            return 'PRODUCT'
        
        return None

    def validate_and_enrich_data(self, extracted_data):
        """Advanced validation and enrichment of extracted data."""
        enriched_data = extracted_data.copy()
        validation_results = {}
        
        # Geospatial validation
        if self.validation_config.get('geospatial', False):
            spatial_validation = self.validate_spatial_data(extracted_data)
            validation_results['spatial'] = spatial_validation
            if spatial_validation.get('enriched'):
                enriched_data.update(spatial_validation['enriched'])
        
        # Temporal validation
        if self.validation_config.get('temporal', False):
            temporal_validation = self.validate_temporal_data(extracted_data)
            validation_results['temporal'] = temporal_validation
            if temporal_validation.get('enriched'):
                enriched_data.update(temporal_validation['enriched'])
        
        # API cross-referencing
        if self.validation_config.get('cross_reference_apis'):
            api_validation = self.cross_reference_apis(extracted_data)
            validation_results['api_cross_reference'] = api_validation
            if api_validation.get('enriched'):
                enriched_data.update(api_validation['enriched'])
        
        # Data quality scoring
        quality_score = self.calculate_data_quality_score(extracted_data, validation_results)
        enriched_data['data_quality_score'] = quality_score
        enriched_data['validation_results'] = validation_results
        
        return enriched_data

    def validate_spatial_data(self, data):
        """Validate and enrich spatial coverage data."""
        result = {'valid': False, 'enriched': {}, 'errors': []}
        
        spatial_text = data.get('spatial_coverage', '') or data.get('region', '')
        if not spatial_text:
            return result
        
        try:
            if self.geocoder:
                # Try to geocode the spatial description
                location = self.geocoder.geocode(spatial_text, timeout=10)
                if location:
                    result['valid'] = True
                    result['enriched'] = {
                        'latitude': location.latitude,
                        'longitude': location.longitude,
                        'normalized_location': location.address,
                        'location_type': 'point'
                    }
                else:
                    result['errors'].append(f"Could not geocode: {spatial_text}")
        except (GeocoderTimedOut, GeocoderUnavailable) as e:
            result['errors'].append(f"Geocoding service unavailable: {e}")
        except Exception as e:
            result['errors'].append(f"Geospatial validation error: {e}")
        
        return result

    def validate_temporal_data(self, data):
        """Validate and enrich temporal coverage data."""
        result = {'valid': False, 'enriched': {}, 'errors': []}
        
        temporal_text = data.get('temporal_coverage', '') or data.get('date_range', '')
        if not temporal_text:
            return result
        
        try:
            # Try to parse date ranges
            date_patterns = [
                r'(\d{4}-\d{2}-\d{2})\s*(?:to|-|–)\s*(\d{4}-\d{2}-\d{2})',
                r'(\d{4})\s*(?:to|-|–)\s*(\d{4})',
                r'(\d{4}-\d{2})\s*(?:to|-|–)\s*(\d{4}-\d{2})'
            ]
            
            for pattern in date_patterns:
                match = re.search(pattern, temporal_text)
                if match:
                    start_date = match.group(1)
                    end_date = match.group(2)
                    
                    # Validate dates
                    try:
                        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
                        
                        if start_dt <= end_dt:
                            result['valid'] = True
                            result['enriched'] = {
                                'start_date': start_date,
                                'end_date': end_date,
                                'duration_days': (end_dt - start_dt).days,
                                'is_current': end_dt >= datetime.now()
                            }
                        else:
                            result['errors'].append("End date before start date")
                    except ValueError as e:
                        result['errors'].append(f"Invalid date format: {e}")
                    break
            else:
                result['errors'].append("No valid date range pattern found")
                
        except Exception as e:
            result['errors'].append(f"Temporal validation error: {e}")
        
        return result

    def cross_reference_apis(self, data):
        """Cross-reference data with external APIs (NASA, ESA, etc.)."""
        result = {'valid': False, 'enriched': {}, 'errors': []}
        
        title = data.get('title', '')
        provider = data.get('provider', '')
        
        # NASA API cross-reference
        if 'NASA' in self.validation_config.get('cross_reference_apis', []):
            nasa_result = self.query_nasa_api(title, provider)
            if nasa_result:
                result['enriched']['nasa_reference'] = nasa_result
        
        # ESA API cross-reference (placeholder)
        if 'ESA' in self.validation_config.get('cross_reference_apis', []):
            esa_result = self.query_esa_api(title, provider)
            if esa_result:
                result['enriched']['esa_reference'] = esa_result
        
        if result['enriched']:
            result['valid'] = True
        
        return result

    def query_nasa_api(self, title, provider):
        """Query NASA API for dataset information."""
        try:
            # NASA CMR (Common Metadata Repository) API
            url = "https://cmr.earthdata.nasa.gov/search/collections.json"
            params = {
                'keyword': title,
                'limit': 5
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('feed', {}).get('entry'):
                    return {
                        'found': True,
                        'results_count': len(data['feed']['entry']),
                        'first_result': data['feed']['entry'][0]
                    }
        except Exception as e:
            pass
        
        return None

    def query_esa_api(self, title, provider):
        """Query ESA API for dataset information (placeholder)."""
        # ESA API integration would go here
        return None

    def calculate_data_quality_score(self, data, validation_results):
        """Calculate overall data quality score based on validation results."""
        score = 0.0
        max_score = 100.0
        
        # Base score from extraction confidence
        confidence_scores = data.get('confidence', {}).values()
        if confidence_scores:
            avg_confidence = sum(confidence_scores) / len(confidence_scores)
            score += avg_confidence * 40  # 40% weight for extraction confidence
        
        # Validation bonus
        if validation_results.get('spatial', {}).get('valid'):
            score += 20  # 20% bonus for valid spatial data
        
        if validation_results.get('temporal', {}).get('valid'):
            score += 20  # 20% bonus for valid temporal data
        
        if validation_results.get('api_cross_reference', {}).get('valid'):
            score += 20  # 20% bonus for API cross-reference
        
        # Penalty for validation errors
        total_errors = 0
        for validation in validation_results.values():
            total_errors += len(validation.get('errors', []))
        
        score -= total_errors * 5  # 5 points penalty per error
        
        return max(0.0, min(100.0, score))

    def intelligent_retry(self, func, *args, **kwargs):
        """Intelligent retry mechanism with exponential backoff."""
        for attempt in range(self.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_type = type(e).__name__
                self.error_tracker['total_errors'] += 1
                self.error_tracker['error_categories'][error_type] += 1
                
                if attempt < self.max_retries:
                    self.error_tracker['retry_attempts'] += 1
                    delay = self.retry_delay * (2 ** attempt)  # Exponential backoff
                    self.log_message(f"[RETRY] Attempt {attempt + 1}/{self.max_retries + 1} failed: {error_type}. Retrying in {delay}s...")
                    time.sleep(delay)
                else:
                    self.log_message(f"[ERROR] All retry attempts failed: {error_type} - {str(e)}")
                    raise e

    def recover_partial_results(self, soup, link, error):
        """Attempt to recover partial results when full extraction fails."""
        self.log_message(f"[RECOVERY] Attempting partial result recovery for {link}")
        
        partial_result = {
            'source_url': link,
            'extraction_report': {'recovery': 'partial'},
            'confidence': {'recovery': 0.3},
            'ml_classification': {},
            'recovery_error': str(error)
        }
        
        # Try to extract at least title and URL
        if soup:
            try:
                title_elem = soup.find(['h1', 'title'])
                if title_elem:
                    partial_result['title'] = title_elem.get_text(strip=True)
                    partial_result['confidence']['title'] = 0.5
            except:
                pass
            
            # Try to extract any available metadata
            try:
                meta_tags = soup.find_all('meta')
                for meta in meta_tags:
                    if meta.get('name') == 'description' and meta.get('content'):
                        partial_result['description'] = meta['content'][:200] + "..."
                        partial_result['confidence']['description'] = 0.4
                        break
            except:
                pass
        
        self.error_tracker['recovered_results'] += 1
        return partial_result

    def categorize_error(self, error):
        """Categorize errors for better error handling and reporting."""
        error_str = str(error).lower()
        
        if 'timeout' in error_str or 'timed out' in error_str:
            return 'TIMEOUT'
        elif 'connection' in error_str or 'network' in error_str:
            return 'NETWORK'
        elif 'not found' in error_str or '404' in error_str:
            return 'NOT_FOUND'
        elif 'permission' in error_str or '403' in error_str:
            return 'PERMISSION'
        elif 'geocoding' in error_str:
            return 'GEOCODING'
        elif 'ml' in error_str or 'model' in error_str:
            return 'ML_MODEL'
        elif 'validation' in error_str:
            return 'VALIDATION'
        else:
            return 'UNKNOWN'

    def log_error_summary(self):
        """Log a summary of all errors encountered during crawling."""
        if self.error_tracker['total_errors'] == 0:
            self.log_message("[ERROR SUMMARY] No errors encountered!")
            return
        
        self.log_message(f"[ERROR SUMMARY] Total errors: {self.error_tracker['total_errors']}")
        self.log_message(f"[ERROR SUMMARY] Retry attempts: {self.error_tracker['retry_attempts']}")
        self.log_message(f"[ERROR SUMMARY] Recovered results: {self.error_tracker['recovered_results']}")
        
        self.log_message("[ERROR SUMMARY] Error categories:")
        for category, count in self.error_tracker['error_categories'].items():
            self.log_message(f"  - {category}: {count}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = EnhancedCrawlerUI()
    win.show()
    sys.exit(app.exec()) 