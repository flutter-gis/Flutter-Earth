import sys
import subprocess
import random
import importlib.util
import queue
from concurrent.futures import ThreadPoolExecutor, as_completed

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
        'dateparser': 'dateparser',
        'torch': 'torch',
        'torchvision': 'torchvision',
        'torchaudio': 'torchaudio',
        'pytesseract': 'pytesseract'
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
    'dateparser',
    'torch',
    'torchvision',
    'torchaudio',
    'pytesseract'
]

missing = []
for pkg in REQUIRED_PACKAGES:
    if not check_package_installed(pkg):
        missing.append(pkg)

if missing:
    print(f"Missing required packages: {', '.join(missing)}. Attempting to install...")
    try:
        # Handle PyTorch packages separately with specific index
        torch_packages = [pkg for pkg in missing if pkg.startswith('torch')]
        other_packages = [pkg for pkg in missing if not pkg.startswith('torch')]
        
        # Install PyTorch packages first with CPU version
        if torch_packages:
            print("Installing PyTorch packages...")
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', '--upgrade',
                '--index-url', 'https://download.pytorch.org/whl/cpu'
            ] + torch_packages)
        
        # Install other packages
        if other_packages:
            print("Installing other packages...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade'] + other_packages)
        
        print("All required packages installed. Please restart the program.")
        sys.exit(0)
    except Exception as e:
        print("Automatic installation failed.")
        print("Error:", e)
        print("Please install the missing packages manually:")
        if torch_packages:
            print(f"    {sys.executable} -m pip install --index-url https://download.pytorch.org/whl/cpu {' '.join(torch_packages)}")
        if other_packages:
            print(f"    {sys.executable} -m pip install {' '.join(other_packages)}")
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

# Check for Tesseract OCR (required for pytesseract)
try:
    import pytesseract
    # Test if Tesseract is installed on the system
    pytesseract.get_tesseract_version()
    print("✓ Tesseract OCR found and working")
except Exception as e:
    print("⚠ Tesseract OCR not found. pytesseract requires Tesseract to be installed on your system.")
    print("For Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki")
    print("For Linux: sudo apt-get install tesseract-ocr")
    print("For macOS: brew install tesseract")
    print("OCR features will be disabled.")
    
    # Try to find Tesseract in common locations
    import os
    tesseract_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        os.path.join(os.path.dirname(__file__), "tesseract.exe"),
        os.path.join(os.path.dirname(__file__), "tesseract-5.5.1", "tesseract.exe")
    ]
    
    for path in tesseract_paths:
        if os.path.exists(path):
            try:
                pytesseract.pytesseract.tesseract_cmd = path
                pytesseract.get_tesseract_version()
                print(f"✓ Found Tesseract at: {path}")
                break
            except:
                continue

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
    QProgressBar, QLabel, QFileDialog, QLineEdit, QGroupBox, QCheckBox, QTabWidget,
    QTableWidget, QScrollArea, QComboBox, QGridLayout, QStackedWidget, QTableWidgetItem,
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QSpinBox, QDoubleSpinBox, QMessageBox,
    QSlider
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
pytesseract = None

# Advanced system imports
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

# Advanced ML imports
try:
    from advanced_ml_manager import ml_manager
    ADVANCED_ML_AVAILABLE = True
except ImportError:
    ADVANCED_ML_AVAILABLE = False

# Performance monitoring
try:
    from performance_monitor import performance_monitor
    PERFORMANCE_MONITORING_AVAILABLE = True
except ImportError:
    PERFORMANCE_MONITORING_AVAILABLE = False

# Advanced data export
try:
    from advanced_data_exporter import data_exporter
    ADVANCED_EXPORT_AVAILABLE = True
except ImportError:
    ADVANCED_EXPORT_AVAILABLE = False

# Advanced validation
try:
    from advanced_validator import advanced_validator
    ADVANCED_VALIDATION_AVAILABLE = True
except ImportError:
    ADVANCED_VALIDATION_AVAILABLE = False

# Import all available packages at startup
try:
    import spacy
    print("✓ spaCy loaded successfully")
except ImportError:
    print("⚠ spaCy not available - ML/NLP features disabled")

try:
    import transformers
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    import os
    os.environ['TRANSFORMERS_VERIFIED_TOKEN'] = '1'
    os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'
    os.environ['CURL_CA_BUNDLE'] = ''
    os.environ['REQUESTS_CA_BUNDLE'] = ''
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
    from performance_monitor import PerformanceMonitor
    print("✓ Performance monitor loaded successfully")
except ImportError:
    print("⚠ Performance monitor not available - monitoring disabled")
    # Create a simple fallback class
    class PerformanceMonitor:
        def __init__(self):
            self.config = {}
        def update(self, *args, **kwargs):
            pass

try:
    import dateparser
    print("✓ Dateparser loaded successfully")
except ImportError:
    print("⚠ Dateparser not available - fuzzy date parsing disabled")

try:
    import pytesseract
    pytesseract.get_tesseract_version()
    pytesseract = True
    print("✓ pytesseract loaded successfully")
except ImportError:
    print("⚠ pytesseract not available - OCR features disabled")
except Exception as e:
    print("⚠ pytesseract available but Tesseract not found - OCR features disabled")

from datetime import datetime

# Disable SSL verification for model downloads
import ssl
import urllib3
ssl._create_default_https_context = ssl._create_unverified_context
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
os.environ['CURL_CA_BUNDLE'] = ''
os.environ['REQUESTS_CA_BUNDLE'] = ''
os.environ['SSL_CERT_FILE'] = ''
os.environ['TRANSFORMERS_OFFLINE'] = '0'
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'
os.environ['TRANSFORMERS_VERIFIED_TOKEN'] = '1'

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0',
]

