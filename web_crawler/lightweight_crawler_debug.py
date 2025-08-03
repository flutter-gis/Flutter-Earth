#!/usr/bin/env python3
"""
Debug Version of Lightweight Web Crawler
Line-by-line debugging with detailed logging
"""

import os
import sys
import json
import time
import threading
import requests
import warnings
import traceback
from datetime import datetime
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

# Suppress SSL warnings
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

def debug_log(message, level="INFO"):
    """Debug logging function"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[{timestamp}] [{level}] {message}")

# Lightweight online classifiers
class OnlineClassifier:
    def __init__(self):
        debug_log("Initializing OnlineClassifier")
        self.categories = {
            'satellite': ['satellite', 'earth observation', 'remote sensing', 'landsat', 'sentinel', 'modis'],
            'climate': ['climate', 'weather', 'temperature', 'precipitation', 'atmospheric'],
            'geology': ['geology', 'mineral', 'rock', 'soil', 'terrain', 'elevation'],
            'ocean': ['ocean', 'marine', 'sea', 'coastal', 'water', 'bathymetry'],
            'forest': ['forest', 'vegetation', 'land cover', 'agriculture', 'crop'],
            'urban': ['urban', 'city', 'infrastructure', 'building', 'population'],
            'disaster': ['disaster', 'flood', 'fire', 'earthquake', 'volcano', 'emergency']
        }
        debug_log(f"OnlineClassifier initialized with {len(self.categories)} categories")
    
    def classify_text(self, text):
        """Simple keyword-based classification"""
        debug_log(f"Classifying text (length: {len(text) if text else 0})")
        
        if not text:
            debug_log("Empty text, returning unknown category")
            return {'category': 'unknown', 'confidence': 0.0}
        
        text_lower = text.lower()
        scores = {}
        
        for category, keywords in self.categories.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                scores[category] = score / len(keywords)
        
        if scores:
            best_category = max(scores, key=scores.get)
            confidence = scores[best_category]
            debug_log(f"Best category: {best_category} (confidence: {confidence:.2f})")
            return {'category': best_category, 'confidence': confidence}
        
        debug_log("No category matches, returning general")
        return {'category': 'general', 'confidence': 0.1}

class LightweightCrawlerUI(QWidget):
    # Define signals for thread-safe UI updates
    progress_updated = Signal(int, int)  # current, total
    status_updated = Signal(str)
    data_updated = Signal()
    log_updated = Signal(str)
    error_updated = Signal(str)
    
    def __init__(self):
        debug_log("Starting LightweightCrawlerUI initialization")
        try:
            super().__init__()
            debug_log("QWidget super().__init__() completed")
            
            self.setWindowTitle("Lightweight Web Crawler (Debug)")
            self.setGeometry(100, 100, 1200, 800)
            debug_log("Window title and geometry set")
            
            # Initialize components
            debug_log("Initializing classifier")
            self.classifier = OnlineClassifier()
            
            debug_log("Initializing data structures")
            self.extracted_data = []
            self.is_crawling = False
            self.stop_requested = False
            
            # Statistics
            self.total_processed = 0
            self.successful_extractions = 0
            self.failed_extractions = 0
            debug_log("Data structures initialized")
            
            debug_log("Setting up UI")
            self.setup_ui()
            debug_log("UI setup completed")
            
            debug_log("Loading configuration")
            self.load_config()
            debug_log("Configuration loaded")
            
            # Connect signals to slots
            debug_log("Connecting signals to slots")
            self.progress_updated.connect(self.update_progress)
            self.status_updated.connect(self.update_status)
            self.data_updated.connect(self.update_results_table)
            self.log_updated.connect(self.log_message)
            self.error_updated.connect(self.log_error)
            debug_log("Signal connections completed")
            
            debug_log("LightweightCrawlerUI initialization completed successfully")
            
        except Exception as e:
            debug_log(f"ERROR in __init__: {e}", "ERROR")
            debug_log(f"Traceback: {traceback.format_exc()}", "ERROR")
            raise
    
    def load_config(self):
        """Load lightweight configuration"""
        debug_log("Loading configuration")
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
            debug_log("Configuration loaded successfully")
            self.log_message("✅ Lightweight configuration loaded")
        except Exception as e:
            debug_log(f"Failed to load configuration: {e}", "ERROR")
            self.log_error(f"Failed to load configuration: {e}")
            self.config = {}
    
    def setup_ui(self):
        """Setup lightweight UI"""
        debug_log("Setting up UI components")
        try:
            layout = QHBoxLayout()
            debug_log("Main layout created")
            
            # Left panel - Controls
            left_panel = QVBoxLayout()
            debug_log("Left panel layout created")
            
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
            left_panel.addWidget(file_group)
            debug_log("File selection group created")
            
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
            left_panel.addWidget(control_group)
            debug_log("Crawl controls group created")
            
            # Progress
            progress_group = QGroupBox("Progress")
            progress_layout = QVBoxLayout()
            
            self.progress_bar = QProgressBar()
            progress_layout.addWidget(self.progress_bar)
            
            self.status_label = QLabel("Ready")
            progress_layout.addWidget(self.status_label)
            
            progress_group.setLayout(progress_layout)
            left_panel.addWidget(progress_group)
            debug_log("Progress group created")
            
            # Statistics
            stats_group = QGroupBox("Statistics")
            stats_layout = QVBoxLayout()
            
            self.stats_text = QTextEdit()
            self.stats_text.setMaximumHeight(150)
            stats_layout.addWidget(self.stats_text)
            
            stats_group.setLayout(stats_layout)
            left_panel.addWidget(stats_group)
            debug_log("Statistics group created")
            
            # Export
            export_group = QGroupBox("Export")
            export_layout = QVBoxLayout()
            
            export_btn = QPushButton("Export Results")
            export_btn.clicked.connect(self.export_results)
            export_layout.addWidget(export_btn)
            
            export_group.setLayout(export_layout)
            left_panel.addWidget(export_group)
            debug_log("Export group created")
            
            layout.addLayout(left_panel, 1)
            debug_log("Left panel added to main layout")
            
            # Right panel - Results
            right_panel = QVBoxLayout()
            debug_log("Right panel layout created")
            
            results_group = QGroupBox("Extracted Data")
            results_layout = QVBoxLayout()
            
            # Results table
            self.results_table = QTableWidget()
            self.results_table.setColumnCount(4)
            self.results_table.setHorizontalHeaderLabels(["Title", "Category", "Confidence", "URL"])
            results_layout.addWidget(self.results_table)
            
            results_group.setLayout(results_layout)
            right_panel.addWidget(results_group)
            debug_log("Results table created")
            
            # Console
            console_group = QGroupBox("Console")
            console_layout = QVBoxLayout()
            
            self.console = QTextEdit()
            self.console.setMaximumHeight(200)
            console_layout.addWidget(self.console)
            
            console_group.setLayout(console_layout)
            right_panel.addWidget(console_group)
            debug_log("Console created")
            
            layout.addLayout(right_panel, 2)
            debug_log("Right panel added to main layout")
            
            self.setLayout(layout)
            debug_log("Main layout set")
            
            debug_log("UI setup completed successfully")
            
        except Exception as e:
            debug_log(f"ERROR in setup_ui: {e}", "ERROR")
            debug_log(f"Traceback: {traceback.format_exc()}", "ERROR")
            raise
    
    def browse_file(self):
        """Browse for HTML file"""
        debug_log("Browse file called")
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Select HTML File", "", "HTML Files (*.html *.htm)"
            )
            if file_path:
                self.file_path_edit.setText(file_path)
                debug_log(f"File selected: {file_path}")
                self.log_message(f"📁 Selected file: {file_path}")
        except Exception as e:
            debug_log(f"ERROR in browse_file: {e}", "ERROR")
            self.log_error(f"Browse failed: {e}")
    
    def start_crawl(self):
        """Start crawling process"""
        debug_log("Start crawl called")
        try:
            file_path = self.file_path_edit.text().strip()
            if not file_path:
                QMessageBox.warning(self, "Warning", "Please select an HTML file!")
                debug_log("No file selected")
                return
            
            if not os.path.exists(file_path):
                QMessageBox.warning(self, "Warning", "Selected file does not exist!")
                debug_log(f"File does not exist: {file_path}")
                return
            
            debug_log(f"Starting crawl with file: {file_path}")
            self.is_crawling = True
            self.stop_requested = False
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            
            # Start crawling in separate thread
            self.crawl_thread = threading.Thread(target=self.crawl_html_file, args=(file_path,))
            self.crawl_thread.daemon = True
            self.crawl_thread.start()
            debug_log("Crawl thread started")
            
        except Exception as e:
            debug_log(f"ERROR in start_crawl: {e}", "ERROR")
            self.log_error(f"Start crawl failed: {e}")
    
    def stop_crawl(self):
        """Stop crawling process"""
        debug_log("Stop crawl called")
        try:
            self.stop_requested = True
            self.status_label.setText("Stopping...")
            debug_log("Stop requested")
        except Exception as e:
            debug_log(f"ERROR in stop_crawl: {e}", "ERROR")
    
    def crawl_html_file(self, html_file):
        """Crawl HTML file for links"""
        debug_log(f"Starting crawl of HTML file: {html_file}")
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            debug_log("HTML file read successfully")
            
            soup = BeautifulSoup(content, 'html.parser')
            debug_log("BeautifulSoup parsing completed")
            
            # Find all links
            links = soup.find_all('a', href=True)
            debug_log(f"Found {len(links)} links")
            
            if not links:
                self.log_message("⚠️ No links found in HTML file")
                self.crawl_finished()
                return
            
            # Extract URLs
            urls = []
            for link in links:
                href = link['href']
                if href.startswith('http'):
                    urls.append(href)
            
            debug_log(f"Extracted {len(urls)} valid URLs")
            
            if not urls:
                self.log_message("⚠️ No valid URLs found")
                self.crawl_finished()
                return
            
            # Process URLs
            for i, url in enumerate(urls, 1):
                if self.stop_requested:
                    debug_log("Stop requested, breaking crawl loop")
                    break
                
                debug_log(f"Processing URL {i}/{len(urls)}: {url}")
                self.process_link(url, i, len(urls))
                time.sleep(0.5)  # Small delay
            
            debug_log("Crawl loop completed")
            self.show_summary()
            
        except Exception as e:
            debug_log(f"ERROR in crawl_html_file: {e}", "ERROR")
            debug_log(f"Traceback: {traceback.format_exc()}", "ERROR")
            self.log_error(f"❌ Crawling failed: {e}")
        finally:
            debug_log("Calling crawl_finished")
            self.crawl_finished()
    
    def update_progress(self, current, total):
        """Thread-safe progress update"""
        debug_log(f"Updating progress: {current}/{total}")
        try:
            progress = int((current / total) * 100)
            self.progress_bar.setMaximum(total)
            self.progress_bar.setValue(current)
            debug_log(f"Progress updated: {progress}%")
        except Exception as e:
            debug_log(f"ERROR in update_progress: {e}", "ERROR")
    
    def update_status(self, status):
        """Thread-safe status update"""
        debug_log(f"Updating status: {status}")
        try:
            self.status_label.setText(status)
            debug_log("Status updated successfully")
        except Exception as e:
            debug_log(f"ERROR in update_status: {e}", "ERROR")
    
    def process_link(self, url, current, total):
        """Process individual link"""
        debug_log(f"Processing link: {url}")
        try:
            self.total_processed += 1
            debug_log(f"Total processed: {self.total_processed}")
            
            # Update progress using signal
            self.progress_updated.emit(current, total)
            self.status_updated.emit(f"Processing: {current}/{total}")
            debug_log("Progress and status signals emitted")
            
            # Make request
            debug_log("Making HTTP request")
            response = requests.get(url, timeout=15, verify=False)
            response.raise_for_status()
            debug_log("HTTP request successful")
            
            # Parse content
            debug_log("Parsing HTML content")
            soup = BeautifulSoup(response.content, 'html.parser')
            debug_log("HTML parsing completed")
            
            # Extract basic info
            debug_log("Extracting title")
            title = soup.find('title')
            title_text = title.get_text().strip() if title else "No title"
            debug_log(f"Title extracted: {title_text[:50]}...")
            
            # Extract main content
            debug_log("Extracting main content")
            content = ""
            for tag in soup.find_all(['p', 'div', 'span']):
                text = tag.get_text().strip()
                if len(text) > 50:  # Only meaningful content
                    content += text + " "
            debug_log(f"Content extracted (length: {len(content)})")
            
            # Classify content
            debug_log("Classifying content")
            classification = self.classifier.classify_text(content[:1000])  # First 1000 chars
            debug_log(f"Classification result: {classification}")
            
            # Create result
            debug_log("Creating result object")
            result = {
                'title': title_text,
                'url': url,
                'category': classification['category'],
                'confidence': classification['confidence'],
                'content_preview': content[:200] + "..." if len(content) > 200 else content,
                'timestamp': datetime.now().isoformat()
            }
            debug_log("Result object created")
            
            # Filter by confidence
            min_confidence = self.config.get('processing', {}).get('min_confidence', 0.3)
            debug_log(f"Checking confidence: {classification['confidence']} >= {min_confidence}")
            
            if classification['confidence'] >= min_confidence:
                self.extracted_data.append(result)
                self.successful_extractions += 1
                debug_log("Result added to extracted data")
                self.data_updated.emit()
                self.log_updated.emit(f"✅ {title_text[:50]}... ({classification['category']})")
            else:
                self.failed_extractions += 1
                debug_log("Result filtered out due to low confidence")
                self.log_updated.emit(f"⚠️ Low confidence: {title_text[:50]}...")
            
            debug_log(f"Processing completed. Success: {self.successful_extractions}, Failed: {self.failed_extractions}")
            
        except Exception as e:
            self.failed_extractions += 1
            debug_log(f"ERROR in process_link: {e}", "ERROR")
            debug_log(f"Traceback: {traceback.format_exc()}", "ERROR")
            self.error_updated.emit(f"❌ Failed to process {url}: {e}")
    
    def update_results_table(self):
        """Update results table"""
        debug_log("Updating results table")
        try:
            self.results_table.setRowCount(len(self.extracted_data))
            debug_log(f"Table row count set to {len(self.extracted_data)}")
            
            for i, item in enumerate(self.extracted_data):
                self.results_table.setItem(i, 0, QTableWidgetItem(item['title'][:50]))
                self.results_table.setItem(i, 1, QTableWidgetItem(item['category']))
                self.results_table.setItem(i, 2, QTableWidgetItem(f"{item['confidence']:.2f}"))
                self.results_table.setItem(i, 3, QTableWidgetItem(item['url'][:50]))
            
            debug_log("Results table updated successfully")
            self.update_statistics()
        except Exception as e:
            debug_log(f"ERROR in update_results_table: {e}", "ERROR")
    
    def update_statistics(self):
        """Update statistics display"""
        debug_log("Updating statistics")
        try:
            success_rate = (self.successful_extractions/self.total_processed*100) if self.total_processed > 0 else 0
            stats = f"""
