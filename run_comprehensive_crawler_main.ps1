# Comprehensive Web Crawler - Main PowerShell Launcher
# ==============================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Comprehensive Web Crawler" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Change to web_crawler directory and run the crawler
Set-Location "web_crawler"
& ".\run_comprehensive_crawler.ps1"

Write-Host ""
Write-Host "Returning to main directory..." -ForegroundColor Green
Set-Location ".." 