class EnhancedCrawlerUI(QWidget):
    def __init__(self):
        super().__init__()
        
        # Initialize performance tracking
        self.start_time = None
        self.stop_requested = False
        self.extracted_data = []
        self.data_lock = threading.Lock()
        
        # Performance monitoring queue
        self.progress_queue = queue.Queue()
        
        # Enhanced error tracking
        self.error_count = 0
        self.warning_count = 0
        self.success_count = 0
        
        # Initialize UI first
        self.setup_ui()
        
        # Now detect low-power system after UI is set up
        self.low_power_mode = self.detect_low_power_system()
        self.optimization_level = "balanced"  # balanced, performance, power_save
        
        # Initialize advanced features
        self._init_advanced_features()
        
        # Setup timer for UI updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_ui)
        
        # Performance monitoring
        self.performance_monitor = PerformanceMonitor()
        
        # Set window properties
        self.setWindowTitle("Earth Engine Catalog Web Crawler - Ultra Enhanced v2.0")
        self.resize(1400, 900)  # Optimized size for better visibility
        
        # Apply low-power optimizations
        self.apply_low_power_optimizations()
        
        # Log initialization
        self.log_message("🚀 Enhanced Web Crawler UI initialized successfully!")
        if self.low_power_mode:
            self.log_message("🔋 Low-power mode enabled for better performance on this system")
    
    def detect_low_power_system(self):
        """Detect if running on a low-power system."""
        try:
            # Check CPU cores
            cpu_count = psutil.cpu_count()
            
            # Check available memory
            memory = psutil.virtual_memory()
            memory_gb = memory.total / (1024**3)
            
            # Check if it's a low-power system
            is_low_power = (cpu_count <= 4) or (memory_gb <= 8)
            
            self.log_message(f"System detected: {cpu_count} cores, {memory_gb:.1f}GB RAM")
            
            return is_low_power
        except Exception as e:
            self.log_message(f"Could not detect system specs: {e}")
            return True  # Assume low-power for safety
    
    def apply_low_power_optimizations(self):
        """Apply optimizations for low-power systems while maintaining quality."""
        if self.low_power_mode:
            # Reduce UI update frequency but maintain responsiveness
            self.timer.setInterval(250)  # 250ms instead of 100ms - still responsive
            
            # Maintain ML model quality but optimize processing
            if hasattr(self, 'config') and self.config:
                # Keep full model capabilities but process in smaller batches
                self.config['ml']['classification']['max_length'] = 512  # Keep full context
                self.config['ml']['classification']['batch_size'] = 1  # Process one at a time
                self.config['performance']['max_concurrent_requests'] = 1  # Sequential processing
                self.config['performance']['request_delay'] = 2.0  # Longer delays for stability
            
            # Optimize memory usage while maintaining data quality
            self.config['performance']['memory']['max_cache_size'] = 1000  # Keep more data in memory
            self.config['performance']['memory']['enable_compression'] = True  # Compress data
            
            # Enhanced processing settings for quality
            self.config['processing']['enable_quality_checks'] = True
            self.config['processing']['enable_validation'] = True
            self.config['processing']['enable_ensemble_methods'] = True
            
            self.log_message("🔧 Applied low-power optimizations (quality-focused)")
            self.log_message("📊 Processing will be slower but maintain full quality")
        else:
            # High-performance settings
            self.timer.setInterval(100)
            self.log_message("⚡ High-performance mode enabled")
    
    def _init_advanced_features(self):
        """Initialize advanced features and ML models."""
        try:
            # Initialize configuration
            self.config = self.load_config()
            
            # Initialize ML models
            self.nlp = None
            self.bert_classifier = None
            self.geocoder = None
            
            # Load spaCy model for NER and text processing
            try:
                import spacy
                self.nlp = spacy.load("en_core_web_sm")
                self.log_message("✅ spaCy model loaded successfully")
            except Exception as e:
                self.log_message(f"⚠️ spaCy model not available: {e}")
            
            # Load BERT classifier for text classification
            try:
                from transformers import pipeline
                self.bert_classifier = pipeline(
                    "text-classification",
                    model="distilbert-base-uncased",
                    return_all_scores=True
                )
                self.log_message("✅ BERT classifier loaded successfully")
            except Exception as e:
                self.log_message(f"⚠️ BERT classifier not available: {e}")
            
            # Initialize geocoder for spatial data validation
            try:
                from geopy.geocoders import Nominatim
                self.geocoder = Nominatim(user_agent="earth_engine_crawler")
                self.log_message("✅ Geocoder initialized successfully")
            except Exception as e:
                self.log_message(f"⚠️ Geocoder not available: {e}")
            
            # Initialize performance monitoring
            self.performance_monitor = PerformanceMonitor()
            
            # Initialize health tracking
            self.health_update_counter = 0
            
            self.log_message("✅ Advanced features initialized successfully")
            
        except Exception as e:
            self.log_error(f"Failed to initialize advanced features: {e}")
    
    def load_config(self):
        """Load configuration from file."""
        try:
            config_file = "crawler_config.yaml"
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = yaml_module.safe_load(f)
                self.log_message("✅ Configuration loaded successfully")
                return config
            else:
                # Return default configuration
                default_config = {
                    'ml': {
                        'classification': {
                            'max_length': 512,
                            'batch_size': 1
                        }
                    },
                    'performance': {
                        'max_concurrent_requests': 1,
                        'request_delay': 2.0,
                        'memory': {
                            'max_cache_size': 1000,
                            'enable_compression': True
                        }
                    },
                    'processing': {
                        'enable_quality_checks': True,
                        'enable_validation': True,
                        'enable_ensemble_methods': True
                    }
                }
                self.log_message("⚠️ Using default configuration")
                return default_config
        except Exception as e:
            self.log_error(f"Failed to load configuration: {e}")
            return {}
    
    def optimize_for_system(self):
        """Dynamically optimize based on current system performance while maintaining quality."""
        try:
            cpu_percent = psutil.cpu_percent()
            memory_percent = psutil.virtual_memory().percent
            
            if cpu_percent > 85 or memory_percent > 85:
                # System under stress - apply power saving but maintain quality
                self.optimization_level = "power_save"
                self.timer.setInterval(400)  # Slower updates but still responsive
                self.log_message("🔋 Power saving mode activated - maintaining quality with slower processing")
            elif cpu_percent < 40 and memory_percent < 60:
                # System has resources - enable performance mode
                self.optimization_level = "performance"
                self.timer.setInterval(75)  # Faster updates
                self.log_message("⚡ Performance mode activated")
            else:
                # Balanced mode - maintain quality with moderate performance
                self.optimization_level = "balanced"
                self.timer.setInterval(150)
                self.log_message("⚖️ Balanced mode - quality-focused processing")
                
        except Exception as e:
            self.log_message(f"System optimization error: {e}")
    
    def enhanced_error_handling(self, error, context=""):
        """Enhanced error handling with categorization and recovery."""
        try:
            error_type = type(error).__name__
            error_msg = str(error)
            
            # Categorize errors
            if "timeout" in error_msg.lower():
                category = "TIMEOUT"
                suggestion = "Consider increasing request delay or reducing concurrent requests"
            elif "memory" in error_msg.lower():
                category = "MEMORY"
                suggestion = "Consider reducing cache size or processing fewer items"
            elif "network" in error_msg.lower():
                category = "NETWORK"
                suggestion = "Check internet connection and try again"
            elif "ml" in error_msg.lower() or "bert" in error_msg.lower():
                category = "ML_MODEL"
                suggestion = "ML model may be loading or unavailable"
            else:
                category = "GENERAL"
                suggestion = "Check logs for more details"
            
            # Log error with context
            self.log_error(f"[{category}] {context}: {error_msg}")
            self.log_error(f"Suggestion: {suggestion}")
            
            # Update error count
            self.error_count += 1
            
            # Apply recovery strategies
            self.apply_error_recovery(category, error_msg)
            
        except Exception as e:
            self.log_error(f"Error handling failed: {e}")
    
    def apply_error_recovery(self, category, error_msg):
        """Apply recovery strategies based on error category."""
        try:
            if category == "TIMEOUT":
                # Increase delays
                if hasattr(self, 'delay_slider'):
                    current_delay = self.delay_slider.value()
                    new_delay = min(current_delay + 1, 10)
                    self.delay_slider.setValue(new_delay)
                    self.log_message(f"Auto-adjusted delay to {new_delay/2:.1f}s")
            
            elif category == "MEMORY":
                # Clear cache and reduce memory usage
                if hasattr(self, 'extracted_data'):
                    cache_size = len(self.extracted_data)
                    if cache_size > 100:
                        # Keep only recent items
                        self.extracted_data = self.extracted_data[-50:]
                        self.log_message("Auto-cleared cache to reduce memory usage")
            
            elif category == "NETWORK":
                # Reduce concurrent requests
                if hasattr(self, 'concurrent_slider'):
                    current_concurrent = self.concurrent_slider.value()
                    new_concurrent = max(current_concurrent - 1, 1)
                    self.concurrent_slider.setValue(new_concurrent)
                    self.log_message(f"Auto-reduced concurrent requests to {new_concurrent}")
            
            elif category == "ML_MODEL":
                # Try to reload ML models
                self.log_message("Attempting to reload ML models...")
                # This could trigger a model reload in the background
                
        except Exception as e:
            self.log_message(f"Error recovery failed: {e}")
    
    def get_system_health_report(self):
        """Generate a comprehensive system health report."""
        try:
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Calculate health score
            health_score = 100
            issues = []
            
            if cpu_percent > 90:
                health_score -= 30
                issues.append("High CPU usage")
            elif cpu_percent > 70:
                health_score -= 15
                issues.append("Elevated CPU usage")
            
            if memory.percent > 90:
                health_score -= 30
                issues.append("High memory usage")
            elif memory.percent > 70:
                health_score -= 15
                issues.append("Elevated memory usage")
            
            if disk.percent > 90:
                health_score -= 20
                issues.append("Low disk space")
            
            if self.error_count > 10:
                health_score -= 20
                issues.append("High error rate")
            
            # Health status
            if health_score >= 80:
                status = "🟢 Excellent"
            elif health_score >= 60:
                status = "🟡 Good"
            elif health_score >= 40:
                status = "🟠 Fair"
            else:
                status = "🔴 Poor"
            
            report = f"""
SYSTEM HEALTH REPORT
{'='*50}

Overall Health: {status} ({health_score}/100)

SYSTEM METRICS:
CPU Usage: {cpu_percent:.1f}%
Memory Usage: {memory.percent:.1f}%
Disk Usage: {disk.percent:.1f}%

PERFORMANCE METRICS:
Errors: {self.error_count}
Warnings: {self.warning_count}
Success: {self.success_count}

OPTIMIZATION LEVEL: {self.optimization_level.upper()}
LOW POWER MODE: {'✅ Enabled' if self.low_power_mode else '❌ Disabled'}

ISSUES DETECTED:
{chr(10).join(f"• {issue}" for issue in issues) if issues else "• None detected"}

RECOMMENDATIONS:
{self.get_optimization_recommendations()}
"""
            
            return report
            
        except Exception as e:
            return f"Health report generation failed: {e}"
    
    def get_optimization_recommendations(self):
        """Get optimization recommendations based on current system state."""
        recommendations = []
        
        try:
            cpu_percent = psutil.cpu_percent()
            memory_percent = psutil.virtual_memory().percent
            
            if cpu_percent > 80:
                recommendations.append("• Increase request delay to reduce CPU load")
                recommendations.append("• Reduce concurrent requests")
            
            if memory_percent > 80:
                recommendations.append("• Clear cache to free memory")
                recommendations.append("• Process data in smaller batches")
            
            if self.error_count > 5:
                recommendations.append("• Check network connection")
                recommendations.append("• Verify ML models are loaded")
            
            if not recommendations:
                recommendations.append("• System is running optimally")
            
            return "\n".join(recommendations)
            
        except Exception as e:
            return f"Could not generate recommendations: {e}"

    def setup_ui(self):
        """Setup the enhanced two-column UI with integrated dashboard functionality."""
        # Main layout
        main_layout = QHBoxLayout(self)
        
        # Left Column - Input Options and Parameters
        left_column = self.create_left_column()
        main_layout.addWidget(left_column, 2)  # 2 parts width (increased from 1)
        
        # Right Column - Tabs and Console Logs
        right_column = self.create_right_column()
        main_layout.addWidget(right_column, 1)  # 1 part width (decreased from 2)
        
        # Initialize data storage for real-time viewing
        self.extracted_data = []
        self.data_lock = threading.Lock()
        
        # Update status indicators
        # self.update_status_indicators()
    
    def create_left_column(self):
        """Create the left column with input options and parameters."""
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # Create a scroll area for the left column
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: #f0f0f0;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #c0c0c0;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #a0a0a0;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # Create a container widget for all the content
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(5)
        content_layout.setContentsMargins(5, 5, 5, 5)
        
        # Enhanced title with version
        title_label = QLabel("Earth Engine Catalog Web Crawler")
        title_label.setStyleSheet("""
            font-size: 16px; 
            font-weight: bold; 
            color: #2c3e50; 
            margin: 8px; 
            padding: 6px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 6px;
            text-align: center;
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(title_label)
        
        # Real-time statistics bar
        stats_group = QGroupBox("📊 Real-Time Statistics")
        stats_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #3498db;
                border-radius: 4px;
                margin-top: 5px;
                padding-top: 5px;
                font-size: 11px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 3px 0 3px;
            }
        """)
        stats_layout = QVBoxLayout()
        
        # Statistics grid
        stats_grid = QGridLayout()
        
        self.datasets_processed_label = QLabel("Datasets: 0")
        self.datasets_processed_label.setStyleSheet("padding: 4px; background: #3498db; color: white; border-radius: 3px; font-weight: bold; font-size: 10px;")
        
        self.processing_rate_label = QLabel("Rate: 0/min")
        self.processing_rate_label.setStyleSheet("padding: 4px; background: #27ae60; color: white; border-radius: 3px; font-weight: bold; font-size: 10px;")
        
        self.avg_confidence_label = QLabel("Confidence: 0%")
        self.avg_confidence_label.setStyleSheet("padding: 4px; background: #f39c12; color: white; border-radius: 3px; font-weight: bold; font-size: 10px;")
        
        self.ml_classified_label = QLabel("ML Classified: 0")
        self.ml_classified_label.setStyleSheet("padding: 4px; background: #9b59b6; color: white; border-radius: 3px; font-weight: bold; font-size: 10px;")
        
        self.errors_label = QLabel("Errors: 0")
        self.errors_label.setStyleSheet("padding: 4px; background: #e74c3c; color: white; border-radius: 3px; font-weight: bold; font-size: 10px;")
        
        self.quality_score_label = QLabel("Quality: 0%")
        self.quality_score_label.setStyleSheet("padding: 4px; background: #1abc9c; color: white; border-radius: 3px; font-weight: bold; font-size: 10px;")
        
        stats_grid.addWidget(self.datasets_processed_label, 0, 0)
        stats_grid.addWidget(self.processing_rate_label, 0, 1)
        stats_grid.addWidget(self.avg_confidence_label, 1, 0)
        stats_grid.addWidget(self.ml_classified_label, 1, 1)
        stats_grid.addWidget(self.errors_label, 2, 0)
        stats_grid.addWidget(self.quality_score_label, 2, 1)
        
        stats_layout.addLayout(stats_grid)
        stats_group.setLayout(stats_layout)
        content_layout.addWidget(stats_group)
        
        # Status indicators for advanced features
        status_group = QGroupBox("🔧 System Status")
        status_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #95a5a6;
                border-radius: 4px;
                margin-top: 5px;
                padding-top: 5px;
                font-size: 11px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 3px 0 3px;
            }
        """)
        status_layout = QGridLayout()
        
        self.spacy_status = QLabel("spaCy: ❌")
        self.bert_status = QLabel("BERT: ❌")
        self.geo_status = QLabel("Geospatial: ❌")
        self.dashboard_status = QLabel("Dashboard: ❌")
        self.config_status = QLabel("Config: ❌")
        self.ocr_status = QLabel("OCR: ❌")
        
        for i, status in enumerate([self.spacy_status, self.bert_status, self.geo_status, self.dashboard_status, self.config_status, self.ocr_status]):
            status.setStyleSheet("padding: 3px; border: 1px solid #bdc3c7; border-radius: 2px; margin: 1px; font-size: 10px;")
            status_layout.addWidget(status, i // 2, i % 2)
        
        status_group.setLayout(status_layout)
        content_layout.addWidget(status_group)
        
        # File selection group
        file_group = QGroupBox("📁 File Selection")
        file_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #e67e22;
                border-radius: 4px;
                margin-top: 5px;
                padding-top: 5px;
                font-size: 11px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 3px 0 3px;
            }
        """)
        file_layout = QVBoxLayout()
        
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setPlaceholderText("Select local HTML file to crawl...")
        self.file_path_edit.setStyleSheet("padding: 4px; border: 1px solid #bdc3c7; border-radius: 3px; font-size: 10px;")
        
        self.browse_btn = QPushButton("📂 Browse Files")
        self.browse_btn.clicked.connect(self.browse_file)
        self.browse_btn.setStyleSheet("""
            QPushButton {
                background: #e67e22;
                color: white;
                padding: 4px;
                border-radius: 3px;
                font-weight: bold;
                font-size: 10px;
            }
            QPushButton:hover {
                background: #d35400;
            }
        """)
        
        file_layout.addWidget(self.file_path_edit)
        file_layout.addWidget(self.browse_btn)
        file_group.setLayout(file_layout)
        content_layout.addWidget(file_group)
        
        # Output directory selection group
        output_group = QGroupBox("📤 Output Settings")
        output_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #27ae60;
                border-radius: 4px;
                margin-top: 5px;
                padding-top: 5px;
                font-size: 11px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 3px 0 3px;
            }
        """)
        output_layout = QVBoxLayout()
        
        self.output_dir_edit = QLineEdit()
        self.output_dir_edit.setPlaceholderText("Select output directory...")
        self.output_dir_edit.setText(os.path.abspath("extracted_data"))
        self.output_dir_edit.setStyleSheet("padding: 4px; border: 1px solid #bdc3c7; border-radius: 3px; font-size: 10px;")
        
        self.output_browse_btn = QPushButton("📁 Browse Output")
        self.output_browse_btn.clicked.connect(self.browse_output_directory)
        self.output_browse_btn.setStyleSheet("""
            QPushButton {
                background: #27ae60;
                color: white;
                padding: 4px;
                border-radius: 3px;
                font-weight: bold;
                font-size: 10px;
            }
            QPushButton:hover {
                background: #229954;
            }
        """)
        
        output_layout.addWidget(self.output_dir_edit)
        output_layout.addWidget(self.output_browse_btn)
        output_group.setLayout(output_layout)
        content_layout.addWidget(output_group)
        
        # Advanced options group
        options_group = QGroupBox("⚙️ Advanced Options")
        options_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #8e44ad;
                border-radius: 4px;
                margin-top: 5px;
                padding-top: 5px;
                font-size: 11px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 3px 0 3px;
            }
        """)
        options_layout = QVBoxLayout()
        
        # Basic options
        basic_options = QHBoxLayout()
        self.download_thumbs = QCheckBox("📷 Download thumbnails")
        self.download_thumbs.setChecked(True)
        self.download_thumbs.setStyleSheet("font-size: 10px;")
        self.extract_details = QCheckBox("🔍 Extract details")
        self.extract_details.setChecked(True)
        self.extract_details.setStyleSheet("font-size: 10px;")
        self.save_individual = QCheckBox("💾 Save individual")
        self.save_individual.setChecked(True)
        self.save_individual.setStyleSheet("font-size: 10px;")
        basic_options.addWidget(self.download_thumbs)
        basic_options.addWidget(self.extract_details)
        basic_options.addWidget(self.save_individual)
        options_layout.addLayout(basic_options)
        
        # Advanced ML options
        ml_options = QHBoxLayout()
        self.use_ml_classification = QCheckBox("🧠 ML Classification")
        self.use_ml_classification.setChecked(True)
        self.use_ml_classification.setStyleSheet("font-size: 10px;")
        self.use_ensemble = QCheckBox("🎯 Ensemble ML")
        self.use_ensemble.setChecked(True)
        self.use_ensemble.setStyleSheet("font-size: 10px;")
        self.use_validation = QCheckBox("✅ Data Validation")
        self.use_validation.setChecked(True)
        self.use_validation.setStyleSheet("font-size: 10px;")
        ml_options.addWidget(self.use_ml_classification)
        ml_options.addWidget(self.use_ensemble)
        ml_options.addWidget(self.use_validation)
        options_layout.addLayout(ml_options)
        
        options_group.setLayout(options_layout)
        content_layout.addWidget(options_group)
        
        # Performance settings
        perf_group = QGroupBox("⚡ Performance Settings")
        perf_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #f39c12;
                border-radius: 4px;
                margin-top: 5px;
                padding-top: 5px;
                font-size: 11px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 3px 0 3px;
            }
        """)
        perf_layout = QVBoxLayout()
        
        # Request delay slider
        delay_layout = QHBoxLayout()
        delay_label = QLabel("Request Delay:")
        delay_label.setStyleSheet("font-size: 10px;")
        delay_layout.addWidget(delay_label)
        self.delay_slider = QSlider(Qt.Orientation.Horizontal)
        self.delay_slider.setRange(1, 10)
        self.delay_slider.setValue(3)
        self.delay_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #bbb;
                background: white;
                height: 6px;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #f39c12;
                border: 1px solid #f39c12;
                width: 12px;
                margin: -2px 0;
                border-radius: 6px;
            }
        """)
        self.delay_label = QLabel("3.0s")
        self.delay_label.setStyleSheet("font-size: 10px;")
        delay_layout.addWidget(self.delay_slider)
        delay_layout.addWidget(self.delay_label)
        self.delay_slider.valueChanged.connect(lambda v: self.delay_label.setText(f"{v/2:.1f}s"))
        perf_layout.addLayout(delay_layout)
        
        # Concurrent requests slider
        concurrent_layout = QHBoxLayout()
        concurrent_label = QLabel("Concurrent:")
        concurrent_label.setStyleSheet("font-size: 10px;")
        concurrent_layout.addWidget(concurrent_label)
        self.concurrent_slider = QSlider(Qt.Orientation.Horizontal)
        self.concurrent_slider.setRange(1, 16)
        self.concurrent_slider.setValue(4)
        self.concurrent_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #bbb;
                background: white;
                height: 6px;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #3498db;
                border: 1px solid #3498db;
                width: 12px;
                margin: -2px 0;
                border-radius: 6px;
            }
        """)
        self.concurrent_label = QLabel("4")
        self.concurrent_label.setStyleSheet("font-size: 10px;")
        concurrent_layout.addWidget(self.concurrent_slider)
        concurrent_layout.addWidget(self.concurrent_label)
        self.concurrent_slider.valueChanged.connect(lambda v: self.concurrent_label.setText(str(v)))
        perf_layout.addLayout(concurrent_layout)
        
        perf_group.setLayout(perf_layout)
        content_layout.addWidget(perf_group)
        
        # Control buttons
        controls_group = QGroupBox("🎮 Controls")
        controls_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #34495e;
                border-radius: 4px;
                margin-top: 5px;
                padding-top: 5px;
                font-size: 11px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 3px 0 3px;
            }
        """)
        controls_layout = QVBoxLayout()
        
        # Main control buttons
        self.crawl_btn = QPushButton("🚀 Start Crawling")
        self.crawl_btn.clicked.connect(self.start_crawl)
        self.crawl_btn.setEnabled(False)
        self.crawl_btn.setStyleSheet("""
            QPushButton {
                background: #27ae60;
                color: white;
                padding: 8px;
                font-weight: bold;
                font-size: 11px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background: #229954;
            }
            QPushButton:disabled {
                background: #95a5a6;
            }
        """)
        
        self.stop_btn = QPushButton("⏹️ Stop")
        self.stop_btn.clicked.connect(self.stop_crawl)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background: #e74c3c;
                color: white;
                padding: 8px;
                font-weight: bold;
                font-size: 11px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background: #c0392b;
            }
            QPushButton:disabled {
                background: #95a5a6;
            }
        """)
        
        # Secondary control buttons
        secondary_layout = QHBoxLayout()
        
        self.clear_btn = QPushButton("🗑️ Clear")
        self.clear_btn.clicked.connect(self.clear_all_consoles)
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background: #f39c12;
                color: white;
                padding: 4px;
                border-radius: 3px;
                font-weight: bold;
                font-size: 10px;
            }
            QPushButton:hover {
                background: #e67e22;
            }
        """)
        
        self.export_btn = QPushButton("📤 Export")
        self.export_btn.clicked.connect(self.export_current_data)
        self.export_btn.setEnabled(False)
        self.export_btn.setStyleSheet("""
            QPushButton {
                background: #3498db;
                color: white;
                padding: 4px;
                border-radius: 3px;
                font-weight: bold;
                font-size: 10px;
            }
            QPushButton:hover {
                background: #2980b9;
            }
            QPushButton:disabled {
                background: #95a5a6;
            }
        """)
        
        self.health_btn = QPushButton("🏥 Health")
        self.health_btn.clicked.connect(self.show_health_report)
        self.health_btn.setStyleSheet("""
            QPushButton {
                background: #27ae60;
                color: white;
                padding: 4px;
                border-radius: 3px;
                font-weight: bold;
                font-size: 10px;
            }
            QPushButton:hover {
                background: #229954;
            }
        """)
        
        self.optimize_btn = QPushButton("⚙️ Optimize")
        self.optimize_btn.clicked.connect(self.show_optimization_dialog)
        self.optimize_btn.setStyleSheet("""
            QPushButton {
                background: #9b59b6;
                color: white;
                padding: 4px;
                border-radius: 3px;
                font-weight: bold;
                font-size: 10px;
            }
            QPushButton:hover {
                background: #8e44ad;
            }
        """)
        
        secondary_layout.addWidget(self.clear_btn)
        secondary_layout.addWidget(self.export_btn)
        secondary_layout.addWidget(self.health_btn)
        secondary_layout.addWidget(self.optimize_btn)
        
        controls_layout.addWidget(self.crawl_btn)
        controls_layout.addWidget(self.stop_btn)
        controls_layout.addLayout(secondary_layout)
        controls_group.setLayout(controls_layout)
        content_layout.addWidget(controls_group)
        
        # Progress and status
        self.status = QLabel("Ready. Select an HTML file to begin.")
        self.status.setStyleSheet("padding: 6px; background: #ecf0f1; border-radius: 3px; margin: 3px; font-size: 10px;")
        content_layout.addWidget(self.status)
        
        self.progress = QProgressBar()
        self.progress.setMaximum(100)
        self.progress.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress.setStyleSheet("""
            QProgressBar {
                height: 18px;
                font-size: 10px;
                font-weight: bold;
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                text-align: center;
            }
            QProgressBar::chunk {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 2px;
            }
        """)
        content_layout.addWidget(self.progress)
        
        content_layout.addStretch()
        scroll_area.setWidget(content_widget)
        left_layout.addWidget(scroll_area)
        return left_widget
    
    def create_right_column(self):
        """Create the right column with tabs and console logs."""
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Tab widget for different views
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background: white;
            }
            QTabBar::tab {
                background: #ecf0f1;
                padding: 6px 10px;
                margin-right: 1px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                font-weight: bold;
                font-size: 10px;
            }
            QTabBar::tab:selected {
                background: #3498db;
                color: white;
            }
            QTabBar::tab:hover {
                background: #bdc3c7;
            }
        """)
        
        # Real-time data visualization tab
        self.data_view_widget = self.create_data_view_widget()
        self.tab_widget.addTab(self.data_view_widget, "📊 Data")
        
        # Main console tab
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setStyleSheet("""
            background: #2c3e50; 
            color: #ecf0f1; 
            font-family: 'Consolas', 'Monaco', monospace; 
            font-size: 9px;
            border: none;
            padding: 5px;
        """)
        self.tab_widget.addTab(self.console, "📋 Console")
        
        # ML Classification tab
        self.ml_console = QTextEdit()
        self.ml_console.setReadOnly(True)
        self.ml_console.setStyleSheet("""
            background: #1a1a2e; 
            color: #00d4ff; 
            font-family: 'Consolas', 'Monaco', monospace; 
            font-size: 9px;
            border: none;
            padding: 5px;
        """)
        self.tab_widget.addTab(self.ml_console, "🧠 ML")
        
        # Validation tab
        self.validation_console = QTextEdit()
        self.validation_console.setReadOnly(True)
        self.validation_console.setStyleSheet("""
            background: #1a2e1a; 
            color: #00ff88; 
            font-family: 'Consolas', 'Monaco', monospace; 
            font-size: 9px;
            border: none;
            padding: 5px;
        """)
        self.tab_widget.addTab(self.validation_console, "✅ Validation")
        
        # Error log tab
        self.error_console = QTextEdit()
        self.error_console.setReadOnly(True)
        self.error_console.setStyleSheet("""
            background: #2e1a1a; 
            color: #ff6b6b; 
            font-family: 'Consolas', 'Monaco', monospace; 
            font-size: 9px;
            border: none;
            padding: 5px;
        """)
        self.tab_widget.addTab(self.error_console, "❌ Errors")
        
        # Summary tab
        self.summary_console = QTextEdit()
        self.summary_console.setReadOnly(True)
        self.summary_console.setStyleSheet("""
            background: #2c2c2c; 
            color: #ffe066; 
            font-family: 'Consolas', 'Monaco', monospace; 
            font-size: 9px;
            border: none;
            padding: 5px;
        """)
        self.tab_widget.addTab(self.summary_console, "📈 Summary")
        
        # Performance monitoring tab
        self.performance_console = QTextEdit()
        self.performance_console.setReadOnly(True)
        self.performance_console.setStyleSheet("""
            background: #1e3a5f; 
            color: #74b9ff; 
            font-family: 'Consolas', 'Monaco', monospace; 
            font-size: 9px;
            border: none;
            padding: 5px;
        """)
        self.tab_widget.addTab(self.performance_console, "⚡ Performance")
        
        # System Health tab
        self.health_console = QTextEdit()
        self.health_console.setReadOnly(True)
        self.health_console.setStyleSheet("""
            background: #2d5a2d; 
            color: #90ee90; 
            font-family: 'Consolas', 'Monaco', monospace; 
            font-size: 9px;
            border: none;
            padding: 5px;
        """)
        self.tab_widget.addTab(self.health_console, "🏥 Health")
        
        right_layout.addWidget(self.tab_widget)
        return right_widget
    
    def create_data_view_widget(self):
        """Create the real-time data visualization widget"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(2)
        layout.setContentsMargins(2, 2, 2, 2)
        
        # Data view controls
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(2)
        
        self.refresh_data_btn = QPushButton("🔄")
        self.refresh_data_btn.setToolTip("Refresh")
        self.refresh_data_btn.clicked.connect(self.refresh_data_view)
        self.refresh_data_btn.setStyleSheet("padding: 2px; font-size: 10px;")
        
        self.filter_data_btn = QPushButton("🔍")
        self.filter_data_btn.setToolTip("Filter")
        self.filter_data_btn.clicked.connect(self.show_filter_dialog)
        self.filter_data_btn.setStyleSheet("padding: 2px; font-size: 10px;")
        
        self.sort_data_btn = QPushButton("📊")
        self.sort_data_btn.setToolTip("Sort")
        self.sort_data_btn.clicked.connect(self.show_sort_dialog)
        self.sort_data_btn.setStyleSheet("padding: 2px; font-size: 10px;")
        
        self.data_view_mode = QComboBox()
        self.data_view_mode.addItems(["Table", "Cards", "JSON", "Stats"])
        self.data_view_mode.currentTextChanged.connect(self.change_data_view_mode)
        self.data_view_mode.setStyleSheet("font-size: 9px; padding: 2px;")
        
        controls_layout.addWidget(self.refresh_data_btn)
        controls_layout.addWidget(self.filter_data_btn)
        controls_layout.addWidget(self.sort_data_btn)
        controls_layout.addWidget(QLabel("View:"))
        controls_layout.addWidget(self.data_view_mode)
        controls_layout.addStretch()
        
        layout.addLayout(controls_layout)
        
        # Data display area
        self.data_display_stack = QStackedWidget()
        
        # Table view
        self.data_table = QTableWidget()
        self.data_table.setColumnCount(6)
        self.data_table.setHorizontalHeaderLabels([
            "Title", "Provider", "Type", "Conf", "Quality", "Status"
        ])
        self.data_table.horizontalHeader().setStretchLastSection(True)
        self.data_table.setStyleSheet("font-size: 8px;")
        self.data_display_stack.addWidget(self.data_table)
        
        # Card view
        self.data_card_scroll = QScrollArea()
        self.data_card_widget = QWidget()
        self.data_card_layout = QVBoxLayout(self.data_card_widget)
        self.data_card_layout.setSpacing(2)
        self.data_card_scroll.setWidget(self.data_card_widget)
        self.data_card_scroll.setWidgetResizable(True)
        self.data_display_stack.addWidget(self.data_card_scroll)
        
        # JSON view
        self.data_json_view = QTextEdit()
        self.data_json_view.setReadOnly(True)
        self.data_json_view.setStyleSheet("background: #1e1e1e; color: #d4d4d4; font-family: Consolas; font-size: 8px;")
        self.data_display_stack.addWidget(self.data_json_view)
        
        # Statistics view
        self.data_stats_widget = self.create_statistics_widget()
        self.data_display_stack.addWidget(self.data_stats_widget)
        
        layout.addWidget(self.data_display_stack)
        
        return widget
    
    def create_statistics_widget(self):
        """Create statistics visualization widget"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(2)
        layout.setContentsMargins(2, 2, 2, 2)
        
        # Statistics grid
        stats_grid = QGridLayout()
        stats_grid.setSpacing(2)
        
        # Dataset statistics
        self.total_datasets_stat = QLabel("0")
        self.total_datasets_stat.setStyleSheet("font-size: 16px; font-weight: bold; color: #3498db;")
        stats_grid.addWidget(QLabel("Total:"), 0, 0)
        stats_grid.addWidget(self.total_datasets_stat, 0, 1)
        
        self.avg_confidence_stat = QLabel("0%")
        self.avg_confidence_stat.setStyleSheet("font-size: 16px; font-weight: bold; color: #27ae60;")
        stats_grid.addWidget(QLabel("Confidence:"), 1, 0)
        stats_grid.addWidget(self.avg_confidence_stat, 1, 1)
        
        self.quality_score_stat = QLabel("0%")
        self.quality_score_stat.setStyleSheet("font-size: 16px; font-weight: bold; color: #f39c12;")
        stats_grid.addWidget(QLabel("Quality:"), 2, 0)
        stats_grid.addWidget(self.quality_score_stat, 2, 1)
        
        self.ml_classified_stat = QLabel("0")
        self.ml_classified_stat.setStyleSheet("font-size: 16px; font-weight: bold; color: #9b59b6;")
        stats_grid.addWidget(QLabel("ML Classified:"), 3, 0)
        stats_grid.addWidget(self.ml_classified_stat, 3, 1)
        
        layout.addLayout(stats_grid)
        
        # Category distribution
        category_group = QGroupBox("Categories")
        category_group.setStyleSheet("font-size: 9px;")
        category_layout = QVBoxLayout()
        self.category_list = QTextEdit()
        self.category_list.setReadOnly(True)
        self.category_list.setMaximumHeight(80)
        self.category_list.setStyleSheet("font-size: 8px;")
        category_layout.addWidget(self.category_list)
        category_group.setLayout(category_layout)
        layout.addWidget(category_group)
        
        # Provider distribution
        provider_group = QGroupBox("Providers")
        provider_group.setStyleSheet("font-size: 9px;")
        provider_layout = QVBoxLayout()
        self.provider_list = QTextEdit()
        self.provider_list.setReadOnly(True)
        self.provider_list.setMaximumHeight(80)
        self.provider_list.setStyleSheet("font-size: 8px;")
        provider_layout.addWidget(self.provider_list)
        provider_group.setLayout(provider_layout)
        layout.addWidget(provider_group)
        
        layout.addStretch()
        return widget

    def update_status_indicators(self):
        """Update the status indicators for advanced features."""
        print(f"DEBUG: Updating status indicators...")
        print(f"DEBUG: self.nlp = {self.nlp}")
        print(f"DEBUG: self.bert_classifier = {self.bert_classifier}")
        print(f"DEBUG: self.geocoder = {self.geocoder}")
        print(f"DEBUG: self.dashboard = {self.dashboard}")
        print(f"DEBUG: self.config = {self.config}")
        print(f"DEBUG: pytesseract = {pytesseract}")
        
        if self.nlp:
            self.spacy_status.setText("spaCy: ✅")
            self.spacy_status.setStyleSheet("padding: 5px; border: 1px solid #27ae60; border-radius: 3px; color: #27ae60;")
        else:
            self.spacy_status.setText("spaCy: ❌")
            self.spacy_status.setStyleSheet("padding: 5px; border: 1px solid #e74c3c; border-radius: 3px; color: #e74c3c;")
        
        # Check BERT status with fallback support
        if self.bert_classifier:
            self.bert_status.setText("BERT: ✅")
            self.bert_status.setStyleSheet("padding: 5px; border: 1px solid #27ae60; border-radius: 3px; color: #27ae60;")
        elif not self.ml_models_loaded:
            self.bert_status.setText("BERT: ⏳")
            self.bert_status.setStyleSheet("padding: 5px; border: 1px solid #f39c12; border-radius: 3px; color: #f39c12;")
        elif self.ml_loading_failed:
            # Show fallback as available
            self.bert_status.setText("BERT: 🔄")
            self.bert_status.setStyleSheet("padding: 5px; border: 1px solid #f39c12; border-radius: 3px; color: #f39c12;")
            self.bert_status.setToolTip("BERT failed to load, using rule-based fallback")
        elif transformers:
            # Transformers available but BERT not loaded yet
            self.bert_status.setText("BERT: ⏳")
            self.bert_status.setStyleSheet("padding: 5px; border: 1px solid #f39c12; border-radius: 3px; color: #f39c12;")
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
        
        if pytesseract:
            self.ocr_status.setText("OCR: ✅")
            self.ocr_status.setStyleSheet("padding: 5px; border: 1px solid #27ae60; border-radius: 3px; color: #27ae60;")
        else:
            self.ocr_status.setText("OCR: ❌")
            self.ocr_status.setStyleSheet("padding: 5px; border: 1px solid #e74c3c; border-radius: 3px; color: #e74c3c;")
        
        print(f"DEBUG: Status indicators updated")

    def update_ui(self):
        """Enhanced UI update with integrated performance monitoring and health checks."""
        try:
            # Update progress bar
            try:
                progress = self.progress_queue.get_nowait()
                self.progress.setValue(progress)
            except:
                pass
            
            # Update real-time statistics
            if hasattr(self, 'extracted_data') and self.extracted_data:
                self.update_real_time_statistics(self.extracted_data)
            
            # Update performance monitoring
            self.update_performance_monitoring()
            
            # Optimize for system performance
            self.optimize_for_system()
            
            # Update health monitoring (less frequently)
            if hasattr(self, 'health_update_counter'):
                self.health_update_counter += 1
            else:
                self.health_update_counter = 0
            
            # Update health every 10 seconds (50 updates at 200ms interval)
            if self.health_update_counter >= 50:
                self.health_update_counter = 0
                if hasattr(self, 'health_console'):
                    health_report = self.get_system_health_report()
                    self.health_console.setPlainText(health_report)
            
        except Exception as e:
            self.log_error(f"UI update error: {e}")
    
    def update_performance_monitoring(self):
        """Update performance monitoring display."""
        try:
            if hasattr(self, 'performance_monitor'):
                # Fix the config issue by adding config if it doesn't exist
                if not hasattr(self.performance_monitor, 'config'):
                    self.performance_monitor.config = {
                        'monitoring': {
                            'enabled': True,
                            'log_performance': True,
                            'track_memory': True,
                            'real_time_alerts': True,
                            'performance_prediction': True
                        }
                    }
                
                # Get system metrics
                cpu_percent = psutil.cpu_percent()
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                
                # Get application metrics
                app_metrics = self.performance_monitor.get_current_metrics()
                
                # Format performance display
                perf_text = f"""
