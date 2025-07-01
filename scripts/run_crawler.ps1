# Flutter Earth - Google Earth Engine Data Crawler
# This script runs the enhanced crawler to collect satellite data

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Flutter Earth - Data Crawler" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "This will collect satellite data from Google Earth Engine." -ForegroundColor White
Write-Host ""
Write-Host "What this does:" -ForegroundColor Yellow
Write-Host "• Connects to Google Earth Engine catalog" -ForegroundColor White
Write-Host "• Downloads comprehensive dataset information" -ForegroundColor White
Write-Host "• Extracts satellite details and capabilities" -ForegroundColor White
Write-Host "• Generates ready-to-use Earth Engine code snippets" -ForegroundColor White
Write-Host "• Takes 2-5 minutes depending on connection speed" -ForegroundColor White
Write-Host ""
Write-Host "The data will be saved to: backend\crawler_data\" -ForegroundColor White
Write-Host ""

$confirm = Read-Host "Do you want to start the data collection? (y/n)"
if ($confirm -ne "y" -and $confirm -ne "Y") {
    Write-Host ""
    Write-Host "Data collection cancelled." -ForegroundColor Yellow
    Read-Host "Press Enter to continue"
    exit
}

Write-Host ""
Write-Host "Starting data collection..." -ForegroundColor Green
Write-Host ""

Set-Location "backend"

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ and try again." -ForegroundColor Red
    Read-Host "Press Enter to continue"
    exit 1
}

# Check if required files exist
if (-not (Test-Path "gee_catalog_crawler_enhanced.py")) {
    Write-Host "ERROR: Crawler script not found: gee_catalog_crawler_enhanced.py" -ForegroundColor Red
    Read-Host "Press Enter to continue"
    exit 1
}

# Create crawler_data directory if it doesn't exist
if (-not (Test-Path "crawler_data")) {
    New-Item -ItemType Directory -Path "crawler_data" | Out-Null
}
if (-not (Test-Path "crawler_data\thumbnails")) {
    New-Item -ItemType Directory -Path "crawler_data\thumbnails" | Out-Null
}

Write-Host "Running enhanced crawler..." -ForegroundColor Green
Write-Host "This may take 2-5 minutes..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Progress will be shown below:" -ForegroundColor White
Write-Host "========================================" -ForegroundColor White

# Run the crawler
$startTime = Get-Date
python gee_catalog_crawler_enhanced.py
$exitCode = $LASTEXITCODE

if ($exitCode -ne 0) {
    Write-Host ""
    Write-Host "ERROR: Data collection failed!" -ForegroundColor Red
    Write-Host "Check the logs for more details." -ForegroundColor Red
    Read-Host "Press Enter to continue"
    exit 1
}

$endTime = Get-Date
$duration = $endTime - $startTime

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Data collection completed successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Duration: $($duration.Minutes)m $($duration.Seconds)s" -ForegroundColor White
Write-Host ""
Write-Host "Files created:" -ForegroundColor Yellow

if (Test-Path "crawler_data\gee_catalog_data_enhanced.json") {
    Write-Host "✓ gee_catalog_data_enhanced.json" -ForegroundColor Green
} else {
    Write-Host "✗ gee_catalog_data_enhanced.json (not found)" -ForegroundColor Red
}

if (Test-Path "catalog_viewer.html") {
    Write-Host "✓ catalog_viewer.html" -ForegroundColor Green
} else {
    Write-Host "✗ catalog_viewer.html (not found)" -ForegroundColor Red
}

Write-Host ""
Write-Host "You can now:" -ForegroundColor Yellow
Write-Host "• Open Flutter Earth and go to Satellite Info" -ForegroundColor White
Write-Host "• View the collected data in the satellite catalog" -ForegroundColor White
Write-Host "• Use the data for downloads and analysis" -ForegroundColor White
Write-Host ""
Read-Host "Press Enter to continue" 