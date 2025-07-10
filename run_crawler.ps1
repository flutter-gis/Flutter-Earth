# Enhanced Earth Engine Data Catalog Crawler Launcher
# PowerShell Script

param(
    [string]$FolderPath = "",
    [switch]$AutoStart = $false
)

# Set console title
$Host.UI.RawUI.WindowTitle = "Enhanced Earth Engine Data Catalog Crawler"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Enhanced Earth Engine Data Catalog Crawler" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Function to check if Python is installed
function Test-Python {
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
            return $true
        }
    }
    catch {
        Write-Host "✗ Python not found in PATH" -ForegroundColor Red
        return $false
    }
    return $false
}

# Function to check and install required packages
function Test-RequiredPackages {
    Write-Host "Checking required packages..." -ForegroundColor Yellow
    
    $requiredPackages = @("tkinter", "requests", "json", "gzip", "bs4")
    $missingPackages = @()
    
    foreach ($package in $requiredPackages) {
        try {
            python -c "import $package" 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✓ $package" -ForegroundColor Green
            } else {
                $missingPackages += $package
                Write-Host "✗ $package" -ForegroundColor Red
            }
        }
        catch {
            $missingPackages += $package
            Write-Host "✗ $package" -ForegroundColor Red
        }
    }
    
    if ($missingPackages.Count -gt 0) {
        Write-Host ""
        Write-Host "Installing missing packages..." -ForegroundColor Yellow
        
        foreach ($package in $missingPackages) {
            if ($package -ne "tkinter" -and $package -ne "json" -and $package -ne "gzip") {
                Write-Host "Installing $package..." -ForegroundColor Yellow
                pip install $package
                if ($LASTEXITCODE -eq 0) {
                    Write-Host "✓ $package installed successfully" -ForegroundColor Green
                } else {
                    Write-Host "✗ Failed to install $package" -ForegroundColor Red
                }
            }
        }
        
        # Also try installing from requirements file
        if (Test-Path "requirements_crawler.txt") {
            Write-Host "Installing from requirements file..." -ForegroundColor Yellow
            pip install -r requirements_crawler.txt
        }
    }
}

# Function to create necessary directories
function Initialize-Directories {
    Write-Host "Creating necessary directories..." -ForegroundColor Yellow
    
    $directories = @("logs", "crawler_data", "output")
    
    foreach ($dir in $directories) {
        if (!(Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-Host "✓ Created directory: $dir" -ForegroundColor Green
        } else {
            Write-Host "✓ Directory exists: $dir" -ForegroundColor Green
        }
    }
}

# Function to run the crawler
function Start-Crawler {
    Write-Host ""
    Write-Host "Starting Enhanced Earth Engine Crawler GUI..." -ForegroundColor Cyan
    Write-Host ""
    
    try {
        # Set environment variables for better compatibility
        $env:PYTHONIOENCODING = "utf-8"
        $env:PYTHONUNBUFFERED = "1"
        
        # Run the crawler
        python crawler_gui.py
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "✓ Enhanced crawler completed successfully!" -ForegroundColor Green
        } else {
            Write-Host ""
            Write-Host "✗ Enhanced crawler encountered an error (Exit code: $LASTEXITCODE)" -ForegroundColor Red
            Write-Host "Check the logs for more information" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host ""
        Write-Host "✗ Error running enhanced crawler: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "Stack trace: $($_.ScriptStackTrace)" -ForegroundColor Red
    }
}

# Main execution
try {
    # Check Python installation
    if (!(Test-Python)) {
        Write-Host ""
        Write-Host "ERROR: Python is required but not found." -ForegroundColor Red
        Write-Host "Please install Python from https://python.org and try again." -ForegroundColor Yellow
        Read-Host "Press Enter to exit"
        exit 1
    }
    
    # Check and install required packages
    Test-RequiredPackages
    
    # Initialize directories
    Initialize-Directories
    
    # Set folder path if provided
    if ($FolderPath -and (Test-Path $FolderPath)) {
        Write-Host ""
        Write-Host "Using provided folder path: $FolderPath" -ForegroundColor Yellow
        $env:CRAWLER_DEFAULT_FOLDER = $FolderPath
    }
    
    # Start the crawler
    Start-Crawler
}
catch {
    Write-Host ""
    Write-Host "✗ Unexpected error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Stack trace: $($_.ScriptStackTrace)" -ForegroundColor Red
}
finally {
    Write-Host ""
    Write-Host "Press any key to exit..." -ForegroundColor Gray
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
} 