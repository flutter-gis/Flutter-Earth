# Output Directory Feature

## Overview

The Enhanced Web Crawler now includes a user-configurable output directory feature that allows users to specify where all cache files, extracted data, and processed results are stored. This provides better organization and control over data storage.

## Features

### 🎯 **User-Configurable Output Directory**
- **Browse Button**: Users can select any directory on their system
- **Default Path**: Automatically set to `./extracted_data` on startup
- **Real-time Updates**: Directory changes are applied immediately

### 📁 **Organized Directory Structure**
When a user selects an output directory, the system automatically creates the following subdirectory structure:

```
Selected_Output_Directory/
├── extracted_data/          # Raw extracted data from crawling
├── thumbnails/              # Downloaded thumbnail images
├── model_cache/             # Cached ML models for faster loading
└── exported_data/           # Processed and exported results
```

### 🔄 **Automatic Directory Management**
- **Auto-creation**: All subdirectories are created automatically
- **Cache Integration**: ML model cache directory is updated dynamically
- **Path Validation**: Ensures all paths are valid and accessible

## How to Use

### 1. **Launch the Crawler**
```bash
cd web_crawler
python enhanced_crawler_ui.py
```

### 2. **Select Output Directory**
1. Look for the **"Output Directory Settings"** section in the UI
2. Click the **"Browse Output"** button
3. Navigate to your desired output directory
4. Click **"Select Folder"**

### 3. **Verify Selection**
- The selected path will appear in the text field
- A confirmation message will be logged in the console
- All subdirectories will be created automatically

### 4. **Start Crawling**
- Select your HTML file
- Click **"Start Advanced Crawling"**
- All data will be saved to your selected output directory

## Directory Purposes

### 📊 **extracted_data/**
- **Raw crawling results** in JSON format
- **Individual dataset files** (if enabled)
- **CSV exports** of processed data
- **Timestamped files** for version control

### 🖼️ **thumbnails/**
- **Downloaded thumbnail images** from datasets
- **Optimized image files** for web display
- **Organized by dataset ID**

### 🤖 **model_cache/**
- **Cached ML models** (BERT, spaCy, etc.)
- **Model manifest files** for tracking
- **Compressed model files** for faster loading
- **Automatic cleanup** when size exceeds limits

### 📤 **exported_data/**
- **Final processed results**
- **Analytics-ready data** for dashboards
- **Backup copies** of important results
- **Export-ready formats** (JSON, CSV)

## Technical Implementation

### **UI Components**
```python
# Output directory selection group
output_group = QGroupBox("Output Directory Settings")
self.output_dir_edit = QLineEdit()
self.output_browse_btn = QPushButton("Browse Output")
```

### **Directory Management**
```python
def update_output_directories(self, base_dir):
    self.output_dir = os.path.join(base_dir, "extracted_data")
    self.images_dir = os.path.join(base_dir, "thumbnails")
    self.cache_dir = os.path.join(base_dir, "model_cache")
    self.exported_dir = os.path.join(base_dir, "exported_data")
```

### **ML Cache Integration**
```python
def update_ml_cache_directory(self):
    if hasattr(ml_manager, 'model_cache'):
        ml_manager.model_cache.cache_dir = self.cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)
```

## Benefits

### 🎯 **User Control**
- **Flexible Storage**: Choose any directory on your system
- **Organization**: Keep all crawler data in one place
- **Backup**: Easy to backup entire output directory

### 🚀 **Performance**
- **Faster Loading**: Cached ML models load quickly
- **Reduced Downloads**: Models are cached locally
- **Efficient Storage**: Automatic cleanup of old cache files

### 📈 **Scalability**
- **Large Datasets**: Handle massive amounts of data
- **Multiple Runs**: Separate data for different crawling sessions
- **Version Control**: Timestamped files for tracking changes

## Configuration

### **Default Settings**
- **Default Output**: `./extracted_data`
- **Cache Size Limit**: 5GB (configurable)
- **Auto-cleanup**: Enabled by default

### **Customization**
Users can modify the following in the configuration:
- **Cache size limits**
- **Cleanup policies**
- **File naming conventions**
- **Compression settings**

## Error Handling

### **Directory Access**
- **Permission Checks**: Validates write access
- **Path Validation**: Ensures valid directory paths
- **Fallback Options**: Uses default if custom path fails

### **Storage Management**
- **Space Monitoring**: Checks available disk space
- **Automatic Cleanup**: Removes old cache files
- **Error Recovery**: Graceful handling of storage issues

## Testing

Run the test script to verify functionality:
```bash
cd web_crawler
python test_output_directory.py
```

This will:
- ✅ Create test directory structure
- ✅ Verify file creation in each directory
- ✅ Test path validation
- ✅ Confirm ML cache integration

## Troubleshooting

### **Common Issues**

1. **Permission Denied**
   - Ensure you have write access to the selected directory
   - Try running as administrator if needed

2. **Path Not Found**
   - Verify the directory exists
   - Check for typos in the path

3. **Cache Not Updating**
   - Restart the crawler after changing output directory
   - Check console logs for cache update messages

### **Debug Information**
- Check the **Console Log** tab for detailed messages
- Look for **"Output directories updated"** messages
- Verify **"ML cache directory updated"** notifications

## Future Enhancements

### **Planned Features**
- **Multiple Output Directories**: Support for different types of data
- **Cloud Storage**: Integration with cloud storage providers
- **Compression**: Automatic compression of large files
- **Synchronization**: Sync with remote storage

### **Advanced Options**
- **Custom Directory Names**: User-defined subdirectory names
- **Template System**: Predefined directory structures
- **Backup Integration**: Automatic backup to secondary locations

---

## Summary

The Output Directory feature provides users with complete control over where their crawler data is stored, while maintaining an organized structure that separates different types of data. This makes the crawler more professional, scalable, and user-friendly while providing better performance through intelligent caching. 