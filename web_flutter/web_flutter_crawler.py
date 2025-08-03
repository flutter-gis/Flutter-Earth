#!/usr/bin/env python3
"""
Standard Web Crawler - Lightweight but Excellent
Uses Selenium, BeautifulSoup, and multiple scrapers with enhanced UI
"""

import os
import sys
import json
import time
import threading
import requests
import re
import csv
from datetime import datetime
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

# Advanced scraping imports
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.firefox.options import Options as FirefoxOptions
    from selenium.common.exceptions import TimeoutException, WebDriverException
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.common.keys import Keys
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("Selenium not available - using requests only")

try:
    import lxml
    LXML_AVAILABLE = True
except ImportError:
    LXML_AVAILABLE = False
    print("lxml not available - using html.parser")

try:
    import cloudscraper
    CLOUDSCRAPER_AVAILABLE = True
except ImportError:
    CLOUDSCRAPER_AVAILABLE = False
    print("cloudscraper not available - using requests")

try:
    import undetected_chromedriver as uc
    UNDETECTED_CHROME_AVAILABLE = True
except ImportError:
    UNDETECTED_CHROME_AVAILABLE = False
    print("undetected_chromedriver not available - using standard selenium")

# Advanced classification imports
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    print("spaCy not available - using basic classification")

try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("Transformers not available - using basic classification")

try:
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("scikit-learn not available - using basic classification")

# Advanced text processing
try:
    import nltk
    from nltk.tokenize import word_tokenize, sent_tokenize
    from nltk.corpus import stopwords
    from nltk.stem import WordNetLemmatizer
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False
    print("NLTK not available - using basic text processing")

# Image processing for thumbnails
try:
    from PIL import Image
    import io
    import base64
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("PIL not available - thumbnail processing disabled")

# Advanced Scraper Class with Multiple Methods
class AdvancedScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Initialize different scrapers
        self.selenium_driver = None
        self.cloudscraper_session = None
        
        if CLOUDSCRAPER_AVAILABLE:
            try:
                self.cloudscraper_session = cloudscraper.create_scraper()
            except Exception as e:
                print(f"Cloudscraper initialization failed: {e}")
    
    def get_selenium_driver(self, headless=True):
        """Initialize Selenium WebDriver with enhanced capabilities"""
        if not SELENIUM_AVAILABLE:
            return None
            
        try:
            if UNDETECTED_CHROME_AVAILABLE:
                options = uc.ChromeOptions()
                if headless:
                    options.add_argument('--headless')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                options.add_argument('--disable-gpu')
                options.add_argument('--window-size=1920,1080')
                options.add_argument('--disable-blink-features=AutomationControlled')
                options.add_experimental_option("excludeSwitches", ["enable-automation"])
                options.add_experimental_option('useAutomationExtension', False)
                self.selenium_driver = uc.Chrome(options=options)
            else:
                options = Options()
                if headless:
                    options.add_argument('--headless')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                options.add_argument('--disable-blink-features=AutomationControlled')
                options.add_experimental_option("excludeSwitches", ["enable-automation"])
                options.add_experimental_option('useAutomationExtension', False)
                self.selenium_driver = webdriver.Chrome(options=options)
            
            # Execute script to remove webdriver property
            self.selenium_driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.selenium_driver.set_page_load_timeout(30)
            return self.selenium_driver
        except Exception as e:
            print(f"Selenium driver initialization failed: {e}")
            return None
    
    def scrape_with_requests(self, url, timeout=15):
        """Basic requests scraping"""
        try:
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Requests scraping failed for {url}: {e}")
            return None
    
    def scrape_with_cloudscraper(self, url, timeout=15):
        """Cloudscraper for bypassing protection"""
        if not self.cloudscraper_session:
            return None
            
        try:
            response = self.cloudscraper_session.get(url, timeout=timeout)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Cloudscraper failed for {url}: {e}")
            return None
    
    def scrape_with_selenium(self, url, wait_time=10):
        """Enhanced Selenium scraping for JavaScript-heavy sites"""
        if not self.selenium_driver:
            self.get_selenium_driver()
        
        if not self.selenium_driver:
            return None
            
        try:
            self.selenium_driver.get(url)
            
            # Wait for page to load
            WebDriverWait(self.selenium_driver, wait_time).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Scroll to load lazy content
            self._scroll_page()
            
            # Wait for dynamic content
            time.sleep(2)
            
            # Try to handle cookie banners
            self._handle_cookie_banners()
            
            return self.selenium_driver.page_source
        except TimeoutException:
            print(f"Selenium timeout for {url}")
            return self.selenium_driver.page_source
        except Exception as e:
            print(f"Selenium scraping failed for {url}: {e}")
            return None
    
    def _scroll_page(self):
        """Scroll page to load lazy content"""
        try:
            # Scroll to bottom
            self.selenium_driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            
            # Scroll to top
            self.selenium_driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(0.5)
            
            # Scroll to middle
            self.selenium_driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(0.5)
        except Exception as e:
            print(f"Scroll failed: {e}")
    
    def _handle_cookie_banners(self):
        """Handle cookie consent banners"""
        try:
            # Common cookie banner selectors
            cookie_selectors = [
                "button[contains(text(), 'Accept')]",
                "button[contains(text(), 'OK')]",
                "button[contains(text(), 'Got it')]",
                "button[contains(text(), 'I agree')]",
                ".cookie-accept",
                ".cookie-consent button",
                "#accept-cookies",
                ".accept-cookies"
            ]
            
            for selector in cookie_selectors:
                try:
                    button = WebDriverWait(self.selenium_driver, 2).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    button.click()
                    print("Cookie banner handled")
                    break
                except:
                    continue
        except Exception as e:
            print(f"Cookie banner handling failed: {e}")
    
    def smart_scrape(self, url, method='auto'):
        """Smart scraping with fallback methods"""
        html_content = None
        
        # Try different methods based on preference
        if method == 'auto':
            # Try requests first, then cloudscraper, then selenium
            html_content = self.scrape_with_requests(url)
            if not html_content:
                html_content = self.scrape_with_cloudscraper(url)
            if not html_content:
                html_content = self.scrape_with_selenium(url)
        elif method == 'selenium':
            html_content = self.scrape_with_selenium(url)
        elif method == 'cloudscraper':
            html_content = self.scrape_with_cloudscraper(url)
        else:  # requests
            html_content = self.scrape_with_requests(url)
        
        return html_content
    
    def cleanup(self):
        """Clean up resources"""
        if self.selenium_driver:
            try:
                self.selenium_driver.quit()
            except:
                pass
            self.selenium_driver = None

