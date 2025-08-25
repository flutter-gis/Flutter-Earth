# Flutter Earth - Satellite Catalog Extractor

A focused tool for extracting satellite catalog data from Earth Engine HTML pages, specifically designed to collect comprehensive satellite dataset information.

## 🎯 Purpose

This tool extracts detailed satellite catalog information from Earth Engine HTML pages, including:
- Layer names and dataset information
- Date ranges and temporal coverage
- Satellite/sensor specifications
- Spatial coverage and location data
- GEE code snippets for data access
- Technical specifications (bands, resolution, pixel size)
- Metadata (provider, citations, DOI, terms of use)

## 🏗️ Repository Structure

```
Flutter-Earth/
├── web_crawler/                    # Main satellite catalog extractor
│   ├── lightweight_crawler.py      # Core extraction engine
│   ├── run_lightweight_crawler.bat # Windows batch runner
│   └── collected_data/             # Output directory
├── gee cat/                        # Earth Engine catalog HTML files
├── requirements.txt                 # Python dependencies
├── start.ps1                       # PowerShell startup script
├── start.bat                       # Windows batch startup script
└── README.md                       # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Required packages: `PySide6`, `BeautifulSoup4`, `requests`

### Installation
```bash
pip install -r requirements.txt
```

### Running the Extractor
```bash
# Windows
run_lightweight_crawler.bat

# PowerShell
python web_crawler/lightweight_crawler.py
```

## 🔧 How It Works

1. **Load Main Catalog**: Opens the main HTML file containing satellite catalog thumbnails
2. **Extract Links**: Identifies and extracts links to individual satellite dataset pages
3. **Follow Links**: Visits each satellite page to extract detailed information
4. **Organize Data**: Saves data organized by satellite in `satellite_catalog.json`
5. **Generate Output**: Creates comprehensive dataset with all requested parameters

## 📊 Output Format

The extractor generates:
- **Individual JSON files** for each processed page
- **Main catalog file** (`satellite_catalog.json`) organized by satellite
- **Thumbnail references** for satellite imagery

## 🎨 Features

- **Focused Extraction**: Specifically designed for satellite catalog data
- **Smart Organization**: Groups data by satellite for easy analysis
- **Comprehensive Coverage**: Extracts all requested technical parameters
- **User-Friendly UI**: PySide6-based interface with progress tracking
- **Batch Processing**: Handles multiple HTML files efficiently

## 📝 License

This project is part of the Flutter Earth initiative for Earth Engine data extraction and analysis. 