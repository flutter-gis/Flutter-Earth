# Flutter Earth Desktop App Launcher
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    Flutter Earth Desktop App" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Starting Flutter Earth..." -ForegroundColor Green
Write-Host "Using local Node.js and Electron (no internet required)" -ForegroundColor Yellow
Write-Host ""

try {
    # Change to the frontend directory
    Set-Location "$PSScriptRoot\frontend"
    
    Write-Host "Running: ..\node-v22.17.0-win-x64\node.exe .\node_modules\electron\cli.js ." -ForegroundColor Gray
    
    # Run the Electron app
    & "..\node-v22.17.0-win-x64\node.exe" ".\node_modules\electron\cli.js" "."
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "Error: App failed to start (Exit code: $LASTEXITCODE)" -ForegroundColor Red
        Write-Host "Check the console for error messages" -ForegroundColor Yellow
        Read-Host "Press Enter to continue"
    }
} catch {
    Write-Host ""
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    Read-Host "Press Enter to continue"
} 