# Advanced Classifier with Multiple Methods
class AdvancedClassifier:
    def __init__(self):
        self.categories = {
            'satellite': ['satellite', 'earth observation', 'remote sensing', 'landsat', 'sentinel', 'modis', 'radar', 'spectral', 'multispectral', 'hyperspectral'],
            'climate': ['climate', 'weather', 'temperature', 'precipitation', 'atmospheric', 'meteorological', 'climate change', 'global warming', 'greenhouse'],
            'geology': ['geology', 'mineral', 'rock', 'soil', 'terrain', 'elevation', 'topography', 'geological', 'lithology', 'stratigraphy'],
            'ocean': ['ocean', 'marine', 'sea', 'coastal', 'water', 'bathymetry', 'oceanography', 'oceanic', 'marine biology', 'coral reef'],
            'forest': ['forest', 'vegetation', 'land cover', 'agriculture', 'crop', 'biomass', 'forestry', 'deforestation', 'reforestation'],
            'urban': ['urban', 'city', 'infrastructure', 'building', 'population', 'settlement', 'urbanization', 'city planning', 'smart city'],
            'disaster': ['disaster', 'flood', 'fire', 'earthquake', 'volcano', 'emergency', 'hazard', 'natural disaster', 'tsunami', 'hurricane'],
            'environmental': ['environmental', 'pollution', 'conservation', 'biodiversity', 'ecosystem', 'environmental protection', 'sustainability'],
            'transportation': ['transportation', 'road', 'highway', 'railway', 'airport', 'port', 'logistics', 'traffic', 'mobility'],
            'energy': ['energy', 'power', 'renewable', 'solar', 'wind', 'hydroelectric', 'fossil fuel', 'nuclear', 'geothermal']
        }
        
        # Initialize advanced models
        self.spacy_model = None
        self.tfidf_vectorizer = None
        self.similarity_matrix = None
        self.nlp_pipeline = None
        
        self._initialize_advanced_models()
    
    def _initialize_advanced_models(self):
        """Initialize advanced classification models"""
        # Initialize spaCy
        if SPACY_AVAILABLE:
            try:
                self.spacy_model = spacy.load("en_core_web_sm")
                print("✅ spaCy model loaded")
            except:
                try:
                    self.spacy_model = spacy.load("en_core_web_md")
                    print("✅ spaCy medium model loaded")
                except:
                    print("⚠️ spaCy model not available")
        
        # Initialize TF-IDF
        if SKLEARN_AVAILABLE:
            try:
                self.tfidf_vectorizer = TfidfVectorizer(
                    max_features=1000,
                    stop_words='english',
                    ngram_range=(1, 2)
                )
                # Create similarity matrix from category keywords
                all_keywords = []
                for category, keywords in self.categories.items():
                    all_keywords.extend(keywords)
                
                if all_keywords:
                    self.tfidf_vectorizer.fit([' '.join(all_keywords)])
                    print("✅ TF-IDF vectorizer initialized")
            except Exception as e:
                print(f"⚠️ TF-IDF initialization failed: {e}")
        
        # Initialize NLTK
        if NLTK_AVAILABLE:
            try:
                nltk.download('punkt', quiet=True)
                nltk.download('stopwords', quiet=True)
                nltk.download('wordnet', quiet=True)
                nltk.download('averaged_perceptron_tagger', quiet=True)
                print("✅ NLTK models downloaded")
            except Exception as e:
                print(f"⚠️ NLTK initialization failed: {e}")
    
    def classify_text(self, text):
        """Advanced classification with multiple methods"""
        if not text:
            return {'category': 'unknown', 'confidence': 0.0}
        
        results = {}
        
        # Method 1: Enhanced keyword classification
        keyword_result = self._keyword_classification(text)
        results['keyword'] = keyword_result
        
        # Method 2: spaCy NER classification
        if self.spacy_model:
            spacy_result = self._spacy_classification(text)
            results['spacy'] = spacy_result
        
        # Method 3: TF-IDF similarity classification
        if self.tfidf_vectorizer:
            tfidf_result = self._tfidf_classification(text)
            results['tfidf'] = tfidf_result
        
        # Method 4: NLTK-based classification
        if NLTK_AVAILABLE:
            nltk_result = self._nltk_classification(text)
            results['nltk'] = nltk_result
        
        # Ensemble the results
        final_result = self._ensemble_classification(results)
        return final_result
    
    def _keyword_classification(self, text):
        """Enhanced keyword-based classification"""
        text_lower = text.lower()
        scores = {}
        
        for category, keywords in self.categories.items():
            score = 0
            for keyword in keywords:
                if keyword in text_lower:
                    # Weight longer keywords more
                    score += len(keyword.split()) * 2
                # Check for partial matches
                elif any(word in text_lower for word in keyword.split()):
                    score += 1
            
            if score > 0:
                scores[category] = score / (len(keywords) * 2)
        
        if scores:
            best_category = max(scores, key=scores.get)
            confidence = min(scores[best_category], 1.0)
            return {'category': best_category, 'confidence': confidence}
        
        return {'category': 'general', 'confidence': 0.1}
    
    def _spacy_classification(self, text):
        """spaCy-based classification using NER and similarity"""
        if not self.spacy_model:
            return {'category': 'unknown', 'confidence': 0.0}
        
        try:
            doc = self.spacy_model(text)
            
            # Extract entities and their types
            entities = {}
            for ent in doc.ents:
                if ent.label_ in ['ORG', 'GPE', 'PRODUCT', 'FAC', 'PERSON', 'LOC']:
                    if ent.label_ not in entities:
                        entities[ent.label_] = []
                    entities[ent.label_].append(ent.text)
            
            # Calculate similarity with category keywords
            scores = {}
            for category, keywords in self.categories.items():
                category_text = ' '.join(keywords)
                category_doc = self.spacy_model(category_text)
                similarity = doc.similarity(category_doc)
                scores[category] = similarity
            
            if scores:
                best_category = max(scores, key=scores.get)
                confidence = min(scores[best_category], 1.0)
                return {'category': best_category, 'confidence': confidence}
            
        except Exception as e:
            print(f"spaCy classification failed: {e}")
        
        return {'category': 'unknown', 'confidence': 0.0}
    
    def _tfidf_classification(self, text):
        """TF-IDF similarity-based classification"""
        if not self.tfidf_vectorizer:
            return {'category': 'unknown', 'confidence': 0.0}
        
        try:
            # Vectorize input text
            text_vector = self.tfidf_vectorizer.transform([text])
            
            # Calculate similarity with each category
            scores = {}
            for category, keywords in self.categories.items():
                category_text = ' '.join(keywords)
                category_vector = self.tfidf_vectorizer.transform([category_text])
                similarity = cosine_similarity(text_vector, category_vector)[0][0]
                scores[category] = similarity
            
            if scores:
                best_category = max(scores, key=scores.get)
                confidence = min(scores[best_category], 1.0)
                return {'category': best_category, 'confidence': confidence}
            
        except Exception as e:
            print(f"TF-IDF classification failed: {e}")
        
        return {'category': 'unknown', 'confidence': 0.0}
    
    def _nltk_classification(self, text):
        """NLTK-based classification using POS and lemmatization"""
        try:
            # Tokenize and lemmatize
            tokens = word_tokenize(text.lower())
            lemmatizer = WordNetLemmatizer()
            lemmatized_tokens = [lemmatizer.lemmatize(token) for token in tokens]
            
            # Remove stopwords
            stop_words = set(stopwords.words('english'))
            filtered_tokens = [token for token in lemmatized_tokens if token not in stop_words]
            
            # Calculate category scores
            scores = {}
            for category, keywords in self.categories.items():
                score = 0
                for keyword in keywords:
                    keyword_tokens = word_tokenize(keyword.lower())
                    keyword_lemmas = [lemmatizer.lemmatize(token) for token in keyword_tokens]
                    
                    # Check for keyword matches
                    for lemma in filtered_tokens:
                        if lemma in keyword_lemmas:
                            score += 1
                
                if score > 0:
                    scores[category] = score / len(keywords)
            
            if scores:
                best_category = max(scores, key=scores.get)
                confidence = min(scores[best_category], 1.0)
                return {'category': best_category, 'confidence': confidence}
            
        except Exception as e:
            print(f"NLTK classification failed: {e}")
        
        return {'category': 'unknown', 'confidence': 0.0}
    
    def _ensemble_classification(self, results):
        """Combine results from multiple classification methods"""
        if not results:
            return {'category': 'unknown', 'confidence': 0.0}
        
        # Weight the different methods
        weights = {
            'keyword': 0.3,
            'spacy': 0.3,
            'tfidf': 0.2,
            'nltk': 0.2
        }
        
        category_scores = {}
        total_weight = 0
        
        for method, result in results.items():
            if method in weights and result['category'] != 'unknown':
                weight = weights[method]
                category = result['category']
                confidence = result['confidence']
                
                if category not in category_scores:
                    category_scores[category] = 0
                
                category_scores[category] += confidence * weight
                total_weight += weight
        
        if category_scores and total_weight > 0:
            # Normalize scores
            for category in category_scores:
                category_scores[category] /= total_weight
            
            best_category = max(category_scores, key=category_scores.get)
            confidence = category_scores[best_category]
            
            return {'category': best_category, 'confidence': confidence}
        
        # Fallback to keyword classification
        if 'keyword' in results:
            return results['keyword']
        
        return {'category': 'general', 'confidence': 0.1}

