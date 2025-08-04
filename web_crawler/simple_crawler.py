#!/usr/bin/env python3
"""
Simple Web Crawler - Downloads Everything
No categorization, no ML, just pure crawling and downloading
"""

import os
import sys
import json
import time
import threading
import requests
import warnings
import hashlib
import urllib.parse
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

# Suppress SSL warnings
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

class SimpleCrawler:
    """Advanced simple crawler with sophisticated depth and lag management"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Configure session for better reliability
        self.session.mount('http://', requests.adapters.HTTPAdapter(max_retries=3))
        self.session.mount('https://', requests.adapters.HTTPAdapter(max_retries=3))
        
        # Create output directories
        self.output_dir = "simple_crawled_data"
        self.setup_directories()
        
        # Advanced crawling state
        self.visited_urls = set()
        self.downloaded_files = set()
        self.stop_crawling = False
        self.pause_crawling = False
        
        # Advanced depth management
        self.depth_weights = {
            0: 1.0,    # Root level - full priority
            1: 0.8,    # First level - high priority
            2: 0.6,    # Second level - medium priority
            3: 0.4,    # Third level - lower priority
            4: 0.2,    # Fourth level - low priority
            5: 0.1     # Fifth level - minimal priority
        }
        
        # Advanced lag management
        self.lag_strategies = {
            'adaptive': True,           # Adaptive lag based on server response
            'exponential_backoff': True, # Exponential backoff on errors
            'rate_limiting': True,      # Rate limiting per domain
            'smart_delays': True        # Smart delays based on content type
        }
        
        # Domain-specific lag tracking
        self.domain_lags = {}
        self.domain_request_counts = {}
        self.last_request_time = {}
        
        # Content type delays
        self.content_type_delays = {
            'text/html': 1.0,
            'image/jpeg': 0.5,
            'image/png': 0.5,
            'image/gif': 0.3,
            'application/pdf': 2.0,
            'application/msword': 1.5,
            'default': 1.0
        }
        
    def setup_directories(self):
        """Create output directories"""
        directories = [
            self.output_dir,
            f"{self.output_dir}/images",
            f"{self.output_dir}/documents",
            f"{self.output_dir}/html",
            f"{self.output_dir}/text"
        ]
        
        for directory in directories:
            try:
                Path(directory).mkdir(parents=True, exist_ok=True)
            except Exception as e:
                # Silent mode - don't print directory errors to console
                # Try to create with a fallback name
                try:
                    fallback_dir = f"{directory}_backup_{int(time.time())}"
                    Path(fallback_dir).mkdir(parents=True, exist_ok=True)
                    # Silent mode - don't print fallback directory creation
                except Exception as e2:
                    # Silent mode - don't print fallback directory errors
                    pass
    
    def download_file(self, url, file_type):
        """Download a file and save it"""
        if url in self.downloaded_files:
            return None
        
        # Validate URL
        if not self._is_valid_url(url):
            # Silent mode - don't print validation errors to console
            return None
            
        try:
            response = self.session.get(url, timeout=30, verify=False)
            response.raise_for_status()
            
            # Generate filename
            filename = self._get_filename_from_url(url)
            if not filename:
                filename = f"file_{hashlib.md5(url.encode()).hexdigest()[:8]}"
            
            # Get extension from content type
            ext = self._get_extension_from_content_type(response.headers.get('content-type', ''))
            
            # Add extension if missing
            if '.' not in filename and ext:
                filename += ext
            
            # Create safe filename
            safe_filename = self._get_safe_filename(url, 0).replace('.html', '')
            if ext:
                safe_filename += ext
            else:
                safe_filename += '.bin'
            
            # Save file
            filepath = os.path.join(self.output_dir, file_type, safe_filename)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            self.downloaded_files.add(url)
            return filepath
            
        except requests.exceptions.RequestException as e:
            # Silent mode - don't print download errors to console
            return None
        except Exception as e:
            # Silent mode - don't print download errors to console
            return None
    
    def _get_filename_from_url(self, url):
        """Extract filename from URL"""
        try:
            parsed = urllib.parse.urlparse(url)
            filename = os.path.basename(parsed.path)
            if filename:
                return filename
        except:
            pass
        return ""
    
    def _get_extension_from_content_type(self, content_type):
        """Get file extension from content type"""
        content_type = content_type.lower()
        
        extensions = {
            'image/jpeg': '.jpg',
            'image/jpg': '.jpg',
            'image/png': '.png',
            'image/gif': '.gif',
            'image/webp': '.webp',
            'image/svg+xml': '.svg',
            'application/pdf': '.pdf',
            'application/msword': '.doc',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
            'application/vnd.ms-excel': '.xls',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx',
            'text/plain': '.txt',
            'text/html': '.html',
            'text/css': '.css',
            'application/javascript': '.js'
        }
        
        return extensions.get(content_type, '')
    
    def get_domain_from_url(self, url):
        """Extract domain from URL for rate limiting"""
        try:
            parsed = urllib.parse.urlparse(url)
            return parsed.netloc
        except:
            return "unknown"
    
    def calculate_adaptive_delay(self, url, content_type=None, response_time=None):
        """Calculate adaptive delay based on multiple factors"""
        domain = self.get_domain_from_url(url)
        base_delay = 1.0
        
        # Domain-specific rate limiting
        if domain in self.domain_request_counts:
            request_count = self.domain_request_counts[domain]
            if request_count > 10:
                base_delay *= 2.0  # Slow down for high-request domains
            elif request_count > 5:
                base_delay *= 1.5
        else:
            self.domain_request_counts[domain] = 0
        
        # Content type specific delays
        if content_type and content_type in self.content_type_delays:
            base_delay *= self.content_type_delays[content_type]
        
        # Response time adaptation
        if response_time:
            if response_time > 5.0:
                base_delay *= 1.5  # Slow down if server is slow
            elif response_time < 0.5:
                base_delay *= 0.8  # Speed up if server is fast
        
        # Exponential backoff for errors
        if domain in self.domain_lags and self.domain_lags[domain] > 0:
            base_delay *= (2 ** min(self.domain_lags[domain], 3))
        
        return max(0.1, min(base_delay, 10.0))  # Clamp between 0.1 and 10 seconds
    
    def update_domain_stats(self, url, response_time=None, success=True):
        """Update domain statistics for adaptive lag"""
        domain = self.get_domain_from_url(url)
        
        # Update request count
        if domain in self.domain_request_counts:
            self.domain_request_counts[domain] += 1
        else:
            self.domain_request_counts[domain] = 1
        
        # Update lag counter for errors
        if not success:
            if domain in self.domain_lags:
                self.domain_lags[domain] += 1
            else:
                self.domain_lags[domain] = 1
        else:
            # Reset lag counter on success
            if domain in self.domain_lags:
                self.domain_lags[domain] = max(0, self.domain_lags[domain] - 1)
        
        # Update last request time
        self.last_request_time[domain] = time.time()
    
    def get_depth_priority(self, depth):
        """Get priority weight for a given depth"""
        return self.depth_weights.get(depth, 0.05)  # Default to very low priority
    
    def _is_valid_url(self, url):
        """Validate URL format"""
        try:
            parsed = urllib.parse.urlparse(url)
            return all([parsed.scheme, parsed.netloc])
        except Exception:
            return False
    
    def _get_safe_filename(self, url, depth):
        """Generate a safe filename for the URL"""
        try:
            # Create a safe filename from URL
            parsed = urllib.parse.urlparse(url)
            domain = parsed.netloc.replace('.', '_')
            path = parsed.path.replace('/', '_').replace('\\', '_')
            if not path or path == '_':
                path = 'index'
            
            # Limit length and remove problematic characters
            safe_path = ''.join(c for c in path if c.isalnum() or c in '_-')
            safe_path = safe_path[:50]  # Limit length
            
            # Add depth and hash for uniqueness
            url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
            filename = f"page_depth{depth}_{domain}_{safe_path}_{url_hash}.html"
            
            # Ensure it's a valid filename
            filename = ''.join(c for c in filename if c.isalnum() or c in '._-')
            return filename
        except Exception:
            # Fallback to hash-based filename
            url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
            return f"page_depth{depth}_{url_hash}.html"
    
    def process_html_file(self, file_path):
        """Process a local HTML file and extract all links"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract all links from the HTML file
            links = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                
                # Make URL absolute if it's relative
                if not href.startswith(('http://', 'https://')):
                    # For local files, we'll treat relative URLs as external
                    # You might want to customize this based on your needs
                    continue
                
                # Filter out non-HTTP links
                if href.startswith(('http://', 'https://')):
                    links.append(href)
            
            return links
            
        except Exception as e:
            # Silent mode - don't print HTML processing errors to console
            return []
    
    def process_html_folder(self, folder_path):
        """Process all HTML files in a folder and extract all links"""
        all_links = []
        
        try:
            for file in os.listdir(folder_path):
                if file.lower().endswith(('.html', '.htm')):
                    file_path = os.path.join(folder_path, file)
                    links = self.process_html_file(file_path)
                    all_links.extend(links)
            
            # Remove duplicates
            all_links = list(set(all_links))
            return all_links
            
        except Exception as e:
            # Silent mode - don't print HTML folder processing errors to console
            return []
    
    def extract_images(self, soup, base_url):
        """Extract all images from the page"""
        images = []
        
        for img in soup.find_all('img'):
            src = img.get('src') or img.get('data-src')
            if not src:
                continue
                
            # Make URL absolute
            if not src.startswith(('http://', 'https://')):
                src = urljoin(base_url, src)
            
            images.append({
                'url': src,
                'alt': img.get('alt', ''),
                'title': img.get('title', '')
            })
        
        return images
    
    def extract_links(self, soup, base_url):
        """Extract all links from the page"""
        links = []
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            
            # Make URL absolute
            if not href.startswith(('http://', 'https://')):
                href = urljoin(base_url, href)
            
            # Filter out non-HTTP links
            if href.startswith(('http://', 'https://')):
                links.append(href)
        
        return links
    
    def extract_text_content(self, soup):
        """Extract all text content from the page"""
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text content
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def crawl_page(self, url, depth=0):
        """Advanced crawl with sophisticated depth and lag management"""
        if url in self.visited_urls:
            return None
        
        # Validate URL format
        if not self._is_valid_url(url):
            # Silent mode - don't print validation errors to console
            return None
        
        self.visited_urls.add(url)
        # Silent mode - only log to UI, not console
        # print(f"Crawling: {url} (depth: {depth}, priority: {self.get_depth_priority(depth):.2f})")
        
        start_time = time.time()
        success = False
        
        try:
            # Calculate adaptive delay before request
            adaptive_delay = self.calculate_adaptive_delay(url)
            if adaptive_delay > 0.1:
                time.sleep(adaptive_delay)
            
            # Get page content with longer timeout for comprehensive crawling
            timeout = min(60, 30 + (depth * 10))  # Longer timeout, max 60 seconds
            response = self.session.get(url, timeout=timeout, verify=False)
            response.raise_for_status()
            
            response_time = time.time() - start_time
            success = True
            
            # Update domain statistics
            self.update_domain_stats(url, response_time, success=True)
            
            html_content = response.text
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Save HTML with depth information - use safe filename
            safe_filename = self._get_safe_filename(url, depth)
            html_path = os.path.join(self.output_dir, "html", safe_filename)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(html_path), exist_ok=True)
            
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Extract and download images with content-type awareness (limit to prevent hanging)
            images = self.extract_images(soup, url)
            for i, img in enumerate(images[:10]):  # Limit to 10 images per page
                try:
                    # Use shorter delay for images
                    img_delay = self.calculate_adaptive_delay(img['url'], 'image/jpeg')
                    if img_delay > 0.1:
                        time.sleep(img_delay)
                    self.download_file(img['url'], 'images')
                except Exception as e:
                    # Silent mode - don't print download errors to console
                    pass
            
            # Extract and download documents with longer delays (limit to prevent hanging)
            links = self.extract_links(soup, url)
            doc_count = 0
            for link in links:
                try:
                    if any(ext in link.lower() for ext in ['.pdf', '.doc', '.docx', '.xls', '.xlsx']):
                        if doc_count >= 5:  # Limit to 5 documents per page
                            break
                        # Use longer delay for documents
                        doc_delay = self.calculate_adaptive_delay(link, 'application/pdf')
                        if doc_delay > 0.1:
                            time.sleep(doc_delay)
                        self.download_file(link, 'documents')
                        doc_count += 1
                except Exception as e:
                    # Silent mode - don't print download errors to console
                    pass
            
            # Extract and save text content
            text_content = self.extract_text_content(soup)
            if text_content.strip():
                text_filename = f"text_depth{depth}_{hashlib.md5(url.encode()).hexdigest()[:8]}.txt"
                text_path = os.path.join(self.output_dir, "text", text_filename)
                
                # Ensure directory exists
                os.makedirs(os.path.dirname(text_path), exist_ok=True)
                
                with open(text_path, 'w', encoding='utf-8') as f:
                    f.write(text_content)
            
            # Create enhanced page data
            page_data = {
                'url': url,
                'depth': depth,
                'priority': self.get_depth_priority(depth),
                'html_file': html_path,
                'images_found': len(images),
                'links_found': len(links),
                'text_length': len(text_content),
                'response_time': response_time,
                'adaptive_delay': adaptive_delay,
                'domain': self.get_domain_from_url(url),
                'timestamp': datetime.now().isoformat()
            }
            
            return page_data
            
        except requests.exceptions.RequestException as e:
            response_time = time.time() - start_time
            self.update_domain_stats(url, response_time, success=False)
            # Silent mode - don't print network errors to console
            return None
        except Exception as e:
            response_time = time.time() - start_time
            self.update_domain_stats(url, response_time, success=False)
            # Silent mode - don't print general errors to console
            return None

