Write-Host "Starting Flutter Earth Desktop Application..." -ForegroundColor Green
Write-Host ""

Set-Location frontend
Write-Host "Changed to frontend directory" -ForegroundColor Yellow
Write-Host ""

Write-Host "Using local Node.js installation..." -ForegroundColor Yellow
& "..\node-v22.17.0-win-x64\npm.cmd" start

Read-Host "Press Enter to continue" 