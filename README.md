# Flutter Earth

A powerful tool for downloading and processing satellite imagery using Google Earth Engine.

## Features

- Download satellite imagery from multiple sensors (Landsat, Sentinel-2, etc.)
- Process and analyze satellite data with cloud masking
- GUI and CLI interfaces
- Configurable processing parameters
- Progress tracking and error handling

## Prerequisites

- Python 3.8 or higher
- Google Earth Engine account and authentication
- Required Python packages (see requirements.txt)

## Installation

### 1. Clone or download the project

```bash
git clone <repository-url>
cd "dead the third"
```

### 2. Install required packages

```bash
pip install -r requirements.txt
```

### 3. Set up Earth Engine authentication

**Option A: Use the built-in authentication dialog (Recommended)**
1. Run the application: `python flutter_earth_6-19.py`
2. When prompted, click "Help" to see detailed setup instructions
3. Follow the steps to create a Google Cloud project and service account
4. Enter your Project ID and select your service account key file
5. Click "Test Connection" to verify everything works
6. Click "Save & Continue" to save your settings

**Option B: Use the setup script**
```bash
python setup_earth_engine.py
```

**Option C: Manual setup**
```bash
# Install Earth Engine API
pip install earthengine-api

# Authenticate with Earth Engine
earthengine authenticate
```

**Note:** You need to sign up for Earth Engine access at: https://developers.google.com/earth-engine/guides/access

### 4. Test the installation

```bash
python test_basic.py
```

### 5. Test the authentication system (Optional)

```bash
python demo_auth.py
```

## Authentication System

Flutter Earth includes a built-in authentication system that makes it easy to set up Google Earth Engine access:

### Features

- **Service Account Authentication**: Uses Google Cloud service accounts for secure, programmatic access
- **Interactive Setup Dialog**: User-friendly GUI for entering project ID and key file
- **Help System**: Built-in instructions for creating Google Cloud projects and service accounts
- **Connection Testing**: Verify your setup before saving
- **Persistent Storage**: Credentials are saved locally for future use
- **Fallback Support**: Still supports traditional OAuth authentication

### Setup Process

1. **Sign up for Earth Engine**: Visit https://developers.google.com/earth-engine/guides/access
2. **Create Google Cloud Project**: Set up a project with Earth Engine API enabled
3. **Create Service Account**: Generate a service account with appropriate Earth Engine roles
4. **Download Key File**: Download the JSON key file for your service account
5. **Configure Flutter Earth**: Use the built-in dialog to enter your Project ID and select your key file

### Security

- Service account key files are stored locally and should be kept secure
- Never commit key files to version control
- The application stores only the file path, not the key contents
- Consider using environment variables for production deployments

## Usage

### GUI Mode (Default)

Run the application with a graphical interface:

```bash
python flutter_earth_6-19.py
```

### CLI Mode

Run the application from the command line:

```bash
python flutter_earth_6-19.py --cli west,south,east,north start_date end_date sensor_name output_dir
```

**Example:**
```bash
python flutter_earth_6-19.py --cli -122.4,37.7,-122.3,37.8 2023-01-01 2023-12-31 LANDSAT_9 ./output
```

### Parameters

- `west,south,east,north`: Bounding box coordinates (longitude, latitude)
- `start_date`: Start date in YYYY-MM-DD format
- `end_date`: End date in YYYY-MM-DD format
- `sensor_name`: Satellite sensor name (e.g., LANDSAT_9, SENTINEL_2)
- `output_dir`: Output directory for processed images

## Configuration

The application uses a configuration file (`flutter_earth_config.json`) that is automatically created on first run. You can modify settings like:

- Output directory
- Tile size
- Maximum cloud cover
- Number of worker threads
- Cloud masking options

## Supported Sensors

- **Landsat 9**: 30m resolution, optical bands
- **Sentinel-2**: 10m resolution, optical bands
- Additional sensors can be configured

## Troubleshooting

### Earth Engine Authentication Issues

1. Make sure you have signed up for Earth Engine access
2. Run `earthengine authenticate` to set up authentication
3. Check that your Google Cloud project has Earth Engine enabled

### Import Errors

1. Ensure all required packages are installed: `pip install -r requirements.txt`
2. Check that you're running Python 3.8 or higher
3. Verify the project structure is correct

### Processing Errors

1. Check that your bounding box coordinates are valid
2. Ensure the date range contains available data
3. Verify the sensor name is supported
4. Check that the output directory is writable

## Project Structure

```
dead the third/
├── dead_the_third/          # Main package
│   ├── __init__.py
│   ├── config.py           # Configuration management
│   ├── download_manager.py # Download and processing logic
│   ├── earth_engine.py     # Earth Engine operations
│   ├── errors.py           # Error handling
│   ├── gui.py             # GUI interface
│   ├── progress_tracker.py # Progress tracking
│   ├── types.py           # Type definitions
│   └── utils.py           # Utility functions
├── flutter_earth_6-19.py   # Main application entry point
├── test_basic.py          # Basic functionality tests
├── setup_earth_engine.py  # Earth Engine setup script
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Development

### Running Tests

```bash
python test_basic.py
```

### Adding New Sensors

1. Add sensor details to the `SATELLITE_DETAILS` dictionary in `config.py`
2. Implement sensor-specific processing in `earth_engine.py`
3. Update the GUI to include the new sensor option

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:

1. Check the troubleshooting section above
2. Run the test script to identify specific problems
3. Check the logs in the `logs/` directory
4. Ensure Earth Engine authentication is properly set up

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request 