📊 Statistics:
• Total Processed: {self.total_processed}
• Successful: {self.successful_extractions}
• Failed: {self.failed_extractions}
• Success Rate: {success_rate:.1f}%
• Categories Found: {len(set(item['category'] for item in self.extracted_data))}
            """
            self.stats_text.setText(stats)
            debug_log("Statistics updated successfully")
        except Exception as e:
            debug_log(f"ERROR in update_statistics: {e}", "ERROR")
    
    def show_summary(self):
        """Show crawl summary"""
        debug_log("Showing crawl summary")
        try:
            success_rate = (self.successful_extractions/self.total_processed*100) if self.total_processed > 0 else 0
            summary = f"""
🎉 Crawl Summary:
• Total Links: {self.total_processed}
• Successful Extractions: {self.successful_extractions}
• Failed Extractions: {self.failed_extractions}
• Success Rate: {success_rate:.1f}%
            """
            self.log_message(summary)
            debug_log("Summary displayed")
        except Exception as e:
            debug_log(f"ERROR in show_summary: {e}", "ERROR")
    
    def export_results(self):
        """Export results to JSON"""
        debug_log("Export results called")
        try:
            if not self.extracted_data:
                QMessageBox.warning(self, "Warning", "No data to export!")
                debug_log("No data to export")
                return
            
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save Results", "crawler_results.json", "JSON Files (*.json)"
            )
            
            if file_path:
                debug_log(f"Exporting to: {file_path}")
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.extracted_data, f, indent=2, ensure_ascii=False)
                self.log_message(f"✅ Results exported to {file_path}")
                debug_log("Export completed successfully")
        except Exception as e:
            debug_log(f"ERROR in export_results: {e}", "ERROR")
            self.log_error(f"❌ Export failed: {e}")
    
    def crawl_finished(self):
        """Cleanup after crawling"""
        debug_log("Crawl finished called")
        try:
            self.is_crawling = False
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.status_label.setText("Ready")
            debug_log("Crawl finished cleanup completed")
        except Exception as e:
            debug_log(f"ERROR in crawl_finished: {e}", "ERROR")
    
    def log_message(self, message):
        """Log message to console (thread-safe)"""
        debug_log(f"Log message: {message}")
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.console.append(f"[{timestamp}] {message}")
            self.console.ensureCursorVisible()
            debug_log("Message logged successfully")
        except Exception as e:
            debug_log(f"ERROR in log_message: {e}", "ERROR")
    
    def log_error(self, message):
        """Log error to console (thread-safe)"""
        debug_log(f"Log error: {message}")
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.console.append(f"[{timestamp}] ERROR: {message}")
            self.console.ensureCursorVisible()
            debug_log("Error logged successfully")
        except Exception as e:
            debug_log(f"ERROR in log_error: {e}", "ERROR")

def main():
    """Main function"""
    debug_log("Starting main function")
    try:
        debug_log("Creating QApplication")
        app = QApplication(sys.argv)
        debug_log("QApplication created")
        
        # Set application style
        app.setStyle('Fusion')
        debug_log("Application style set to Fusion")
        
        # Create and show window
        debug_log("Creating LightweightCrawlerUI")
        window = LightweightCrawlerUI()
        debug_log("LightweightCrawlerUI created")
        
        debug_log("Showing window")
        window.show()
        debug_log("Window shown")
        
        debug_log("Starting application event loop")
        sys.exit(app.exec())
        
    except Exception as e:
        debug_log(f"ERROR in main: {e}", "ERROR")
        debug_log(f"Traceback: {traceback.format_exc()}", "ERROR")
        raise

if __name__ == "__main__":
    debug_log("Script started")
    main() 