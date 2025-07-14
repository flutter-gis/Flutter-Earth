import sys
import os
import json
import threading
import time
import requests
from queue import Queue
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from PySide6.QtCore import QObject, QUrl, Signal, Property, Slot
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
import subprocess

class CrawlerBackend(QObject):
    # Signals for QML communication
    logMessage = Signal(str)
    progressUpdated = Signal(int)
    statusChanged = Signal(str)
    crawlingStateChanged = Signal(bool)
    datasetsUpdated = Signal(list)
    mlLog = Signal(str)
    validationLog = Signal(str)
    errorLog = Signal(str)
    spacyStatusChanged = Signal(bool)
    bertStatusChanged = Signal(bool)
    geoStatusChanged = Signal(bool)
    dashboardStatusChanged = Signal(bool)
    configStatusChanged = Signal(bool)

    def __init__(self):
        super().__init__()
        self.is_crawling = False
        self.stop_requested = False
        self.datasets = []
        self.output_dir = "extracted_data"
        self.images_dir = "thumbnails"
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.images_dir, exist_ok=True)
        # Advanced feature flags
        self.spacy_available = self.check_and_install('spacy')
        self.bert_available = self.check_and_install('transformers')
        self.sklearn_available = self.check_and_install('sklearn', 'scikit-learn')
        self.geopy_available = self.check_and_install('geopy')
        self.yaml_available = self.check_and_install('pyyaml')
        self.dash_available = self.check_and_install('dash')
        self.pytesseract_available = self.check_and_install('pytesseract')
        self.plotly_available = self.check_and_install('plotly')
        # Status signals
        self.spacyStatusChanged.emit(self.spacy_available)
        self.bertStatusChanged.emit(self.bert_available)
        self.geoStatusChanged.emit(self.geopy_available)
        self.dashboardStatusChanged.emit(self.dash_available)
        self.configStatusChanged.emit(self.yaml_available)
        # Placeholders for advanced objects
        self.nlp = None
        self.bert_classifier = None
        self.tfidf_vectorizer = None
        self.geocoder = None
        self.dashboard = None
        self.config = None
        self.plugins = {}
        # Load advanced features
        self.init_advanced_features()
        # Error handling
        self.error_tracker = {
            'total_errors': 0,
            'retry_attempts': 0,
            'recovered_results': 0,
            'error_categories': {}
        }
        self.max_retries = 3
        self.retry_delay = 2

    def check_and_install(self, import_name, pip_name=None):
        if pip_name is None:
            pip_name = import_name
        try:
            __import__(import_name)
            return True
        except ImportError:
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', pip_name])
                __import__(import_name)
                return True
            except Exception as e:
                print(f"Failed to install {pip_name}: {e}")
                return False

    def init_advanced_features(self):
        # spaCy
        if self.spacy_available:
            try:
                import spacy
                self.nlp = spacy.load("en_core_web_sm")
                self.spacyStatusChanged.emit(True)
            except Exception as e:
                print(f"spaCy model not loaded: {e}")
                self.spacyStatusChanged.emit(False)
        # BERT/Transformers
        if self.bert_available and self.sklearn_available:
            try:
                from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
                from sklearn.feature_extraction.text import TfidfVectorizer
                self.bert_tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
                self.bert_model = AutoModelForSequenceClassification.from_pretrained("bert-base-uncased")
                self.bert_classifier = pipeline("text-classification", model=self.bert_model, tokenizer=self.bert_tokenizer)
                self.tfidf_vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
                self.bertStatusChanged.emit(True)
            except Exception as e:
                print(f"Advanced ML models not loaded: {e}")
                self.bertStatusChanged.emit(False)
        # Geopy
        if self.geopy_available:
            try:
                from geopy.geocoders import Nominatim
                self.geocoder = Nominatim(user_agent="earth_engine_crawler")
                self.geoStatusChanged.emit(True)
            except Exception as e:
                print(f"Geocoder not initialized: {e}")
                self.geoStatusChanged.emit(False)
        # Config/plugins
        if self.yaml_available:
            try:
                import yaml
                from config_utils import load_config, load_plugins
                self.config = load_config()
                self.plugins = load_plugins(self.config.get('plugins', []))
                self.configStatusChanged.emit(True)
            except Exception as e:
                print(f"Config/plugins not loaded: {e}")
                self.configStatusChanged.emit(False)
        # Dashboard
        if self.dash_available:
            try:
                from analytics_dashboard import get_dashboard
                self.dashboard = get_dashboard()
                self.dashboard.start_background()
                self.dashboardStatusChanged.emit(True)
                print("Analytics dashboard started on http://127.0.0.1:8080")
            except Exception as e:
                print(f"Analytics dashboard not started: {e}")
                self.dashboardStatusChanged.emit(False)

    @Slot()
    def openDashboard(self):
        import webbrowser
        webbrowser.open("http://127.0.0.1:8080")

    @Slot()
    def editConfig(self):
        config_path = os.path.join(os.path.dirname(__file__), "crawler_config.yaml")
        os.startfile(config_path)

    # Add ML, validation, and error log methods
    def logML(self, message):
        self.mlLog.emit(message)
    def logValidation(self, message):
        self.validationLog.emit(message)
    def logError(self, message):
        self.errorLog.emit(message)

    @Slot(str, bool, bool, bool)
    def startCrawling(self, html_file, download_thumbs, extract_details, save_individual):
        """Start the crawling process"""
        if not html_file or not os.path.exists(html_file):
            self.logMessage.emit("ERROR: Please select a valid HTML file")
            return
        
        self.is_crawling = True
        self.stop_requested = False
        self.crawlingStateChanged.emit(True)
        self.statusChanged.emit("Crawling...")
        self.progressUpdated.emit(0)
        self.logMessage.emit(f"Starting crawl of: {html_file}")
        
        # Start crawling in a separate thread
        thread = threading.Thread(
            target=self.crawl_html_file,
            args=(html_file, download_thumbs, extract_details, save_individual),
            daemon=True
        )
        thread.start()
    
    @Slot()
    def stopCrawling(self):
        """Stop the crawling process"""
        self.stop_requested = True
        self.logMessage.emit("Stopping crawler...")
    
    def crawl_html_file(self, html_file, download_thumbs, extract_details, save_individual):
        """Main crawling function"""
        try:
            # Read the HTML file
            with open(html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            self.logMessage.emit("Parsing HTML content...")
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find all dataset links
            links = soup.find_all('a', href=True)
            dataset_links = []
            
            for link in links:
                href = link.get('href')
                if href and ('catalog' in href or 'datasets' in href):
                    # Convert relative URLs to absolute
                    if href.startswith('/'):
                        href = f"https://developers.google.com{href}"
                    elif not href.startswith('http'):
                        href = urljoin("https://developers.google.com/earth-engine/datasets/", href)
                    dataset_links.append(href)
            
            self.logMessage.emit(f"Found {len(dataset_links)} potential dataset links")
            
            # Remove duplicates
            dataset_links = list(set(dataset_links))
            self.logMessage.emit(f"Unique links to process: {len(dataset_links)}")
            
            # Setup webdriver for detailed crawling
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            options.add_argument('--window-size=1920,1080')
            driver = webdriver.Edge(options=options)
            
            processed_count = 0
            total_links = len(dataset_links)
            self.datasets = []
            
            for i, link in enumerate(dataset_links):
                if self.stop_requested:
                    self.logMessage.emit("Crawling stopped by user")
                    break
                
                try:
                    self.logMessage.emit(f"Processing {i+1}/{total_links}: {link}")
                    
                    # Get the page content
                    driver.get(link)
                    time.sleep(2)  # Wait for page to load
                    
                    page_html = driver.page_source
                    page_soup = BeautifulSoup(page_html, 'html.parser')
                    
                    # Extract dataset information
                    dataset_data = self.extract_dataset_info(page_soup, link)
                    
                    if dataset_data:
                        # Download thumbnail if requested
                        if download_thumbs and dataset_data.get('thumbnail_url'):
                            thumb_path = self.download_image(dataset_data['thumbnail_url'])
                            dataset_data['thumbnail_path'] = thumb_path
                        
                        # Add to datasets list
                        self.datasets.append(dataset_data)
                        
                        # Save as individual JSON file
                        if save_individual:
                            safe_title = "".join(c for c in dataset_data.get('title', 'dataset') if c.isalnum() or c in (' ', '-', '_')).rstrip()
                            safe_title = safe_title[:50]  # Limit length
                            json_filename = f"{safe_title}_{i}.json"
                            json_path = os.path.join(self.output_dir, json_filename)
                            
                            with open(json_path, 'w', encoding='utf-8') as f:
                                json.dump(dataset_data, f, ensure_ascii=False, indent=2)
                            
                            self.logMessage.emit(f"Saved: {json_filename}")
                            processed_count += 1
                    
                    # Update progress
                    progress = int((i + 1) / total_links * 100)
                    self.progressUpdated.emit(progress)
                    
                    # Update datasets in QML
                    self.datasetsUpdated.emit(self.datasets)
                    
                    # Small delay to be respectful
                    time.sleep(0.5)
                    
                except Exception as e:
                    self.logMessage.emit(f"ERROR processing {link}: {str(e)}")
                    continue
            
            driver.quit()
            
            self.logMessage.emit(f"Crawling complete! Processed {processed_count} datasets.")
            self.logMessage.emit(f"Data saved to: {self.output_dir}")
            if download_thumbs:
                self.logMessage.emit(f"Thumbnails saved to: {self.images_dir}")
            
            # Final status update
            self.is_crawling = False
            self.crawlingStateChanged.emit(False)
            self.statusChanged.emit("Crawling complete!")
            
        except Exception as e:
            self.logMessage.emit(f"ERROR: Crawling failed: {str(e)}")
            self.is_crawling = False
            self.crawlingStateChanged.emit(False)
            self.statusChanged.emit("Crawling failed!")
    
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
            self.logMessage.emit(f"Failed to download image {url}: {str(e)}")
            return None
    
    @Slot()
    def clearConsole(self):
        """Clear the console output"""
        # This will be handled by QML
        pass
    
    @Slot(str)
    def logMessage(self, message):
        """Log a message to the console"""
        timestamp = time.strftime('%H:%M:%S')
        self.logMessage.emit(f"[{timestamp}] {message}")

def main():
    app = QGuiApplication(sys.argv)
    
    # Create QML engine
    engine = QQmlApplicationEngine()
    
    # Create backend instance
    backend = CrawlerBackend()
    
    # Expose backend to QML
    engine.rootContext().setContextProperty("crawlerBackend", backend)
    
    # Load main QML file
    engine.load(QUrl.fromLocalFile(os.path.join(os.path.dirname(__file__), "main.qml")))
    
    if not engine.rootObjects():
        sys.exit(-1)
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 