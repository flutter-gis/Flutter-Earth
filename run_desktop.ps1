# Flutter Earth Desktop App Launcher (PowerShell)
# This script launches the Electron desktop application

Write-Host "Flutter Earth Desktop App" -ForegroundColor Cyan
Write-Host "=========================" -ForegroundColor Cyan
Write-Host ""

# Change to the frontend directory
Set-Location "frontend"

# Check if node_modules exists
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    & "..\node-v22.17.0-win-x64\npm.cmd" install
}

# Start the Electron app
Write-Host "Starting Flutter Earth Desktop App..." -ForegroundColor Green
& "..\node-v22.17.0-win-x64\npm.cmd" start 