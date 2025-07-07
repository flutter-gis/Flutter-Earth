# Backend (Python)

This directory contains the Python backend for Flutter Earth, responsible for crawling, processing, and serving satellite data from Google Earth Engine.

## Main Components
- **gee_catalog_crawler_enhanced.py**: Crawls the GEE catalog, extracts metadata, thumbnails, and code snippets, and writes progress for the frontend.
- **earth_engine_processor.py**: Handles backend processing, download management, and communication with the frontend.

## Features
- Live progress reporting (JSON file for UI updates)
- Robust logging (logs/ directory)
- Error handling and recovery
- Modular, extensible codebase

## Usage

### 1. Install dependencies
```
pip install -r ../requirements.txt
```

### 2. Run the crawler
```
python gee_catalog_crawler_enhanced.py
```

### 3. Run the processor (if applicable)
```
python earth_engine_processor.py
```

## Developer Notes
- Progress is written to `backend/crawler_data/crawler_progress.json` for live UI updates.
- Logs are stored in the `logs/` directory with timestamps.
- The backend is designed to be called from the Electron frontend, but can be run standalone for testing.

## See Also
- Main project README for overall architecture
- `docs/README_GEE_CRAWLER.md` for detailed crawler documentation 