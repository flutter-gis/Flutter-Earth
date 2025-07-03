# New Authentication Logic Implementation

## Overview

The new authentication logic implements a centralized approach to managing Google Earth Engine credentials using a dedicated "FE Auth" folder structure.

## How It Works

### 1. FE Auth Directory Structure

The system creates a dedicated authentication folder:
- **Windows**: `C:\FE Auth\`
- **macOS**: `/Users/username/FE Auth/`
- **Linux**: `/home/username/FE Auth/`

### 2. File Structure

```
FE Auth/
├── project_info.txt          # Contains project name and JSON key path
└── [copied-json-key].json   # The actual service account key file
```

### 3. Project Info File Format

The `project_info.txt` file contains:
```
project_name=your-project-id
json_key_path=C:\FE Auth\your-service-account-key.json
```

## Implementation Details

### Authentication Flow

1. **Startup Check**: On application startup, the system checks if `C:\FE Auth\project_info.txt` exists
2. **Auth Required**: If the file doesn't exist, the authentication dialog is shown
3. **Credential Entry**: User provides:
   - Project ID (Google Cloud Project)
   - JSON key file path (service account credentials)
4. **File Processing**: The system:
   - Copies the JSON key file to `C:\FE Auth\`
   - Creates `project_info.txt` with project name and key path
   - Updates legacy configuration files for backward compatibility
5. **Initialization**: Earth Engine initializes using the stored credentials

### Backward Compatibility

The system maintains backward compatibility by:
- Still checking legacy locations (`.flutter_earth` folder)
- Saving credentials to both new and legacy locations
- Supporting environment variables

### Key Methods

#### `needs_authentication()`
- Returns `True` if `C:\FE Auth\project_info.txt` doesn't exist
- Used to determine if auth dialog should be shown

#### `save_credentials(project_id, key_file)`
- Copies JSON key file to FE Auth directory
- Creates project_info.txt with project details
- Updates legacy configuration files

#### `load_credentials()`
- Prioritizes FE Auth folder over legacy locations
- Falls back to environment variables, legacy files, etc.

## Benefits

1. **Centralized Storage**: All auth files in one predictable location
2. **Cross-Platform**: Works on Windows, macOS, and Linux
3. **Secure**: JSON keys are copied to a dedicated folder
4. **User-Friendly**: Clear project name in text file
5. **Backward Compatible**: Existing installations continue to work

## Testing

Run the test script to verify the implementation:
```bash
python test_auth_logic.py
```

## Integration

The new logic is integrated into:
- Frontend JavaScript (`flutter_earth.js`)
- Backend Python (`earth_engine_processor.py`)
- Electron IPC handlers (`main_electron.js`, `preload.js`)

## Migration

Existing users will:
1. Continue using their current credentials (loaded from legacy locations)
2. Be prompted for authentication if they haven't set up credentials
3. Have their credentials automatically migrated to the new structure when they next authenticate 