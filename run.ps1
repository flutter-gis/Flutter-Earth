# Flutter Earth Launcher Script
Write-Host "Starting Flutter Earth..." -ForegroundColor Green

try {
    # Check if Python is available
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: Python not found. Please ensure Python is installed and in your PATH." -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    
    Write-Host "Python version: $pythonVersion" -ForegroundColor Yellow
    
    # Run the application
    python main.py
    
} catch {
    Write-Host "Error running Flutter Earth: $_" -ForegroundColor Red
    Write-Host "Please check the logs for more details." -ForegroundColor Yellow
} finally {
    Write-Host "Press Enter to exit..." -ForegroundColor Cyan
    Read-Host
} 