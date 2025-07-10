@echo off
title Enhanced Earth Engine Data Catalog Crawler
echo ========================================
echo Enhanced Earth Engine Data Catalog Crawler
echo ========================================
echo.
echo Starting the enhanced crawler application...
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
python -c "import tkinter, requests, json, gzip, bs4" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install -r requirements_crawler.txt
    echo.
)

REM Create logs directory if it doesn't exist
if not exist "logs" mkdir logs

REM Run the crawler
echo Starting Enhanced Earth Engine Crawler GUI...
echo.
python crawler_gui.py

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
pause 