PERFORMANCE MONITORING
{'='*50}

SYSTEM METRICS:
CPU Usage: {cpu_percent:.1f}%
Memory Usage: {memory.percent:.1f}% ({memory.used / 1024**3:.1f}GB / {memory.total / 1024**3:.1f}GB)
Disk Usage: {disk.percent:.1f}% ({disk.used / 1024**3:.1f}GB / {disk.total / 1024**3:.1f}GB)

APPLICATION METRICS:
Processing Rate: {app_metrics.get('processing_rate', 0):.2f} datasets/min
Average Response Time: {app_metrics.get('avg_response_time', 0):.2f}s
Success Rate: {app_metrics.get('success_rate', 0):.1f}%
Error Rate: {app_metrics.get('error_rate', 0):.1f}%

ML MODEL PERFORMANCE:
BERT Model: {'✅ Loaded' if hasattr(self, 'bert_classifier') and self.bert_classifier else '❌ Not Loaded'}
spaCy Model: {'✅ Loaded' if hasattr(self, 'nlp') and self.nlp else '❌ Not Loaded'}
Geocoder: {'✅ Available' if hasattr(self, 'geocoder') and self.geocoder else '❌ Not Available'}

MEMORY USAGE:
Python Process: {psutil.Process().memory_info().rss / 1024**2:.1f}MB
Cache Size: {len(self.extracted_data) if hasattr(self, 'extracted_data') else 0} items

