# New Authentication Logic Implementation

## Overview

The new authentication system provides a clean, centralized approach to managing Google Earth Engine credentials with proper startup integration and conflict-free operation.

## Key Features

- **Centralized Storage**: All auth data stored in dedicated `FE Auth` directory
- **Startup Integration**: Auth is checked and initialized during application startup
- **Conflict-Free**: Single source of truth for credentials
- **Comprehensive Status Tracking**: Real-time auth status monitoring
- **Error Handling**: Robust error handling with clear user feedback
- **Backward Compatibility**: Supports environment variables as fallback

## Directory Structure

### FE Auth Directory
The system creates a dedicated authentication folder:
- **Windows**: `C:\FE Auth\`
- **macOS**: `/Users/username/FE Auth/`
- **Linux**: `/home/username/FE Auth/`

### File Structure
```
FE Auth/
├── auth_config.json      # Main auth configuration
├── auth_status.json      # Current auth status
└── service_account_key.json  # Copied service account key
```

## Authentication Flow

### 1. Application Startup
1. **Auth System Initialization**: AuthManager is created and loads existing credentials
2. **Status Check**: System checks if valid credentials exist
3. **Earth Engine Initialization**: If credentials exist, Earth Engine is initialized
4. **Status Reporting**: Auth status is reported to the UI

### 2. Authentication Required
1. **Auth Dialog**: If no credentials found, auth dialog is shown
2. **Credential Entry**: User provides project ID and JSON key file
3. **Connection Test**: System tests the connection before saving
4. **Credential Storage**: Valid credentials are saved to FE Auth directory
5. **Earth Engine Init**: Earth Engine is initialized with new credentials

### 3. Ongoing Operation
1. **Health Checks**: Regular connection health monitoring
2. **Status Updates**: Real-time auth status updates
3. **Error Recovery**: Automatic error handling and recovery

## Implementation Details

### AuthManager Class

The `AuthManager` class provides the core authentication functionality:

```python
class AuthManager(QObject):
    # Signals for UI updates
    credentialsChanged = Signal()
    authStatusChanged = Signal(bool)
    testResult = Signal(bool, str)
    errorOccurred = Signal(str)
    successOccurred = Signal(str)
```

#### Key Methods

- `load_credentials()`: Load credentials from auth config
- `save_credentials(project_id, key_file)`: Save and validate credentials
- `initialize_earth_engine()`: Initialize Earth Engine with credentials
- `test_connection(project_id, key_file)`: Test connection before saving
- `has_credentials()`: Check if valid credentials exist
- `needs_authentication()`: Check if auth setup is required
- `get_auth_info()`: Get comprehensive auth status

### EarthEngineManager Integration

The `EarthEngineManager` works seamlessly with the new auth system:

```python
class EarthEngineManager:
    def __init__(self):
        self.auth_manager = AuthManager()
    
    def initialize(self):
        # Check auth status first
        if not self.auth_manager.has_credentials():
            return {"status": "auth_required", ...}
        
        # Initialize with stored credentials
        success, message = self.auth_manager.initialize_earth_engine()
        return {"status": "online" if success else "error", ...}
```

## Configuration Files

### auth_config.json
```json
{
  "project_id": "your-project-id",
  "key_file": "C:/FE Auth/service_account_key.json",
  "created_at": "2024-01-01T00:00:00",
  "version": "2.0"
}
```

### auth_status.json
```json
{
  "is_authenticated": true,
  "project_id": "your-project-id",
  "last_updated": "2024-01-01T00:00:00"
}
```

## Frontend Integration

### JavaScript API
The frontend communicates with the auth system through Electron IPC:

```javascript
// Check auth status
const authCheck = await window.electronAPI.pythonAuthCheck();

// Test connection
const testResult = await window.electronAPI.pythonAuthTest(keyFile, projectId);

// Save credentials
const saveResult = await window.electronAPI.pythonAuth(keyFile, projectId);

// Get auth status
const authStatus = await window.electronAPI.pythonAuthStatus();
```

### Startup Sequence
1. **Auth Check**: Check if authentication is needed
2. **Dialog Display**: Show auth dialog if required
3. **Connection Test**: Test credentials before saving
4. **Initialization**: Initialize Earth Engine after successful auth
5. **Status Update**: Update UI with connection status

## Error Handling

### Common Error Scenarios

1. **No Credentials**: User needs to set up authentication
2. **Invalid Key File**: Key file is corrupted or invalid
3. **Network Issues**: Connection to Earth Engine fails
4. **Permission Issues**: Service account lacks required permissions
5. **Project Issues**: Project ID is invalid or not found

### Error Recovery

- **Automatic Retry**: System attempts to reinitialize on connection loss
- **Clear Error Messages**: User-friendly error messages with guidance
- **Graceful Degradation**: Application continues in offline mode if needed
- **Logging**: Comprehensive logging for debugging

## Security Considerations

### Credential Storage
- **Local Storage**: Credentials stored locally in FE Auth directory
- **File Permissions**: Key files have restricted permissions
- **No Network Transmission**: Credentials never sent over network
- **Automatic Cleanup**: Old credentials can be cleared

### Best Practices
- **Service Account**: Use dedicated service account for Earth Engine
- **Minimal Permissions**: Grant only necessary permissions
- **Regular Rotation**: Rotate service account keys periodically
- **Secure Storage**: Keep key files in secure location

## Migration from Old System

### Automatic Migration
The new system automatically migrates from old auth systems:
1. **Legacy Support**: Checks old auth file locations
2. **Environment Variables**: Supports existing environment variables
3. **Backward Compatibility**: Maintains compatibility with old configs

### Manual Migration
If automatic migration fails:
1. **Export Credentials**: Export from old system
2. **Import to New**: Use new auth dialog to import
3. **Verify Connection**: Test connection after migration
4. **Clean Up**: Remove old auth files

## Troubleshooting

### Common Issues

1. **"Authentication Required" Message**
   - Check if credentials exist in FE Auth directory
   - Verify key file is valid and accessible
   - Ensure project ID is correct

2. **"Connection Test Failed"**
   - Verify internet connection
   - Check Earth Engine service status
   - Validate service account permissions

3. **"Key File Not Found"**
   - Ensure key file path is correct
   - Check file permissions
   - Verify file is not corrupted

### Debug Information

Enable debug logging to get detailed information:
```python
logging.getLogger('flutter_earth.auth_setup').setLevel(logging.DEBUG)
```

### Support Commands

The system provides several commands for debugging:
- `auth-check`: Check authentication status
- `auth-test`: Test connection with credentials
- `auth-status`: Get comprehensive auth information

## Future Enhancements

### Planned Features
- **Multi-Project Support**: Support for multiple Earth Engine projects
- **Credential Encryption**: Encrypt stored credentials
- **Cloud Sync**: Sync credentials across devices
- **Advanced Permissions**: Granular permission management
- **Audit Logging**: Track authentication events

### API Extensions
- **REST API**: HTTP API for auth management
- **CLI Tools**: Command-line auth management
- **SDK Integration**: Native SDK support
- **Plugin System**: Extensible auth plugins 