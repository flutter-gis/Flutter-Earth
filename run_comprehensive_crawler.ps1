# Comprehensive Web Crawler - PowerShell Launcher
# ==============================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Comprehensive Web Crawler" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python and try again" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if required packages are installed
Write-Host "Checking required packages..." -ForegroundColor Yellow
try {
    python -c "import requests, bs4, lxml" 2>$null
    Write-Host "Required packages found" -ForegroundColor Green
} catch {
    Write-Host "Installing required packages..." -ForegroundColor Yellow
    try {
        pip install requests beautifulsoup4 lxml
        Write-Host "Packages installed successfully" -ForegroundColor Green
    } catch {
        Write-Host "ERROR: Failed to install required packages" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Check if tkinter is available (for GUI)
try {
    python -c "import tkinter" 2>$null
    Write-Host "GUI mode available" -ForegroundColor Green
} catch {
    Write-Host "WARNING: tkinter not available, running in console mode" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Starting Comprehensive Web Crawler..." -ForegroundColor Green
Write-Host ""

# Run the crawler
try {
    python comprehensive_crawler.py
} catch {
    Write-Host "ERROR: Failed to run crawler" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}

Write-Host ""
Write-Host "Crawler finished. Press Enter to exit..." -ForegroundColor Cyan
Read-Host 