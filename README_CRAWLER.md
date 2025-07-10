# Enhanced Earth Engine Data Catalog Crawler

## Overview

This project is a powerful, user-friendly tool for crawling and extracting detailed metadata from the Google Earth Engine Data Catalog. It features a modern Tkinter-based GUI, real-time progress and speed tracking, and outputs fully indexed, filterable JSON for downstream analysis or UI integration.

---

## Features

- **Graphical User Interface (GUI)**: Built with Tkinter for easy folder selection, progress tracking, and log viewing.
- **Satellite Dataset Extraction**: Crawls Earth Engine catalog HTML files and follows links to all satellite dataset pages.
- **Comprehensive Metadata Extraction**: For each dataset, extracts:
  - Title
  - Dataset Availability
  - Tags
  - Dataset Provider
  - Earth Engine Snippet
  - Thumbnail/Image URL
  - Description (from Description tab)
  - Code Editor Example (JavaScript)
  - Bands (parsed as a table of dicts)
  - Terms of Use
  - Citations
  - DOIs
- **Real-Time Progress Bar**: Shows percent complete, ETA, and current file being processed.
- **Download Speed Graph**: Task Manager-style, shows real network download speed for each satellite page fetch.
- **Clear Saved Files**: One-click button to delete all output/log files with confirmation dialog.
- **Output**: Single, well-indexed JSON file with all datasets, ready for fast UI filtering/searching.
- **Batch and PowerShell Launchers**: Easy to start the GUI from Windows.
- **SSL Verification Disabled**: Works in all environments, even with self-signed or intercepted certificates.

---

## Installation

1. **Install Python 3.8+** (with Tkinter)
2. **Clone the repo**
3. **Install dependencies**:
   ```sh
   pip install -r requirements_crawler.txt
   ```
   (The batch file will also auto-install dependencies if needed.)

---

## Usage

### Launch the GUI
- **Windows**: Double-click `run_crawler.bat` or run:
  ```sh
  python crawler_gui.py
  ```
- **PowerShell**: Run `run_crawler.ps1` for advanced checks.

### Using the GUI
1. **Select Folder**: Choose the directory containing your Earth Engine HTML files.
2. **Start Enhanced Crawling**: Click the button to begin. Progress, ETA, and download speed will update live.
3. **Save Results**: When done, click "Save Results" and choose a directory. The output JSON will be saved there.
4. **Clear Saved Files**: Use this to delete all output/log files (with confirmation).
5. **Log**: View all actions, errors, and progress in the log window.

### Output
- The main output is a single JSON file (and a compressed `.json.gz`), containing a list of all datasets with all extracted fields, ready for UI filtering/searching.
- Intermediate files and logs are stored in `logs/`, `crawler_data/`, and `output/`.

---

## Example Extracted Fields (per dataset)
```json
{
  "title": "Actual Evapotranspiration for Australia (CMRSET Landsat V2.2)",
  "availability": "2020-07-01T00:00:00Z–2024-06-01T00:00:00Z",
  "tags": ["agriculture", "australia", ...],
  "provider": "TERN Landscapes / CSIRO Land and Water",
  "snippet": "ee.ImageCollection(\"TERN/AET/CMRSET_LANDSAT_V2_2\")",
  "thumbnail_url": "https://...",
  "description": "This dataset provides...",
  "code_example": "var dataset = ...",
  "bands": [
    {"Name": "AET", "Min": "0", "Max": "100", "Units": "mm", ...},
    ...
  ],
  "terms_of_use": "...",
  "citations": "...",
  "dois": ["10.1234/abcd.efgh"]
}
```

---

## Troubleshooting
- **No GUI appears?**
  - Make sure Python and Tkinter are installed.
  - Run `python crawler_gui.py` from a command prompt to see errors.
- **SSL errors?**
  - SSL verification is disabled by default for maximum compatibility.
- **Output files location?**
  - You choose the output directory when saving results. Logs and intermediate files are in `logs/`, `crawler_data/`, and `output/`.

---

## Recent Changes
- Real network download speed bar (Task Manager style)
- ETA and progress bar
- Full metadata extraction from all dataset tabs (bands, terms, citations, DOIs)
- Output is a single, indexed JSON file for UI filtering/searching
- One-click clear saved files with confirmation
- SSL verification disabled for all requests

---

## Contributing
Pull requests and suggestions are welcome!

---

## License
MIT 