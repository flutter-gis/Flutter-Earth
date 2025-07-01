# Google Earth Engine Catalog Crawler

This directory contains the Google Earth Engine catalog crawler and related tools for Flutter Earth.

## Overview

The GEE Catalog Crawler is a Python-based tool that automatically discovers and catalogs available datasets from Google Earth Engine. It provides a comprehensive interface for browsing satellite imagery, climate data, terrain data, and other geospatial datasets.

## Components

### Core Files

- **`gee_catalog_crawler_enhanced.py`**: Main crawler script with enhanced functionality
- **`earth_engine_processor.py`**: Earth Engine processing and data management
- **`catalog_viewer.html`**: Web interface for browsing catalog data
- **`gee_catalog_viewer.html`**: Enhanced catalog viewer with advanced features

### Data Directory

- **`crawler_data/`**: Directory containing crawled catalog data
- **`crawler_data/thumbnails/`**: Thumbnail images for datasets (if available)

## Features

### 🕷️ Enhanced Crawling
- **Automatic Discovery**: Discovers all available Earth Engine datasets
- **Metadata Extraction**: Extracts comprehensive metadata for each dataset
- **Thumbnail Generation**: Creates thumbnail previews for datasets
- **Incremental Updates**: Only crawls new or updated datasets

### 📊 Data Management
- **Structured Storage**: Organizes data in JSON format
- **Search and Filter**: Advanced search and filtering capabilities
- **Export Functions**: Export catalog data in various formats
- **Data Validation**: Validates dataset metadata and accessibility

### 🌐 Web Interface
- **Interactive Browser**: Web-based catalog browser
- **Real-time Search**: Instant search and filtering
- **Dataset Preview**: Preview dataset information and metadata
- **Export Tools**: Export selected datasets or entire catalog

## Usage

### Command Line Interface

#### Basic Crawling
```bash
# Crawl all available datasets
python gee_catalog_crawler_enhanced.py --crawl-all

# Crawl specific categories
python gee_catalog_crawler_enhanced.py --categories satellite,climate,terrain

# Update existing catalog
python gee_catalog_crawler_enhanced.py --update
```

#### Advanced Options
```bash
# Crawl with custom output directory
python gee_catalog_crawler_enhanced.py --output-dir /path/to/output

# Generate thumbnails
python gee_catalog_crawler_enhanced.py --thumbnails

# Verbose logging
python gee_catalog_crawler_enhanced.py --verbose

# Dry run (no actual crawling)
python gee_catalog_crawler_enhanced.py --dry-run
```

#### Search and Export
```bash
# Search for specific datasets
python gee_catalog_crawler_enhanced.py --search "Landsat"

# Export catalog to JSON
python gee_catalog_crawler_enhanced.py --export-json catalog.json

# Export catalog to CSV
python gee_catalog_crawler_enhanced.py --export-csv catalog.csv
```

### Web Interface

#### Starting the Viewer
1. Open `catalog_viewer.html` in a web browser
2. Click "Load Catalog" to load the crawled data
3. Use filters and search to find datasets
4. Click on datasets to view details

#### Features
- **Category Filtering**: Filter by dataset category
- **Resolution Filtering**: Filter by spatial resolution
- **Search**: Text-based search across dataset names and descriptions
- **Export**: Export filtered results or entire catalog
- **Activity Log**: View crawler activity and operations

## Configuration

### Environment Setup
```bash
# Install required packages
pip install earthengine-api google-auth google-auth-oauthlib

# Authenticate with Earth Engine
earthengine authenticate
```

### Configuration File
Create `crawler_config.json`:
```json
{
  "output_directory": "crawler_data",
  "generate_thumbnails": true,
  "max_datasets": 1000,
  "categories": ["satellite", "climate", "terrain", "demographics"],
  "log_level": "INFO",
  "export_formats": ["json", "csv"]
}
```

## Data Structure

### Catalog Data Format
```json
{
  "id": "USGS/SRTMGL1_003",
  "name": "SRTM Digital Elevation",
  "category": "terrain",
  "resolution": "30m",
  "description": "Digital elevation data from SRTM",
  "tags": ["elevation", "terrain", "global"],
  "bands": ["elevation"],
  "temporal_coverage": "2000-02-11 to 2000-02-22",
  "spatial_coverage": "Global",
  "provider": "USGS",
  "license": "Public Domain",
  "thumbnail_url": "thumbnails/srtm_thumbnail.png",
  "metadata": {
    "collection_type": "ImageCollection",
    "data_type": "Float32",
    "crs": "EPSG:4326"
  }
}
```

