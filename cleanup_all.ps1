# Comprehensive Cleanup Script for Flutter-Earth
# Removes log files, cache files, and unnecessary documentation
# Preserves GEE cat HTML files and essential project files

Write-Host "Starting comprehensive cleanup..." -ForegroundColor Green

# Remove all log files
Write-Host "Removing log files..." -ForegroundColor Yellow
Get-ChildItem -Recurse -Include *.log | Remove-Item -Force
Write-Host "Log files removed." -ForegroundColor Green

# Remove temporary and cache files
Write-Host "Removing temporary and cache files..." -ForegroundColor Yellow
Get-ChildItem -Recurse -Include *.tmp,*.cache,*.bak,*.old,*.temp | Remove-Item -Force
Write-Host "Temporary files removed." -ForegroundColor Green

# Remove unnecessary documentation files (keeping main README.md)
Write-Host "Removing unnecessary documentation files..." -ForegroundColor Yellow
$docsToRemove = @(
    "COMPREHENSIVE_DEBUG_OPTIMIZATION_SUMMARY.md",
    "COMPREHENSIVE_README.md", 
    "CRASH_PREVENTION_FINAL_SUMMARY.md",
    "MASSIVE_DEBUG_OPTIMIZATION_FINAL_SUMMARY.md",
    "TESSERACT_INSTALL_GUIDE.md",
    "ENHANCED_V2_README.md",
    "CRAWLER_README.md",
    "README_CRAWLER.md"
)

foreach ($doc in $docsToRemove) {
    if (Test-Path $doc) {
        Remove-Item $doc -Force
        Write-Host "Removed: $doc" -ForegroundColor Red
    }
}

# Remove docs directory contents (keeping the directory)
if (Test-Path "docs") {
    Get-ChildItem "docs" -Recurse | Remove-Item -Force
    Write-Host "Cleaned docs directory." -ForegroundColor Green
}

# Remove docs_md directory contents (keeping the directory)
if (Test-Path "docs_md") {
    Get-ChildItem "docs_md" -Recurse | Remove-Item -Force
    Write-Host "Cleaned docs_md directory." -ForegroundColor Green
}

# Remove unnecessary files from web_crawler
Write-Host "Cleaning web_crawler directory..." -ForegroundColor Yellow
$webCrawlerFilesToRemove = @(
    "FINAL_ENHANCEMENTS_SUMMARY.md",
    "FINAL_FIXES_SUMMARY.md", 
    "FINAL_LAUNCH_SUCCESS.md",
    "MASSIVE_ENHANCEMENTS_SUMMARY.md",
    "check_db.py",
    "comprehensive_cleanup.py",
    "comprehensive_debug.py",
    "comprehensive_none_fix_test.py",
    "debug_crawling.py",
    "debug_full.py",
    "integration_debug.py",
    "nonetype_test.py",
    "test_path.py"
)

foreach ($file in $webCrawlerFilesToRemove) {
    $path = "web_crawler/$file"
    if (Test-Path $path) {
        Remove-Item $path -Force
        Write-Host "Removed: $path" -ForegroundColor Red
    }
}

# Remove plugins directory contents (keeping the directory)
if (Test-Path "plugins") {
    Get-ChildItem "plugins" -Recurse | Remove-Item -Force
    Write-Host "Cleaned plugins directory." -ForegroundColor Green
}

# Remove test files that are not essential
Write-Host "Removing test files..." -ForegroundColor Yellow
$testFilesToRemove = @(
    "test_debug.html",
    "debug_test.py",
    "test_crawler.py",
    "crawler_output.txt"
)

foreach ($file in $testFilesToRemove) {
    if (Test-Path $file) {
        Remove-Item $file -Force
        Write-Host "Removed: $file" -ForegroundColor Red
    }
}

# Remove duplicate config files (keep the main ones)
if (Test-Path "optimized_crawler_config.yaml") {
    Remove-Item "optimized_crawler_config.yaml" -Force
    Write-Host "Removed duplicate config file." -ForegroundColor Red
}

# Clean up exported_data directory (keep the directory)
if (Test-Path "exported_data") {
    Get-ChildItem "exported_data" -Recurse | Remove-Item -Force
    Write-Host "Cleaned exported_data directory." -ForegroundColor Green
}

Write-Host "Cleanup completed!" -ForegroundColor Green
Write-Host "GEE cat HTML files have been preserved." -ForegroundColor Cyan 