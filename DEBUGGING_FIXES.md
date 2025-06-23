# Flutter Earth QML Interface - Major Debugging Fixes

## Issues Fixed

### 1. **Duplicate Properties**
- **Issue**: Line 43 had duplicate `verticalAlignment: Text.AlignVCenter` property
- **Fix**: Removed the duplicate property

### 2. **Missing Palette Object**
- **Issue**: Code referenced `palette.windowBg` but no palette object was defined
- **Fix**: Changed to use direct property `windowBg`

### 3. **Missing Styled Components**
- **Issue**: Form controls (TextField, ComboBox, SpinBox, ProgressBar) had no styling
- **Fix**: Created styled components:
  - `StyledTextField`: Dark theme with proper borders and focus states
  - `StyledComboBox`: Custom dropdown with dark theme styling
  - `StyledSpinBox`: Number input with dark theme
  - `StyledProgressBar`: Progress bars with green accent color

### 4. **Missing Event Handlers**
- **Issue**: Buttons had no onClicked handlers
- **Fix**: Added proper event handlers for all buttons:
  - `handleSelectFromMap()`: For map selection (placeholder)
  - `handleLoadShapefile()`: Opens file dialog for shapefile selection
  - `handleBrowseOutput()`: Opens directory dialog for output selection
  - `handleStartDownload()`: Validates inputs and starts download
  - `handleCancelDownload()`: Cancels ongoing download

### 5. **Incomplete Dialog Styling**
- **Issue**: Dialogs had no proper dark theme styling
- **Fix**: Added background styling to both `appDialog` and `inputDialog` with:
  - Dark background color
  - Proper borders
  - Rounded corners

### 6. **Missing Bridge Methods**
- **Issue**: QML expected Python bridge methods that didn't exist
- **Fix**: Added missing methods to `FlutterEarthBridge`:
  - `show_file_dialog()`: For file/directory selection
  - `show_input_dialog()`: For text/number input
  - `log_message()`: For logging from QML
  - `get_application_info()`: For app information

### 7. **Missing Signal Connections**
- **Issue**: QML wasn't properly connected to Python signals
- **Fix**: Added proper signal connections for:
  - `onFileDialogResult`: Handles file dialog results
  - `onInputDialogResult`: Handles input dialog results

### 8. **Missing Dependencies**
- **Issue**: QML module dependency was missing
- **Fix**: Added `PyQt6-QtQml>=6.4.0` to requirements.txt

### 9. **Input Validation**
- **Issue**: No validation for user inputs before starting download
- **Fix**: Added comprehensive validation in `handleStartDownload()`:
  - Checks for required fields
  - Validates BBOX format
  - Parses coordinates properly

### 10. **Error Handling**
- **Issue**: No proper error handling in QML
- **Fix**: Added try-catch blocks and user-friendly error messages

## How to Run

### Prerequisites
1. Install Python dependencies:
```bash
cd flutter_earth
pip install -r requirements.txt
```

2. Ensure you have PyQt6 with QML support:
```bash
pip install PyQt6-QtQml
```

### Running the Application

#### Option 1: Main Application
```bash
python main.py
```

#### Option 2: Test Script (for debugging)
```bash
python test_qml.py
```

#### Option 3: Direct Module
```bash
cd flutter_earth
python -m src.flutter_earth.main
```

## Features

### UI Components
- **Dark Theme**: Modern dark interface with green accents
- **Responsive Layout**: Sidebar with tabs and main content area
- **Styled Controls**: All form controls have consistent dark theme styling
- **Progress Tracking**: Visual progress bars for download status
- **Log Console**: Real-time logging display

### Functionality
- **Area Selection**: BBOX input with validation
- **Date Range**: Start and end date selection
- **Satellite Selection**: Dropdown for satellite collections
- **Cloud Cover**: Configurable cloud cover percentage
- **Output Settings**: Format and directory selection
- **File Dialogs**: Native file/directory selection dialogs
- **Error Handling**: User-friendly error messages

### Bridge Communication
- **Python to QML**: Signals for status updates, progress, and dialogs
- **QML to Python**: Method calls for file operations, downloads, and logging
- **Real-time Updates**: Live progress and status updates

## Troubleshooting

### Common Issues

1. **QML not loading**:
   - Check that PyQt6-QtQml is installed
   - Verify QML file paths are correct
   - Check console for QML errors

2. **Bridge not working**:
   - Ensure `flutterEarth` object is registered in QML context
   - Check that bridge methods are properly exposed
   - Verify signal connections

3. **Styling issues**:
   - Check that all styled components are properly defined
   - Verify color properties are accessible
   - Ensure proper QML syntax

4. **File dialogs not working**:
   - Check PyQt6.QtWidgets import
   - Verify dialog types are correct
   - Check signal connections for results

### Debug Mode
Run with debug logging:
```bash
python -u main.py 2>&1 | tee debug.log
```

## Architecture

### QML Structure
```
main.qml
├── ApplicationWindow
├── Styled Components (Button, TextField, ComboBox, etc.)
├── Main Layout (RowLayout with Sidebar + Map Panel)
├── Tab System (Download, Satellite Info, Post-Processing)
├── Cards (Progress, Settings, Output, Log)
└── Dialogs (App Dialog, Input Dialog)
```

### Python Bridge
```
FlutterEarthBridge
├── Signals (to QML)
├── Methods (from QML)
├── File Operations
├── Download Management
└── Error Handling
```

### Manager Classes
- `ConfigManager`: Application configuration
- `EarthEngineManager`: Google Earth Engine integration
- `DownloadManager`: Download task management
- `ProgressTracker`: Progress monitoring

## Future Improvements

1. **Map Integration**: Add interactive map for area selection
2. **Shapefile Parsing**: Implement shapefile coordinate extraction
3. **Advanced Validation**: More comprehensive input validation
4. **Progress Details**: More granular progress reporting
5. **Error Recovery**: Better error handling and recovery
6. **Themes**: Support for multiple UI themes
7. **Accessibility**: Improve accessibility features 