@echo off
REM Flutter Earth - Google Earth Engine Data Crawler
REM This script runs the enhanced crawler to collect satellite data

echo.
echo ========================================
echo    Flutter Earth - Data Crawler
echo ========================================
echo.
echo This will collect satellite data from Google Earth Engine.
echo.
echo What this does:
echo • Connects to Google Earth Engine catalog
echo • Downloads comprehensive dataset information
echo • Extracts satellite details and capabilities
echo • Generates ready-to-use Earth Engine code snippets
echo • Takes 2-5 minutes depending on connection speed
echo.
echo The data will be saved to: backend\crawler_data\
echo.

set /p confirm="Do you want to start the data collection? (y/n): "
if /i not "%confirm%"=="y" (
    echo.
    echo Data collection cancelled.
    pause
    exit /b
)

echo.
echo Starting data collection...
echo.

cd backend

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again.
    pause
    exit /b 1
)

REM Check if required files exist
if not exist "gee_catalog_crawler_enhanced.py" (
    echo ERROR: Crawler script not found: gee_catalog_crawler_enhanced.py
    pause
    exit /b 1
)

REM Create crawler_data directory if it doesn't exist
if not exist "crawler_data" mkdir crawler_data
if not exist "crawler_data\thumbnails" mkdir crawler_data\thumbnails

echo Running enhanced crawler...
echo This may take 2-5 minutes...
echo.
echo Progress will be shown below:
echo ========================================

python gee_catalog_crawler_enhanced.py

if errorlevel 1 (
    echo.
    echo ERROR: Data collection failed!
    echo Check the logs for more details.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Data collection completed successfully!
echo ========================================
echo.
echo Files created:
if exist "crawler_data\gee_catalog_data_enhanced.json" (
    echo ✓ gee_catalog_data_enhanced.json
) else (
    echo ✗ gee_catalog_data_enhanced.json (not found)
)

if exist "catalog_viewer.html" (
    echo ✓ catalog_viewer.html
) else (
    echo ✗ catalog_viewer.html (not found)
)

echo.
echo You can now:
echo • Open Flutter Earth and go to Satellite Info
echo • View the collected data in the satellite catalog
echo • Use the data for downloads and analysis
echo.
pause 