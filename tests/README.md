# Tests Directory

This directory contains all test files for the Flutter Earth project.

## Contents

### UI Tests
- **`test_satellite_catalog_ui.spec.js`** - Playwright test for satellite catalog UI functionality
- **`satellite_info_test.html`** - Test interface for satellite catalog and crawler functionality
- **`test_themes.html`** - Theme testing interface for validating theme functionality

### Integration Tests
- **`test_download_flow.py`** - Python test for the complete download workflow from Earth Engine to local storage

## Running Tests

### UI Tests (Playwright)
```bash
# From the frontend directory
npm test

# Or directly with Playwright
npx playwright test tests/test_satellite_catalog_ui.spec.js
```

### Theme Tests
Open `tests/test_themes.html` in a web browser to test theme functionality.

### Satellite Info Tests
Open `tests/satellite_info_test.html` in a web browser to test satellite catalog functionality.

### Python Integration Tests
```bash
# From the project root
python tests/test_download_flow.py
```

## Test Coverage

- **UI Functionality**: Tab navigation, theme switching, satellite catalog interaction
- **Theme System**: Theme loading, switching, customization options
- **Download Workflow**: Complete Earth Engine to local storage pipeline
- **Error Handling**: Invalid inputs, network failures, authentication issues

## Adding New Tests

When adding new tests:
1. Place UI tests in this directory
2. Update the test script in `frontend/package.json` if needed
3. Document new test functionality in this README
4. Ensure tests follow the existing naming conventions

## Test Results

Test results and logs are stored in the `logs/` directory with timestamps for easy tracking and debugging. 