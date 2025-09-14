# Flutter Earth - Enhanced Satellite Catalog Extractor

Write-Host "========================================" -ForegroundColor Green
Write-Host " 🛰️  FLUTTER EARTH - ENHANCED v3.0  🛰️" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[INFO] Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ and try again" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "[INFO] Starting Flutter Earth Dear PyGui v2.0..." -ForegroundColor Cyan
Write-Host ""

# Create logs directory if it doesn't exist
if (!(Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs" | Out-Null
}

# Check if required packages are installed
Write-Host "[INFO] Checking required packages..." -ForegroundColor Yellow

$required_packages = @("PySide6", "BeautifulSoup4", "requests", "lxml")

foreach ($package in $required_packages) {
    try {
        $package_name = $package.ToLower() -replace "beautifulsoup4", "bs4"
        python -c "import $package_name" 2>$null
        Write-Host "[INFO] $package found" -ForegroundColor Green
    } catch {
        Write-Host "[WARNING] $package not found, installing..." -ForegroundColor Yellow
        pip install $package
    }
}

# Start Enhanced Satellite Catalog Extractor
Write-Host "[INFO] Starting Enhanced Satellite Catalog Extractor..." -ForegroundColor Yellow
Start-Process -FilePath "cmd" -ArgumentList "/k", "cd /d '$PWD\web_crawler' && python lightweight_crawler.py" -WindowStyle Normal

Write-Host ""
Write-Host "[SUCCESS] Flutter Earth Enhanced UI is starting up!" -ForegroundColor Green
Write-Host ""
Write-Host "Application: Enhanced Satellite Catalog Extractor window will open automatically" -ForegroundColor Cyan
Write-Host "Features: Modern dark theme, enhanced UI, improved performance" -ForegroundColor Yellow
Write-Host ""
Read-Host "Press Enter to close this window" 