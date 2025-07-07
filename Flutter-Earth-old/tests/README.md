# Tests

This directory contains all test files for Flutter Earth, including UI and integration tests.

## Types of Tests
- **UI Tests**: Playwright and HTML-based tests for frontend functionality
- **Integration Tests**: Python tests for backend and download workflows

## Running Tests
- UI: `npm test` (from frontend) or open HTML files in browser
- Integration: `python tests/test_download_flow.py`

## Coverage
- Tab navigation, theme switching, satellite catalog, download flow, error handling

## Adding Tests
- Place new tests in this directory
- Update this README with new test info

## See Also
- Main project README for architecture and workflow

## Contents

### UI Tests
- **`test_satellite_catalog_ui.spec.js`** - Playwright test for satellite catalog UI functionality
- **`satellite_info_test.html`** - Test interface for satellite catalog and crawler functionality
- **`test_themes.html`** - Theme testing interface for validating theme functionality

### Integration Tests
- **`test_download_flow.py`** - Python test for the complete download workflow from Earth Engine to local storage

## Test Results

Test results and logs are stored in the `logs/` directory with timestamps for easy tracking and debugging. 