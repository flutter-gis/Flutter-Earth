# Flutter Earth Electron Launcher
Write-Host "Starting Flutter Earth Electron App..." -ForegroundColor Green
Write-Host "Using local Node.js: ..\node-v22.17.0-win-x64\node.exe" -ForegroundColor Cyan
Write-Host "Using local Electron: .\node_modules\electron\dist\electron.exe" -ForegroundColor Cyan

try {
    # Change to the frontend directory
    Set-Location $PSScriptRoot
    
    # Run Electron using local Node.js
    & "..\node-v22.17.0-win-x64\node.exe" ".\node_modules\electron\cli.js" "."
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: Failed to start Electron app (Exit code: $LASTEXITCODE)" -ForegroundColor Red
        Write-Host "Please check that all dependencies are installed correctly" -ForegroundColor Yellow
        Read-Host "Press Enter to continue"
    }
} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    Read-Host "Press Enter to continue"
} 