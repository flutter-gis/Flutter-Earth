# Flutter Earth - Cleanup Script
# Removes unnecessary files and cleans up Dear PyGui application

Write-Host "========================================" -ForegroundColor Green
Write-Host "   FLUTTER EARTH - CLEANUP SCRIPT" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

$filesToRemove = @(
    "startup.lock",
    "console_log.txt"
)

$directoriesToClean = @(
    "__pycache__",
    "logs",
    "temp"
)

Write-Host "[INFO] Starting cleanup process..." -ForegroundColor Yellow

# Remove specified files
foreach ($file in $filesToRemove) {
    if (Test-Path $file) {
        Remove-Item $file -Force
        Write-Host "[REMOVED] $file" -ForegroundColor Red
    }
}

# Clean directories
foreach ($dir in $directoriesToClean) {
    if (Test-Path $dir) {
        Remove-Item $dir -Recurse -Force
        Write-Host "[REMOVED] $dir" -ForegroundColor Red
    }
}

# Recreate necessary directories
Write-Host "[INFO] Recreating necessary directories..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path "logs" -Force | Out-Null
New-Item -ItemType Directory -Path "temp" -Force | Out-Null

Write-Host ""
Write-Host "[SUCCESS] Cleanup completed!" -ForegroundColor Green
Write-Host ""
Write-Host "Application is ready for Dear PyGui startup" -ForegroundColor Cyan
Write-Host ""
Read-Host "Press Enter to continue" 