class WebFlutterCrawlerUI(QWidget):
    # Define signals for thread-safe UI updates
    progress_updated = Signal(int, int, int)  # current, total, progress
    status_updated = Signal(str)
    data_updated = Signal()
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Web Flutter Crawler v2.0 - Lightweight but Excellent")
        self.setGeometry(100, 100, 1600, 1000)
        
        # Initialize components
        self.classifier = AdvancedClassifier()
        self.scraper = AdvancedScraper()
        self.extracted_data = []
        self.is_crawling = False
        self.stop_requested = False
        
        # Statistics
        self.total_processed = 0
        self.successful_extractions = 0
        self.failed_extractions = 0
        self.error_count = 0
        self.warning_count = 0
        
        # Scraping configuration
        self.scraping_method = 'auto'  # auto, selenium, cloudscraper, requests
        self.use_selenium = True
        self.use_cloudscraper = True
        self.use_requests = True
        
        self.setup_ui()
        self.load_config()
        
        # Connect signals
        self.progress_updated.connect(self.update_progress)
        self.status_updated.connect(self.update_status)
        self.data_updated.connect(self.update_results_display)
    
    def load_config(self):
        """Load lightweight configuration"""
        try:
            self.config = {
                'performance': {
                    'max_concurrent_requests': 4,
                    'request_delay': 1.0,
                    'timeout': 15
                },
                'processing': {
                    'enable_quality_checks': True,
                    'min_confidence': 0.3
                }
            }
            self.log_message("✅ Lightweight configuration loaded")
        except Exception as e:
            self.log_error(f"Failed to load configuration: {e}")
            self.config = {}
    
    def setup_ui(self):
        """Setup the same UI as enhanced crawler but simplified"""
        layout = QHBoxLayout()
        
        # Left panel - Controls (same as enhanced)
        left_panel = self.create_left_column()
        layout.addLayout(left_panel, 1)
        
        # Right panel - Results (same as enhanced)
        right_panel = self.create_right_column()
        layout.addLayout(right_panel, 2)
        
        self.setLayout(layout)
    
    def create_left_column(self):
        """Create left column with controls"""
        left_layout = QVBoxLayout()
        
        # File selection
        file_group = QGroupBox("Input File")
        file_layout = QVBoxLayout()
        
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setPlaceholderText("Select HTML file to crawl...")
        file_layout.addWidget(self.file_path_edit)
        
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_file)
        file_layout.addWidget(browse_btn)
        
        file_group.setLayout(file_layout)
        left_layout.addWidget(file_group)
        
        # Scraping method selection
        scraping_group = QGroupBox("Scraping Method")
        scraping_layout = QVBoxLayout()
        
        self.scraping_method_combo = QComboBox()
        self.scraping_method_combo.addItems(['Auto (Smart Fallback)', 'Selenium (JavaScript)', 'Cloudscraper (Anti-Bot)', 'Requests (Fast)'])
        self.scraping_method_combo.currentTextChanged.connect(self.on_scraping_method_changed)
        scraping_layout.addWidget(self.scraping_method_combo)
        
        # Scraping options
        self.use_selenium_cb = QCheckBox("Use Selenium")
        self.use_selenium_cb.setChecked(True)
        scraping_layout.addWidget(self.use_selenium_cb)
        
        self.use_cloudscraper_cb = QCheckBox("Use Cloudscraper")
        self.use_cloudscraper_cb.setChecked(True)
        scraping_layout.addWidget(self.use_cloudscraper_cb)
        
        self.use_requests_cb = QCheckBox("Use Requests")
        self.use_requests_cb.setChecked(True)
        scraping_layout.addWidget(self.use_requests_cb)
        
        scraping_group.setLayout(scraping_layout)
        left_layout.addWidget(scraping_group)
        
        # Crawl controls
        control_group = QGroupBox("Crawl Controls")
        control_layout = QVBoxLayout()
        
        self.start_btn = QPushButton("Start Crawling")
        self.start_btn.clicked.connect(self.start_crawl)
        control_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("Stop Crawling")
        self.stop_btn.clicked.connect(self.stop_crawl)
        self.stop_btn.setEnabled(False)
        control_layout.addWidget(self.stop_btn)
        
        control_group.setLayout(control_layout)
        left_layout.addWidget(control_group)
        
        # Progress
        progress_group = QGroupBox("Progress")
        progress_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        progress_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Ready")
        progress_layout.addWidget(self.status_label)
        
        progress_group.setLayout(progress_layout)
        left_layout.addWidget(progress_group)
        
        # Statistics
        stats_group = QGroupBox("Statistics")
        stats_layout = QVBoxLayout()
        
        self.stats_text = QTextEdit()
        self.stats_text.setMaximumHeight(150)
        stats_layout.addWidget(self.stats_text)
        
        stats_group.setLayout(stats_layout)
        left_layout.addWidget(stats_group)
        
        # Export
        export_group = QGroupBox("Export")
        export_layout = QVBoxLayout()
        
        export_btn = QPushButton("Export Results")
        export_btn.clicked.connect(self.export_results)
        export_layout.addWidget(export_btn)
        
        export_group.setLayout(export_layout)
        left_layout.addWidget(export_group)
        
        return left_layout
    
    def create_right_column(self):
        """Create right column with results"""
        right_layout = QVBoxLayout()
        
        # Results tabs
        self.results_tabs = QTabWidget()
        
        # Table view
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(8)
        self.results_table.setHorizontalHeaderLabels([
            "Title", "Category", "Confidence", "Quality", "Provider", "Dataset ID", "Thumbnail", "URL"
        ])
        self.results_tabs.addTab(self.results_table, "Table View")
        
        # Card view
        self.card_scroll = QScrollArea()
        self.card_widget = QWidget()
        self.card_layout = QVBoxLayout()
        self.card_widget.setLayout(self.card_layout)
        self.card_scroll.setWidget(self.card_widget)
        self.card_scroll.setWidgetResizable(True)
        self.results_tabs.addTab(self.card_scroll, "Card View")
        
        # JSON view
        self.json_view = QTextEdit()
        self.json_view.setReadOnly(True)
        self.results_tabs.addTab(self.json_view, "JSON View")
        
        right_layout.addWidget(self.results_tabs)
        
        # Console
        console_group = QGroupBox("Console")
        console_layout = QVBoxLayout()
        
        self.console = QTextEdit()
        self.console.setMaximumHeight(200)
        console_layout.addWidget(self.console)
        
        console_group.setLayout(console_layout)
        right_layout.addWidget(console_group)
        
        return right_layout
    
    def browse_file(self):
        """Browse for HTML file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select HTML File", "", "HTML Files (*.html *.htm)"
        )
        if file_path:
            self.file_path_edit.setText(file_path)
    
    def start_crawl(self):
        """Start crawling process"""
        if not self.file_path_edit.text():
            QMessageBox.warning(self, "Warning", "Please select an HTML file first!")
            return
        
        self.is_crawling = True
        self.stop_requested = False
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        
        # Reset statistics
        self.total_processed = 0
        self.successful_extractions = 0
        self.failed_extractions = 0
        self.extracted_data = []
        
        # Start crawling in background
        self.crawl_thread = threading.Thread(target=self.crawl_html_file, args=(self.file_path_edit.text(),))
        self.crawl_thread.daemon = True
        self.crawl_thread.start()
    
    def stop_crawl(self):
        """Stop crawling process"""
        self.stop_requested = True
        self.is_crawling = False
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.log_message("🛑 Crawling stopped by user")
    
    def crawl_html_file(self, html_file):
        """Main crawling function"""
        try:
            self.log_message("🚀 Starting lightweight enhanced crawl...")
            
            # Read HTML file
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            soup = BeautifulSoup(content, 'html.parser')
            
            # Extract all links - be flexible with any HTML structure
            links = []
            
            # Find all anchor tags
            for link in soup.find_all('a', href=True):
                url = link.get('href')
                if url:
                    # Handle relative URLs by making them absolute
                    if url.startswith('http'):
                        # Already absolute URL
                        links.append(url)
                    elif url.startswith('/'):
                        # Root-relative URL - we'll need to determine base
                        # For now, skip these as we don't know the base
                        continue
                    elif url.startswith('./') or url.startswith('../'):
                        # Relative URL - skip for now
                        continue
                    else:
                        # Could be relative or absolute - try to make it absolute
                        # For now, only process clearly absolute URLs
                        if '://' in url:
                            links.append(url)
            
            self.log_message(f"📊 Found {len(links)} absolute links to process")
            
            if not links:
                self.log_message("⚠️ No valid absolute links found in HTML file")
                self.log_message("💡 Tip: The HTML file should contain absolute URLs (starting with http:// or https://)")
                return
            
            # Process links in batches
            batch_size = 5  # Smaller batch size for better control
            for i in range(0, len(links), batch_size):
                if self.stop_requested:
                    break
                
                batch = links[i:i + batch_size]
                self.log_message(f"📦 Processing batch {i//batch_size + 1}/{(len(links) + batch_size - 1)//batch_size}")
                
                for j, url in enumerate(batch):
                    if self.stop_requested:
                        break
                    
                    current = i + j + 1
                    progress = int((current / len(links)) * 100)
                    
                    # Emit signals for UI updates
                    self.progress_updated.emit(current, len(links), progress)
                    self.status_updated.emit(f"Processing: {current}/{len(links)} ({progress}%)")
                    
                    self.process_link(url, current, len(links))
                    time.sleep(1.0)  # Slightly longer delay to be respectful
            
            self.log_message("✅ Crawling completed!")
            self.show_summary()
            
        except Exception as e:
            self.log_error(f"❌ Crawling failed: {e}")
        finally:
            self.crawl_finished()
    
    def process_link(self, url, current, total):
        """Process individual link with advanced scraping and enhanced extraction"""
        try:
            self.total_processed += 1
            
            # Update progress using signals to avoid threading issues
            progress = int((current / total) * 100)
            
            # Smart scraping with fallback methods
            self.log_message(f"🔍 Scraping {url} with {self.scraping_method} method...")
            html_content = self.scraper.smart_scrape(url, method=self.scraping_method)
            
            if not html_content:
                self.failed_extractions += 1
                self.log_error(f"❌ Failed to scrape {url}")
                return
            
            # Parse content with best available parser
            try:
                if LXML_AVAILABLE:
                    soup = BeautifulSoup(html_content, 'lxml')
                else:
                    soup = BeautifulSoup(html_content, 'html.parser')
            except Exception as parse_error:
                self.log_error(f"❌ Failed to parse HTML for {url}: {parse_error}")
                return
            
            # Extract enhanced information
            try:
                result = self.enhanced_extract(soup, url)
            except Exception as extract_error:
                self.log_error(f"❌ Failed to extract data from {url}: {extract_error}")
                return
            
            if result and result.get('title') and result.get('title') != 'No data available':
                self.extracted_data.append(result)
                self.successful_extractions += 1
                self.log_message(f"✅ {result['title'][:50]}... ({result.get('category', 'unknown')})")
                # Emit signal to update UI
                self.data_updated.emit()
            else:
                self.failed_extractions += 1
                self.log_message(f"⚠️ No meaningful data from {url}")
            
        except Exception as e:
            self.failed_extractions += 1
            self.log_error(f"❌ Failed to process {url}: {e}")
    
    def enhanced_extract(self, soup, url):
        """Enhanced extraction with lightweight classification and thumbnails"""
        result = {
            'title': '', 'provider': '', 'tags': [], 'date_range': '', 'description': '',
            'bands': [], 'terms_of_use': '', 'snippet': '', 'spatial_coverage': '',
            'temporal_coverage': '', 'citation': '', 'type': '', 'region': '', 'source_url': url,
            'category': 'unknown', 'confidence': 0.0, 'quality_score': 0.0, 'timestamp': datetime.now().isoformat(),
            'thumbnail_url': '', 'thumbnail_alt': '', 'dataset_id': '', 'resolution': '', 'coverage_area': '',
            'update_frequency': '', 'license': '', 'documentation_url': '', 'sample_code': ''
        }
        
        # Extract basic information
        result = self.extract_basic_info(soup, result)
        
        # Extract thumbnails and images
        result = self.extract_thumbnails(soup, result)
        
        # Extract dataset-specific information
        result = self.extract_dataset_info(soup, result)
        
        # Apply lightweight classification
        if result.get('description'):
            classification = self.classifier.classify_text(result['description'])
            result['category'] = classification['category']
            result['confidence'] = classification['confidence']
        
        # Calculate quality score
        result['quality_score'] = self.calculate_quality_score(result)
        
        return result
    
    def extract_basic_info(self, soup, result):
        """Extract basic dataset information with smarter parsing"""
        # Title - look for the most specific title
        title = ""
        
        # Generic titles to avoid
        generic_titles = [
            'google developers', 'developers', 'documentation', 'api reference', 
            'google earth engine', 'earth engine', 'google for developers',
            'developers.google.com', 'google', 'earth engine data catalog',
            'data catalog', 'catalog', 'api', 'reference', 'guide', 'tutorial'
        ]
        
        # Method 1: Look for dataset-specific titles in headings
        for heading in soup.find_all(['h1', 'h2', 'h3']):
            heading_text = heading.get_text(strip=True)
            if heading_text and len(heading_text) > 5:
                # Check if it's not a generic title
                if not any(generic in heading_text.lower() for generic in generic_titles):
                    # Look for dataset-like patterns
                    if any(pattern in heading_text.lower() for pattern in [
                        'dataset', 'collection', 'product', 'satellite', 'landsat', 'sentinel',
                        'modis', 'radar', 'climate', 'weather', 'ocean', 'forest', 'urban'
                    ]):
                        title = heading_text
                        break
        
        # Method 2: Look for breadcrumb navigation
        if not title:
            breadcrumbs = soup.find_all(['nav', 'ol', 'ul'], class_=lambda x: x and any(word in x.lower() for word in ['breadcrumb', 'nav', 'crumb']))
            for breadcrumb in breadcrumbs:
                links = breadcrumb.find_all('a')
                if len(links) > 1:
                    # Get the last non-generic link
                    for link in reversed(links):
                        link_text = link.get_text(strip=True)
                        if link_text and not any(generic in link_text.lower() for generic in generic_titles):
                            if len(link_text) > 3:
                                title = link_text
                                break
        
        # Method 3: Look for dataset ID patterns in the page
        if not title:
            text = soup.get_text()
            # Look for common dataset naming patterns
            dataset_patterns = [
                r'([A-Z]{2,}_[A-Z0-9_]+)',  # LANDSAT_8, SENTINEL_2, etc.
                r'([A-Z]{2,}\d{4})',  # MODIS2019, etc.
                r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Dataset|Collection|Product))',  # "Landsat 8 Dataset"
                r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Satellite|Imagery|Data))',  # "Sentinel 2 Satellite"
            ]
            
            for pattern in dataset_patterns:
                matches = re.findall(pattern, text)
                if matches:
                    for match in matches:
                        if len(match) > 3 and not any(generic in match.lower() for generic in generic_titles):
                            title = match
                            break
                    if title:
                        break
        
        # Method 4: Look for specific data attributes
        if not title:
            # Look for data attributes that might contain dataset names
            for elem in soup.find_all(attrs={'data-dataset': True}):
                dataset_name = elem.get('data-dataset')
                if dataset_name and not any(generic in dataset_name.lower() for generic in generic_titles):
                    title = dataset_name
                    break
        
        # Method 5: Look for structured data (JSON-LD)
        if not title:
            for script in soup.find_all('script', type='application/ld+json'):
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict):
                        name = data.get('name') or data.get('title')
                        if name and not any(generic in name.lower() for generic in generic_titles):
                            title = name
                            break
                except:
                    continue
        
        # Method 6: Look for meta tags but filter carefully
        if not title:
            meta_title = soup.find('meta', attrs={'property': 'og:title'})
            if meta_title and meta_title.get('content'):
                meta_content = meta_title['content']
                if not any(generic in meta_content.lower() for generic in generic_titles):
                    title = meta_content
        
        # Method 7: Last resort - page title but with strict filtering
        if not title:
            page_title = soup.find('title')
            if page_title:
                title_text = page_title.get_text(strip=True)
                # Only use if it's not generic and has some substance
                if (not any(generic in title_text.lower() for generic in generic_titles) and 
                    len(title_text) > 10 and 
                    any(word in title_text.lower() for word in ['dataset', 'collection', 'satellite', 'landsat', 'sentinel', 'modis'])):
                    title = title_text
        
        # Clean up the title
        if title:
            # Remove common suffixes
            title = re.sub(r'\s*[-|]\s*(Google|Developers|Documentation|API|Reference|Guide).*$', '', title, flags=re.IGNORECASE)
            # Remove extra whitespace
            title = re.sub(r'\s+', ' ', title).strip()
        
        result['title'] = title if title else "No specific dataset title found"
        
        # Description - look for actual content, not navigation
        description = ""
        
        # Look for main content areas
        main_content = soup.find(['main', 'article', 'div'], class_=re.compile(r'content|main|body|description', re.IGNORECASE))
        if main_content:
            # Get text but exclude navigation and footer
            for nav in main_content.find_all(['nav', 'header', 'footer']):
                nav.decompose()
            description = main_content.get_text(strip=True)[:800] + "..."
        
        # If no main content, try meta description
        if not description:
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc and meta_desc.get('content'):
                description = meta_desc['content']
        
        result['description'] = description
        
        # Provider - look for actual organization names, not generic terms
        provider = ""
        
        # Generic providers to avoid
        generic_providers = [
            'google', 'developers', 'documentation', 'api', 'earth engine',
            'google for developers', 'developers.google.com'
        ]
        
        # Method 1: Look for breadcrumbs or navigation
        breadcrumbs = soup.find(['nav', 'ol', 'ul'], class_=re.compile(r'breadcrumb|nav', re.IGNORECASE))
        if breadcrumbs:
            breadcrumb_text = breadcrumbs.get_text()
            # Look for organization names in breadcrumbs
            org_patterns = [r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', r'([A-Z]{2,})']
            for pattern in org_patterns:
                matches = re.findall(pattern, breadcrumb_text)
                for match in matches:
                    if match.lower() not in generic_providers and len(match) > 2:
                        provider = match
                        break
                if provider:
                    break
        
        # Method 2: Look for specific provider patterns in content
        if not provider:
            provider_patterns = [
                r'Provider[:\s]+([^\n]+)', 
                r'Source[:\s]+([^\n]+)', 
                r'Organization[:\s]+([^\n]+)',
                r'by\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
                r'from\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
                r'NASA', r'ESA', r'USGS', r'NOAA', r'Copernicus', r'Landsat', r'Sentinel'
            ]
            for pattern in provider_patterns:
                match = re.search(pattern, soup.get_text(), re.IGNORECASE)
                if match:
                    potential_provider = match.group(1).strip() if len(match.groups()) > 0 else match.group(0)
                    if potential_provider.lower() not in generic_providers and len(potential_provider) > 2:
                        provider = potential_provider
                        break
        
        # Method 3: Look for dataset-specific organizations
        if not provider:
            text = soup.get_text()
            org_keywords = [
                'NASA', 'ESA', 'USGS', 'NOAA', 'Copernicus', 'Landsat', 'Sentinel',
                'European Space Agency', 'National Aeronautics', 'United States Geological',
                'National Oceanic', 'Atmospheric Administration'
            ]
            for org in org_keywords:
                if org.lower() in text.lower():
                    provider = org
                    break
        
        # Method 4: Look for structured data
        if not provider:
            for script in soup.find_all('script', type='application/ld+json'):
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict):
                        org = data.get('provider') or data.get('publisher') or data.get('author')
                        if org and org.lower() not in generic_providers:
                            provider = org
                            break
                except:
                    continue
        
        result['provider'] = provider if provider else "Unknown Provider"
        
        # Tags - look for actual tags, not navigation links
        tags = set()
        
        # Look for actual tag elements
        tag_elems = soup.find_all(['span', 'div', 'a'], class_=re.compile(r'tag|chip|label|badge', re.IGNORECASE))
        for elem in tag_elems:
            tag_text = elem.get_text(strip=True)
            if tag_text and len(tag_text) > 1:
                tags.add(tag_text.title())
        
        # If no explicit tags, try to extract keywords from content
        if not tags and description:
            # Extract potential keywords from description
            keywords = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', description)
            for keyword in keywords[:5]:  # Limit to 5 keywords
                if keyword.lower() not in ['google', 'developers', 'documentation', 'api', 'reference']:
                    tags.add(keyword)
        
        result['tags'] = list(tags)
        
        # Date range - look for actual date patterns
        date_range = ""
        date_patterns = [
            r'(\d{4}-\d{4})', 
            r'(\d{4}/\d{4})', 
            r'(\d{4}\s+to\s+\d{4})',
            r'(\d{4}\s+-\s+\d{4})',
            r'Updated[:\s]+([^\n]+)',
            r'Date[:\s]+([^\n]+)'
        ]
        for pattern in date_patterns:
            match = re.search(pattern, soup.get_text(), re.IGNORECASE)
            if match:
                date_range = match.group(1).strip()
                break
        
        result['date_range'] = date_range
        
        # Spatial coverage - look for geographic information
        spatial_coverage = ""
        spatial_patterns = [
            r'Latitude[:\s]+([^\n]+)', 
            r'Longitude[:\s]+([^\n]+)', 
            r'Region[:\s]+([^\n]+)',
            r'Coverage[:\s]+([^\n]+)',
            r'Area[:\s]+([^\n]+)',
            r'Location[:\s]+([^\n]+)'
        ]
        for pattern in spatial_patterns:
            match = re.search(pattern, soup.get_text(), re.IGNORECASE)
            if match:
                spatial_coverage = match.group(1).strip()
                break
        
        result['spatial_coverage'] = spatial_coverage
        
        # Bands - look for spectral information
        bands = []
        band_patterns = [
            r'Band[:\s]+([^\n]+)', 
            r'Bands[:\s]+([^\n]+)', 
            r'Spectral[:\s]+([^\n]+)',
            r'Channels[:\s]+([^\n]+)',
            r'Wavelength[:\s]+([^\n]+)'
        ]
        for pattern in band_patterns:
            match = re.search(pattern, soup.get_text(), re.IGNORECASE)
            if match:
                bands = [b.strip() for b in match.group(1).split(',')]
                break
        
        result['bands'] = bands
        
        return result
    
    def extract_thumbnails(self, soup, result):
        """Extract and process thumbnail images from the page"""
        try:
            thumbnails = []
            
            # Look for images with thumbnail-like attributes
            for img in soup.find_all('img'):
                src = img.get('src', '')
                alt = img.get('alt', '')
                
                # Check if this looks like a thumbnail
                if any(keyword in alt.lower() or keyword in src.lower() 
                       for keyword in ['thumb', 'preview', 'sample', 'image', 'photo', 'dataset', 'cover', 'satellite', 'landsat', 'sentinel', 'modis']):
                    thumbnails.append({
                        'src': src,
                        'alt': alt,
                        'width': img.get('width', ''),
                        'height': img.get('height', ''),
                        'title': img.get('title', ''),
                        'class': img.get('class', []),
                        'id': img.get('id', '')
                    })
            
            # Also look for satellite/remote sensing specific images
            for img in soup.find_all('img'):
                src = img.get('src', '')
                alt = img.get('alt', '')
                class_attr = ' '.join(img.get('class', []))
                
                # Look for satellite imagery keywords
                if any(keyword in alt.lower() or keyword in src.lower() or keyword in class_attr.lower()
                       for keyword in ['satellite', 'landsat', 'sentinel', 'modis', 'radar', 'optical', 'multispectral', 'coverage', 'area']):
                    thumbnails.append({
                        'src': src,
                        'alt': alt,
                        'width': img.get('width', ''),
                        'height': img.get('height', ''),
                        'title': img.get('title', ''),
                        'class': img.get('class', []),
                        'id': img.get('id', ''),
                        'priority': 'high'  # Mark as high priority
                    })
            
            if thumbnails:
                # Use the best thumbnail found
                best_thumbnail = self._select_best_thumbnail(thumbnails)
                result['thumbnail_url'] = best_thumbnail['src']
                result['thumbnail_alt'] = best_thumbnail['alt']
                result['thumbnail_width'] = best_thumbnail['width']
                result['thumbnail_height'] = best_thumbnail['height']
                result['thumbnail_title'] = best_thumbnail['title']
                result['thumbnail_class'] = best_thumbnail.get('class', [])
                result['thumbnail_id'] = best_thumbnail.get('id', '')
            else:
                # Look for any image as fallback
                img = soup.find('img')
                if img:
                    result['thumbnail_url'] = img.get('src', '')
                    result['thumbnail_alt'] = img.get('alt', '')
                    result['thumbnail_width'] = img.get('width', '')
                    result['thumbnail_height'] = img.get('height', '')
                    result['thumbnail_title'] = img.get('title', '')
                    result['thumbnail_class'] = img.get('class', [])
                    result['thumbnail_id'] = img.get('id', '')
            
            # Process thumbnail if PIL is available
            if PIL_AVAILABLE and result.get('thumbnail_url'):
                result = self._process_thumbnail(result)
                
        except Exception as e:
            self.log_error(f"Error extracting thumbnails: {e}")
        
        return result
    
    def _select_best_thumbnail(self, thumbnails):
        """Select the best thumbnail from multiple options"""
        if not thumbnails:
            return {}
        
        # Score thumbnails based on various criteria
        scored_thumbnails = []
        for thumb in thumbnails:
            score = 0
            
            # High priority for satellite imagery
            if thumb.get('priority') == 'high':
                score += 10
            
            # Prefer thumbnails with descriptive alt text
            if thumb['alt'] and len(thumb['alt']) > 5:
                score += 3
            
            # Prefer thumbnails with reasonable dimensions
            try:
                width = int(thumb['width']) if thumb['width'] else 0
                height = int(thumb['height']) if thumb['height'] else 0
                
                if 50 <= width <= 500 and 50 <= height <= 500:
                    score += 2
                elif width > 0 and height > 0:
                    score += 1
            except:
                pass
            
            # Prefer thumbnails with satellite/dataset-related keywords
            alt_lower = thumb['alt'].lower()
            class_attr = ' '.join(thumb.get('class', [])).lower()
            
            satellite_keywords = [
                'dataset', 'satellite', 'earth', 'observation', 'landsat', 'sentinel', 
                'modis', 'radar', 'optical', 'multispectral', 'coverage', 'area',
                'remote sensing', 'imagery', 'spectral'
            ]
            
            if any(keyword in alt_lower or keyword in class_attr for keyword in satellite_keywords):
                score += 6
            
            # Bonus for specific satellite names
            if any(sat in alt_lower for sat in ['landsat', 'sentinel', 'modis', 'aster', 'spot']):
                score += 4
            
            # Prefer images with meaningful IDs or classes
            if thumb.get('id') and len(thumb['id']) > 3:
                score += 2
            
            if thumb.get('class') and len(thumb['class']) > 0:
                score += 1
            
            scored_thumbnails.append((score, thumb))
        
        # Return the highest scored thumbnail
        if scored_thumbnails:
            scored_thumbnails.sort(reverse=True)
            return scored_thumbnails[0][1]
        
        return thumbnails[0]
    
    def _process_thumbnail(self, result):
        """Process thumbnail image for additional information"""
        try:
            thumbnail_url = result.get('thumbnail_url', '')
            if not thumbnail_url:
                return result
            
            # Download and analyze thumbnail
            response = requests.get(thumbnail_url, timeout=10)
            if response.status_code == 200:
                # Open image with PIL
                img = Image.open(io.BytesIO(response.content))
                
                # Extract image information
                result['thumbnail_format'] = img.format
                result['thumbnail_mode'] = img.mode
                result['thumbnail_size'] = img.size
                
                # Calculate aspect ratio
                width, height = img.size
                if height > 0:
                    result['thumbnail_aspect_ratio'] = width / height
                
                # Check if image is grayscale or color
                if img.mode in ['L', 'LA']:
                    result['thumbnail_type'] = 'grayscale'
                elif img.mode in ['RGB', 'RGBA']:
                    result['thumbnail_type'] = 'color'
                else:
                    result['thumbnail_type'] = 'other'
                
        except Exception as e:
            self.log_error(f"Thumbnail processing failed: {e}")
        
        return result
    
    def extract_dataset_info(self, soup, result):
        """Extract dataset-specific information with smarter parsing"""
        try:
            text = soup.get_text()
            
            # Extract satellite/instrument information first
            satellite = self._extract_satellite_info(soup, text)
            result['satellite'] = satellite
            
            # Extract resolution based on satellite
            resolution = self._extract_resolution_from_satellite(satellite, text)
            result['resolution'] = resolution
            
            # Extract sensor type (optical, radar, etc.)
            sensor_type = self._extract_sensor_type(satellite, text)
            result['sensor_type'] = sensor_type
            
            # Extract dataset ID
            dataset_id = self._extract_dataset_id(text)
            result['dataset_id'] = dataset_id
            
            # Extract date ranges
            date_info = self._extract_date_ranges(text)
            result['temporal_coverage'] = date_info.get('temporal_coverage', '')
            result['date_range'] = date_info.get('date_range', '')
            result['update_frequency'] = date_info.get('update_frequency', '')
            
            # Extract spatial coverage
            spatial_coverage = self._extract_spatial_coverage(text)
            result['spatial_coverage'] = spatial_coverage
            
            # Extract bands information
            bands = self._extract_bands_info(text)
            result['bands'] = bands
            
            # Extract additional technical details
            technical_details = self._extract_technical_details(text)
            result.update(technical_details)
            
        except Exception as e:
            self.log_error(f"Error extracting dataset info: {e}")
        
        return result
    
    def _extract_satellite_info(self, soup, text):
        """Extract satellite/instrument information"""
        satellite = ""
        
        # Common satellite patterns
        satellite_patterns = [
            r'Landsat\s*(\d+)',  # Landsat 8, Landsat 9
            r'Sentinel\s*[-]?\s*(\d+)',  # Sentinel-1, Sentinel 2
            r'MODIS\s*(Terra|Aqua)?',  # MODIS Terra, MODIS Aqua
            r'SRTM',  # Shuttle Radar Topography Mission
            r'ASTER',  # Advanced Spaceborne Thermal Emission
            r'SPOT\s*(\d+)',  # SPOT 5, SPOT 6
            r'Pleiades',  # Pleiades satellites
            r'WorldView\s*(\d+)',  # WorldView-2, WorldView-3
            r'RapidEye',  # RapidEye constellation
            r'PlanetScope',  # PlanetScope
            r'GOES\s*(\d+)',  # GOES-16, GOES-17
            r'NOAA\s*(\d+)',  # NOAA satellites
            r'Envisat',  # Envisat
            r'ERS\s*(\d+)',  # ERS-1, ERS-2
            r'Radarsat\s*(\d+)',  # Radarsat-1, Radarsat-2
        ]
        
        for pattern in satellite_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                satellite = match.group(0).strip()
                break
        
        # If no satellite found, look for instrument names
        if not satellite:
            instrument_patterns = [
                r'OLI\s*(Operational Land Imager)?',
                r'TIRS\s*(Thermal Infrared Sensor)?',
                r'MSI\s*(Multi-Spectral Instrument)?',
                r'C-SAR\s*(C-band Synthetic Aperture Radar)?',
                r'OLCI\s*(Ocean and Land Colour Instrument)?',
                r'SLSTR\s*(Sea and Land Surface Temperature Radiometer)?',
            ]
            
            for pattern in instrument_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    satellite = match.group(0).strip()
                    break
        
        return satellite
    
    def _extract_resolution_from_satellite(self, satellite, text):
        """Extract resolution based on satellite type"""
        resolution = ""
        
        # Known satellite resolutions
        satellite_resolutions = {
            'Landsat 8': '30m (optical), 15m (panchromatic), 100m (thermal)',
            'Landsat 9': '30m (optical), 15m (panchromatic), 100m (thermal)',
            'Landsat 7': '30m (optical), 15m (panchromatic), 60m (thermal)',
            'Sentinel-1': '5m (SAR)',
            'Sentinel-2': '10m (visible/NIR), 20m (SWIR), 60m (atmospheric)',
            'Sentinel-3': '300m (OLCI), 1km (SLSTR)',
            'MODIS Terra': '250m, 500m, 1km',
            'MODIS Aqua': '250m, 500m, 1km',
            'SRTM': '30m (global), 90m (global)',
            'ASTER': '15m (visible/NIR), 30m (SWIR), 90m (TIR)',
            'SPOT 5': '2.5m (panchromatic), 10m (multispectral)',
            'Pleiades': '0.5m (panchromatic), 2m (multispectral)',
            'WorldView-2': '0.5m (panchromatic), 2m (multispectral)',
            'WorldView-3': '0.3m (panchromatic), 1.2m (multispectral)',
            'RapidEye': '5m (multispectral)',
            'PlanetScope': '3-4m (multispectral)',
            'GOES-16': '0.5km (visible), 2km (IR)',
            'GOES-17': '0.5km (visible), 2km (IR)',
        }
        
        # Try to match satellite name
        for sat_name, res in satellite_resolutions.items():
            if sat_name.lower() in satellite.lower():
                resolution = res
                break
        
        # If no match found, look for resolution in text
        if not resolution:
            resolution_patterns = [
                r'(\d+\s*(?:m|km|meters?|kilometers?))',
                r'(\d+\s*(?:arc|degree|minute|second))',
                r'(\d+\s*(?:pixel|px))',
                r'Resolution[:\s]+([^\n]+)',
                r'Pixel size[:\s]+([^\n]+)',
                r'Scale[:\s]+([^\n]+)',
            ]
            
            for pattern in resolution_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    resolution = match.group(1).strip()
                    break
        
        return resolution
    
    def _extract_sensor_type(self, satellite, text):
        """Extract sensor type (optical, radar, thermal, etc.)"""
        sensor_type = ""
        
        # Determine sensor type from satellite
        if any(radar_sat in satellite.lower() for radar_sat in ['sentinel-1', 'radarsat', 'ers', 'envisat']):
            sensor_type = "SAR (Synthetic Aperture Radar)"
        elif any(optical_sat in satellite.lower() for optical_sat in ['landsat', 'sentinel-2', 'spot', 'pleiades', 'worldview', 'rapideye', 'planetscope']):
            sensor_type = "Optical (Multispectral)"
        elif any(thermal_sat in satellite.lower() for thermal_sat in ['aster', 'landsat']):
            sensor_type = "Thermal Infrared"
        elif any(modis_sat in satellite.lower() for modis_sat in ['modis']):
            sensor_type = "Multispectral (Coarse Resolution)"
        elif any(weather_sat in satellite.lower() for weather_sat in ['goes', 'noaa']):
            sensor_type = "Weather/Meteorological"
        else:
            # Look for sensor type in text
            sensor_keywords = {
                'optical': ['optical', 'multispectral', 'visible', 'near infrared', 'nir'],
                'radar': ['sar', 'radar', 'synthetic aperture', 'microwave'],
                'thermal': ['thermal', 'infrared', 'tir', 'temperature'],
                'lidar': ['lidar', 'laser', 'altimetry'],
                'hyperspectral': ['hyperspectral', 'spectral', 'narrow band']
            }
            
            text_lower = text.lower()
            for sensor, keywords in sensor_keywords.items():
                if any(keyword in text_lower for keyword in keywords):
                    sensor_type = sensor.title()
                    break
        
        return sensor_type
    
    def _extract_dataset_id(self, text):
        """Extract dataset ID"""
        dataset_id = ""
        dataset_patterns = [
            r'Dataset ID[:\s]+([^\n]+)', 
            r'ID[:\s]+([^\n]+)', 
            r'Dataset[:\s]+([^\n]+)',
            r'Collection[:\s]+([^\n]+)',
            r'Product[:\s]+([^\n]+)',
            r'([A-Z]{2,}_[A-Z0-9_]+)',  # Common dataset ID pattern
            r'([A-Z]{2,}\d{4})'  # Another common pattern
        ]
        
        for pattern in dataset_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                potential_id = match.group(1).strip()
                # Filter out generic terms
                if potential_id.lower() not in ['google', 'developers', 'documentation', 'api']:
                    dataset_id = potential_id
                    break
        
        return dataset_id
    
    def _extract_date_ranges(self, text):
        """Extract date ranges and temporal information"""
        date_info = {
            'temporal_coverage': '',
            'date_range': '',
            'update_frequency': ''
        }
        
        # Extract temporal coverage
        temporal_patterns = [
            r'Temporal coverage[:\s]+([^\n]+)',
            r'Time period[:\s]+([^\n]+)',
            r'Date range[:\s]+([^\n]+)',
            r'(\d{4}[-/]\d{2}[-/]\d{2}\s*[-–]\s*\d{4}[-/]\d{2}[-/]\d{2})',
            r'(\d{4}\s*[-–]\s*\d{4})',
        ]
        
        for pattern in temporal_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                date_info['temporal_coverage'] = match.group(1).strip()
                break
        
        # Extract update frequency
        frequency_patterns = [
            r'Update frequency[:\s]+([^\n]+)',
            r'Refresh rate[:\s]+([^\n]+)',
            r'(\d+\s*(?:day|week|month|year)s?)',
        ]
        
        for pattern in frequency_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                date_info['update_frequency'] = match.group(1).strip()
                break
        
        return date_info
    
    def _extract_spatial_coverage(self, text):
        """Extract spatial coverage information"""
        spatial_coverage = ""
        
        spatial_patterns = [
            r'Spatial coverage[:\s]+([^\n]+)',
            r'Coverage area[:\s]+([^\n]+)',
            r'Geographic extent[:\s]+([^\n]+)',
            r'Region[:\s]+([^\n]+)',
            r'(\d+[°°]\s*[NS]\s*[-–]\s*\d+[°°]\s*[NS],\s*\d+[°°]\s*[EW]\s*[-–]\s*\d+[°°]\s*[EW])',
        ]
        
        for pattern in spatial_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                spatial_coverage = match.group(1).strip()
                break
        
        return spatial_coverage
    
    def _extract_bands_info(self, text):
        """Extract spectral bands information"""
        bands = []
        
        # Common band patterns
        band_patterns = [
            r'Band\s*(\d+)[:\s]+([^\n]+)',
            r'(\w+)\s*band[:\s]+([^\n]+)',
            r'(\d+)\s*nm[:\s]+([^\n]+)',
        ]
        
        for pattern in band_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                band_info = f"{match[0]}: {match[1].strip()}"
                bands.append(band_info)
        
        return bands
    
    def _extract_technical_details(self, text):
        """Extract additional technical details"""
        details = {}
        
        # Extract various technical parameters
        tech_patterns = {
            'orbit_type': r'Orbit[:\s]+([^\n]+)',
            'swath_width': r'Swath[:\s]+([^\n]+)',
            'revisit_time': r'Revisit[:\s]+([^\n]+)',
            'altitude': r'Altitude[:\s]+([^\n]+)',
            'launch_date': r'Launch[:\s]+([^\n]+)',
            'mission_duration': r'Mission[:\s]+([^\n]+)',
        }
        
        for key, pattern in tech_patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                details[key] = match.group(1).strip()
        
        return details
    
    def calculate_quality_score(self, result):
        """Calculate quality score based on extracted information"""
        score = 0.0
        total_fields = 0
        
        # Check each field with weights
        fields_to_check = [
            ('title', 2.0), ('description', 2.0), ('provider', 1.0), 
            ('tags', 1.0), ('date_range', 1.0), ('spatial_coverage', 1.0),
            ('thumbnail_url', 1.0), ('dataset_id', 1.0), ('resolution', 1.0),
            ('coverage_area', 1.0), ('update_frequency', 0.5), ('license', 0.5),
            ('documentation_url', 0.5), ('sample_code', 0.5)
        ]
        
        for field, weight in fields_to_check:
            total_fields += weight
            if result.get(field):
                if field == 'tags' and len(result[field]) > 0:
                    score += weight
                elif field in ['title', 'description'] and len(result[field]) > 10:
                    score += weight
                elif field in ['thumbnail_url', 'dataset_id', 'resolution', 'coverage_area'] and result[field]:
                    score += weight
                elif field in ['provider', 'date_range', 'spatial_coverage', 'update_frequency', 'license', 'documentation_url', 'sample_code'] and result[field]:
                    score += weight
        
        return (score / total_fields) if total_fields > 0 else 0.0
    
    def update_results_display(self):
        """Update all result displays"""
        self.update_table_view()
        self.update_card_view()
        self.update_json_view()
        self.update_statistics()
    
    def update_table_view(self):
        """Update table view"""
        self.results_table.setRowCount(len(self.extracted_data))
        
        for i, item in enumerate(self.extracted_data):
            self.results_table.setItem(i, 0, QTableWidgetItem(item.get('title', '')[:50]))
            self.results_table.setItem(i, 1, QTableWidgetItem(item.get('category', 'unknown')))
            self.results_table.setItem(i, 2, QTableWidgetItem(f"{item.get('confidence', 0.0):.2f}"))
            self.results_table.setItem(i, 3, QTableWidgetItem(f"{item.get('quality_score', 0.0):.2f}"))
            self.results_table.setItem(i, 4, QTableWidgetItem(item.get('provider', '')[:30]))
            self.results_table.setItem(i, 5, QTableWidgetItem(item.get('dataset_id', '')[:20]))
            self.results_table.setItem(i, 6, QTableWidgetItem("Yes" if item.get('thumbnail_url') else "No"))
            self.results_table.setItem(i, 7, QTableWidgetItem(item.get('source_url', '')[:50]))
    
    def update_card_view(self):
        """Update card view"""
        # Clear existing cards
        for i in reversed(range(self.card_layout.count())):
            self.card_layout.itemAt(i).widget().setParent(None)
        
        # Create new cards
        for item in self.extracted_data:
            card = self.create_data_card(item)
            self.card_layout.addWidget(card)
    
    def create_data_card(self, item):
        """Create a data card widget"""
        card = QFrame()
        card.setFrameStyle(QFrame.Box)
        card.setStyleSheet("""
            QFrame { 
                background-color: #2b2b2b; 
                border: 2px solid #404040; 
                border-radius: 8px; 
                padding: 15px; 
                margin: 5px;
            }
            QLabel { 
                color: #ffffff; 
                background-color: transparent;
                font-size: 11px;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel(f"<b>{item.get('title', 'No Title')}</b>")
        title_label.setWordWrap(True)
        layout.addWidget(title_label)
        
        # Category and confidence
        cat_conf = QLabel(f"Category: {item.get('category', 'unknown')} (Confidence: {item.get('confidence', 0.0):.2f})")
        layout.addWidget(cat_conf)
        
        # Quality score
        quality = QLabel(f"Quality Score: {item.get('quality_score', 0.0):.2f}")
        layout.addWidget(quality)
        
        # Dataset ID
        if item.get('dataset_id'):
            dataset_id = QLabel(f"Dataset ID: {item.get('dataset_id')}")
            layout.addWidget(dataset_id)
        
        # Provider
        if item.get('provider'):
            provider = QLabel(f"Provider: {item.get('provider')}")
            layout.addWidget(provider)
        
        # Resolution
        if item.get('resolution'):
            resolution = QLabel(f"Resolution: {item.get('resolution')}")
            layout.addWidget(resolution)
        
        # Coverage area
        if item.get('coverage_area'):
            coverage = QLabel(f"Coverage: {item.get('coverage_area')}")
            layout.addWidget(coverage)
        
        # Thumbnail
        if item.get('thumbnail_url'):
            thumbnail = QLabel(f"Thumbnail: Yes ({item.get('thumbnail_alt', 'No alt text')})")
            layout.addWidget(thumbnail)
        
        # Tags
        if item.get('tags'):
            tags = QLabel(f"Tags: {', '.join(item.get('tags', [])[:3])}")
            layout.addWidget(tags)
        
        # URL
        url = QLabel(f"URL: {item.get('source_url', '')[:50]}...")
        url.setWordWrap(True)
        layout.addWidget(url)
        
        card.setLayout(layout)
        return card
    
    def update_json_view(self):
        """Update JSON view"""
        json_data = json.dumps(self.extracted_data, indent=2, ensure_ascii=False)
        self.json_view.setText(json_data)
    
    def update_statistics(self):
        """Update statistics display"""
        success_rate = (self.successful_extractions/self.total_processed*100) if self.total_processed > 0 else 0
        categories = set(item.get('category', 'unknown') for item in self.extracted_data)
        
        stats = f"""
📊 Statistics:
• Total Processed: {self.total_processed}
• Successful: {self.successful_extractions}
• Failed: {self.failed_extractions}
• Success Rate: {success_rate:.1f}%
• Categories Found: {len(categories)}
• Categories: {', '.join(categories)}
        """
        self.stats_text.setText(stats)
    
    def show_summary(self):
        """Show crawl summary"""
        success_rate = (self.successful_extractions/self.total_processed*100) if self.total_processed > 0 else 0
        summary = f"""
🎉 Crawl Summary:
• Total Links: {self.total_processed}
• Successful Extractions: {self.successful_extractions}
• Failed Extractions: {self.failed_extractions}
• Success Rate: {success_rate:.1f}%
        """
        self.log_message(summary)
    
    def export_results(self):
        """Export results to JSON"""
        if not self.extracted_data:
            QMessageBox.warning(self, "Warning", "No data to export!")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Results", "lightweight_crawler_results.json", "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.extracted_data, f, indent=2, ensure_ascii=False)
                self.log_message(f"✅ Results exported to {file_path}")
            except Exception as e:
                self.log_error(f"❌ Export failed: {e}")
    
    def crawl_finished(self):
        """Cleanup after crawling"""
        self.is_crawling = False
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.status_label.setText("Ready")
    
    def update_progress(self, current, total, progress):
        """Thread-safe progress update"""
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
    
    def update_status(self, status):
        """Thread-safe status update"""
        self.status_label.setText(status)
    
    def on_scraping_method_changed(self, text):
        """Handle scraping method selection"""
        if "Auto" in text:
            self.scraping_method = 'auto'
        elif "Selenium" in text:
            self.scraping_method = 'selenium'
        elif "Cloudscraper" in text:
            self.scraping_method = 'cloudscraper'
        else:
            self.scraping_method = 'requests'
        
        self.log_message(f"Scraping method changed to: {self.scraping_method}")
    
    def log_message(self, message):
        """Log message to console"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.console.append(f"[{timestamp}] {message}")
    
    def log_error(self, message):
        """Log error to console"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.console.append(f"[{timestamp}] ERROR: {message}")

def main():
    """Main function"""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show window
    window = WebFlutterCrawlerUI()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 