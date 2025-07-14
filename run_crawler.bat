@echo off
title Enhanced Earth Engine Data Catalog Crawler
echo ========================================
echo Enhanced Earth Engine Data Catalog Crawler
echo ========================================
echo.
echo Starting the enhanced crawler with image link extraction...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

REM Check if required packages are installed
echo Checking required packages...
python -c "import tkinter, requests, json, gzip, bs4, asyncio" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install -r requirements_crawler.txt
    echo.
)

REM Create necessary directories
if not exist "logs" mkdir logs
if not exist "backend\backend\crawler_data" mkdir "backend\backend\crawler_data"
if not exist "satellite_thumbnails" mkdir satellite_thumbnails

REM Check if HTML file exists
if not exist "gee cat\*.html" (
    echo ERROR: No HTML files found in 'gee cat' directory
    echo Please ensure the Earth Engine catalog HTML file is downloaded
    pause
    exit /b 1
)

echo Found HTML files in 'gee cat' directory
echo.

REM Test the updated crawler logic first
echo Testing updated crawler logic...
python test_updated_crawler.py
if errorlevel 1 (
    echo ERROR: Crawler logic test failed
    pause
    exit /b 1
)

echo.
echo Crawler logic test passed! Starting main crawler...
echo.

REM Run the enhanced crawler with GUI
echo Starting Enhanced Earth Engine Crawler with GUI...
echo This will extract all dataset information from the HTML file
echo and process each dataset page to generate download scripts.
echo.
python crawler_gui_enhanced.py

REM Check if the script ran successfully
if errorlevel 1 (
    echo.
    echo ERROR: The crawler encountered an error
    echo Check the logs for more information
    pause
    exit /b 1
)

echo.
echo Enhanced crawler completed successfully!
echo.
echo Data files created:
if exist "backend\backend\crawler_data\gee_catalog_data_enhanced.json.gz" (
    echo - Main catalog: backend\backend\crawler_data\gee_catalog_data_enhanced.json.gz
)
if exist "backend\backend\crawler_data\dataset_*.json" (
    echo - Individual dataset files: backend\backend\crawler_data\dataset_*.json
)
if exist "satellite_thumbnails\*.png" (
    echo - Thumbnail images: satellite_thumbnails\
)
echo.
pause 