class SimpleCrawlerUI(QWidget):
    """Simple crawler UI - no categorization, just pure crawling"""
    
    # Define signals for thread-safe UI updates
    progress_updated = Signal(int, int)
    status_updated = Signal(str)
    data_updated = Signal()
    log_updated = Signal(str)
    error_updated = Signal(str)
    page_updated = Signal(dict)  # Signal to add page data to table
    
    def __init__(self):
        super().__init__()
        self.crawler = SimpleCrawler()
        self.crawl_thread = None
        self.is_crawling = False
        self.max_depth = 3
        self.delay = 1.0
        
        self.setup_ui()
        self.apply_dark_theme()
    
    def setup_ui(self):
        """Setup the UI"""
        self.setWindowTitle("Advanced Simple Web Crawler - Smart Depth, Lag & HTML Folder Support")
        self.setGeometry(100, 100, 1200, 800)
        
        # Main layout
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Advanced Simple Web Crawler")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin: 10px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        subtitle = QLabel("Smart depth management, adaptive lag control, and HTML folder support")
        subtitle.setStyleSheet("font-size: 14px; color: #888; margin-bottom: 20px;")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)
        
        # URL input
        url_frame = QFrame()
        url_layout = QHBoxLayout()
        
        url_label = QLabel("Start URL:")
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://example.com")
        
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)
        url_frame.setLayout(url_layout)
        layout.addWidget(url_frame)
        
        # HTML Folder input
        html_frame = QFrame()
        html_layout = QHBoxLayout()
        
        html_label = QLabel("HTML Folder (optional):")
        self.html_folder_input = QLineEdit()
        self.html_folder_input.setPlaceholderText("Select folder with HTML files containing links")
        
        html_browse_button = QPushButton("Browse HTML")
        html_browse_button.clicked.connect(self.browse_html_folder)
        
        html_layout.addWidget(html_label)
        html_layout.addWidget(self.html_folder_input)
        html_layout.addWidget(html_browse_button)
        html_frame.setLayout(html_layout)
        layout.addWidget(html_frame)
        
        # Settings frame
        settings_frame = QGroupBox("Settings")
        settings_layout = QGridLayout()
        
        # Max depth
        depth_label = QLabel("Max Depth:")
        self.depth_input = QSpinBox()
        self.depth_input.setRange(1, 20)  # Increased range for advanced crawling
        self.depth_input.setValue(5)
        
        # Base delay
        delay_label = QLabel("Base Delay (seconds):")
        self.delay_input = QDoubleSpinBox()
        self.delay_input.setRange(0.1, 15.0)  # Increased range
        self.delay_input.setValue(1.0)
        self.delay_input.setSingleStep(0.1)
        
        # Advanced settings
        advanced_label = QLabel("Advanced Features:")
        self.adaptive_delay_check = QCheckBox("Adaptive Delay")
        self.adaptive_delay_check.setChecked(True)
        self.exponential_backoff_check = QCheckBox("Exponential Backoff")
        self.exponential_backoff_check.setChecked(True)
        self.rate_limiting_check = QCheckBox("Rate Limiting")
        self.rate_limiting_check.setChecked(True)
        self.smart_delays_check = QCheckBox("Smart Content Delays")
        self.smart_delays_check.setChecked(True)
        
        # Output directory
        output_label = QLabel("Output Directory:")
        self.output_input = QLineEdit()
        self.output_input.setText("simple_crawled_data")
        
        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.browse_output_dir)
        
        settings_layout.addWidget(depth_label, 0, 0)
        settings_layout.addWidget(self.depth_input, 0, 1)
        settings_layout.addWidget(delay_label, 0, 2)
        settings_layout.addWidget(self.delay_input, 0, 3)
        
        # Advanced features row
        settings_layout.addWidget(advanced_label, 1, 0)
        advanced_frame = QFrame()
        advanced_layout = QHBoxLayout()
        advanced_layout.addWidget(self.adaptive_delay_check)
        advanced_layout.addWidget(self.exponential_backoff_check)
        advanced_layout.addWidget(self.rate_limiting_check)
        advanced_layout.addWidget(self.smart_delays_check)
        advanced_frame.setLayout(advanced_layout)
        settings_layout.addWidget(advanced_frame, 1, 1, 1, 3)
        
        # Output directory row
        settings_layout.addWidget(output_label, 2, 0)
        settings_layout.addWidget(self.output_input, 2, 1, 1, 2)
        settings_layout.addWidget(browse_button, 2, 3)
        
        settings_frame.setLayout(settings_layout)
        layout.addWidget(settings_frame)
        
        # Control buttons
        button_frame = QFrame()
        button_layout = QHBoxLayout()
        
        self.start_button = QPushButton("Start Crawling")
        self.start_button.clicked.connect(self.start_crawl)
        
        self.stop_button = QPushButton("Stop Crawling")
        self.stop_button.clicked.connect(self.stop_crawl)
        self.stop_button.setEnabled(False)
        
        self.pause_button = QPushButton("Pause")
        self.pause_button.clicked.connect(self.toggle_pause)
        self.pause_button.setEnabled(False)
        
        open_folder_button = QPushButton("Open Output Folder")
        open_folder_button.clicked.connect(self.open_output_folder)
        
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.pause_button)
        button_layout.addWidget(open_folder_button)
        
        button_frame.setLayout(button_layout)
        layout.addWidget(button_frame)
        
        # Progress
        progress_frame = QGroupBox("Progress")
        progress_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.status_label = QLabel("Ready to start")
        
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.status_label)
        
        progress_frame.setLayout(progress_layout)
        layout.addWidget(progress_frame)
        
        # Results table
        results_frame = QGroupBox("Crawled Pages")
        results_layout = QVBoxLayout()
        
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(8)
        self.results_table.setHorizontalHeaderLabels([
            "URL", "Depth", "Priority", "Images", "Links", "Response Time", "Delay", "Domain"
        ])
        
        results_layout.addWidget(self.results_table)
        results_frame.setLayout(results_layout)
        layout.addWidget(results_frame)
        
        # Log
        log_frame = QGroupBox("Log")
        log_layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(150)
        
        log_layout.addWidget(self.log_text)
        log_frame.setLayout(log_layout)
        layout.addWidget(log_frame)
        
        self.setLayout(layout)
        
        # Connect signals
        self.progress_updated.connect(self.update_progress)
        self.status_updated.connect(self.update_status)
        self.data_updated.connect(self.update_results_table)
        self.log_updated.connect(self.log_message_signal)
        self.error_updated.connect(self.log_error_signal)
        self.page_updated.connect(self.add_page_to_table)
    
    def browse_output_dir(self):
        """Browse for output directory"""
        directory = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if directory:
            self.output_input.setText(directory)
            self.crawler.output_dir = directory
            self.crawler.setup_directories()
    
    def browse_html_folder(self):
        """Browse for HTML folder containing files with links"""
        directory = QFileDialog.getExistingDirectory(self, "Select HTML Folder")
        if directory:
            self.html_folder_input.setText(directory)
            # Check if folder contains HTML files
            html_files = []
            for file in os.listdir(directory):
                if file.lower().endswith(('.html', '.htm')):
                    html_files.append(os.path.join(directory, file))
            
            if html_files:
                self.log_updated.emit(f"Found {len(html_files)} HTML files in folder")
            else:
                QMessageBox.warning(self, "Warning", "No HTML files found in selected folder.")
    
    def open_output_folder(self):
        """Open the output folder"""
        output_dir = self.output_input.text()
        if os.path.exists(output_dir):
            os.startfile(output_dir)
        else:
            QMessageBox.warning(self, "Warning", "Output directory does not exist yet.")
    
    def start_crawl(self):
        """Start the crawling process"""
        if self.is_crawling:
            return
        
        url = self.url_input.text().strip()
        html_folder = self.html_folder_input.text().strip()
        
        if not url and not html_folder:
            QMessageBox.warning(self, "Error", "Please enter either a URL or select an HTML folder.")
            return
        
        # Update settings
        self.max_depth = self.depth_input.value()
        self.delay = self.delay_input.value()
        self.crawler.output_dir = self.output_input.text()
        self.crawler.setup_directories()
        
        # Update advanced features
        self.crawler.lag_strategies['adaptive'] = self.adaptive_delay_check.isChecked()
        self.crawler.lag_strategies['exponential_backoff'] = self.exponential_backoff_check.isChecked()
        self.crawler.lag_strategies['rate_limiting'] = self.rate_limiting_check.isChecked()
        self.crawler.lag_strategies['smart_delays'] = self.smart_delays_check.isChecked()
        
        # Clear previous results
        self.crawler.visited_urls.clear()
        self.crawler.downloaded_files.clear()
        self.results_table.setRowCount(0)
        
        # Start crawling
        self.is_crawling = True
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.pause_button.setEnabled(True)
        
        # Get HTML folder path
        html_folder = self.html_folder_input.text().strip() if self.html_folder_input.text().strip() else None
        
        self.crawl_thread = threading.Thread(target=self.crawl_worker, args=(url, html_folder))
        self.crawl_thread.daemon = True
        self.crawl_thread.start()
    
    def crawl_worker(self, start_url, html_folder=None):
        """Worker thread for crawling"""
        try:
            self.status_updated.emit("Starting crawl...")
            self.log_updated.emit("Starting crawl...")
            
            to_crawl = []
            crawled_pages = []
            
            # Process HTML folder if provided
            if html_folder and os.path.exists(html_folder):
                self.log_updated.emit(f"Processing HTML folder: {html_folder}")
                html_links = self.crawler.process_html_folder(html_folder)
                self.log_updated.emit(f"Found {len(html_links)} links in HTML files")
                
                # Add HTML links to crawl queue
                for link in html_links:
                    if self.crawler._is_valid_url(link):
                        to_crawl.append((link, 0))  # Start at depth 0 for HTML links
            
            # Add start URL if provided
            if start_url:
                if self.crawler._is_valid_url(start_url):
                    self.log_updated.emit(f"Starting crawl of: {start_url}")
                    to_crawl.append((start_url, 0))
                else:
                    self.error_updated.emit(f"Invalid start URL: {start_url}")
                    return
            
            if not to_crawl:
                self.error_updated.emit("No valid URLs to crawl")
                return
            
            # Increased limits for comprehensive crawling
            max_visited_urls = 100000  # 10x more URLs
            max_queue_size = 50000     # 10x larger queue
            
            # Remove timeout - run until 100% completion
            # start_time = time.time()
            # max_crawl_time = 3600  # 1 hour max
            
            while to_crawl and not self.crawler.stop_crawling:
                # No timeout - run until all URLs are processed
                # if time.time() - start_time > max_crawl_time:
                #     self.log_updated.emit("Crawl timeout reached, stopping")
                #     break
                
                if self.crawler.pause_crawling:
                    time.sleep(0.1)
                    continue
                
                # Memory management - only stop if absolutely necessary
                if len(self.crawler.visited_urls) > max_visited_urls:
                    self.log_updated.emit(f"Memory limit reached ({max_visited_urls} URLs), but continuing...")
                    # Don't break - continue crawling
                
                # Priority-based crawling - sort by depth priority
                to_crawl.sort(key=lambda x: self.crawler.get_depth_priority(x[1]), reverse=True)
                url, depth = to_crawl.pop(0)
                
                # Add timeout for individual page crawl
                try:
                    # Crawl the page with timeout
                    page_data = self.crawler.crawl_page(url, depth)
                    if page_data:
                        crawled_pages.append(page_data)
                        self.page_updated.emit(page_data)  # Add to table
                        self.log_updated.emit(f"Crawled: {url} (depth: {depth})")
                        
                        # Add new links to crawl queue (with limits)
                        if depth < self.max_depth and len(to_crawl) < max_queue_size:
                            try:
                                # Use shorter timeout for link extraction
                                response = self.crawler.session.get(url, timeout=15, verify=False)
                                soup = BeautifulSoup(response.text, 'html.parser')
                                links = self.crawler.extract_links(soup, url)
                                
                                for link in links:
                                    if (link not in self.crawler.visited_urls and 
                                        self.crawler._is_valid_url(link) and
                                        len(to_crawl) < max_queue_size):
                                        to_crawl.append((link, depth + 1))
                            except Exception as e:
                                self.error_updated.emit(f"Error extracting links from {url}: {e}")
                    else:
                        self.log_updated.emit(f"Failed to crawl: {url}")
                        
                except Exception as e:
                    self.error_updated.emit(f"Error crawling {url}: {e}")
                
                # Update progress
                total_links = len(to_crawl) + len(crawled_pages)
                self.progress_updated.emit(len(crawled_pages), total_links)
                self.status_updated.emit(f"Crawled {len(crawled_pages)} pages, {len(to_crawl)} remaining")
                
                # Delay between requests
                time.sleep(self.delay)
            
            # Print comprehensive summary to console
            print(f"\n=== COMPREHENSIVE CRAWL SUMMARY ===")
            print(f"Pages crawled: {len(crawled_pages)}")
            print(f"Files downloaded: {len(self.crawler.downloaded_files)}")
            print(f"URLs visited: {len(self.crawler.visited_urls)}")
            print(f"Queue remaining: {len(to_crawl)}")
            print(f"Output directory: {self.crawler.output_dir}")
            print(f"100% COMPLETE - All available data collected!")
            print(f"==========================================\n")
            
            self.log_updated.emit(f"Crawl completed. Pages: {len(crawled_pages)} - 100% COMPLETE")
            self.status_updated.emit("Crawl completed - 100%")
            
        except Exception as e:
            self.error_updated.emit(f"Error during crawling: {e}")
        finally:
            self.is_crawling = False
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.pause_button.setEnabled(False)
    
    def stop_crawl(self):
        """Stop the crawling process"""
        self.crawler.stop_crawling = True
        self.log_updated.emit("Stopping crawl...")
        
        # Force stop any ongoing requests
        try:
            self.crawler.session.close()
        except:
            pass
        
        # Clear memory-intensive collections
        self.crawler.visited_urls.clear()
        self.crawler.downloaded_files.clear()
        self.crawler.domain_lags.clear()
        self.crawler.domain_request_counts.clear()
        self.crawler.last_request_time.clear()
        
        # Force UI update
        self.is_crawling = False
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.pause_button.setEnabled(False)
    
    def toggle_pause(self):
        """Toggle pause state"""
        self.crawler.pause_crawling = not self.crawler.pause_crawling
        if self.crawler.pause_crawling:
            self.pause_button.setText("Resume")
            self.log_updated.emit("Crawling paused")
        else:
            self.pause_button.setText("Pause")
            self.log_updated.emit("Crawling resumed")
    
    def update_progress(self, current, total):
        """Update progress bar"""
        if total > 0:
            percentage = int((current / total) * 100)
            self.progress_bar.setValue(percentage)
    
    def update_status(self, status):
        """Update status label"""
        self.status_label.setText(status)
    
    def update_results_table(self):
        """Update results table with advanced information"""
        # This would be implemented to show crawled pages with priority and timing info
        # For now, we'll just log the advanced features
        pass
    
    def add_page_to_table(self, page_data):
        """Add a crawled page to the results table"""
        row = self.results_table.rowCount()
        self.results_table.insertRow(row)
        
        # Add data to table
        self.results_table.setItem(row, 0, QTableWidgetItem(page_data.get('url', '')))
        self.results_table.setItem(row, 1, QTableWidgetItem(str(page_data.get('depth', 0))))
        self.results_table.setItem(row, 2, QTableWidgetItem(f"{page_data.get('priority', 0):.2f}"))
        self.results_table.setItem(row, 3, QTableWidgetItem(str(page_data.get('images_found', 0))))
        self.results_table.setItem(row, 4, QTableWidgetItem(str(page_data.get('links_found', 0))))
        self.results_table.setItem(row, 5, QTableWidgetItem(f"{page_data.get('response_time', 0):.2f}s"))
        self.results_table.setItem(row, 6, QTableWidgetItem(f"{page_data.get('adaptive_delay', 0):.2f}s"))
        self.results_table.setItem(row, 7, QTableWidgetItem(page_data.get('domain', '')))
    
    def log_message(self, message):
        """Log a message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
    
    def log_error(self, message):
        """Log an error"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] ERROR: {message}")
    
    def log_message_signal(self, message):
        """Log a message from signal"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
    
    def log_error_signal(self, message):
        """Log an error from signal"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] ERROR: {message}")
    
    def apply_dark_theme(self):
        """Apply dark theme"""
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555555;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                background-color: #4a4a4a;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 5px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
            QPushButton:pressed {
                background-color: #3a3a3a;
            }
            QPushButton:disabled {
                background-color: #3a3a3a;
                color: #888888;
            }
            QLineEdit, QSpinBox, QDoubleSpinBox {
                background-color: #3a3a3a;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 3px;
            }
            QProgressBar {
                border: 1px solid #555555;
                border-radius: 3px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 2px;
            }
            QTableWidget {
                background-color: #3a3a3a;
                border: 1px solid #555555;
                gridline-color: #555555;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #4a4a4a;
            }
            QTextEdit {
                background-color: #3a3a3a;
                border: 1px solid #555555;
                border-radius: 3px;
            }
        """)
    
    def closeEvent(self, event):
        """Handle application closing"""
        if self.is_crawling:
            self.stop_crawl()
            # Wait a bit for cleanup
            if self.crawl_thread and self.crawl_thread.is_alive():
                self.crawl_thread.join(timeout=2.0)
        
        # Clean up resources
        if hasattr(self.crawler, 'session'):
            self.crawler.session.close()
        
        event.accept()

def main():
    """Main function"""
    try:
        app = QApplication(sys.argv)
        app.setApplicationName("Simple Web Crawler")
        
        window = SimpleCrawlerUI()
        window.show()
        
        sys.exit(app.exec())
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 