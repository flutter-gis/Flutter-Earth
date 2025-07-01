# Google Earth Engine Data Catalog Crawler

This crawler extracts comprehensive dataset information from the Google Earth Engine Data Catalog.

## Features

- Extracts name, description, resolution, categories, tags, satellites, dates, frequency, data type, and download links
- Automatically categorizes datasets by satellite and data type
- Generates JSON data files and HTML reports
- Provides a web interface to browse the data

## Files

- `gee_catalog_crawler.py` - Basic crawler
- `gee_catalog_crawler_enhanced.py` - Enhanced crawler with better extraction
- `test_crawler.py` - Test script
- `run_crawler.py` - Simple runner script
- `catalog_viewer.html` - Web interface
- `README_GEE_CRAWLER.md` - This file

## Installation

```bash
pip install beautifulsoup4 lxml requests
```

## Usage

1. **Test the crawler**:
```bash
python run_crawler.py
```

2. **Run the full crawler**:
```bash
python gee_catalog_crawler.py
```

3. **View results**:
   - Open `catalog_viewer.html` in your browser
   - Or check the generated JSON files

## Output

The crawler generates:
- JSON files with dataset data
- HTML reports
- Web interface for browsing

## Data Structure

Each dataset contains:
- name, description, resolution
- satellites, tags, categories
- dates, frequency, data type
- download links

## Web Interface

Open `catalog_viewer.html` to:
- Search datasets
- Filter by satellite or category
- View dataset details
- Access Earth Engine links 