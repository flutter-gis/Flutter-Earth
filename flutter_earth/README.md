# Flutter Earth - Advanced GEE Downloader

A powerful Python application for downloading and processing satellite imagery from Google Earth Engine. This application provides a modern Qt-based GUI interface for selecting areas of interest, managing satellite data downloads, and processing imagery.

## Features

- Modern Qt-based GUI interface with theme customization
- Support for multiple satellite data sources (Landsat 9/8/7/5/4, Sentinel-2, VIIRS, MODIS, ERA5)
- Advanced cloud masking and image processing
- Vector data support (Shapefiles, GeoJSON, WFS, Overpass API)
- Interactive map selection with drawing tools
- Multi-threaded downloads with progress tracking
- Index analysis (NDVI, EVI, NDWI, etc.)
- Data visualization with matplotlib integration
- Sample data management
- Comprehensive logging and error handling

## Installation

1. Clone this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Authenticate with Google Earth Engine:
```bash
earthengine authenticate
```

## Usage

1. Run the application:
```bash
python main.py
```

2. Select your area of interest using one of the following methods:
   - Draw on the interactive map
   - Import a shapefile (.shp)
   - Enter coordinates manually (BBOX or GeoJSON)

3. Choose your satellite data source and time range

4. Configure processing options:
   - Cloud masking and maximum cloud cover
   - Resolution and tiling method
   - Output format (GeoTIFF, PNG, JPEG)
   - Sensor priority order

5. Start the download process

## Advanced Features

- **Vector Download**: Download OpenStreetMap data, WFS services, or direct GeoJSON URLs
- **Index Analysis**: Calculate vegetation indices (NDVI, EVI, NDWI, etc.) from satellite imagery
- **Data Viewer**: Visualize raster and vector data with zoom and pan capabilities
- **Theme System**: Choose from multiple themes including MLP and Minecraft-inspired designs
- **Sample Data**: Pre-configured sample datasets for testing and demonstration

## Configuration

The application stores its configuration in `flutter_earth_config.json`. You can modify:
- Default output directory
- Tile size and overlap settings
- UI theme and suboptions
- Processing parameters
- Sensor priority order

## Troubleshooting

1. **Authentication Issues**:
   - Ensure you've run `earthengine authenticate`
   - Check your internet connection
   - Verify your Google Earth Engine account is active
   - Use the built-in authentication setup dialog

2. **Performance Issues**:
   - Reduce the size of your area of interest
   - Increase tile size
   - Check available disk space
   - Adjust the number of worker threads

3. **Missing Dependencies**:
   - Install missing packages: `pip install matplotlib geopandas pyshp`
   - For vector features: `pip install overpass`

## CLI Mode

For automated processing, you can use CLI mode:
```bash
python main.py --cli <bbox> <start_date> <end_date> <sensor> <output_dir>
```

Example:
```bash
python main.py --cli '35.2,30.5,35.8,32.0' '2023-01-01' '2023-01-31' 'LANDSAT_9' './output'
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 