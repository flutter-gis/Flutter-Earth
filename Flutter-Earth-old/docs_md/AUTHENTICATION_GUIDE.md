# Flutter Earth Authentication Guide

## 🔐 **Understanding Authentication**

Flutter Earth uses Google Earth Engine (GEE) to access satellite imagery and geospatial data. To use these features, you need to authenticate with Google Cloud.

## 📋 **Current Status**

### **Test Mode (Default)**
- ✅ **App Status**: Ready to use (UI features work)
- ⚠️ **Earth Engine**: Test credentials detected
- 📝 **Next Step**: Set up real Google Cloud credentials

### **Fully Authenticated Mode**
- ✅ **App Status**: Full functionality available
- ✅ **Earth Engine**: Connected and ready
- 🎯 **Features**: All satellite data access enabled

## 🚀 **Quick Setup (Recommended)**

### **Option 1: Use the App Interface**
1. **Launch Flutter Earth**
2. **Click the 🔐 button** in the top toolbar
3. **Enter your Google Cloud Project ID**
4. **Select your service account JSON key file**
5. **Click "Test Connection"**
6. **Click "Save" if test passes**

### **Option 2: Use Environment Variables**
```bash
# Set these environment variables before starting the app
set FLUTTER_EARTH_PROJECT_ID=your-project-id
set FLUTTER_EARTH_KEY_FILE=C:\path\to\your\service-account-key.json
```

## 🔧 **Detailed Setup Instructions**

### **Step 1: Create Google Cloud Project**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing project
3. Note your **Project ID** (you'll need this)

### **Step 2: Enable Earth Engine API**
1. In Google Cloud Console, go to **APIs & Services > Library**
2. Search for **"Earth Engine API"**
3. Click **Enable**

### **Step 3: Create Service Account**
1. Go to **IAM & Admin > Service Accounts**
2. Click **"Create Service Account"**
3. **Name**: `flutter-earth-service`
4. **Description**: `Service account for Flutter Earth`
5. Click **"Create and Continue"**

### **Step 4: Grant Permissions**
1. **Add Role**: `Earth Engine Resource Viewer`
2. **Add Role**: `Earth Engine Resource User`
3. Click **"Continue"**
4. Click **"Done"**

### **Step 5: Create and Download Key**
1. Click on your service account
2. Go to **"Keys"** tab
3. Click **"Add Key" > "Create new key"**
4. Choose **"JSON"** format
5. Click **"Create"**
6. **Save the downloaded file** (keep it secure!)

### **Step 6: Configure Flutter Earth**
1. **Launch Flutter Earth**
2. **Click 🔐** (authentication button)
3. **Project ID**: Enter your Google Cloud Project ID
4. **Key File**: Select the downloaded JSON file
5. **Test Connection**: Verify it works
6. **Save**: Store credentials securely

## 🔍 **Troubleshooting**

### **"Incorrect padding" Error**
- **Cause**: Corrupted or malformed service account key
- **Solution**: Download a fresh key file from Google Cloud Console

### **"Authentication failed" Error**
- **Check**: Project ID is correct
- **Check**: Key file is valid JSON
- **Check**: Service account has Earth Engine permissions
- **Check**: Earth Engine API is enabled

### **"Connection timeout" Error**
- **Check**: Internet connection
- **Check**: Firewall settings
- **Check**: Google Cloud project is active

### **"Permission denied" Error**
- **Check**: Service account has correct roles
- **Check**: Earth Engine API is enabled
- **Check**: Project has billing enabled

## 📁 **File Locations**

### **Windows**
- **Auth Directory**: `C:\FE Auth\`
- **Config File**: `C:\FE Auth\auth_config.json`
- **Key File**: `C:\FE Auth\service_account_key.json`
- **Status File**: `C:\FE Auth\auth_status.json`

### **macOS/Linux**
- **Auth Directory**: `~/FE Auth/`
- **Config File**: `~/FE Auth/auth_config.json`
- **Key File**: `~/FE Auth/service_account_key.json`
- **Status File**: `~/FE Auth/auth_status.json`

## 🔒 **Security Notes**

### **Best Practices**
- ✅ Keep your service account key secure
- ✅ Don't share your key file
- ✅ Use environment variables in production
- ✅ Regularly rotate your keys
- ✅ Monitor usage in Google Cloud Console

### **What Flutter Earth Does**
- ✅ Copies your key to a secure local directory
- ✅ Never transmits keys over the internet
- ✅ Stores credentials locally only
- ✅ Validates credentials before use

## 🎯 **Feature Availability**

### **Without Authentication**
- ✅ **UI Navigation**: All interface features work
- ✅ **Theme System**: 35+ themes available
- ✅ **Settings**: App configuration
- ✅ **Help**: Documentation and guides

### **With Authentication**
- ✅ **All above features** plus:
- 🛰️ **Satellite Data**: Browse Earth Engine catalog
- 📥 **Downloads**: Download satellite imagery
- 🔍 **Analysis**: Perform geospatial analysis
- 📊 **Data Viewer**: View and process data

## 🆘 **Getting Help**

### **Common Issues**
1. **"Test credentials detected"**: You need real Google Cloud credentials
2. **"Key file not found"**: Check the file path is correct
3. **"Project ID invalid"**: Verify your Google Cloud Project ID
4. **"API not enabled"**: Enable Earth Engine API in Google Cloud Console

### **Support Resources**
- **Google Cloud Documentation**: [Earth Engine Setup](https://developers.google.com/earth-engine/guides/service_account)
- **Flutter Earth Logs**: Check `logs/` directory for detailed error messages
- **Debug Tools**: Run `python debug_auth_issue.py` for diagnostics

## 🎉 **Success Indicators**

When authentication is working correctly, you should see:
- ✅ **Status**: "Connected to Earth Engine"
- ✅ **Satellite Info**: Browse satellite catalog
- ✅ **Download**: Configure and start downloads
- ✅ **No Error Messages**: Clean startup without auth errors

---

**Need help?** The authentication system is designed to be user-friendly and secure. If you encounter issues, the app provides clear error messages and the debug tools can help identify problems. 