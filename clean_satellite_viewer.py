import sys
import os
import json
import glob
import re
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QLineEdit, QScrollArea, QFrame, QSplitter, QListWidget, 
    QListWidgetItem, QTextBrowser, QComboBox, QGroupBox
)
from PySide6.QtCore import Qt, QThread, QObject, Signal, QSize
from PySide6.QtGui import QFont, QPixmap, QTextOption

class DatasetProcessor:
    """Process and clean dataset information"""
    
    @staticmethod
    def clean_title(title):
        """Extract a clean, meaningful title from the raw title"""
        if not title:
            return "Untitled Dataset"
        
        # Remove common suffixes and prefixes
        title = re.sub(r'bookmark_border.*$', '', title, flags=re.IGNORECASE)
        title = re.sub(r'^.*?Dataset Availability', '', title, flags=re.IGNORECASE)
        title = re.sub(r'^.*?Dataset Provider', '', title, flags=re.IGNORECASE)
        title = re.sub(r'^.*?Earth Engine Snippet', '', title, flags=re.IGNORECASE)
        
        # Extract meaningful parts
        parts = title.split()
        if len(parts) > 10:
            # Take first meaningful part
            meaningful_parts = []
            for part in parts[:10]:
                if len(part) > 2 and not part.isdigit():
                    meaningful_parts.append(part)
            title = ' '.join(meaningful_parts)
        
        # Clean up special characters
        title = re.sub(r'[^\w\s\-\.]', '', title)
        title = title.strip()
        
        if len(title) > 80:
            title = title[:80] + "..."
        
        return title if title else "Untitled Dataset"
    
    @staticmethod
    def extract_provider(description):
        """Extract provider information from description"""
        if not description:
            return "Unknown"
        
        # Look for common providers
        providers = [
            "USGS", "NASA", "ESA", "NOAA", "USDA", "EPA", "JAXA", "CNES", 
            "Copernicus", "Sentinel", "Landsat", "MODIS", "GOES", "VIIRS"
        ]
        
        for provider in providers:
            if provider.lower() in description.lower():
                return provider
        
        # Look for "Dataset Provider" pattern
        match = re.search(r'Dataset Provider\s*([^\n]+)', description, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        
        return "Unknown"
    
    @staticmethod
    def extract_tags(description, title):
        """Extract meaningful tags from description and title"""
        tags = []
        
        # Common satellite and sensor tags
        satellite_tags = [
            "landsat", "sentinel", "modis", "goes", "viirs", "aster", "alos", 
            "planet", "rapideye", "worldview", "pleiades", "spot", "quickbird"
        ]
        
        # Category tags
        category_tags = [
            "satellite", "climate", "weather", "temperature", "precipitation",
            "land", "cover", "vegetation", "forest", "agriculture", "crop",
            "water", "hydrology", "river", "flood", "ocean", "marine",
            "population", "census", "demographic", "urban", "settlement",
            "elevation", "topography", "dem", "terrain", "soil", "geology",
            "atmosphere", "air", "pollution", "aerosol", "cloud", "snow",
            "ice", "glacier", "fire", "burn", "wildfire"
        ]
        
        # Process tags
        text = (title + " " + description).lower()
        
        # Add satellite tags
        for tag in satellite_tags:
            if tag in text:
                tags.append(tag.title())
        
        # Add category tags
        for tag in category_tags:
            if tag in text:
                tags.append(tag.title())
        
        # Remove duplicates and limit
        tags = list(set(tags))[:8]
        return tags
    
    @staticmethod
    def extract_key_metadata(metadata):
        """Extract key metadata fields"""
        if not metadata:
            return {}
        
        key_fields = [
            "DATE_ACQUIRED", "CLOUD_COVER", "SPATIAL_RESOLUTION", "TEMPORAL_RESOLUTION",
            "COVERAGE", "ACCURACY", "PROVIDER", "SENSOR", "PLATFORM", "BANDS",
            "WAVELENGTH", "REVISIT_INTERVAL", "COLLECTION", "VERSION", "TIER"
        ]
        
        extracted = {}
        for field in key_fields:
            if field in metadata:
                extracted[field] = metadata[field]
        
        return extracted
    
    @staticmethod
    def extract_date_range(description):
        """Extract date range from description"""
        if not description:
            return None
        
        # Look for date patterns
        date_pattern = r'(\d{4}-\d{2}-\d{2})[T\s](\d{2}:\d{2}:\d{2})[Z\s]–(\d{4}-\d{2}-\d{2})[T\s](\d{2}:\d{2}:\d{2})'
        match = re.search(date_pattern, description)
        
        if match:
            start_date = match.group(1)
            end_date = match.group(3)
            return f"{start_date} to {end_date}"
        
        return None
    
    @staticmethod
    def extract_spatial_coverage(description):
        """Extract spatial coverage from description"""
        if not description:
            return None
        
        # Look for coordinate patterns
        coord_pattern = r'(-?\d+\.?\d*)\s+(-?\d+\.?\d*)\s+(-?\d+\.?\d*)\s+(-?\d+\.?\d*)'
        match = re.search(coord_pattern, description)
        
        if match:
            coords = [float(match.group(i)) for i in range(1, 5)]
            return f"Lat: {coords[0]:.2f} to {coords[2]:.2f}, Lon: {coords[1]:.2f} to {coords[3]:.2f}"
        
        return None

    @staticmethod
    def parse_description(description):
        """Parse and categorize description into sections."""
        if not description:
            return {
                'provider': '',
                'snippet': '',
                'tags': [],
                'date_range': '',
                'bands': '',
                'terms_of_use': '',
                'main': '',
            }
        # Remove newlines for easier regex
        desc = description.replace('\n', ' ')
        # Provider
        provider = ''
        match = re.search(r'Dataset Provider([A-Za-z0-9 /-]+)', desc)
        if match:
            provider = match.group(1).strip()
        # Earth Engine Snippet
        snippet = ''
        match = re.search(r'Earth Engine Snippet(ee\.[^\s]+)', desc)
        if match:
            snippet = match.group(1).strip()
        # Tags
        tags = []
        match = re.search(r'Tags([a-z0-9\- ]+)', desc, re.IGNORECASE)
        if match:
            tags = [t.strip().title() for t in re.split(r'[^a-z0-9\-]+', match.group(1), flags=re.IGNORECASE) if t.strip()]
        # Date Range
        date_range = ''
        match = re.search(r'Dataset Availability([0-9TZ: \-–]+)', desc)
        if match:
            date_range = match.group(1).replace('T', ' ').replace('Z', '').replace('–', ' to ').strip()
        # Bands
        bands = ''
        match = re.search(r'Bands([^T]+)Terms of Use', desc)
        if match:
            bands = match.group(1).strip()
        # Terms of Use
        terms = ''
        match = re.search(r'Terms of Use([^M]+)More', desc)
        if match:
            terms = match.group(1).strip()
        # Main description: after 'More' or after 'Terms of UseMore'
        main = ''
        match = re.search(r'More(.*)', desc)
        if match:
            main = match.group(1).strip()
        if not main:
            # fallback: first long sentence after all boilerplate
            main = re.sub(r'(Dataset Availability|Dataset Provider|Earth Engine Snippet|Tags|Bands|Terms of Use|More)[^\.]+', '', desc)
            main = main.strip()
        # Clean up main
        main = re.sub(r'\s+', ' ', main)
        return {
            'provider': provider,
            'snippet': snippet,
            'tags': tags,
            'date_range': date_range,
            'bands': bands,
            'terms_of_use': terms,
            'main': main,
        }

class DatasetLoader(QObject):
    datasets_loaded = Signal(list)
    
    def __init__(self, data_dir):
        super().__init__()
        self.data_dir = data_dir
    
    def load_datasets(self):
        """Load and process all JSON datasets"""
        try:
            json_files = glob.glob(os.path.join(self.data_dir, "*.json"))
            datasets = []
            
            for json_file in json_files:
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        raw_dataset = json.load(f)
                    
                    # Process the dataset
                    processed_dataset = self.process_dataset(raw_dataset, json_file)
                    datasets.append(processed_dataset)
                    
                except Exception as e:
                    print(f"Error loading {json_file}: {e}")
                    continue
            
            self.datasets_loaded.emit(datasets)
            
        except Exception as e:
            print(f"Error loading datasets: {e}")
            self.datasets_loaded.emit([])
    
    def process_dataset(self, raw_dataset, file_path):
        """Process a single dataset to extract meaningful information"""
        # Extract basic info
        raw_title = raw_dataset.get('title', '')
        description = raw_dataset.get('description', '')
        
        # Process the data
        clean_title = DatasetProcessor.clean_title(raw_title)
        provider = DatasetProcessor.extract_provider(description)
        tags = DatasetProcessor.extract_tags(description, raw_title)
        key_metadata = DatasetProcessor.extract_key_metadata(raw_dataset.get('metadata', {}))
        date_range = DatasetProcessor.extract_date_range(description)
        spatial_coverage = DatasetProcessor.extract_spatial_coverage(description)
        
        parsed = DatasetProcessor.parse_description(description)

        # Create processed dataset
        processed_dataset = {
            'original_title': raw_title,
            'title': clean_title,
            'description': parsed['main'],
            'provider': parsed['provider'] or provider,
            'snippet': parsed['snippet'],
            'tags': list(set(tags + parsed['tags'])),
            'url': raw_dataset.get('url', ''),
            'file_path': file_path,
            'thumbnail_path': raw_dataset.get('thumbnail_path', ''),
            'date_range': parsed['date_range'] or date_range,
            'spatial_coverage': spatial_coverage,
            'key_metadata': key_metadata,
            'raw_metadata': raw_dataset.get('metadata', {}),
            'dataset_id': self.extract_dataset_id(raw_dataset.get('url', '')),
            'bands': parsed['bands'],
            'terms_of_use': parsed['terms_of_use'],
        }
        
        return processed_dataset
    
    def extract_clean_description(self, description):
        """Extract a clean description"""
        if not description:
            return "No description available"
        
        # Remove HTML-like content and excessive whitespace
        description = re.sub(r'<[^>]+>', '', description)
        description = re.sub(r'\s+', ' ', description)
        
        # Take first meaningful paragraph
        paragraphs = description.split('\n')
        for para in paragraphs:
            para = para.strip()
            if len(para) > 50 and not para.startswith('Dataset'):
                return para[:500] + "..." if len(para) > 500 else para
        
        return description[:300] + "..." if len(description) > 300 else description
    
    def extract_dataset_id(self, url):
        """Extract dataset ID from URL"""
        if not url:
            return "unknown"
        
        # Extract catalog ID from URL
        match = re.search(r'/catalog/([^/]+)', url)
        if match:
            return match.group(1)
        
        return "unknown"

class CleanSatelliteViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.datasets = []
        self.filtered_datasets = []
        self.loader_thread = None
        self.loader_worker = None
        self.setup_ui()
        self.setup_styles()
        self.load_datasets()
    
    def setup_ui(self):
        self.setWindowTitle("Satellite Dataset Viewer")
        self.resize(1600, 1000)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout - minimal spacing
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Compact header
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)
        header_layout.setContentsMargins(16, 8, 16, 8)
        
        title_label = QLabel("🛰️ Satellite Datasets")
        title_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #2c3e50;")
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search datasets...")
        self.search_input.textChanged.connect(self.filter_datasets)
        self.search_input.setMaximumWidth(320)
        self.search_input.setMinimumHeight(32)
        
        self.category_combo = QComboBox()
        self.category_combo.addItems(["All", "Satellite", "Climate", "Land", "Water", "Population", "Elevation"])
        self.category_combo.currentTextChanged.connect(self.filter_datasets)
        self.category_combo.setMaximumWidth(140)
        self.category_combo.setMinimumHeight(32)
        
        self.stats_label = QLabel("Loading...")
        self.stats_label.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        
        header_layout.addWidget(title_label)
        header_layout.addSpacing(16)
        header_layout.addWidget(self.search_input)
        header_layout.addWidget(self.category_combo)
        header_layout.addStretch()
        header_layout.addWidget(self.stats_label)
        
        main_layout.addLayout(header_layout)
        
        # Main splitter - maximize space for content
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_splitter.setHandleWidth(1)
        
        # Left panel - Dataset list (compact)
        self.dataset_list = QListWidget()
        self.dataset_list.currentItemChanged.connect(self.on_dataset_selected)
        self.dataset_list.setMinimumWidth(380)
        self.dataset_list.setMaximumWidth(420)
        self.dataset_list.setStyleSheet('''
            QListWidget {
                border-right: 1px solid #e0e0e0;
                background: #fafbfc;
                font-size: 13px;
            }
            QListWidget::item {
                padding: 10px 8px 6px 16px;
                border-bottom: 1px solid #f1f3f4;
                background: #fafbfc;
            }
            QListWidget::item:selected {
                background: #e3f0fa;
                color: #1a232a;
                border-left: 4px solid #3498db;
                font-weight: bold;
            }
            QListWidget::item:alternate {
                background: #f5f7fa;
            }
        ''')
        self.dataset_list.setAlternatingRowColors(True)
        
        # Right panel - Details (maximize space)
        self.details_content = QTextBrowser()
        self.details_content.setOpenExternalLinks(True)
        self.details_content.setStyleSheet('''
            QTextBrowser {
                background: #f7f9fa;
                border: none;
                font-size: 13px;
                color: #222;
                padding: 24px 32px 24px 32px;
            }
        ''')
        
        self.main_splitter.addWidget(self.dataset_list)
        self.main_splitter.addWidget(self.details_content)
        self.main_splitter.setSizes([400, 1200])
        main_layout.addWidget(self.main_splitter)
    
    def setup_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
            }
            QLineEdit {
                padding: 4px 8px;
                border: 1px solid #dee2e6;
                border-radius: 3px;
                background-color: white;
                font-size: 11px;
                color: #2c3e50;
            }
            QLineEdit:focus {
                border: 1px solid #3498db;
            }
            QComboBox {
                padding: 4px 8px;
                border: 1px solid #dee2e6;
                border-radius: 3px;
                background-color: white;
                color: #2c3e50;
                font-size: 11px;
            }
            QComboBox:focus {
                border: 1px solid #3498db;
            }
            QListWidget {
                border: 1px solid #dee2e6;
                border-radius: 3px;
                background-color: white;
                font-size: 11px;
                color: #2c3e50;
                outline: none;
                padding: 0px;
            }
            QListWidget::item {
                padding: 6px 8px;
                border-bottom: 1px solid #f1f3f4;
                background-color: white;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #ecf0f1;
            }
            QTextBrowser {
                border: 1px solid #dee2e6;
                border-radius: 3px;
                background-color: white;
                font-size: 11px;
                color: #2c3e50;
                padding: 8px;
            }
            QTextBrowser a {
                color: #3498db;
                text-decoration: underline;
            }
            QTextBrowser a:hover {
                color: #2980b9;
            }
        """)
    
    def load_datasets(self):
        """Load datasets from the extracted_data directory"""
        data_dir = os.path.join(os.path.dirname(__file__), "extracted_data")
        
        if not os.path.exists(data_dir):
            self.stats_label.setText("No data directory found")
            return
        
        # Load in separate thread
        self.loader_worker = DatasetLoader(data_dir)
        self.loader_thread = QThread()
        self.loader_worker.moveToThread(self.loader_thread)
        
        # Connect signals
        self.loader_worker.datasets_loaded.connect(self.on_datasets_loaded)
        
        # Start loading
        self.loader_thread.started.connect(self.loader_worker.load_datasets)
        self.loader_thread.start()
    
    def on_datasets_loaded(self, datasets):
        self.datasets = datasets
        self.filtered_datasets = datasets.copy()
        
        self.stats_label.setText(f"{len(datasets)} datasets")
        self.update_dataset_list()
        self.filter_datasets()
    
    def filter_datasets(self):
        search_text = self.search_input.text().lower()
        category_filter = self.category_combo.currentText()
        
        self.filtered_datasets = []
        for dataset in self.datasets:
            # Search filter
            if search_text:
                title_match = dataset.get('title', '').lower().find(search_text) != -1
                desc_match = dataset.get('description', '').lower().find(search_text) != -1
                tags_match = any(search_text in tag.lower() for tag in dataset.get('tags', []))
                provider_match = dataset.get('provider', '').lower().find(search_text) != -1
                if not (title_match or desc_match or tags_match or provider_match):
                    continue
            
            # Category filter
            if category_filter != "All":
                has_matching_category = False
                tags_lower = [tag.lower() for tag in dataset.get('tags', [])]
                title_lower = dataset.get('title', '').lower()
                
                if category_filter == "Satellite" and any(word in title_lower for word in ['landsat', 'sentinel', 'modis', 'satellite']):
                    has_matching_category = True
                elif category_filter == "Climate" and any(word in title_lower for word in ['climate', 'weather', 'temperature', 'precipitation']):
                    has_matching_category = True
                elif category_filter == "Land" and any(word in title_lower for word in ['land', 'cover', 'vegetation', 'forest']):
                    has_matching_category = True
                elif category_filter == "Water" and any(word in title_lower for word in ['water', 'hydrology', 'river', 'flood']):
                    has_matching_category = True
                elif category_filter == "Population" and any(word in title_lower for word in ['population', 'census', 'demographic']):
                    has_matching_category = True
                elif category_filter == "Elevation" and any(word in title_lower for word in ['elevation', 'dem', 'topography']):
                    has_matching_category = True
                
                if not has_matching_category:
                    continue
            
            self.filtered_datasets.append(dataset)
        
        self.update_dataset_list()
        self.stats_label.setText(f"{len(self.datasets)} total, {len(self.filtered_datasets)} filtered")
    
    def update_dataset_list(self):
        self.dataset_list.clear()
        for dataset in self.filtered_datasets:
            title = dataset.get('title', 'Untitled Dataset')
            provider = dataset.get('provider', 'Unknown')
            tags = dataset.get('tags', [])
            tag_str = f"<span style='color:#3498db;'>{tags[0]}</span>" if tags else ""
            # Compact display text with provider and a key tag
            display_text = f"<b>{title}</b><br><span style='font-size:11px;color:#888;'>{provider}</span>"
            if tag_str:
                display_text += f"<br>{tag_str}"
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, dataset)
            item.setTextAlignment(Qt.AlignmentFlag.AlignLeft)
            item.setSizeHint(QSize(380, 48))
            item.setData(Qt.ItemDataRole.DisplayRole, "")  # We'll use setItemWidget for rich text
            self.dataset_list.addItem(item)
            # Use a QLabel for rich text in the list
            label = QLabel(display_text)
            label.setTextFormat(Qt.TextFormat.RichText)
            label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            label.setStyleSheet("padding:0 0 0 0;")
            self.dataset_list.setItemWidget(item, label)
    
    def on_dataset_selected(self, current, previous):
        if not current:
            self.details_content.clear()
            return
        
        dataset = current.data(Qt.ItemDataRole.UserRole)
        self.display_dataset_details(dataset)
    
    def display_dataset_details(self, dataset):
        content = []
        title = dataset.get('title', 'Untitled Dataset')
        provider = dataset.get('provider', 'Unknown')
        thumbnail_path = dataset.get('thumbnail_path')
        if thumbnail_path and os.path.exists(thumbnail_path):
            content.append(f"<div style='display:flex;align-items:center;'><img src='file:///{thumbnail_path.replace(os.sep, '/')}' style='max-width: 120px; max-height: 90px; margin-right: 18px; border: 1px solid #ddd; border-radius: 3px;'><div><h2 style='color: #2c3e50; margin: 0 0 2px 0;'>{title}</h2><div style='color: #7f8c8d; font-size:13px;'><b>Provider:</b> {provider}</div></div></div>")
        else:
            content.append(f"<h2 style='color: #2c3e50; margin: 0 0 2px 0;'>{title}</h2><div style='color: #7f8c8d; font-size:13px;'><b>Provider:</b> {provider}</div>")
        # Snippet
        if dataset.get('snippet'):
            content.append(f"<div style='margin: 8px 0 8px 0;'><span style='font-weight:bold;color:#2c3e50;'>Earth Engine Snippet:</span> <span style='font-family:monospace;background:#f0f0f0;padding:2px 6px;border-radius:4px;'>{dataset['snippet']}</span></div>")
        # Key info
        info_items = []
        if dataset.get('date_range'):
            info_items.append(f"<b>Date Range:</b> {dataset['date_range']}")
        if dataset.get('spatial_coverage'):
            info_items.append(f"<b>Coverage:</b> {dataset['spatial_coverage']}")
        if dataset.get('dataset_id'):
            info_items.append(f"<b>ID:</b> {dataset['dataset_id']}")
        if info_items:
            content.append(f"<div style='margin: 8px 0 12px 0; color:#444;'>{' | '.join(info_items)}</div>")
        # Description
        if dataset.get('description'):
            content.append(f"<div style='margin: 10px 0 10px 0;'><span style='font-weight:bold;color:#2c3e50;'>Description:</span> <span style='color:#222;'>{dataset['description']}</span></div>")
        # Bands
        if dataset.get('bands'):
            content.append(f"<div style='margin: 8px 0 8px 0;'><span style='font-weight:bold;color:#2c3e50;'>Bands:</span> <span style='color:#222;'>{dataset['bands']}</span></div>")
        # Tags inline, wrap if needed
        if dataset.get('tags'):
            tags_html = " ".join([f'<span style="background-color: #3498db; color: white; padding: 2px 8px; border-radius: 8px; font-size: 11px; margin: 1px; display:inline-block;">{tag}</span>' for tag in dataset['tags']])
            content.append(f"<div style='margin: 8px 0 8px 0;'><span style='font-weight:bold;color:#2c3e50;'>Tags:</span> {tags_html}</div>")
        # Key metadata in compact table
        if dataset.get('key_metadata'):
            content.append(f"<div style='margin: 8px 0 8px 0;'><span style='font-weight:bold;color:#2c3e50;'>Key Metadata:</span><table style='border-collapse: collapse; width: 100%; margin: 4px 0 0 0; font-size: 11px;'>")
            for key, value in dataset['key_metadata'].items():
                content.append(f"<tr><td style='padding: 2px 8px; border: 1px solid #eee; background-color: #f8f9fa;'><b>{key}</b></td><td style='padding: 2px 8px; border: 1px solid #eee;'>{value}</td></tr>")
            content.append("</table></div>")
        # Terms of Use
        if dataset.get('terms_of_use'):
            content.append(f"<div style='margin: 8px 0 8px 0;'><span style='font-weight:bold;color:#2c3e50;'>Terms of Use:</span> <span style='color:#222;'>{dataset['terms_of_use']}</span></div>")
        # URL
        if dataset.get('url'):
            content.append(f"<div style='margin: 8px 0 0 0;'><span style='font-weight:bold;color:#2c3e50;'>Source:</span> <a href='{dataset['url']}' style='color: #3498db; text-decoration: underline; font-size: 11px;'>{dataset['url']}</a></div>")
        self.details_content.setHtml("".join(content))

def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show main window
    window = CleanSatelliteViewer()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 