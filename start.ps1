# Flutter Earth - Enhanced v2.0 PowerShell Startup Script

Write-Host "========================================" -ForegroundColor Green
Write-Host "   FLUTTER EARTH - ENHANCED v2.0" -ForegroundColor Green
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

# Check if local Node.js is available
$nodePath = Join-Path $PWD "node-v22.17.0-win-x64\node.exe"
if (!(Test-Path $nodePath)) {
    Write-Host "[ERROR] Local Node.js not found at node-v22.17.0-win-x64\node.exe" -ForegroundColor Red
    Write-Host "Please ensure Node.js is properly installed in the project directory" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "[INFO] Local Node.js found" -ForegroundColor Green
Write-Host ""

# Set PATH to include local Node.js
$env:PATH = "$PWD\node-v22.17.0-win-x64;$env:PATH"

Write-Host "[INFO] Starting Flutter Earth Enhanced v2.0..." -ForegroundColor Cyan
Write-Host ""

# Create logs directory if it doesn't exist
if (!(Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs" | Out-Null
}

# Start Python backend
Write-Host "[INFO] Starting Python backend..." -ForegroundColor Yellow
Start-Process -FilePath "cmd" -ArgumentList "/k", "cd /d $PWD && python main.py" -WindowStyle Normal

# Wait a moment for backend to start
Start-Sleep -Seconds 3

# Start Electron frontend using local Node.js
Write-Host "[INFO] Starting Electron frontend..." -ForegroundColor Yellow
Set-Location frontend
Start-Process -FilePath "cmd" -ArgumentList "/k", "npm start" -WindowStyle Normal

Write-Host ""
Write-Host "[SUCCESS] Flutter Earth is starting up!" -ForegroundColor Green
Write-Host ""
Write-Host "Backend: http://localhost:5000" -ForegroundColor Cyan
Write-Host "Frontend: Electron app will open automatically" -ForegroundColor Cyan
Write-Host ""
Read-Host "Press Enter to close this window" 