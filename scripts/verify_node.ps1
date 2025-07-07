# Verify Local Node.js Installation
# This script checks if the local Node.js installation is working correctly

Write-Host "========================================" -ForegroundColor Green
Write-Host "   NODE.JS VERIFICATION SCRIPT" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Get the project root directory
$projectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$nodeDir = Join-Path $projectRoot "node-v22.17.0-win-x64"
$nodeExe = Join-Path $nodeDir "node.exe"
$npmExe = Join-Path $nodeDir "npm.cmd"

Write-Host "Project Root: $projectRoot" -ForegroundColor Cyan
Write-Host "Node.js Directory: $nodeDir" -ForegroundColor Cyan
Write-Host ""

# Check if Node.js directory exists
if (!(Test-Path $nodeDir)) {
    Write-Host "[ERROR] Node.js directory not found: $nodeDir" -ForegroundColor Red
    exit 1
}

# Check if node.exe exists
if (!(Test-Path $nodeExe)) {
    Write-Host "[ERROR] node.exe not found: $nodeExe" -ForegroundColor Red
    exit 1
}

# Check if npm.cmd exists
if (!(Test-Path $npmExe)) {
    Write-Host "[ERROR] npm.cmd not found: $npmExe" -ForegroundColor Red
    exit 1
}

Write-Host "[SUCCESS] Node.js files found" -ForegroundColor Green

# Set PATH to include local Node.js
$env:PATH = "$nodeDir;$env:PATH"

# Test Node.js version
try {
    $nodeVersion = & "$nodeExe" --version 2>&1
    Write-Host "[SUCCESS] Node.js version: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Failed to get Node.js version: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test npm version
try {
    $npmVersion = & "$npmExe" --version 2>&1
    Write-Host "[SUCCESS] npm version: $npmVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Failed to get npm version: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test if npm can list packages in frontend directory
$frontendDir = Join-Path $projectRoot "frontend"
if (Test-Path $frontendDir) {
    Write-Host ""
    Write-Host "Testing npm in frontend directory..." -ForegroundColor Yellow
    
    try {
        Set-Location $frontendDir
        $packageList = & "$npmExe" list --depth=0 2>&1
        Write-Host "[SUCCESS] npm list command works" -ForegroundColor Green
        
        # Check if Electron is installed
        if ($packageList -match "electron") {
            Write-Host "[SUCCESS] Electron is installed" -ForegroundColor Green
        } else {
            Write-Host "[WARNING] Electron not found in package list" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "[ERROR] npm list failed: $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "[WARNING] Frontend directory not found: $frontendDir" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "   VERIFICATION COMPLETE" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Local Node.js installation is working correctly!" -ForegroundColor Green
Write-Host ""
Read-Host "Press Enter to continue" 