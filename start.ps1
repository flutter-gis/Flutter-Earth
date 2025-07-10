# Flutter Earth - Dear PyGui PowerShell Startup Script

Write-Host "========================================" -ForegroundColor Green
Write-Host "   FLUTTER EARTH - DEAR PYGUI v2.0" -ForegroundColor Green
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
try {
    python -c "import dearpygui" 2>$null
    Write-Host "[INFO] Dear PyGui found" -ForegroundColor Green
} catch {
    Write-Host "[WARNING] Dear PyGui not found, installing..." -ForegroundColor Yellow
    pip install dearpygui
}

try {
    python -c "import matplotlib" 2>$null
    Write-Host "[INFO] Matplotlib found" -ForegroundColor Green
} catch {
    Write-Host "[WARNING] Matplotlib not found, installing..." -ForegroundColor Yellow
    pip install matplotlib
}

# Run startup coordinator
Write-Host "[INFO] Running startup coordinator..." -ForegroundColor Yellow
python startup_coordinator.py

# Start Dear PyGui application
Write-Host "[INFO] Starting Dear PyGui application..." -ForegroundColor Yellow
Start-Process -FilePath "cmd" -ArgumentList "/k", "cd /d $PWD && python main.py" -WindowStyle Normal

Write-Host ""
Write-Host "[SUCCESS] Flutter Earth is starting up!" -ForegroundColor Green
Write-Host ""
Write-Host "Application: Dear PyGui window will open automatically" -ForegroundColor Cyan
Write-Host ""
Read-Host "Press Enter to close this window" 