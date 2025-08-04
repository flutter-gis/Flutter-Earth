# Web Crawlers - Three Versions

This directory contains three different web crawlers, each designed for different use cases:

## 🚀 **1. Simple Crawler** (No ML)
**File:** `simple_crawler.py` (22KB)
**Batch:** `run_simple_crawler.bat`

### Features:
- ✅ **No Machine Learning** - Pure crawling and downloading
- ✅ **Downloads Everything** - Images, documents, HTML, text
- ✅ **Lightweight** - Fast startup, low memory usage
- ✅ **No Categorization** - Just saves everything it finds

### Use When:
- You want to download everything from a website
- No need for categorization or analysis
- Fast, simple crawling
- Minimal dependencies

---

## 🎯 **2. Lightweight Crawler** (Simplified ML)
**File:** `lightweight_crawler.py` (138KB)
**Batch:** `run_lightweight_crawler.bat`

### Features:
- ✅ **Basic ML** - Pattern-based extraction
- ✅ **Earth Engine Focus** - Satellite data extraction
- ✅ **Keyword Classification** - Simple text analysis
- ✅ **Moderate Dependencies** - Some ML libraries

### Use When:
- You need basic categorization
- Working with satellite/Earth Engine data
- Want some ML features without heavy dependencies
- Need pattern-based extraction

---

## 🤖 **3. Enhanced Crawler** (Heavy ML)
**File:** `enhanced_crawler_ui.py` (244KB)
**Batch:** `run_enhanced_crawler.bat`

### Features:
- ✅ **Advanced ML** - BERT models, scikit-learn
- ✅ **Complex Analysis** - Deep content understanding
- ✅ **Advanced UI** - Rich interface with many features
- ✅ **Heavy Dependencies** - torch, sklearn, numpy, pandas

### Use When:
- You need advanced content analysis
- Working with complex data extraction
- Need sophisticated ML capabilities
- Want the most feature-rich crawler

---

## 📁 **Output Directories:**

### Simple Crawler:
```
simple_crawled_data/
├── images/          # All downloaded images
├── documents/       # All downloaded documents
├── html/           # All HTML pages
└── text/           # All extracted text content
```

### Lightweight Crawler:
```
crawled_data/
├── images/          # Downloaded images
├── documents/       # Downloaded documents
├── html/           # HTML pages
└── data/           # Extracted data with categorization
```

### Enhanced Crawler:
```
exported_data/
├── images/          # Downloaded images
├── documents/       # Downloaded documents
├── html/           # HTML pages
├── data/           # Advanced extracted data
└── analysis/       # ML analysis results
```

## 🚀 **Quick Start:**

1. **Simple Crawler (No ML):**
   ```bash
   run_simple_crawler.bat
   ```

2. **Lightweight Crawler (Basic ML):**
   ```bash
   run_lightweight_crawler.bat
   ```

3. **Enhanced Crawler (Heavy ML):**
   ```bash
   run_enhanced_crawler.bat
   ```

## 📊 **Comparison:**

| Feature | Simple | Lightweight | Enhanced |
|---------|--------|-------------|----------|
| **ML Dependencies** | None | Basic | Heavy |
| **Startup Speed** | Fast | Medium | Slow |
| **Memory Usage** | Low | Medium | High |
| **Categorization** | None | Basic | Advanced |
| **File Size** | 22KB | 138KB | 244KB |
| **Complexity** | Simple | Moderate | Complex |

## 🎯 **Choose Your Crawler:**

- **Simple Crawler**: When you just want to download everything
- **Lightweight Crawler**: When you need basic categorization
- **Enhanced Crawler**: When you need advanced ML analysis 