### Directory Structure
```
crawler_data/
├── catalog.json              # Main catalog file
├── catalog_metadata.json     # Catalog metadata
├── categories/               # Category-specific data
│   ├── satellite.json
│   ├── climate.json
│   └── terrain.json
├── thumbnails/              # Dataset thumbnails
│   ├── srtm_thumbnail.png
│   └── landsat_thumbnail.png
└── exports/                 # Exported data
    ├── catalog.csv
    └── catalog.json
```

## API Reference

### Crawler Class
```python
class GEECatalogCrawler:
    def __init__(self, config=None)
    def crawl_all_datasets(self)
    def crawl_category(self, category)
    def search_datasets(self, query)
    def export_catalog(self, format='json', filename=None)
    def generate_thumbnails(self)
    def update_catalog(self)
```

### Processor Class
```python
class EarthEngineProcessor:
    def __init__(self)
    def initialize(self)
    def get_dataset_info(self, dataset_id)
    def validate_dataset(self, dataset_id)
    def get_dataset_metadata(self, dataset_id)
```

## Error Handling

### Common Issues
1. **Authentication Errors**: Ensure Earth Engine authentication is set up
2. **Rate Limiting**: Implement delays between requests
3. **Network Errors**: Handle connection timeouts and retries
4. **Data Validation**: Validate dataset metadata before storage

### Error Recovery
```python
# Retry mechanism for failed requests
def retry_request(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            time.sleep(2 ** attempt)  # Exponential backoff
```

## Performance Optimization

### Caching
- **Metadata Cache**: Cache dataset metadata to avoid repeated requests
- **Thumbnail Cache**: Cache generated thumbnails
- **Search Cache**: Cache search results for common queries

### Parallel Processing
```python
# Parallel dataset processing
from concurrent.futures import ThreadPoolExecutor

def process_datasets_parallel(datasets, max_workers=4):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(process_dataset, datasets))
    return results
```

### Memory Management
- **Streaming**: Process large catalogs in chunks
- **Cleanup**: Remove temporary files and cache entries
- **Monitoring**: Monitor memory usage during crawling

## Monitoring and Logging

### Log Levels
- **DEBUG**: Detailed debugging information
- **INFO**: General information about operations
- **WARNING**: Warning messages for potential issues
- **ERROR**: Error messages for failed operations

### Log Format
```
2024-01-15 10:30:45 - INFO - Starting catalog crawl
2024-01-15 10:30:46 - INFO - Crawled 50 datasets
2024-01-15 10:30:47 - WARNING - Dataset XYZ not accessible
2024-01-15 10:30:48 - ERROR - Failed to generate thumbnail for ABC
```

### Metrics
- **Crawl Duration**: Time taken to complete crawl
- **Dataset Count**: Number of datasets discovered
- **Success Rate**: Percentage of successful operations
- **Error Rate**: Percentage of failed operations

## Integration

### Flutter Earth Integration
The crawler integrates with Flutter Earth through:
- **Data Sharing**: Shared catalog data between components
- **API Integration**: Direct API calls for dataset information
- **UI Integration**: Web interface for browsing catalogs

### External Tools
- **QGIS**: Export data for use in QGIS
- **ArcGIS**: Export data for use in ArcGIS
- **Python Scripts**: Use catalog data in custom scripts

## Troubleshooting

### Common Problems

#### Authentication Issues
```bash
# Re-authenticate with Earth Engine
earthengine authenticate

# Check authentication status
python -c "import ee; ee.Initialize(); print('Authenticated')"
```

#### Memory Issues
```python
# Increase memory limit for large catalogs
import gc
gc.collect()  # Force garbage collection
```

#### Network Issues
```python
# Implement connection retry logic
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

session = requests.Session()
retry = Retry(connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)
```

### Debug Mode
```bash
# Enable debug logging
python gee_catalog_crawler_enhanced.py --debug

# Verbose output
python gee_catalog_crawler_enhanced.py --verbose
```

## Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

### Code Style
- Follow PEP 8 guidelines
- Add docstrings to all functions
- Include type hints where appropriate
- Write unit tests for new features

### Testing
```bash
# Run unit tests
python -m pytest tests/

# Run integration tests
python -m pytest tests/integration/

# Run with coverage
python -m pytest --cov=crawler tests/
```

## License

This project is licensed under the MIT License - see the main project license for details.

## Support

For support and questions:
- Check the troubleshooting section
- Review the documentation
- Open an issue on GitHub
- Contact the development team

---

**Note**: This crawler requires a valid Google Earth Engine account and proper authentication to function correctly. 