# Google Earth Engine Setup Guide

This guide explains how to set up Google Earth Engine authentication and configuration for Flutter Earth.

## Prerequisites

### Required Accounts
- **Google Account**: A Google account is required
- **Earth Engine Account**: Sign up for Google Earth Engine access
- **Google Cloud Project**: Optional but recommended for advanced features

### System Requirements
- **Python 3.8+**: Required for Earth Engine Python API
- **Internet Connection**: Required for Earth Engine API access
- **Sufficient Storage**: At least 1GB free space for data downloads

## Step 1: Earth Engine Account Setup

### 1.1 Sign Up for Earth Engine
1. Visit [Google Earth Engine](https://earthengine.google.com/)
2. Click "Sign up for Earth Engine"
3. Fill out the application form:
   - **Purpose**: Select "Research" or "Education"
   - **Use Case**: Describe your intended use
   - **Data Requirements**: Specify what data you need
4. Submit the application
5. Wait for approval (usually 1-3 business days)

### 1.2 Verify Account Access
1. Check your email for approval notification
2. Log in to [Earth Engine Code Editor](https://code.earthengine.google.com/)
3. Verify you can access the platform
4. Note your Earth Engine username

## Step 2: Python Environment Setup

### 2.1 Install Python Dependencies
```bash
# Install required packages
pip install earthengine-api
pip install google-auth
pip install google-auth-oauthlib
pip install google-auth-httplib2
```

### 2.2 Verify Installation
```python
import ee
print("Earth Engine API version:", ee.__version__)
```

## Step 3: Authentication Setup

### 3.1 Service Account (Recommended for Production)

#### Create Service Account
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing project
3. Enable Earth Engine API:
   - Go to "APIs & Services" > "Library"
   - Search for "Earth Engine API"
   - Click "Enable"
4. Create service account:
   - Go to "IAM & Admin" > "Service Accounts"
   - Click "Create Service Account"
   - Name: `earth-engine-service`
   - Description: `Service account for Earth Engine access`
5. Grant permissions:
   - Role: "Earth Engine Resource Viewer"
   - Role: "Earth Engine Resource User"
6. Create and download key:
   - Click on the service account
   - Go to "Keys" tab
   - Click "Add Key" > "Create new key"
   - Choose "JSON" format
   - Download the key file

#### Configure Service Account
1. Save the JSON key file securely
2. Set environment variable:
   ```bash
   # Windows
   set GOOGLE_APPLICATION_CREDENTIALS=path\to\service-account-key.json
   
   # Linux/Mac
   export GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-key.json
   ```

### 3.2 Personal Authentication (Development)

#### Install Earth Engine CLI
```bash
# Install Earth Engine CLI
pip install earthengine-api

# Authenticate
earthengine authenticate
```

#### Follow Authentication Flow
1. Run the authentication command
2. Open the provided URL in your browser
3. Sign in with your Google account
4. Grant Earth Engine permissions
5. Copy the authorization code
6. Paste the code in the terminal

## Step 4: Flutter Earth Configuration

### 4.1 Configure Authentication in Flutter Earth

#### Using Service Account
1. Place your service account JSON file in the project
2. Update configuration in `flutter_earth_pkg/flutter_earth/config.py`:
   ```python
   EARTH_ENGINE_CONFIG = {
       'service_account_file': 'path/to/service-account-key.json',
       'project_id': 'your-project-id'
   }
   ```

#### Using Personal Authentication
1. Ensure you've completed `earthengine authenticate`
2. The application will use your personal credentials automatically

### 4.2 Test Configuration
```python
import ee

# Initialize Earth Engine
ee.Initialize()

# Test with a simple dataset
dataset = ee.ImageCollection('USGS/SRTMGL1_003')
print("Earth Engine connection successful!")
```

## Step 5: Advanced Configuration

### 5.1 Google Cloud Project Setup

#### Enable Required APIs
1. **Earth Engine API**: For Earth Engine access
2. **Cloud Storage API**: For data export (optional)
3. **Compute Engine API**: For processing (optional)

#### Set Up Billing
1. Enable billing for your Google Cloud project
2. Set up budget alerts to avoid unexpected charges
3. Monitor usage in Google Cloud Console

### 5.2 Environment Variables
```bash
# Required
export GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-key.json

# Optional
export EARTH_ENGINE_PROJECT_ID=your-project-id
export EARTH_ENGINE_SERVICE_ACCOUNT=your-service-account@project.iam.gserviceaccount.com
```

### 5.3 Configuration File
Create `earth_engine_config.json`:
```json
{
  "service_account_file": "path/to/service-account-key.json",
  "project_id": "your-project-id",
  "region": "us-central1",
  "max_retries": 3,
  "timeout": 300
}
```

## Step 6: Testing and Validation

### 6.1 Basic Connection Test
```python
import ee

try:
    ee.Initialize()
    print("✅ Earth Engine connection successful")
    
    # Test data access
    dataset = ee.ImageCollection('USGS/SRTMGL1_003')
    print(f"✅ Dataset access successful: {dataset.size().getInfo()} images")
    
except Exception as e:
    print(f"❌ Earth Engine connection failed: {e}")
```

### 6.2 Data Download Test
```python
import ee
from datetime import datetime

# Initialize
ee.Initialize()

# Test download
image = ee.Image('USGS/SRTMGL1_003').select('elevation')
region = ee.Geometry.Rectangle([-122.5, 37.5, -122.0, 38.0])

# Export to drive
task = ee.batch.Export.image.toDrive(
    image=image,
    description='test_export',
    folder='earth_engine_exports',
    region=region,
    scale=30
)

task.start()
print("✅ Export task started successfully")
```

### 6.3 Flutter Earth Integration Test
1. Start Flutter Earth application
2. Go to Settings > Earth Engine
3. Test authentication status
4. Try downloading a small dataset
5. Verify data appears in the interface

## Troubleshooting

### Common Issues

#### Authentication Errors
**Problem**: "Authentication failed" or "Invalid credentials"
**Solutions**:
1. Verify service account JSON file path
2. Check environment variables
3. Ensure Earth Engine API is enabled
4. Verify account has Earth Engine access

#### Permission Errors
**Problem**: "Insufficient permissions" or "Access denied"
**Solutions**:
1. Check service account roles
2. Verify project permissions
3. Ensure Earth Engine access is granted
4. Check billing status

#### Network Errors
**Problem**: "Connection timeout" or "Network error"
**Solutions**:
1. Check internet connection
2. Verify firewall settings
3. Try different network
4. Check Google Cloud status

#### Quota Errors
**Problem**: "Quota exceeded" or "Rate limit exceeded"
**Solutions**:
1. Check Earth Engine quotas
2. Implement rate limiting
3. Use batch processing
4. Contact Google support

### Debug Information

#### Enable Debug Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)

import ee
ee.Initialize()
```

#### Check Account Status
```python
import ee
ee.Initialize()

# Check user info
user_info = ee.data.getAssetRoots()
print("User info:", user_info)
```

#### Verify Permissions
```python
import ee
ee.Initialize()

# List accessible datasets
datasets = ee.data.listAssets('users/')
print("Accessible datasets:", datasets)
```

## Best Practices

### Security
1. **Secure Storage**: Store service account keys securely
2. **Environment Variables**: Use environment variables for sensitive data
3. **Access Control**: Limit service account permissions
4. **Regular Rotation**: Rotate service account keys regularly

### Performance
1. **Batch Processing**: Use batch operations for large datasets
2. **Caching**: Implement local caching for frequently used data
3. **Rate Limiting**: Respect API rate limits
4. **Resource Management**: Monitor and optimize resource usage

### Monitoring
1. **Usage Tracking**: Monitor API usage and costs
2. **Error Logging**: Implement comprehensive error logging
3. **Health Checks**: Regular connection health checks
4. **Alerting**: Set up alerts for failures and quota limits

## Support and Resources

### Official Documentation
- [Earth Engine Documentation](https://developers.google.com/earth-engine)
- [Python API Guide](https://developers.google.com/earth-engine/guides/python_install)
- [Authentication Guide](https://developers.google.com/earth-engine/guides/service_account)

### Community Resources
- [Earth Engine Community](https://groups.google.com/g/google-earth-engine-developers)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/google-earth-engine)
- [GitHub Examples](https://github.com/google/earthengine-api)

### Getting Help
1. **Check Documentation**: Review official documentation first
2. **Search Community**: Look for similar issues in community forums
3. **Create Minimal Example**: Create a minimal example to reproduce the issue
4. **Contact Support**: Contact Google Earth Engine support for account issues

## Conclusion

Proper Earth Engine setup is essential for Flutter Earth functionality. Follow this guide carefully to ensure reliable access to Earth Engine data and services. Regular monitoring and maintenance will help maintain optimal performance and avoid common issues.

### Next Steps
1. Complete the setup process
2. Test with sample data
3. Configure advanced features as needed
4. Monitor usage and performance
5. Set up automated monitoring and alerting

Happy Earth Engine development! 🌍✨ 