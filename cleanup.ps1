# Flutter Earth - Cleanup Script
# Removes duplicate and unnecessary files

Write-Host "========================================" -ForegroundColor Green
Write-Host "   FLUTTER EARTH - CLEANUP SCRIPT" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

$filesToRemove = @(
    "frontend\map_selector.html",
    "frontend\themes.md",
    "frontend\theme_effects.md",
    "frontend\tabs.md",
    "frontend\cleanup_themes.py",
    "frontend\convert_themes_json_to_js.py",
    "frontend\theme_converter.py",
    "frontend\tailwind.config.js",
    "frontend\preload.js",
    "frontend\main_electron.js"
)

$directoriesToClean = @(
    "frontend\dist",
    "frontend\node_modules",
    "__pycache__"
)

Write-Host "[INFO] Starting cleanup process..." -ForegroundColor Yellow

# Remove specified files
foreach ($file in $filesToRemove) {
    if (Test-Path $file) {
        Remove-Item $file -Force
        Write-Host "[REMOVED] $file" -ForegroundColor Red
    }
}

# Clean directories (but keep node_modules for now as it's needed)
foreach ($dir in $directoriesToClean) {
    if ($dir -eq "frontend\node_modules") {
        Write-Host "[SKIPPED] $dir (needed for npm)" -ForegroundColor Yellow
        continue
    }
    
    if (Test-Path $dir) {
        Remove-Item $dir -Recurse -Force
        Write-Host "[REMOVED] $dir" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "[SUCCESS] Cleanup completed!" -ForegroundColor Green
Write-Host ""
Write-Host "Remaining files:" -ForegroundColor Cyan
Get-ChildItem -Path "frontend" -Name "*.html" | ForEach-Object { Write-Host "  $_" -ForegroundColor White }
Write-Host ""
Read-Host "Press Enter to continue" 