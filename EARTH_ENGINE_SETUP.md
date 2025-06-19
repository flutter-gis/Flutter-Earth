# Earth Engine Setup Guide

This guide will help you set up Google Earth Engine for use with Flutter Earth.

## Prerequisites

1. **Google Account**: You need a Google account
2. **Earth Engine Access**: You need to sign up for Earth Engine access
3. **Google Cloud Project**: You need a Google Cloud project with Earth Engine enabled

## Step-by-Step Setup

### 1. Sign up for Earth Engine Access

1. Visit: https://developers.google.com/earth-engine/guides/access
2. Click "Sign up for Earth Engine"
3. Fill out the application form
4. Wait for approval (usually takes 1-2 business days)

### 2. Create a Google Cloud Project

1. Go to: https://console.cloud.google.com/
2. Click "Select a project" → "New Project"
3. Give your project a name (e.g., "flutter-earth-project")
4. Click "Create"

### 3. Enable Earth Engine API

1. In your Google Cloud project, go to "APIs & Services" → "Library"
2. Search for "Earth Engine API"
3. Click on "Earth Engine API"
4. Click "Enable"

### 4. Set up Authentication

#### Option A: Using Python (Recommended)

```bash
# Install the Earth Engine API
pip install earthengine-api

# Authenticate (this will open a browser)
python -c "import ee; ee.Authenticate()"

# Initialize with your project
python -c "import ee; ee.Initialize(project='your-project-id')"
```

#### Option B: Using Command Line (if available)

```bash
# Install the Earth Engine API
pip install earthengine-api

# Authenticate
earthengine authenticate

# Set your project
earthengine set_project your-project-id
```

### 5. Test Your Setup

Run the test script to verify everything is working:

```bash
python test_basic.py
```

## Troubleshooting

### "No project found" Error

This error occurs when Earth Engine doesn't know which Google Cloud project to use.

**Solution:**
1. Make sure you have a Google Cloud project with Earth Engine API enabled
2. Initialize Earth Engine with your project ID:

```python
import ee
ee.Initialize(project='your-project-id')
```

### "PERMISSION_DENIED" Error

This error occurs when your account doesn't have the necessary permissions.

**Solution:**
1. Make sure you're signed up for Earth Engine access
2. Make sure you're using the correct Google account
3. Make sure your Google Cloud project has Earth Engine API enabled
4. Try re-authenticating:

```python
import ee
ee.Authenticate()
ee.Initialize(project='your-project-id')
```

### "Token has expired" Error

This error occurs when your authentication token has expired.

**Solution:**
Re-authenticate:

```python
import ee
ee.Authenticate()
ee.Initialize(project='your-project-id')
```

## Project ID Configuration

To avoid having to specify your project ID every time, you can:

1. **Set it in your code** (recommended for development):
   ```python
   import ee
   ee.Initialize(project='your-project-id')
   ```

2. **Set it as an environment variable**:
   ```bash
   # Windows
   set EARTHENGINE_PROJECT=your-project-id
   
   # Linux/Mac
   export EARTHENGINE_PROJECT=your-project-id
   ```

3. **Modify the application** to use your project ID by default

## Verification

To verify your setup is working, run this Python code:

```python
import ee
from ee import data as ee_data

# Initialize with your project
ee.Initialize(project='your-project-id')

# Test basic functionality
test_image = ee.Image('USGS/SRTMGL1_003')
bounds = test_image.geometry().bounds().getInfo()
print(f"Success! Test image bounds: {bounds}")
```

## Common Issues

### Windows-specific Issues

1. **Command not found**: The `earthengine` command might not be available on Windows. Use the Python authentication method instead.

2. **Path issues**: Make sure Python and pip are in your PATH.

### Authentication Issues

1. **Browser doesn't open**: Copy the URL from the terminal and paste it into your browser manually.

2. **Wrong account**: Make sure you're signed in with the correct Google account that has Earth Engine access.

### Project Issues

1. **Wrong project ID**: Make sure you're using the correct project ID from your Google Cloud console.

2. **API not enabled**: Make sure the Earth Engine API is enabled in your Google Cloud project.

## Getting Help

If you're still having issues:

1. Check the Earth Engine documentation: https://developers.google.com/earth-engine
2. Check the Earth Engine Python API documentation: https://developers.google.com/earth-engine/guides/python_install
3. Visit the Earth Engine forum: https://groups.google.com/g/google-earth-engine-developers

## Next Steps

Once Earth Engine is working:

1. Run the test script: `python test_basic.py`
2. Try the main application: `python flutter_earth_6-19.py`
3. Check the logs in the `logs/` directory for any issues 