# 🕷️ Enhanced GEE Catalog Crawler

Welcome to the **Enhanced Google Earth Engine Catalog Crawler**! This is the backend powerhouse that fetches, parses, and organizes all the satellite dataset goodness from Google Earth Engine. 🚀

---

## 🌟 What Does It Do?
- Crawls the GEE catalog for all available datasets
- Extracts metadata, thumbnails, tags, and code snippets
- Saves everything in a structured, frontend-friendly format
- Reports live progress for a responsive UI experience
- Handles errors gracefully and logs everything for you

---

## 🛠️ How It Works
1. **Starts at the GEE catalog homepage**
2. **Follows links** to every dataset page
3. **Extracts**:
   - Name, description, tags, publisher, coverage
   - Thumbnails and preview images
   - Download links and code snippets
   - Dates, satellites, bands, and more!
4. **Saves** all data to JSON (and compressed .gz) for the frontend
5. **Writes progress** to `crawler_progress.json` so the UI can show spinners, bars, and logs

---

## 🚦 Usage

### Run the crawler
```bash
python gee_catalog_crawler_enhanced.py
```

### Options
- Configure the base URL or output directory by editing the script or passing arguments (see code comments)

---

## 📊 Progress Reporting
- Progress is written to `backend/crawler_data/crawler_progress.json`
- UI reads this file for live updates (spinners, bars, logs)
- Each step (fetch, parse, save) is logged with timestamps

---

## 🧑‍💻 Developer Tips
- All HTTP requests use a custom User-Agent for reliability
- Thumbnails are downloaded and saved locally for fast UI loading
- Errors are logged but don't crash the crawler (robust and resilient!)
- Modular functions: easy to extend for new metadata fields or output formats

---

## 🐞 Error Handling
- All errors are logged to `logs/` with timestamps
- Progress file is always updated, even on failure
- Network retries and backoff for flaky connections

---

## 🧩 Integration
- Designed to be called from the Electron frontend, but can run standalone
- Output is consumed by the frontend for catalog browsing and search

---

## 📝 Example Output
```json
{
  "datasets": [
    {
      "name": "Landsat 8 Surface Reflectance",
      "description": "Atmospherically corrected surface reflectance...",
      "dataset_id": "LANDSAT/LC08/C01/T1_SR",
      "tags": ["landsat", "surface reflectance", "usgs"],
      "thumbnail": "backend/crawler_data/thumbnails/LANDSAT_LC08_C01_T1_SR.jpg",
      ...
    }
  ],
  "progress": {
    "current_page": 3,
    "total_pages": 10,
    "current_dataset": 120,
    "total_datasets": 200
  }
}
```

---

## 🤓 For More Info
- See the main backend README for architecture
- Check the code for advanced options and extension points
- Logs and progress files are your friends for debugging!

---

Happy crawling! 🕷️🌍 