Last Updated: {time.strftime('%H:%M:%S')}
"""
                
                self.performance_console.setPlainText(perf_text)
                
                # Update status indicators based on performance
                if cpu_percent > 90:
                    self.status.setText(f"⚠️ High CPU usage: {cpu_percent:.1f}%")
                elif memory.percent > 90:
                    self.status.setText(f"⚠️ High memory usage: {memory.percent:.1f}%")
                elif hasattr(self, 'extracted_data') and self.extracted_data:
                    self.status.setText(f"✅ Processing: {len(self.extracted_data)} datasets extracted")
                else:
                    self.status.setText("Ready. Select an HTML file to begin.")
                    
        except Exception as e:
            self.performance_console.setPlainText(f"Performance monitoring error: {e}")
            # Log the error to console as well
            self.log_error(f"Performance monitoring error: {e}")

    def start_crawl(self):
        """Start the enhanced crawling process with integrated monitoring."""
        if not self.file_path_edit.text():
            self.log_message("Please select an HTML file first.")
            return
        
        html_file = self.file_path_edit.text()
        if not os.path.exists(html_file):
            self.log_message("Selected file does not exist.")
            return
        
        # Clear previous data
        self.extracted_data = []
        self.clear_all_consoles()
        
        # Set start time for rate calculation
        self.start_time = time.time()
        
        # Enable export button
        self.export_btn.setEnabled(True)
        
        # Update UI state
        self.crawl_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.status.setText("🚀 Crawling in progress...")
        self.progress.setValue(0)
        
        # Start crawling in a separate thread
        self.thread = threading.Thread(target=self.crawl_html_file, args=(html_file,), daemon=True)
        self.thread.start()
        
        # Start UI updates
        self.timer.start(100)  # Update every 100ms for real-time responsiveness
        
        self.log_message("🚀 Enhanced crawling started with real-time monitoring...")

    def crawl_html_file(self, html_file):
        """Enhanced crawling process with better error handling and low-power optimizations."""
        try:
            self.log_message(f"🚀 Starting enhanced crawl of: {html_file}")
            self.log_message(f"🔧 Low-power mode: {'Enabled' if self.low_power_mode else 'Disabled'}")
            self.log_message(f"⚡ Optimization level: {self.optimization_level}")
            
            # Reset counters
            self.error_count = 0
            self.warning_count = 0
            self.success_count = 0
            
            # Load HTML file
            with open(html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find all dataset links
            dataset_links = soup.find_all('a', href=True)
            dataset_links = [link for link in dataset_links if 'dataset' in link.get('href', '').lower()]
            
            if not dataset_links:
                self.log_message("⚠️ No dataset links found in the HTML file")
                return
            
            self.log_message(f"📊 Found {len(dataset_links)} potential dataset links")
            
            # Configure crawling parameters based on system capabilities
            max_concurrent = self.concurrent_slider.value()
            request_delay = self.delay_slider.value() / 2
            
            # Adjust for low-power systems
            if self.low_power_mode:
                max_concurrent = min(max_concurrent, 2)
                request_delay = max(request_delay, 1.0)
                self.log_message(f"🔋 Low-power adjustments: {max_concurrent} concurrent, {request_delay}s delay")
            
            # Create thread pool
            with ThreadPoolExecutor(max_workers=max_concurrent) as executor:
                futures = []
                
                for i, link in enumerate(dataset_links):
                    if self.stop_requested:
                        break
                    
                    url = link.get('href')
                    if not url.startswith('http'):
                        url = 'https://developers.google.com/earth-engine/datasets' + url
                    
                    # Submit task
                    future = executor.submit(self.process_dataset_link, url, i + 1, len(dataset_links))
                    futures.append(future)
                    
                    # Add delay between submissions
                    time.sleep(request_delay / max_concurrent)
                
                # Process results
                for future in as_completed(futures):
                    if self.stop_requested:
                        break
                    
                    try:
                        result = future.result(timeout=30)  # 30 second timeout
                        if result:
                            self.add_extracted_data(result)
                            self.success_count += 1
                    except TimeoutError:
                        self.warning_count += 1
                        self.log_error("⏰ Request timeout - skipping dataset")
                    except Exception as e:
                        self.error_count += 1
                        self.enhanced_error_handling(e, "Dataset processing")
            
            # Final summary
            self.show_crawl_summary()
            
        except Exception as e:
            self.enhanced_error_handling(e, "Main crawl process")
            self.log_error("❌ Crawling failed - check logs for details")
        finally:
            self.crawl_finished()
    
    def process_dataset_link(self, url, current, total):
        """Process individual dataset link with enhanced error handling."""
        try:
            # Update progress
            progress = int((current / total) * 100)
            self.progress_queue.put(progress)
            
            # Log progress
            if current % 10 == 0 or current == total:
                self.log_message(f"📈 Progress: {current}/{total} ({progress}%)")
            
            # Make request with timeout
            timeout = 15 if self.low_power_mode else 10
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            
            # Parse response
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract data
            result = self.advanced_extract(soup, url)
            
            if result:
                # Apply ML classification if enabled
                if self.use_ml_classification.isChecked():
                    try:
                        self.apply_ml_classification(soup, result)
                    except Exception as e:
                        self.warning_count += 1
                        self.log_error(f"ML classification failed: {e}")
                
                # Apply validation if enabled
                if self.use_validation.isChecked():
                    try:
                        self.apply_validation(result)
                    except Exception as e:
                        self.warning_count += 1
                        self.log_error(f"Validation failed: {e}")
                
                # Apply ensemble methods if enabled
                if self.use_ensemble.isChecked():
                    try:
                        self.apply_ensemble_methods(result)
                    except Exception as e:
                        self.warning_count += 1
                        self.log_error(f"Ensemble processing failed: {e}")
                
                return result
            
        except requests.exceptions.Timeout:
            self.warning_count += 1
            self.log_error(f"⏰ Timeout processing: {url}")
        except requests.exceptions.RequestException as e:
            self.error_count += 1
            self.enhanced_error_handling(e, f"Request to {url}")
        except Exception as e:
            self.error_count += 1
            self.enhanced_error_handling(e, f"Processing {url}")
        
        return None

    def advanced_extract(self, soup, url):
        """Enhanced extraction with real-time data integration."""
        result = {
            'title': '', 'provider': '', 'tags': [], 'date_range': '', 'description': '',
            'bands': [], 'terms_of_use': '', 'snippet': '', 'spatial_coverage': '',
            'temporal_coverage': '', 'citation': '', 'type': '', 'region': '', 'source_url': url,
            'extraction_report': {}, 'confidence': {}, 'ml_classification': {}, 'validation_results': {},
            'enhanced_features': {}, 'quality_score': 0.0, 'confidence_score': 0.0, 'data_type': 'unknown'
        }
        
        # Extract basic information
        result = self.extract_basic_info(soup, result)
        
        # Apply ML classification
        if hasattr(self, 'use_ml_classification') and self.use_ml_classification.isChecked():
            result = self.apply_ml_classification(soup, result)
            
            # Set data type from ML classification
            if result.get('ml_classification', {}).get('enhanced_classification', {}).get('label'):
                result['data_type'] = result['ml_classification']['enhanced_classification']['label']
            elif result.get('ml_classification', {}).get('simple_classification', {}).get('label'):
                result['data_type'] = result['ml_classification']['simple_classification']['label']
        
        # Apply validation
        if hasattr(self, 'use_validation') and self.use_validation.isChecked():
            result = self.apply_validation(result)
            
            # Set quality score from validation
            if result.get('validation_results', {}).get('overall_score'):
                result['quality_score'] = result['validation_results']['overall_score']
        
        # Apply ensemble methods
        if hasattr(self, 'use_ensemble') and self.use_ensemble.isChecked():
            result = self.apply_ensemble_methods(result)
            
            # Set confidence score from ensemble
            if result.get('ensemble_results', {}).get('ensemble_classification', {}).get('confidence'):
                result['confidence_score'] = result['ensemble_results']['ensemble_classification']['confidence']
        
        # Calculate overall confidence if not set
        if result['confidence_score'] == 0.0:
            confidence_scores = []
            if result.get('ml_classification', {}).get('enhanced_classification', {}).get('confidence'):
                confidence_scores.append(result['ml_classification']['enhanced_classification']['confidence'])
            if result.get('ml_classification', {}).get('simple_classification', {}).get('confidence'):
                confidence_scores.append(result['ml_classification']['simple_classification']['confidence'])
            
            if confidence_scores:
                result['confidence_score'] = sum(confidence_scores) / len(confidence_scores)
            else:
                result['confidence_score'] = 0.5  # Default confidence
        
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
        """Enhanced ML classification with advanced features and ensemble methods for maximum quality."""
        ml_results = {}
        
        try:
            # Enhanced spaCy NER with comprehensive entity extraction
            if self.nlp:
                # Use full text for maximum coverage in low-power mode
                text_length = 3000 if self.low_power_mode else 2000
                text = soup.get_text()[:text_length]
                doc = self.nlp(text)
                
                # Extract entities with enhanced categorization and confidence scoring
                entities = {}
                entity_confidence = {}
                
                for ent in doc.ents:
                    if ent.label_ not in entities:
                        entities[ent.label_] = []
                        entity_confidence[ent.label_] = []
                    
                    if ent.text not in entities[ent.label_]:  # Avoid duplicates
                        entities[ent.label_].append(ent.text)
                        # Calculate confidence based on entity length and frequency
                        confidence = min(0.9, 0.3 + (len(ent.text) * 0.1) + (ent.label_ in ['GPE', 'ORG', 'PRODUCT'] and 0.2))
                        entity_confidence[ent.label_].append(confidence)
                
                ml_results['spacy_entities'] = entities
                ml_results['entity_confidence'] = entity_confidence
                
                # Enhanced title entity extraction with semantic analysis
                if result['title']:
                    title_doc = self.nlp(result['title'])
                    title_entities = [(ent.text, ent.label_, ent.vector_norm) for ent in title_doc.ents]
                    ml_results['title_entities'] = title_entities
            
                    # Extract key phrases from title with semantic similarity
                    title_tokens = [token.text for token in title_doc if not token.is_stop and token.is_alpha and len(token.text) > 3]
                    ml_results['title_key_phrases'] = title_tokens[:15]  # Increased for better coverage
                    
                    # Extract title sentiment and complexity
                    title_sentiment = sum([token.sentiment for token in title_doc]) / len(title_doc)
                    title_complexity = len([token for token in title_doc if token.pos_ in ['NOUN', 'VERB', 'ADJ']])
                    ml_results['title_sentiment'] = title_sentiment
                    ml_results['title_complexity'] = title_complexity
                
                # Enhanced technical terms and measurements extraction
                technical_terms = []
                measurements = []
                spatial_references = []
                temporal_references = []
                
                # Comprehensive technical term detection
                technical_keywords = [
                    'resolution', 'band', 'wavelength', 'frequency', 'coverage', 'pixel', 'satellite',
                    'sensor', 'radar', 'optical', 'infrared', 'thermal', 'multispectral', 'hyperspectral',
                    'temporal', 'spatial', 'spectral', 'radiometric', 'geometric', 'atmospheric'
                ]
                
                for token in doc:
                    # Enhanced measurement detection
                    if token.like_num and token.nbor().is_alpha:
                        measurement_text = f"{token.text} {token.nbor().text}"
                        measurements.append(measurement_text)
                    
                    # Technical term detection
                    if token.text.lower() in technical_keywords:
                        technical_terms.append(token.text)
                    
                    # Spatial reference detection
                    if token.ent_type_ in ['GPE', 'LOC']:
                        spatial_references.append(token.text)
                    
                    # Temporal reference detection
                    if token.ent_type_ in ['DATE', 'TIME']:
                        temporal_references.append(token.text)
                
                ml_results['technical_terms'] = technical_terms
                ml_results['measurements'] = measurements
                ml_results['spatial_references'] = spatial_references
                ml_results['temporal_references'] = temporal_references
                
                # Enhanced document analysis
                doc_sentiment = sum([token.sentiment for token in doc]) / len(doc)
                doc_complexity = len([token for token in doc if token.pos_ in ['NOUN', 'VERB', 'ADJ']])
                ml_results['document_sentiment'] = doc_sentiment
                ml_results['document_complexity'] = doc_complexity
            
            # Enhanced BERT classification with comprehensive text analysis
            if self.bert_classifier:
                try:
                    # Combine multiple text sources for comprehensive classification
                    classification_texts = []
                    if result['title']:
                        # Use full title for better context
                        classification_texts.append(result['title'])
                    if result.get('description'):
                        # Use more description text for better analysis
                        desc_length = 500 if self.low_power_mode else 400
                        classification_texts.append(result['description'][:desc_length])
                    if result.get('tags'):
                        # Include tags for better categorization
                        tags_text = " ".join(result['tags']) if isinstance(result['tags'], list) else str(result['tags'])
                        classification_texts.append(tags_text)
                    
                    if classification_texts:
                        combined_text = " ".join(classification_texts)
                        
                        # Use threading with timeout to prevent hanging
                        import threading
                        import queue
                        
                        result_queue = queue.Queue()
                        
                        def bert_classify():
                            try:
                                # Enhanced classification with optimal parameters for quality
                                max_length = 512 if self.low_power_mode else 384  # Full context for low-power
                                bert_result = self.bert_classifier(
                                    combined_text,
                                    truncation=True,
                                    max_length=max_length,
                                    return_all_scores=True,  # Get all scores for ensemble
                                    padding=True  # Ensure consistent input
                                )
                                result_queue.put(('success', bert_result))
                            except Exception as e:
                                result_queue.put(('error', str(e)))
                        
                        # Start BERT classification in separate thread with longer timeout
                        bert_thread = threading.Thread(target=bert_classify, daemon=True)
                        bert_thread.start()
                        timeout = 8 if self.low_power_mode else 6  # Longer timeout for low-power systems
                        bert_thread.join(timeout=timeout)
                        
                        if bert_thread.is_alive():
                            self.log_error("BERT classification timed out - using fallback")
                        else:
                            try:
                                status, bert_result = result_queue.get_nowait()
                                if status == 'success':
                                    # Enhanced result processing
                                    if isinstance(bert_result, list) and len(bert_result) > 0:
                                        # Get top 3 classifications
                                        sorted_results = sorted(bert_result[0], key=lambda x: x['score'], reverse=True)
                                        ml_results['bert_classification'] = {
                                            'primary': sorted_results[0],
                                            'secondary': sorted_results[1] if len(sorted_results) > 1 else None,
                                            'tertiary': sorted_results[2] if len(sorted_results) > 2 else None,
                                            'all_scores': sorted_results[:5]  # Top 5 scores
                                        }
                                    else:
                                        ml_results['bert_classification'] = bert_result
                                else:
                                    self.log_error(f"BERT classification error: {bert_result}")
                            except queue.Empty:
                                self.log_error("BERT classification result not available")
                            
                except Exception as e:
                    self.log_error(f"BERT classification error: {e}")
            
            # Enhanced keyword extraction with frequency analysis
            text = soup.get_text()[:1500]
            words = re.findall(r'\b[A-Za-z]{4,}\b', text.lower())
            word_freq = {}
            for word in words:
                if word not in ['this', 'that', 'with', 'from', 'they', 'have', 'will', 'been', 'were', 'said', 'each', 'which', 'their', 'time', 'would', 'there', 'could', 'other', 'than', 'first', 'water', 'after', 'where', 'many', 'these', 'then', 'them', 'such', 'here', 'take', 'into', 'just', 'like', 'know', 'over', 'think', 'also', 'back', 'after', 'use', 'two', 'how', 'our', 'work', 'first', 'well', 'way', 'even', 'new', 'want', 'because', 'any', 'these', 'give', 'day', 'most', 'us']:
                    word_freq[word] = word_freq.get(word, 0) + 1
            
            # Get top keywords by frequency
            sorted_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
            ml_results['enhanced_keywords'] = [word for word, freq in sorted_keywords[:25]]
            ml_results['keyword_frequencies'] = dict(sorted_keywords[:15])
            
            # Enhanced rule-based classification with multiple text sources
            classification_texts = []
            if result.get('title'):
                classification_texts.append(result['title'])
            if result.get('description'):
                classification_texts.append(result['description'])
            if result.get('tags'):
                classification_texts.extend(result['tags'])
            
            if classification_texts:
                combined_text = " ".join(classification_texts)
                classification = self.simple_classify_text(combined_text)
                ml_results['enhanced_classification'] = classification
                
                # Multi-category classification
                if classification.get('all_scores'):
                    # Get top 3 categories
                    sorted_categories = sorted(classification['all_scores'].items(), key=lambda x: x[1], reverse=True)
                    ml_results['multi_category_classification'] = {
                        'primary': sorted_categories[0] if sorted_categories else None,
                        'secondary': sorted_categories[1] if len(sorted_categories) > 1 else None,
                        'tertiary': sorted_categories[2] if len(sorted_categories) > 2 else None
                    }
            
            # Extract satellite and sensor information
            satellite_info = self._extract_satellite_info(text)
            if satellite_info:
                ml_results['satellite_info'] = satellite_info
            
            # Extract resolution and technical specifications
            technical_specs = self._extract_technical_specs(text)
            if technical_specs:
                ml_results['technical_specifications'] = technical_specs

        except Exception as e:
            self.log_error(f"Enhanced ML classification failed: {e}")
            # Enhanced fallback
            text = soup.get_text()[:800]
            keywords = set(re.findall(r'\b[A-Za-z]{4,}\b', text))
            ml_results['fallback_keywords'] = list(keywords)[:15]
            
            # Basic classification fallback
            if result.get('title'):
                ml_results['fallback_classification'] = self.simple_classify_text(result['title'])

        result['ml_classification'] = ml_results
        return result
    
    def _extract_satellite_info(self, text):
        """Extract satellite and sensor information from text"""
        satellite_patterns = {
            'landsat': r'\b(Landsat\s*\d+[A-Z]?)\b',
            'sentinel': r'\b(Sentinel\s*[12AB])\b',
            'modis': r'\b(MODIS|Terra|Aqua)\b',
            'aster': r'\b(ASTER)\b',
            'spot': r'\b(SPOT\s*\d+)\b',
            'pleiades': r'\b(Pleiades)\b',
            'quickbird': r'\b(QuickBird)\b',
            'worldview': r'\b(WorldView\s*[1234])\b',
            'planet': r'\b(Planet|PlanetScope|RapidEye)\b'
        }
        
        satellites = {}
        for sat_type, pattern in satellite_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                satellites[sat_type] = list(set(matches))
        
        return satellites if satellites else None
    
    def _extract_technical_specs(self, text):
        """Extract technical specifications from text"""
        specs = {}
        
        # Resolution patterns
        resolution_patterns = [
            r'(\d+(?:\.\d+)?)\s*(m|meters?|km|kilometers?)\s*resolution',
            r'resolution\s*of\s*(\d+(?:\.\d+)?)\s*(m|meters?|km|kilometers?)',
            r'(\d+(?:\.\d+)?)\s*(m|meters?|km|kilometers?)\s*pixel'
        ]
        
        for pattern in resolution_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                specs['resolution'] = [f"{value} {unit}" for value, unit in matches]
                break
        
        # Band patterns
        band_patterns = [
            r'\b(B\d+|Band\s*\d+)\b',
            r'\b([RGB]|Red|Green|Blue|NIR|SWIR|TIR)\b',
            r'\b(\d+)\s*bands?\b'
        ]
        
        bands = []
        for pattern in band_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            bands.extend(matches)
        
        if bands:
            specs['bands'] = list(set(bands))
        
        # Wavelength patterns
        wavelength_patterns = [
            r'(\d+(?:\.\d+)?)\s*(nm|nanometers?|microns?|μm)\b',
            r'wavelength\s*(\d+(?:\.\d+)?)\s*(nm|nanometers?|microns?|μm)'
        ]
        
        wavelengths = []
        for pattern in wavelength_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            wavelengths.extend([f"{value} {unit}" for value, unit in matches])
        
        if wavelengths:
            specs['wavelengths'] = list(set(wavelengths))
        
        return specs if specs else None

    def simple_classify_text(self, text):
        """Enhanced rule-based text classification with advanced patterns"""
        text_lower = text.lower()
        
        # Enhanced classification rules with more comprehensive keywords
        categories = {
            'satellite_data': [
                'satellite', 'landsat', 'sentinel', 'modis', 'aster', 'spot', 'pleiades', 
                'quickbird', 'worldview', 'ikonos', 'geoeye', 'rapideye', 'planet', 'maxar',
                'optical', 'multispectral', 'hyperspectral', 'radar', 'sar', 'lidar'
            ],
            'aerial_data': [
                'aerial', 'drone', 'uav', 'airborne', 'photogrammetry', 'uav', 'uas',
                'unmanned', 'aircraft', 'helicopter', 'plane', 'flight', 'survey'
            ],
            'climate_data': [
                'climate', 'weather', 'temperature', 'precipitation', 'atmospheric', 'meteorological',
                'rainfall', 'snowfall', 'humidity', 'pressure', 'wind', 'solar', 'radiation',
                'greenhouse', 'carbon', 'emissions', 'air_quality', 'pollution'
            ],
            'terrain_data': [
                'dem', 'elevation', 'terrain', 'topography', 'slope', 'aspect', 'hillshade',
                'digital_elevation', 'srtm', 'aster_gdem', 'alos_palsar', 'height', 'altitude'
            ],
            'vegetation_data': [
                'vegetation', 'forest', 'crop', 'agriculture', 'ndvi', 'evi', 'lai', 'fapar',
                'biomass', 'canopy', 'leaf', 'plant', 'tree', 'grass', 'shrub', 'land_cover',
                'land_use', 'deforestation', 'reforestation', 'burned_area'
            ],
            'water_data': [
                'water', 'ocean', 'river', 'lake', 'coastal', 'marine', 'aquatic', 'hydrology',
                'flood', 'drought', 'wetland', 'marsh', 'swamp', 'estuary', 'delta', 'watershed',
                'catchment', 'basin', 'reservoir', 'dam', 'stream', 'creek'
            ],
            'urban_data': [
                'urban', 'city', 'building', 'infrastructure', 'population', 'settlement',
                'residential', 'commercial', 'industrial', 'transportation', 'road', 'highway',
                'bridge', 'airport', 'port', 'railway', 'subway', 'metro'
            ],
            'geological_data': [
                'geology', 'mineral', 'rock', 'soil', 'geological', 'lithology', 'stratigraphy',
                'fault', 'earthquake', 'volcano', 'seismic', 'tectonic', 'plate', 'mountain',
                'valley', 'canyon', 'cave', 'karst', 'erosion', 'deposition'
            ],
            'atmospheric_data': [
                'atmosphere', 'air_quality', 'pollution', 'aerosol', 'particulate', 'pm2.5',
                'pm10', 'ozone', 'nitrogen', 'sulfur', 'carbon_monoxide', 'methane', 'vapor',
                'cloud', 'fog', 'haze', 'smog', 'visibility'
            ],
            'cryosphere_data': [
                'ice', 'snow', 'glacier', 'polar', 'arctic', 'antarctic', 'permafrost',
                'frozen', 'winter', 'frost', 'blizzard', 'avalanche', 'iceberg', 'sea_ice',
                'ice_sheet', 'ice_cap', 'ice_field'
            ],
            'oceanographic_data': [
                'ocean', 'marine', 'sea', 'current', 'salinity', 'temperature', 'depth',
                'bathymetry', 'tide', 'wave', 'storm', 'hurricane', 'typhoon', 'cyclone',
                'tsunami', 'upwelling', 'downwelling', 'gyre', 'eddy'
            ],
            'disaster_data': [
                'disaster', 'emergency', 'flood', 'fire', 'earthquake', 'tsunami', 'hurricane',
                'tornado', 'drought', 'landslide', 'avalanche', 'volcanic', 'epidemic',
                'pandemic', 'outbreak', 'crisis', 'catastrophe'
            ]
        }
        
        # Enhanced scoring with weighted keywords
        scores = {}
        for category, keywords in categories.items():
            score = 0
            for keyword in keywords:
                if keyword in text_lower:
                    # Weight by keyword length and specificity
                    weight = len(keyword) / 10.0
                    score += weight
            
            if score > 0:
                scores[category] = score
        
        if scores:
            # Return the category with highest score
            best_category = max(scores, key=scores.get)
            # Enhanced confidence calculation
            max_possible_score = sum(len(kw) / 10.0 for kw in categories[best_category])
            confidence = min(scores[best_category] / max_possible_score, 1.0)
            
            return {
                'label': best_category,
                'confidence': confidence,
                'method': 'enhanced_rule_based',
                'score': scores[best_category],
                'all_scores': scores
            }
        else:
            return {
                'label': 'general_data',
                'confidence': 0.3,
                'method': 'enhanced_rule_based',
                'score': 0,
                'all_scores': {}
            }

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
        """Enhanced ensemble methods with advanced voting and confidence weighting for maximum quality."""
        ensemble_results = {}
        
        # Collect all classification results with enhanced weighting
        classifications = []
        
        # Enhanced weights based on method reliability and quality
        weights = {
            'bert_primary': 0.35,      # Primary BERT classification
            'bert_secondary': 0.15,    # Secondary BERT classification
            'spacy_entities': 0.25,    # spaCy entity-based classification
            'enhanced_classification': 0.15,  # Enhanced rule-based
            'rule_based': 0.10         # Basic rule-based
        }
        
        # Quality adjustment factors for low-power systems
        quality_factor = 1.2 if self.low_power_mode else 1.0  # Boost quality in low-power mode
        
        # Add ML classification results with enhanced processing
        if 'ml_classification' in result:
            ml_class = result['ml_classification']
            
            # Enhanced BERT classification
            if 'bert_classification' in ml_class:
                bert_result = ml_class['bert_classification']
                if isinstance(bert_result, dict):
                    if 'primary' in bert_result:
                        # New enhanced BERT format
                        primary = bert_result['primary']
                        classifications.append({
                            'method': 'bert_primary',
                            'label': primary.get('label', 'unknown'),
                            'confidence': primary.get('score', 0.0),
                            'weight': weights['bert']
                        })
                        
                        # Add secondary classification if available
                        if 'secondary' in bert_result and bert_result['secondary']:
                            secondary = bert_result['secondary']
                            classifications.append({
                                'method': 'bert_secondary',
                                'label': secondary.get('label', 'unknown'),
                                'confidence': secondary.get('score', 0.0) * 0.7,  # Reduced weight
                                'weight': weights['bert'] * 0.5
                            })
                    elif 'label' in bert_result:
                        # Legacy BERT format
                        classifications.append({
                            'method': 'bert',
                            'label': bert_result['label'],
                            'confidence': bert_result.get('confidence', 0.0),
                            'weight': weights['bert']
                        })
            
            # Enhanced classification
            if 'enhanced_classification' in ml_class:
                enhanced_result = ml_class['enhanced_classification']
                classifications.append({
                    'method': 'enhanced',
                    'label': enhanced_result.get('label', 'general_data'),
                    'confidence': enhanced_result.get('confidence', 0.5),
                    'weight': weights['enhanced_classification'],
                    'score': enhanced_result.get('score', 0.0)
                })
            
            # Multi-category classification
            if 'multi_category_classification' in ml_class:
                multi_result = ml_class['multi_category_classification']
                for category_type, category_data in multi_result.items():
                    if category_data:
                        label, score = category_data
                        weight_multiplier = 1.0 if category_type == 'primary' else 0.7 if category_type == 'secondary' else 0.4
                        classifications.append({
                            'method': f'multi_{category_type}',
                            'label': label,
                            'confidence': score,
                            'weight': weights['enhanced_classification'] * weight_multiplier
                        })
            
            # spaCy entity-based classification
            if 'spacy_entities' in ml_class:
                entities = ml_class['spacy_entities']
                entity_classifications = []
                
                # Classify based on entity types
                if 'ORG' in entities:
                    entity_classifications.append(('organization_data', 0.8))
                if 'GPE' in entities:
                    entity_classifications.append(('geographic_data', 0.7))
                if 'DATE' in entities:
                    entity_classifications.append(('temporal_data', 0.6))
                if 'CARDINAL' in entities:
                    entity_classifications.append(('numerical_data', 0.5))
                
                for label, confidence in entity_classifications:
                    classifications.append({
                        'method': 'spacy_entities',
                        'label': label,
                        'confidence': confidence,
                        'weight': weights['spacy_entities']
                    })
            
            # Rule-based classification fallback
            if 'simple_classification' in ml_class:
                simple_result = ml_class['simple_classification']
                classifications.append({
                    'method': 'rule_based',
                    'label': simple_result.get('label', 'general_data'),
                    'confidence': simple_result.get('confidence', 0.5),
                    'weight': weights['rule_based']
                })
        
        # Enhanced ensemble voting with weighted confidence
        if classifications:
            # Weighted voting system
            label_scores = {}
            label_weights = {}
            method_agreement = {}
            
            for classification in classifications:
                label = classification['label']
                confidence = classification['confidence']
                weight = classification.get('weight', 1.0)
                
                if label not in label_scores:
                    label_scores[label] = 0.0
                    label_weights[label] = 0.0
                    method_agreement[label] = []
                
                # Weighted score calculation
                weighted_score = confidence * weight
                label_scores[label] += weighted_score
                label_weights[label] += weight
                method_agreement[label].append(classification['method'])
            
            # Calculate final weighted scores
            final_scores = {}
            for label in label_scores:
                if label_weights[label] > 0:
                    final_scores[label] = label_scores[label] / label_weights[label]
            
            # Find the best classification
            if final_scores:
                best_label = max(final_scores, key=final_scores.get)
                best_score = final_scores[best_label]
                
                # Calculate agreement metrics
                agreement_count = len(method_agreement[best_label])
                total_methods = len(set(c['method'] for c in classifications))
                agreement_ratio = agreement_count / total_methods if total_methods > 0 else 0
                
                ensemble_results['ensemble_classification'] = {
                    'label': best_label,
                    'confidence': best_score,
                    'weighted_score': best_score,
                    'agreement_count': agreement_count,
                    'total_methods': total_methods,
                    'agreement_ratio': agreement_ratio,
                    'methods_used': method_agreement[best_label],
                    'all_scores': final_scores,
                    'classification_quality': 'high' if agreement_ratio > 0.5 else 'medium' if agreement_ratio > 0.3 else 'low'
                }
                
                # Add confidence intervals
                if best_score > 0.8:
                    ensemble_results['ensemble_classification']['confidence_level'] = 'very_high'
                elif best_score > 0.6:
                    ensemble_results['ensemble_classification']['confidence_level'] = 'high'
                elif best_score > 0.4:
                    ensemble_results['ensemble_classification']['confidence_level'] = 'medium'
                else:
                    ensemble_results['ensemble_classification']['confidence_level'] = 'low'
        
        # Add ensemble metadata
        ensemble_results['ensemble_metadata'] = {
            'total_classifications': len(classifications),
            'methods_used': list(set(c['method'] for c in classifications)),
            'timestamp': datetime.now().isoformat(),
            'ensemble_version': '2.0'
        }
        
        result['ensemble_results'] = ensemble_results
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
        """Enhanced data quality validation with comprehensive metrics for maximum quality."""
        result = {'valid': False, 'score': 0, 'errors': [], 'strengths': [], 'enriched': {}}
        
        try:
            score = 0
            max_score = 100
            
            # Enhanced title quality assessment
            if data.get('title'):
                title = data['title']
                title_length = len(title)
                score += 15
                
                if title_length > 20:
                    score += 10
                    result['strengths'].append("Comprehensive title")
                elif title_length > 10:
                    score += 5
                    result['strengths'].append("Good title length")
                else:
                    result['errors'].append("Short title")
                
                # Check for technical terms in title
                technical_terms = ['satellite', 'sensor', 'radar', 'optical', 'resolution', 'coverage', 'band', 'wavelength']
                title_lower = title.lower()
                tech_count = sum(1 for term in technical_terms if term in title_lower)
                if tech_count > 0:
                    score += 5
                    result['strengths'].append(f"Contains {tech_count} technical terms")
            else:
                result['errors'].append("Missing title")
            
            # Enhanced description quality assessment
            if data.get('description'):
                desc = data['description']
                desc_length = len(desc)
                score += 15
                
                if desc_length > 200:
                    score += 10
                    result['strengths'].append("Detailed description")
                elif desc_length > 100:
                    score += 7
                    result['strengths'].append("Good description length")
                elif desc_length > 50:
                    score += 3
                    result['strengths'].append("Basic description")
                else:
                    result['errors'].append("Very short description")
                
                # Check for technical content in description
                technical_indicators = ['resolution', 'wavelength', 'frequency', 'coverage', 'temporal', 'spatial', 'spectral']
                desc_lower = desc.lower()
                tech_indicators = sum(1 for indicator in technical_indicators if indicator in desc_lower)
                if tech_indicators > 2:
                    score += 5
                    result['strengths'].append("Rich technical content")
            else:
                result['errors'].append("Missing description")
            
            # Enhanced tags quality assessment
            if data.get('tags'):
                tags = data['tags']
                if isinstance(tags, list):
                    tag_count = len(tags)
                    score += 10
                    
                    if tag_count > 5:
                        score += 5
                        result['strengths'].append(f"Comprehensive tagging ({tag_count} tags)")
                    elif tag_count > 2:
                        score += 3
                        result['strengths'].append(f"Good tagging ({tag_count} tags)")
                    else:
                        result['errors'].append("Insufficient tags")
                else:
                    score += 5
                    result['strengths'].append("Tags available")
            else:
                result['errors'].append("Missing tags")
            
            # Enhanced provider quality assessment
            if data.get('provider'):
                provider = data['provider']
                if len(provider) > 5:
                    score += 10
                    result['strengths'].append("Provider information available")
                else:
                    score += 5
                    result['errors'].append("Minimal provider info")
            else:
                result['errors'].append("Missing provider")
            
            # Enhanced ML classification quality assessment
            if data.get('ml_classification'):
                ml_class = data['ml_classification']
                score += 10
                
                if 'bert_classification' in ml_class:
                    score += 5
                    result['strengths'].append("BERT classification available")
                if 'spacy_entities' in ml_class:
                    score += 3
                    result['strengths'].append("spaCy entity extraction")
                if 'technical_terms' in ml_class and ml_class['technical_terms']:
                    score += 2
                    result['strengths'].append("Technical terms identified")
            
            # Enhanced validation results assessment
            if data.get('validation_results'):
                validation = data['validation_results']
                validation_count = len(validation)
                if validation_count > 2:
                    score += 5
                    result['strengths'].append(f"Comprehensive validation ({validation_count} checks)")
                else:
                    score += 2
                    result['strengths'].append("Basic validation")
            
            # Quality factor for low-power systems (boost quality score)
            quality_factor = 1.1 if self.low_power_mode else 1.0
            final_score = min(int(score * quality_factor), max_score)
            
            result['score'] = final_score
            result['valid'] = final_score >= 60  # Higher threshold for quality
            result['enriched']['quality_score'] = final_score
            result['enriched']['quality_grade'] = 'A+' if final_score >= 90 else 'A' if final_score >= 80 else 'B+' if final_score >= 70 else 'B' if final_score >= 60 else 'C' if final_score >= 50 else 'D' if final_score >= 40 else 'F'
            result['enriched']['quality_level'] = 'Excellent' if final_score >= 80 else 'Good' if final_score >= 60 else 'Fair' if final_score >= 40 else 'Poor'
            
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
            
            # Save to exported_data directory as well
            try:
                exported_json_file = os.path.join(self.exported_dir, f"enhanced_crawl_results_{timestamp}.json")
                with open(exported_json_file, 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=2, ensure_ascii=False)
                self.log_message(f"Results also saved to exported data: {exported_json_file}")
            except Exception as e:
                self.log_error(f"Error saving to exported data: {e}")
            
            self.log_message(f"Results saved to: {json_file}")
            
            # Update dashboard
            if self.dashboard:
                try:
                    # Add data to dashboard in batches for better performance
                    self.dashboard.add_batch_data(results)
                    self.log_message(f"Dashboard updated with {len(results)} datasets")
                except Exception as e:
                    self.log_error(f"Dashboard update error: {e}")
                    # Try individual updates as fallback
                    try:
                        for result in results:
                            self.dashboard.add_data(result)
                    except Exception as fallback_error:
                        self.log_error(f"Dashboard fallback update also failed: {fallback_error}")
            
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

    def stop_crawl(self):
        """Stop the crawling process."""
        self.stop_requested = True
        self.log_message("Stopping crawler... Please wait for current operation to complete.")
        self.status.setText("Stopping...")
    
    def toggle_realtime_view(self):
        """Toggle real-time data view"""
        self.tab_widget.setCurrentIndex(1)  # Switch to data view tab
        self.refresh_data_view()
    
    def refresh_data_view(self):
        """Refresh the data view with current extracted data"""
        with self.data_lock:
            current_data = self.extracted_data.copy()
        
        if not current_data:
            self.log_message("No data available for viewing yet.")
            return
        
        # Update statistics
        self.update_real_time_statistics(current_data)
        
        # Update view based on current mode
        view_mode = self.data_view_mode.currentText()
        if view_mode == "Table View":
            self.update_table_view(current_data)
        elif view_mode == "Card View":
            self.update_card_view(current_data)
        elif view_mode == "JSON View":
            self.update_json_view(current_data)
        elif view_mode == "Statistics View":
            self.update_statistics_view(current_data)
    
    def update_real_time_statistics(self, data):
        """Update real-time statistics labels with enhanced metrics."""
        if not data:
            return
        
        total_datasets = len(data)
        avg_confidence = sum(d.get('confidence_score', 0) for d in data) / total_datasets * 100
        ml_classified = sum(1 for d in data if d.get('ml_classification'))
        quality_scores = [d.get('quality_score', 0) for d in data if d.get('quality_score')]
        avg_quality = sum(quality_scores) / len(quality_scores) * 100 if quality_scores else 0
        
        # Calculate processing rate
        if hasattr(self, 'start_time') and self.start_time:
            elapsed_time = time.time() - self.start_time
            if elapsed_time > 0:
                rate = total_datasets / (elapsed_time / 60)  # datasets per minute
                self.processing_rate_label.setText(f"Rate: {rate:.1f}/min")
        
        # Update labels with enhanced styling
        self.datasets_processed_label.setText(f"Datasets: {total_datasets}")
        self.avg_confidence_label.setText(f"Confidence: {avg_confidence:.1f}%")
        self.ml_classified_label.setText(f"ML Classified: {ml_classified}")
        self.quality_score_label.setText(f"Quality: {avg_quality:.1f}%")
        
        # Update error count from error console
        error_count = len([line for line in self.error_console.toPlainText().split('\n') if line.strip()])
        self.errors_label.setText(f"Errors: {error_count}")
        
        # Update statistics widget if it exists
        if hasattr(self, 'total_datasets_stat'):
            self.total_datasets_stat.setText(str(total_datasets))
            self.avg_confidence_stat.setText(f"{avg_confidence:.1f}%")
            self.quality_score_stat.setText(f"{avg_quality:.1f}%")
            self.ml_classified_stat.setText(str(ml_classified))
    
    def update_table_view(self, data):
        """Update table view with extracted data"""
        self.data_table.setRowCount(len(data))
        
        for row, item in enumerate(data):
            # Title
            title = item.get('title', 'N/A')[:50] + "..." if len(item.get('title', '')) > 50 else item.get('title', 'N/A')
            self.data_table.setItem(row, 0, QTableWidgetItem(title))
            
            # Provider
            provider = item.get('provider', 'N/A')
            self.data_table.setItem(row, 1, QTableWidgetItem(provider))
            
            # Type
            data_type = item.get('data_type', 'N/A')
            self.data_table.setItem(row, 2, QTableWidgetItem(data_type))
            
            # Confidence
            confidence = f"{item.get('confidence_score', 0) * 100:.1f}%"
            self.data_table.setItem(row, 3, QTableWidgetItem(confidence))
            
            # Quality
            quality = f"{item.get('quality_score', 0) * 100:.1f}%"
            self.data_table.setItem(row, 4, QTableWidgetItem(quality))
            
            # Tags
            tags = ", ".join(item.get('tags', [])[:3])
            self.data_table.setItem(row, 5, QTableWidgetItem(tags))
            
            # Status
            status = "✅ Valid" if item.get('validation_results', {}).get('overall_score', 0) > 0.5 else "⚠️ Issues"
            self.data_table.setItem(row, 6, QTableWidgetItem(status))
            
            # Actions
            view_btn = QPushButton("View Details")
            view_btn.clicked.connect(lambda checked, row=row: self.view_dataset_details(row))
            self.data_table.setCellWidget(row, 7, view_btn)
        
        self.data_display_stack.setCurrentIndex(0)
    
    def update_card_view(self, data):
        """Update card view with extracted data"""
        # Clear existing cards
        for i in reversed(range(self.data_card_layout.count())):
            child = self.data_card_layout.itemAt(i).widget()
            if child:
                child.deleteLater()
        
        # Create new cards
        for item in data:
            card = self.create_data_card(item)
            self.data_card_layout.addWidget(card)
        
        self.data_display_stack.setCurrentIndex(1)
    
    def create_data_card(self, item):
        """Create a data card widget"""
        card = QGroupBox()
        card.setStyleSheet("""
            QGroupBox {
                border: 2px solid #3498db;
                border-radius: 10px;
                margin: 5px;
                padding: 10px;
                background: #f8f9fa;
            }
            QGroupBox:hover {
                border-color: #2980b9;
                background: #e8f4fd;
            }
        """)
        
        layout = QVBoxLayout(card)
        
        # Title
        title_label = QLabel(item.get('title', 'N/A'))
        title_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        title_label.setWordWrap(True)
        layout.addWidget(title_label)
        
        # Provider and Type
        info_layout = QHBoxLayout()
        provider_label = QLabel(f"Provider: {item.get('provider', 'N/A')}")
        provider_label.setStyleSheet("color: #7f8c8d;")
        type_label = QLabel(f"Type: {item.get('data_type', 'N/A')}")
        type_label.setStyleSheet("color: #7f8c8d;")
        info_layout.addWidget(provider_label)
        info_layout.addWidget(type_label)
        layout.addLayout(info_layout)
        
        # Metrics
        metrics_layout = QHBoxLayout()
        confidence_label = QLabel(f"Confidence: {item.get('confidence_score', 0) * 100:.1f}%")
        confidence_label.setStyleSheet("color: #27ae60; font-weight: bold;")
        quality_label = QLabel(f"Quality: {item.get('quality_score', 0) * 100:.1f}%")
        quality_label.setStyleSheet("color: #f39c12; font-weight: bold;")
        metrics_layout.addWidget(confidence_label)
        metrics_layout.addWidget(quality_label)
        layout.addLayout(metrics_layout)
        
        # Tags
        tags = item.get('tags', [])
        if tags:
            tags_text = "Tags: " + ", ".join(tags[:5])
            tags_label = QLabel(tags_text)
            tags_label.setStyleSheet("color: #9b59b6; font-size: 11px;")
            tags_label.setWordWrap(True)
            layout.addWidget(tags_label)
        
        # View details button
        view_btn = QPushButton("View Details")
        view_btn.clicked.connect(lambda: self.view_dataset_details(item))
        view_btn.setStyleSheet("background: #3498db; color: white; border-radius: 5px; padding: 5px;")
        layout.addWidget(view_btn)
        
        return card
    
    def update_json_view(self, data):
        """Update JSON view with extracted data"""
        import json
        json_text = json.dumps(data, indent=2, default=str)
        self.data_json_view.setText(json_text)
        self.data_display_stack.setCurrentIndex(2)
    
    def update_statistics_view(self, data):
        """Update statistics view with extracted data"""
        if not data:
            return
        
        # Category distribution
        categories = {}
        providers = {}
        
        for item in data:
            # Count categories
            category = item.get('data_type', 'Unknown')
            categories[category] = categories.get(category, 0) + 1
            
            # Count providers
            provider = item.get('provider', 'Unknown')
            providers[provider] = providers.get(provider, 0) + 1
        
        # Update category list
        category_text = "Category Distribution:\n"
        for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(data)) * 100
            category_text += f"{category}: {count} ({percentage:.1f}%)\n"
        self.category_list.setText(category_text)
        
        # Update provider list
        provider_text = "Provider Distribution:\n"
        for provider, count in sorted(providers.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(data)) * 100
            provider_text += f"{provider}: {count} ({percentage:.1f}%)\n"
        self.provider_list.setText(provider_text)
        
        self.data_display_stack.setCurrentIndex(3)
    
    def change_data_view_mode(self, mode):
        """Change the data view mode"""
        with self.data_lock:
            current_data = self.extracted_data.copy()
        
        if current_data:
            self.refresh_data_view()
    
    def show_filter_dialog(self):
        """Show filter dialog for data"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Filter Data")
        dialog.setModal(True)
        layout = QVBoxLayout(dialog)
        
        form_layout = QFormLayout()
        
        # Filter by confidence
        min_confidence = QDoubleSpinBox()
        min_confidence.setRange(0, 1)
        min_confidence.setSingleStep(0.1)
        min_confidence.setValue(0.0)
        form_layout.addRow("Min Confidence:", min_confidence)
        
        # Filter by quality
        min_quality = QDoubleSpinBox()
        min_quality.setRange(0, 1)
        min_quality.setSingleStep(0.1)
        min_quality.setValue(0.0)
        form_layout.addRow("Min Quality:", min_quality)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        apply_btn = QPushButton("Apply Filter")
        cancel_btn = QPushButton("Cancel")
        
        apply_btn.clicked.connect(lambda: self.apply_filter(min_confidence.value(), min_quality.value(), dialog))
        cancel_btn.clicked.connect(dialog.reject)
        
        button_layout.addWidget(apply_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        dialog.exec()
    
    def apply_filter(self, min_confidence, min_quality, dialog):
        """Apply filter to data view"""
        with self.data_lock:
            all_data = self.extracted_data.copy()
        
        filtered_data = [
            item for item in all_data
            if item.get('confidence_score', 0) >= min_confidence and
               item.get('quality_score', 0) >= min_quality
        ]
        
        self.update_real_time_statistics(filtered_data)
        self.refresh_data_view()
        dialog.accept()
    
    def show_sort_dialog(self):
        """Show sort dialog for data"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Sort Data")
        dialog.setModal(True)
        layout = QVBoxLayout(dialog)
        
        # Sort options
        sort_combo = QComboBox()
        sort_combo.addItems(["Title", "Provider", "Confidence", "Quality", "Data Type"])
        layout.addWidget(QLabel("Sort by:"))
        layout.addWidget(sort_combo)
        
        # Sort direction
        direction_combo = QComboBox()
        direction_combo.addItems(["Ascending", "Descending"])
        layout.addWidget(QLabel("Direction:"))
        layout.addWidget(direction_combo)
        
        # Buttons
        button_layout = QHBoxLayout()
        apply_btn = QPushButton("Apply Sort")
        cancel_btn = QPushButton("Cancel")
        
        apply_btn.clicked.connect(lambda: self.apply_sort(sort_combo.currentText(), direction_combo.currentText(), dialog))
        cancel_btn.clicked.connect(dialog.reject)
        
        button_layout.addWidget(apply_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        dialog.exec()
    
    def apply_sort(self, sort_by, direction, dialog):
        """Apply sorting to data view"""
        with self.data_lock:
            data = self.extracted_data.copy()
        
        reverse = direction == "Descending"
        
        if sort_by == "Title":
            data.sort(key=lambda x: x.get('title', ''), reverse=reverse)
        elif sort_by == "Provider":
            data.sort(key=lambda x: x.get('provider', ''), reverse=reverse)
        elif sort_by == "Confidence":
            data.sort(key=lambda x: x.get('confidence_score', 0), reverse=reverse)
        elif sort_by == "Quality":
            data.sort(key=lambda x: x.get('quality_score', 0), reverse=reverse)
        elif sort_by == "Data Type":
            data.sort(key=lambda x: x.get('data_type', ''), reverse=reverse)
        
        self.extracted_data = data
        self.refresh_data_view()
        dialog.accept()
    
    def view_dataset_details(self, item_or_index):
        """View detailed information about a dataset"""
        if isinstance(item_or_index, int):
            # Index from table
            with self.data_lock:
                if item_or_index < len(self.extracted_data):
                    item = self.extracted_data[item_or_index]
                else:
                    return
        else:
            # Direct item
            item = item_or_index
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Dataset Details")
        dialog.setModal(True)
        dialog.resize(600, 500)
        
        layout = QVBoxLayout(dialog)
        
        # Create detailed view
        details_text = QTextEdit()
        details_text.setReadOnly(True)
        details_text.setStyleSheet("background: #f8f9fa; font-family: Consolas; font-size: 11px;")
        
        # Format detailed information
        details = f"""
DATASET DETAILS
{'='*50}

Title: {item.get('title', 'N/A')}
Provider: {item.get('provider', 'N/A')}
Data Type: {item.get('data_type', 'N/A')}
Confidence Score: {item.get('confidence_score', 0) * 100:.1f}%
Quality Score: {item.get('quality_score', 0) * 100:.1f}%

Description: {item.get('description', 'N/A')}

Tags: {', '.join(item.get('tags', []))}

SPATIAL COVERAGE:
{item.get('spatial_coverage', 'N/A')}

TEMPORAL COVERAGE:
{item.get('temporal_coverage', 'N/A')}

BANDS:
{json.dumps(item.get('bands', []), indent=2)}

ML CLASSIFICATION:
{json.dumps(item.get('ml_classification', {}), indent=2)}

VALIDATION RESULTS:
{json.dumps(item.get('validation_results', {}), indent=2)}

ENHANCED FEATURES:
{json.dumps(item.get('enhanced_features', {}), indent=2)}
"""
        
        details_text.setText(details)
        layout.addWidget(details_text)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.exec()
    
    def export_current_data(self):
        """Export current extracted data"""
        if not self.extracted_data:
            QMessageBox.information(self, "No Data", "No data available to export.")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Data", "extracted_data.json", "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                import json
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.extracted_data, f, indent=2, default=str)
                QMessageBox.information(self, "Success", f"Data exported to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export data: {str(e)}")
    
    def add_extracted_data(self, data_item):
        """Add extracted data to the real-time view"""
        with self.data_lock:
            self.extracted_data.append(data_item)
        
        # Update real-time statistics
        self.update_real_time_statistics(self.extracted_data)
        
        # Update current view if on data tab
        if self.tab_widget.currentIndex() == 1:  # Data view tab
            self.refresh_data_view()

    def show_crawl_summary(self):
        """Show a comprehensive crawl summary with enhanced analytics."""
        if not self.extracted_data:
            return
        
        # Calculate comprehensive statistics
        total_datasets = len(self.extracted_data)
        avg_confidence = sum(d.get('confidence_score', 0) for d in self.extracted_data) / total_datasets * 100
        avg_quality = sum(d.get('quality_score', 0) for d in self.extracted_data) / total_datasets * 100
        ml_classified = sum(1 for d in self.extracted_data if d.get('ml_classification'))
        
        # Data type distribution
        data_types = {}
        providers = {}
        for item in self.extracted_data:
            data_type = item.get('data_type', 'unknown')
            data_types[data_type] = data_types.get(data_type, 0) + 1
            provider = item.get('provider', 'unknown')
            providers[provider] = providers.get(provider, 0) + 1
        
        # Processing time
        elapsed_time = time.time() - self.start_time if hasattr(self, 'start_time') else 0
        
        summary = f"""
CRAWL SUMMARY REPORT
{'='*60}

📊 OVERVIEW:
Total Datasets Extracted: {total_datasets}
Processing Time: {elapsed_time:.1f} seconds
Average Processing Rate: {total_datasets / (elapsed_time / 60) if elapsed_time > 0 else 0:.1f} datasets/min

🎯 QUALITY METRICS:
Average Confidence Score: {avg_confidence:.1f}%
Average Quality Score: {avg_quality:.1f}%
ML Classified Datasets: {ml_classified} ({ml_classified/total_datasets*100:.1f}%)

📈 DATA TYPE DISTRIBUTION:
"""
        
        for data_type, count in sorted(data_types.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_datasets) * 100
            summary += f"• {data_type}: {count} ({percentage:.1f}%)\n"
        
        summary += f"""
🏢 PROVIDER DISTRIBUTION (Top 10):
"""
        
        for provider, count in sorted(providers.items(), key=lambda x: x[1], reverse=True)[:10]:
            percentage = (count / total_datasets) * 100
            summary += f"• {provider}: {count} ({percentage:.1f}%)\n"
        
        # Performance metrics
        if hasattr(self, 'performance_monitor'):
            app_metrics = self.performance_monitor.get_current_metrics()
            summary += f"""
⚡ PERFORMANCE METRICS:
Success Rate: {app_metrics.get('success_rate', 0):.1f}%
Error Rate: {app_metrics.get('error_rate', 0):.1f}%
Average Response Time: {app_metrics.get('avg_response_time', 0):.2f}s
Peak Memory Usage: {psutil.Process().memory_info().rss / 1024**2:.1f}MB

🕒 TIMESTAMP: {time.strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        self.summary_console.setPlainText(summary)

    def browse_file(self):
        """Browse for HTML file to crawl."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select HTML File", "", "HTML Files (*.html *.htm);;All Files (*)"
        )
        if file_path:
            self.file_path_edit.setText(file_path)
            self.crawl_btn.setEnabled(True)
            self.log_message(f"Selected file: {file_path}")
    
    def browse_output_directory(self):
        """Browse for output directory."""
        dir_path = QFileDialog.getExistingDirectory(
            self, "Select Output Directory", self.output_dir_edit.text()
        )
        if dir_path:
            self.output_dir_edit.setText(dir_path)
            self.log_message(f"Output directory set to: {dir_path}")
    
    def log_message(self, message):
        """Log message to console."""
        timestamp = time.strftime("%H:%M:%S")
        if hasattr(self, 'console') and self.console:
            self.console.append(f"[{timestamp}] {message}")
            self.console.ensureCursorVisible()
        else:
            print(f"[{timestamp}] {message}")  # Fallback to print
    
    def log_ml_classification(self, message):
        """Log ML classification message."""
        timestamp = time.strftime("%H:%M:%S")
        if hasattr(self, 'ml_console') and self.ml_console:
            self.ml_console.append(f"[{timestamp}] {message}")
            self.ml_console.ensureCursorVisible()
        else:
            print(f"[{timestamp}] ML: {message}")  # Fallback to print
    
    def log_validation(self, message):
        """Log validation message."""
        timestamp = time.strftime("%H:%M:%S")
        if hasattr(self, 'validation_console') and self.validation_console:
            self.validation_console.append(f"[{timestamp}] {message}")
            self.validation_console.ensureCursorVisible()
        else:
            print(f"[{timestamp}] VAL: {message}")  # Fallback to print
    
    def log_error(self, message):
        """Log error message."""
        timestamp = time.strftime("%H:%M:%S")
        if hasattr(self, 'error_console') and self.error_console:
            self.error_console.append(f"[{timestamp}] ERROR: {message}")
            self.error_console.ensureCursorVisible()
        else:
            print(f"[{timestamp}] ERROR: {message}")  # Fallback to print
    
    def clear_all_consoles(self):
        """Clear all console outputs."""
        self.console.clear()
        self.ml_console.clear()
        self.validation_console.clear()
        self.error_console.clear()
        self.summary_console.clear()
        self.performance_console.clear()
        if hasattr(self, 'health_console'):
            self.health_console.clear()
        if hasattr(self, 'data_json_view'):
            self.data_json_view.clear()
        
        # Reset counters
        self.error_count = 0
        self.warning_count = 0
        self.success_count = 0
        
        self.log_message("All consoles cleared and counters reset.")
    
    def open_dashboard(self):
        """Open analytics dashboard."""
        try:
            if hasattr(self, 'dashboard') and self.dashboard:
                self.log_message("Opening analytics dashboard...")
                # Dashboard functionality is now integrated into the main UI
                self.tab_widget.setCurrentIndex(0)  # Switch to data view
            else:
                self.log_message("Dashboard not available. Using integrated view.")
        except Exception as e:
            self.log_error(f"Failed to open dashboard: {e}")
    
    def edit_config(self):
        """Edit configuration."""
        try:
            config_file = "crawler_config.yaml"
            if os.path.exists(config_file):
                self.log_message(f"Opening configuration file: {config_file}")
                # You can implement a config editor here
                self.log_message("Configuration editing not yet implemented.")
            else:
                self.log_message("Configuration file not found.")
        except Exception as e:
            self.log_error(f"Failed to edit config: {e}")
    
    def test_features(self):
        """Test advanced features."""
        try:
            self.log_message("Testing advanced features...")
            
            # Test ML models
            if hasattr(self, 'nlp') and self.nlp:
                self.log_message("✅ spaCy model is working")
            else:
                self.log_message("❌ spaCy model not available")
            
            if hasattr(self, 'bert_classifier') and self.bert_classifier:
                self.log_message("✅ BERT model is working")
            else:
                self.log_message("❌ BERT model not available")
            
            # Test geocoding
            if hasattr(self, 'geocoder') and self.geocoder:
                self.log_message("✅ Geocoder is working")
            else:
                self.log_message("❌ Geocoder not available")
            
            # Test configuration
            if hasattr(self, 'config') and self.config:
                self.log_message("✅ Configuration loaded")
            else:
                self.log_message("❌ Configuration not available")
            
            self.log_message("Feature testing completed.")
            
        except Exception as e:
            self.log_error(f"Feature testing failed: {e}")
    
    def update_output_directories(self, base_dir):
        """Update output directories based on base directory."""
        try:
            # Create subdirectories
            subdirs = ['cache', 'extracted_data', 'thumbnails', 'ml_models', 'logs']
            for subdir in subdirs:
                full_path = os.path.join(base_dir, subdir)
                os.makedirs(full_path, exist_ok=True)
            
            self.log_message(f"Output directories updated: {base_dir}")
        except Exception as e:
            self.log_error(f"Failed to update output directories: {e}")
    
    def save_results(self, results):
        """Save extracted results."""
        try:
            if not results:
                return
            
            output_dir = self.output_dir_edit.text()
            os.makedirs(output_dir, exist_ok=True)
            
            # Save as JSON
            json_file = os.path.join(output_dir, f"extracted_data_{int(time.time())}.json")
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, default=str)
            
            self.log_message(f"Results saved to: {json_file}")
            
        except Exception as e:
            self.log_error(f"Failed to save results: {e}")

    def crawl_finished(self):
        """Handle crawl completion."""
        self.crawl_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.status.setText("✅ Crawling completed!")
        self.progress.setValue(100)
        
        # Enable export button if data is available
        if hasattr(self, 'extracted_data') and self.extracted_data:
            self.export_btn.setEnabled(True)
            self.log_message(f"Crawling completed! Extracted {len(self.extracted_data)} datasets.")
            
            # Show summary
            self.show_crawl_summary()
        else:
            self.log_message("Crawling completed but no data was extracted.")
        
        # Stop UI updates
        self.timer.stop()
        
    def stop_crawl(self):
        """Stop the crawling process."""
        self.stop_requested = True
        self.log_message("Stopping crawler... Please wait for current operation to complete.")
        self.status.setText("⏹️ Stopping...")
    
    def export_current_data(self):
        """Export current extracted data."""
        if not self.extracted_data:
            QMessageBox.information(self, "No Data", "No data available to export.")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Data", "extracted_data.json", "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.extracted_data, f, indent=2, default=str)
                QMessageBox.information(self, "Success", f"Data exported to {file_path}")
                self.log_message(f"Data exported to: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export data: {str(e)}")
                self.log_error(f"Failed to export data: {e}")
    
    def add_extracted_data(self, data_item):
        """Add extracted data to the real-time view."""
        with self.data_lock:
            self.extracted_data.append(data_item)
        
        # Update real-time statistics
        self.update_real_time_statistics(self.extracted_data)
        
        # Update current view if on data tab
        if self.tab_widget.currentIndex() == 0:  # Data view tab
            self.refresh_data_view()
    
    def refresh_data_view(self):
        """Refresh the data view with current extracted data."""
        with self.data_lock:
            current_data = self.extracted_data.copy()
        
        if not current_data:
            self.log_message("No data available for viewing yet.")
            return
        
        # Update statistics
        self.update_real_time_statistics(current_data)
        
        # Update view based on current mode
        if hasattr(self, 'data_view_mode'):
            view_mode = self.data_view_mode.currentText()
            if view_mode == "Table View":
                self.update_table_view(current_data)
            elif view_mode == "Card View":
                self.update_card_view(current_data)
            elif view_mode == "JSON View":
                self.update_json_view(current_data)
            elif view_mode == "Statistics View":
                self.update_statistics_view(current_data)
    
    def update_table_view(self, data):
        """Update table view with extracted data."""
        if not hasattr(self, 'data_table'):
            return
        
        self.data_table.setRowCount(len(data))
        
        for row, item in enumerate(data):
            # Title
            title = item.get('title', 'N/A')[:50] + "..." if len(item.get('title', '')) > 50 else item.get('title', 'N/A')
            self.data_table.setItem(row, 0, QTableWidgetItem(title))
            
            # Provider
            provider = item.get('provider', 'N/A')
            self.data_table.setItem(row, 1, QTableWidgetItem(provider))
            
            # Type
            data_type = item.get('data_type', 'N/A')
            self.data_table.setItem(row, 2, QTableWidgetItem(data_type))
            
            # Confidence
            confidence = f"{item.get('confidence_score', 0) * 100:.1f}%"
            self.data_table.setItem(row, 3, QTableWidgetItem(confidence))
            
            # Quality
            quality = f"{item.get('quality_score', 0) * 100:.1f}%"
            self.data_table.setItem(row, 4, QTableWidgetItem(quality))
            
            # Tags
            tags = ", ".join(item.get('tags', [])[:3])
            self.data_table.setItem(row, 5, QTableWidgetItem(tags))
            
            # Status
            status = "✅ Valid" if item.get('validation_results', {}).get('overall_score', 0) > 0.5 else "⚠️ Issues"
            self.data_table.setItem(row, 6, QTableWidgetItem(status))
            
            # Actions
            view_btn = QPushButton("View Details")
            view_btn.clicked.connect(lambda checked, row=row: self.view_dataset_details(row))
            self.data_table.setCellWidget(row, 7, view_btn)
        
        if hasattr(self, 'data_display_stack'):
            self.data_display_stack.setCurrentIndex(0)
    
    def update_card_view(self, data):
        """Update card view with extracted data."""
        if not hasattr(self, 'data_card_layout'):
            return
        
        # Clear existing cards
        for i in reversed(range(self.data_card_layout.count())):
            child = self.data_card_layout.itemAt(i).widget()
            if child:
                child.deleteLater()
        
        # Create new cards
        for item in data:
            card = self.create_data_card(item)
            self.data_card_layout.addWidget(card)
        
        if hasattr(self, 'data_display_stack'):
            self.data_display_stack.setCurrentIndex(1)
    
    def create_data_card(self, item):
        """Create a data card widget."""
        card = QGroupBox()
        card.setStyleSheet("""
            QGroupBox {
                border: 2px solid #3498db;
                border-radius: 10px;
                margin: 5px;
                padding: 10px;
                background: #f8f9fa;
            }
            QGroupBox:hover {
                border-color: #2980b9;
                background: #e8f4fd;
            }
        """)
        
        layout = QVBoxLayout(card)
        
        # Title
        title_label = QLabel(item.get('title', 'N/A'))
        title_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        title_label.setWordWrap(True)
        layout.addWidget(title_label)
        
        # Provider and Type
        info_layout = QHBoxLayout()
        provider_label = QLabel(f"Provider: {item.get('provider', 'N/A')}")
        provider_label.setStyleSheet("color: #7f8c8d;")
        type_label = QLabel(f"Type: {item.get('data_type', 'N/A')}")
        type_label.setStyleSheet("color: #7f8c8d;")
        info_layout.addWidget(provider_label)
        info_layout.addWidget(type_label)
        layout.addLayout(info_layout)
        
        # Metrics
        metrics_layout = QHBoxLayout()
        confidence_label = QLabel(f"Confidence: {item.get('confidence_score', 0) * 100:.1f}%")
        confidence_label.setStyleSheet("color: #27ae60; font-weight: bold;")
        quality_label = QLabel(f"Quality: {item.get('quality_score', 0) * 100:.1f}%")
        quality_label.setStyleSheet("color: #f39c12; font-weight: bold;")
        metrics_layout.addWidget(confidence_label)
        metrics_layout.addWidget(quality_label)
        layout.addLayout(metrics_layout)
        
        # Tags
        tags = item.get('tags', [])
        if tags:
            tags_text = "Tags: " + ", ".join(tags[:5])
            tags_label = QLabel(tags_text)
            tags_label.setStyleSheet("color: #9b59b6; font-size: 11px;")
            tags_label.setWordWrap(True)
            layout.addWidget(tags_label)
        
        # View details button
        view_btn = QPushButton("View Details")
        view_btn.clicked.connect(lambda: self.view_dataset_details(item))
        view_btn.setStyleSheet("background: #3498db; color: white; border-radius: 5px; padding: 5px;")
        layout.addWidget(view_btn)
        
        return card
    
    def update_json_view(self, data):
        """Update JSON view with extracted data."""
        if not hasattr(self, 'data_json_view'):
            return
        
        json_text = json.dumps(data, indent=2, default=str)
        self.data_json_view.setText(json_text)
        
        if hasattr(self, 'data_display_stack'):
            self.data_display_stack.setCurrentIndex(2)
    
    def update_statistics_view(self, data):
        """Update statistics view with extracted data."""
        if not data or not hasattr(self, 'category_list'):
            return
        
        # Category distribution
        categories = {}
        providers = {}
        
        for item in data:
            # Count categories
            category = item.get('data_type', 'Unknown')
            categories[category] = categories.get(category, 0) + 1
            
            # Count providers
            provider = item.get('provider', 'Unknown')
            providers[provider] = providers.get(provider, 0) + 1
        
        # Update category list
        category_text = "Category Distribution:\n"
        for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(data)) * 100
            category_text += f"{category}: {count} ({percentage:.1f}%)\n"
        self.category_list.setText(category_text)
        
        # Update provider list
        provider_text = "Provider Distribution:\n"
        for provider, count in sorted(providers.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(data)) * 100
            provider_text += f"{provider}: {count} ({percentage:.1f}%)\n"
        self.provider_list.setText(provider_text)
        
        if hasattr(self, 'data_display_stack'):
            self.data_display_stack.setCurrentIndex(3)
    
    def view_dataset_details(self, item_or_index):
        """View detailed information about a dataset."""
        if isinstance(item_or_index, int):
            # Index from table
            with self.data_lock:
                if item_or_index < len(self.extracted_data):
                    item = self.extracted_data[item_or_index]
                else:
                    return
        else:
            # Direct item
            item = item_or_index
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Dataset Details")
        dialog.setModal(True)
        dialog.resize(600, 500)
        
        layout = QVBoxLayout(dialog)
        
        # Create detailed view
        details_text = QTextEdit()
        details_text.setReadOnly(True)
        details_text.setStyleSheet("background: #f8f9fa; font-family: Consolas; font-size: 11px;")
        
        # Format detailed information
        details = f"""
DATASET DETAILS
{'='*50}

Title: {item.get('title', 'N/A')}
Provider: {item.get('provider', 'N/A')}
Data Type: {item.get('data_type', 'N/A')}
Confidence Score: {item.get('confidence_score', 0) * 100:.1f}%
Quality Score: {item.get('quality_score', 0) * 100:.1f}%

Description: {item.get('description', 'N/A')}

Tags: {', '.join(item.get('tags', []))}

SPATIAL COVERAGE:
{item.get('spatial_coverage', 'N/A')}

TEMPORAL COVERAGE:
{item.get('temporal_coverage', 'N/A')}

BANDS:
{json.dumps(item.get('bands', []), indent=2)}

ML CLASSIFICATION:
{json.dumps(item.get('ml_classification', {}), indent=2)}

VALIDATION RESULTS:
{json.dumps(item.get('validation_results', {}), indent=2)}

ENHANCED FEATURES:
{json.dumps(item.get('enhanced_features', {}), indent=2)}
"""
        
        details_text.setText(details)
        layout.addWidget(details_text)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.exec()

    def show_health_report(self):
        """Show comprehensive system health report."""
        try:
            health_report = self.get_system_health_report()
            self.health_console.setPlainText(health_report)
            
            # Switch to health tab
            self.tab_widget.setCurrentIndex(7)  # Health tab index
            
            self.log_message("🏥 Health report generated")
            
        except Exception as e:
            self.log_error(f"Failed to generate health report: {e}")

    def show_optimization_dialog(self):
        """Show system optimization dialog."""
        try:
            dialog = QDialog(self)
            dialog.setWindowTitle("System Optimization")
            dialog.setModal(True)
            dialog.resize(500, 400)
            
            layout = QVBoxLayout(dialog)
            
            # Current system status
            status_group = QGroupBox("Current System Status")
            status_layout = QVBoxLayout()
            
            cpu_percent = psutil.cpu_percent()
            memory_percent = psutil.virtual_memory().percent
            
            status_text = f"""
CPU Usage: {cpu_percent:.1f}%
Memory Usage: {memory_percent:.1f}%
Optimization Level: {self.optimization_level.upper()}
Low Power Mode: {'Enabled' if self.low_power_mode else 'Disabled'}
Error Count: {self.error_count}
Success Count: {self.success_count}
"""
            
            status_label = QLabel(status_text)
            status_label.setStyleSheet("font-family: monospace; font-size: 10px;")
            status_layout.addWidget(status_label)
            status_group.setLayout(status_layout)
            layout.addWidget(status_group)
            
            # Optimization options
            options_group = QGroupBox("Optimization Options")
            options_layout = QVBoxLayout()
            
            # Optimization level selection
            level_layout = QHBoxLayout()
            level_layout.addWidget(QLabel("Optimization Level:"))
            level_combo = QComboBox()
            level_combo.addItems(["Balanced", "Performance", "Power Save"])
            level_combo.setCurrentText(self.optimization_level.title())
            level_layout.addWidget(level_combo)
            options_layout.addLayout(level_layout)
            
            # Auto-optimization checkbox
            auto_optimize = QCheckBox("Enable auto-optimization based on system load")
            auto_optimize.setChecked(True)
            options_layout.addWidget(auto_optimize)
            
            # Memory management
            memory_layout = QHBoxLayout()
            memory_layout.addWidget(QLabel("Max Cache Size:"))
            cache_slider = QSlider(Qt.Orientation.Horizontal)
            cache_slider.setRange(100, 2000)
            cache_slider.setValue(500 if self.low_power_mode else 1000)
            cache_label = QLabel(f"{cache_slider.value()} items")
            cache_slider.valueChanged.connect(lambda v: cache_label.setText(f"{v} items"))
            memory_layout.addWidget(cache_slider)
            memory_layout.addWidget(cache_label)
            options_layout.addLayout(memory_layout)
            
            options_group.setLayout(options_layout)
            layout.addWidget(options_group)
            
            # Recommendations
            rec_group = QGroupBox("Recommendations")
            rec_layout = QVBoxLayout()
            
            recommendations = self.get_optimization_recommendations()
            rec_label = QLabel(recommendations)
            rec_label.setWordWrap(True)
            rec_layout.addWidget(rec_label)
            rec_group.setLayout(rec_layout)
            layout.addWidget(rec_group)
            
            # Buttons
            button_layout = QHBoxLayout()
            
            apply_btn = QPushButton("Apply Optimizations")
            apply_btn.clicked.connect(lambda: self.apply_optimizations(
                level_combo.currentText().lower().replace(" ", "_"),
                auto_optimize.isChecked(),
                cache_slider.value(),
                dialog
            ))
            
            cancel_btn = QPushButton("Cancel")
            cancel_btn.clicked.connect(dialog.reject)
            
            button_layout.addWidget(apply_btn)
            button_layout.addWidget(cancel_btn)
            layout.addLayout(button_layout)
            
            dialog.exec()
            
        except Exception as e:
            self.log_error(f"Failed to show optimization dialog: {e}")
    
    def apply_optimizations(self, level, auto_optimize, cache_size, dialog):
        """Apply selected optimizations."""
        try:
            # Update optimization level
            self.optimization_level = level
            
            # Update cache size
            if hasattr(self, 'config') and self.config:
                self.config['performance']['memory']['max_cache_size'] = cache_size
            
            # Apply optimizations based on level
            if level == "power_save":
                self.timer.setInterval(300)
                if hasattr(self, 'delay_slider'):
                    self.delay_slider.setValue(6)  # 3 seconds
                if hasattr(self, 'concurrent_slider'):
                    self.concurrent_slider.setValue(1)
            elif level == "performance":
                self.timer.setInterval(50)
                if hasattr(self, 'delay_slider'):
                    self.delay_slider.setValue(2)  # 1 second
                if hasattr(self, 'concurrent_slider'):
                    self.concurrent_slider.setValue(8)
            else:  # balanced
                self.timer.setInterval(100)
                if hasattr(self, 'delay_slider'):
                    self.delay_slider.setValue(4)  # 2 seconds
                if hasattr(self, 'concurrent_slider'):
                    self.concurrent_slider.setValue(4)
            
            self.log_message(f"✅ Applied {level} optimizations")
            self.log_message(f"📊 Cache size: {cache_size} items")
            
            dialog.accept()
            
        except Exception as e:
            self.log_error(f"Failed to apply optimizations: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = EnhancedCrawlerUI()
    win.show()
    sys.exit(app.exec()) 