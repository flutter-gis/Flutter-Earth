# Earth Engine Catalog Web Crawler - QML Interface

A modern, QML-based interface for crawling and extracting Earth Engine catalog datasets with advanced filtering and search capabilities.

## Features

- **Modern QML Interface**: Beautiful, responsive UI built with Qt Quick
- **Advanced Search**: Real-time search through dataset titles and descriptions
- **Category Filters**: Filter datasets by categories (Satellite, Climate, Land Cover, Hydrology)
- **Detailed View**: View comprehensive dataset information in a modal dialog
- **Progress Tracking**: Real-time progress updates during crawling
- **Thumbnail Download**: Download dataset thumbnails automatically
- **Export Options**: Export individual datasets as JSON files
- **Console Output**: Real-time logging of crawling operations

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Make sure you have Microsoft Edge WebDriver installed for Selenium automation.

## Usage

### Running the Application

```bash
python qml_crawler_launcher.py
```

### Interface Overview

#### File Selection
- Click "Browse" to select an HTML file containing Earth Engine catalog links
- The crawler will automatically detect and process dataset links

#### Crawling Options
- **Download thumbnails**: Automatically download dataset thumbnail images
- **Extract detailed information**: Extract comprehensive metadata from each dataset
- **Save as individual JSON files**: Save each dataset as a separate JSON file

#### Search & Filters
- **Search Bar**: Type to search through dataset titles and descriptions
- **Category Filters**: Click filter buttons to show only specific categories:
  - All: Show all datasets
  - Satellite: Satellite imagery datasets
  - Climate: Climate and weather datasets
  - Land Cover: Land cover and vegetation datasets
  - Hydrology: Water and hydrological datasets

#### Results Display
- **Datasets Tab**: View all crawled datasets in a card-based layout
- **Console Tab**: View real-time crawling logs and status messages

#### Dataset Actions
- **View**: Open the dataset URL in your default browser
- **Details**: Open a detailed view with comprehensive dataset information

### Output

- **JSON Files**: Individual dataset files saved in `extracted_data/` directory
- **Thumbnails**: Dataset images saved in `thumbnails/` directory
- **Console Logs**: Real-time logging of all operations

## File Structure

```
Flutter-Earth/
├── main.qml                    # Main QML interface
├── DatasetDetailsDialog.qml    # Dataset details dialog
├── qml_crawler_launcher.py     # Python launcher with backend logic
├── enhanced_crawler_ui.py      # Original PySide6 implementation
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Technical Details

### QML Components

- **main.qml**: Main application window with all UI elements
- **DatasetDetailsDialog.qml**: Modal dialog for detailed dataset information

### Backend Integration

The QML interface communicates with Python backend through:
- **Signals**: Real-time updates for progress, status, and data
- **Slots**: Method calls from QML to Python backend
- **Context Properties**: Data sharing between QML and Python

### Data Flow

1. User selects HTML file and options
2. Python backend crawls the file and extracts dataset information
3. Real-time updates sent to QML interface via signals
4. QML displays results with search and filtering capabilities
5. Users can interact with datasets through the modern interface

## Troubleshooting

### Common Issues

1. **WebDriver not found**: Install Microsoft Edge WebDriver
2. **QML not loading**: Ensure PySide6 is properly installed
3. **Permission errors**: Check file permissions for output directories

### Performance Tips

- Use SSD storage for better I/O performance
- Close other applications during crawling
- Consider reducing the number of concurrent operations for large datasets

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is open source and available under the MIT License. 