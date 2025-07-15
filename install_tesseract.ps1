Write-Host "Installing Tesseract OCR..." -ForegroundColor Green

# Create Tesseract installation directory
$TesseractDir = "C:\Program Files\Tesseract-OCR"
$SourceDir = "C:\Users\U1060469\Downloads\tesseract-5.5.1"

# Check if source exists
if (-not (Test-Path $SourceDir)) {
    Write-Host "❌ Source directory not found: $SourceDir" -ForegroundColor Red
    Write-Host "Please ensure Tesseract is downloaded to the correct location." -ForegroundColor Yellow
    pause
    exit 1
}

# Create installation directory
if (-not (Test-Path $TesseractDir)) {
    New-Item -ItemType Directory -Path $TesseractDir -Force | Out-Null
    Write-Host "✓ Created installation directory: $TesseractDir" -ForegroundColor Green
}

# Copy files
Write-Host "Copying Tesseract files..." -ForegroundColor Yellow
try {
    Copy-Item -Path "$SourceDir\*" -Destination $TesseractDir -Recurse -Force
    Write-Host "✓ Files copied successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Error copying files: $($_.Exception.Message)" -ForegroundColor Red
    pause
    exit 1
}

# Add to PATH
Write-Host "Adding Tesseract to PATH..." -ForegroundColor Yellow
$CurrentPath = [Environment]::GetEnvironmentVariable("PATH", "Machine")
if ($CurrentPath -notlike "*$TesseractDir*") {
    $NewPath = "$CurrentPath;$TesseractDir"
    [Environment]::SetEnvironmentVariable("PATH", $NewPath, "Machine")
    Write-Host "✓ Added to system PATH" -ForegroundColor Green
} else {
    Write-Host "✓ Already in PATH" -ForegroundColor Green
}

# Test installation
Write-Host "Testing Tesseract installation..." -ForegroundColor Yellow
try {
    $TesseractExe = Join-Path $TesseractDir "tesseract.exe"
    if (Test-Path $TesseractExe) {
        $Version = & $TesseractExe --version 2>&1
        Write-Host "✓ Tesseract installed successfully!" -ForegroundColor Green
        Write-Host "Version: $Version" -ForegroundColor Cyan
        Write-Host "Location: $TesseractDir" -ForegroundColor Cyan
    } else {
        Write-Host "❌ Tesseract executable not found" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Error testing Tesseract: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`nInstallation complete!" -ForegroundColor Green
Write-Host "You may need to restart your terminal for PATH changes to take effect." -ForegroundColor Yellow
pause 