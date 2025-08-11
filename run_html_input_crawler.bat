@echo off
title HTML Input Web Crawler
echo ========================================
echo    HTML Input Web Crawler
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

REM Check if required packages are installed
echo Checking required packages...
python -c "import requests, bs4, lxml" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install requests beautifulsoup4 lxml
    if errorlevel 1 (
        echo ERROR: Failed to install required packages
        pause
        exit /b 1
    )
)

echo Starting HTML Input Web Crawler...
echo.

REM Change to web_crawler directory and run the crawler
cd web_crawler
python html_input_crawler.py

echo.
echo Crawler finished. Press any key to exit...
pause >nul 