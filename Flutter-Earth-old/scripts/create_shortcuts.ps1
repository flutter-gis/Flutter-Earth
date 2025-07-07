# Flutter Earth Shortcut Creator (PowerShell)
# This script creates desktop shortcuts for Flutter Earth applications

param(
    [switch]$Desktop,
    [switch]$StartMenu,
    [switch]$All,
    [switch]$Help
)

# Colors for output
$Red = "Red"
$Green = "Green"
$Yellow = "Yellow"
$Blue = "Blue"
$White = "White"

# Function to print colored output
function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor $Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor $Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor $Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor $Red
}

# Function to create shortcut
function New-Shortcut {
    param(
        [string]$TargetPath,
        [string]$ShortcutPath,
        [string]$Description,
        [string]$IconPath = "",
        [string]$WorkingDirectory = ""
    )
    
    try {
        $WshShell = New-Object -ComObject WScript.Shell
        $Shortcut = $WshShell.CreateShortcut($ShortcutPath)
        $Shortcut.TargetPath = $TargetPath
        $Shortcut.Description = $Description
        
        if (-not [string]::IsNullOrEmpty($WorkingDirectory)) {
            $Shortcut.WorkingDirectory = $WorkingDirectory
        }
        
        if (-not [string]::IsNullOrEmpty($IconPath)) {
            $Shortcut.IconLocation = $IconPath
        }
        
        $Shortcut.Save()
        return $true
    }
    catch {
        Write-Error "Failed to create shortcut: $($_.Exception.Message)"
        return $false
    }
}

# Function to get project directory
function Get-ProjectDirectory {
    $ScriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
    return $ScriptPath
}

# Function to create desktop shortcuts
function New-DesktopShortcuts {
    Write-Status "Creating desktop shortcuts..."
    
    $ProjectDir = Get-ProjectDirectory
    $DesktopPath = [Environment]::GetFolderPath("Desktop")
    
    # Flutter Earth Desktop App shortcut
    $DesktopAppPath = Join-Path $ProjectDir "run_desktop.bat"
    $DesktopShortcutPath = Join-Path $DesktopPath "Flutter Earth.lnk"
    $IconPath = Join-Path $ProjectDir "logo.ico"
    
    if (Test-Path $DesktopAppPath) {
        if (New-Shortcut -TargetPath $DesktopAppPath -ShortcutPath $DesktopShortcutPath -Description "Flutter Earth Desktop Application" -IconPath $IconPath -WorkingDirectory $ProjectDir) {
            Write-Success "Created desktop shortcut: Flutter Earth"
        }
    } else {
        Write-Warning "Desktop app launcher not found: $DesktopAppPath"
    }
    
    # Flutter Earth Web App shortcut
    $WebAppPath = Join-Path $ProjectDir "run_app.bat"
    $WebShortcutPath = Join-Path $DesktopPath "Flutter Earth Web.lnk"
    
    if (Test-Path $WebAppPath) {
        if (New-Shortcut -TargetPath $WebAppPath -ShortcutPath $WebShortcutPath -Description "Flutter Earth Web Application" -IconPath $IconPath -WorkingDirectory $ProjectDir) {
            Write-Success "Created desktop shortcut: Flutter Earth Web"
        }
    } else {
        Write-Warning "Web app launcher not found: $WebAppPath"
    }
    
    # Theme Showcase shortcut
    $ThemeShowcasePath = Join-Path $ProjectDir "frontend\theme_showcase.html"
    $ThemeShortcutPath = Join-Path $DesktopPath "Flutter Earth Themes.lnk"
    
    if (Test-Path $ThemeShowcasePath) {
        $BrowserPath = "chrome.exe"
        if (Test-Path "C:\Program Files\Google\Chrome\Application\chrome.exe") {
            $BrowserPath = "C:\Program Files\Google\Chrome\Application\chrome.exe"
        } elseif (Test-Path "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe") {
            $BrowserPath = "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
        }
        
        $ThemeShowcaseUrl = "file:///$($ThemeShowcasePath -replace '\\', '/')"
        if (New-Shortcut -TargetPath $BrowserPath -ShortcutPath $ThemeShortcutPath -Description "Flutter Earth Theme Showcase" -IconPath $IconPath -WorkingDirectory $ProjectDir) {
            # Add arguments to open the theme showcase
            $WshShell = New-Object -ComObject WScript.Shell
            $Shortcut = $WshShell.CreateShortcut($ThemeShortcutPath)
            $Shortcut.Arguments = $ThemeShowcaseUrl
            $Shortcut.Save()
            Write-Success "Created desktop shortcut: Flutter Earth Themes"
        }
    } else {
        Write-Warning "Theme showcase not found: $ThemeShowcasePath"
    }
}

# Function to create start menu shortcuts
function New-StartMenuShortcuts {
    Write-Status "Creating start menu shortcuts..."
    
    $ProjectDir = Get-ProjectDirectory
    $StartMenuPath = [Environment]::GetFolderPath("StartMenu")
    $FlutterEarthStartMenu = Join-Path $StartMenuPath "Flutter Earth"
    
    # Create Flutter Earth folder in start menu
    if (-not (Test-Path $FlutterEarthStartMenu)) {
        New-Item -ItemType Directory -Path $FlutterEarthStartMenu -Force | Out-Null
        Write-Status "Created start menu folder: Flutter Earth"
    }
    
    $IconPath = Join-Path $ProjectDir "logo.ico"
    
    # Flutter Earth Desktop App shortcut
    $DesktopAppPath = Join-Path $ProjectDir "run_desktop.bat"
    $DesktopShortcutPath = Join-Path $FlutterEarthStartMenu "Flutter Earth Desktop.lnk"
    
    if (Test-Path $DesktopAppPath) {
        if (New-Shortcut -TargetPath $DesktopAppPath -ShortcutPath $DesktopShortcutPath -Description "Flutter Earth Desktop Application" -IconPath $IconPath -WorkingDirectory $ProjectDir) {
            Write-Success "Created start menu shortcut: Flutter Earth Desktop"
        }
    }
    
    # Flutter Earth Web App shortcut
    $WebAppPath = Join-Path $ProjectDir "run_app.bat"
    $WebShortcutPath = Join-Path $FlutterEarthStartMenu "Flutter Earth Web.lnk"
    
    if (Test-Path $WebAppPath) {
        if (New-Shortcut -TargetPath $WebAppPath -ShortcutPath $WebShortcutPath -Description "Flutter Earth Web Application" -IconPath $IconPath -WorkingDirectory $ProjectDir) {
            Write-Success "Created start menu shortcut: Flutter Earth Web"
        }
    }
    
    # Theme Showcase shortcut
    $ThemeShowcasePath = Join-Path $ProjectDir "frontend\theme_showcase.html"
    $ThemeShortcutPath = Join-Path $FlutterEarthStartMenu "Theme Showcase.lnk"
    
    if (Test-Path $ThemeShowcasePath) {
        $BrowserPath = "chrome.exe"
        if (Test-Path "C:\Program Files\Google\Chrome\Application\chrome.exe") {
            $BrowserPath = "C:\Program Files\Google\Chrome\Application\chrome.exe"
        } elseif (Test-Path "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe") {
            $BrowserPath = "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
        }
        
        $ThemeShowcaseUrl = "file:///$($ThemeShowcasePath -replace '\\', '/')"
        if (New-Shortcut -TargetPath $BrowserPath -ShortcutPath $ThemeShortcutPath -Description "Flutter Earth Theme Showcase" -IconPath $IconPath -WorkingDirectory $ProjectDir) {
            $WshShell = New-Object -ComObject WScript.Shell
            $Shortcut = $WshShell.CreateShortcut($ThemeShortcutPath)
            $Shortcut.Arguments = $ThemeShowcaseUrl
            $Shortcut.Save()
            Write-Success "Created start menu shortcut: Theme Showcase"
        }
    }
    
    # Test Interface shortcut
    $TestInterfacePath = Join-Path $ProjectDir "frontend\satellite_info_test.html"
    $TestShortcutPath = Join-Path $FlutterEarthStartMenu "Test Interface.lnk"
    
    if (Test-Path $TestInterfacePath) {
        $BrowserPath = "chrome.exe"
        if (Test-Path "C:\Program Files\Google\Chrome\Application\chrome.exe") {
            $BrowserPath = "C:\Program Files\Google\Chrome\Application\chrome.exe"
        } elseif (Test-Path "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe") {
            $BrowserPath = "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
        }
        
        $TestInterfaceUrl = "file:///$($TestInterfacePath -replace '\\', '/')"
        if (New-Shortcut -TargetPath $BrowserPath -ShortcutPath $TestShortcutPath -Description "Flutter Earth Test Interface" -IconPath $IconPath -WorkingDirectory $ProjectDir) {
            $WshShell = New-Object -ComObject WScript.Shell
            $Shortcut = $WshShell.CreateShortcut($TestShortcutPath)
            $Shortcut.Arguments = $TestInterfaceUrl
            $Shortcut.Save()
            Write-Success "Created start menu shortcut: Test Interface"
        }
    }
    
    # Documentation shortcut
    $ReadmePath = Join-Path $ProjectDir "frontend\readme_page.html"
    $ReadmeShortcutPath = Join-Path $FlutterEarthStartMenu "Documentation.lnk"
    
    if (Test-Path $ReadmePath) {
        $BrowserPath = "chrome.exe"
        if (Test-Path "C:\Program Files\Google\Chrome\Application\chrome.exe") {
            $BrowserPath = "C:\Program Files\Google\Chrome\Application\chrome.exe"
        } elseif (Test-Path "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe") {
            $BrowserPath = "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
        }
        
        $ReadmeUrl = "file:///$($ReadmePath -replace '\\', '/')"
        if (New-Shortcut -TargetPath $BrowserPath -ShortcutPath $ReadmeShortcutPath -Description "Flutter Earth Documentation" -IconPath $IconPath -WorkingDirectory $ProjectDir) {
            $WshShell = New-Object -ComObject WScript.Shell
            $Shortcut = $WshShell.CreateShortcut($ReadmeShortcutPath)
            $Shortcut.Arguments = $ReadmeUrl
            $Shortcut.Save()
            Write-Success "Created start menu shortcut: Documentation"
        }
    }
}

# Function to show help
function Show-Help {
    Write-Host "Flutter Earth Shortcut Creator" -ForegroundColor $White
    Write-Host "=============================" -ForegroundColor $White
    Write-Host "" -ForegroundColor $White
    Write-Host "Usage: $($MyInvocation.MyCommand.Name) [OPTIONS]" -ForegroundColor $White
    Write-Host "" -ForegroundColor $White
    Write-Host "Options:" -ForegroundColor $White
    Write-Host "  -Desktop               Create desktop shortcuts" -ForegroundColor $White
    Write-Host "  -StartMenu             Create start menu shortcuts" -ForegroundColor $White
    Write-Host "  -All                   Create both desktop and start menu shortcuts" -ForegroundColor $White
    Write-Host "  -Help                  Show this help message" -ForegroundColor $White
    Write-Host "" -ForegroundColor $White
    Write-Host "Examples:" -ForegroundColor $White
    Write-Host "  $($MyInvocation.MyCommand.Name) -Desktop" -ForegroundColor $White
    Write-Host "  $($MyInvocation.MyCommand.Name) -StartMenu" -ForegroundColor $White
    Write-Host "  $($MyInvocation.MyCommand.Name) -All" -ForegroundColor $White
    Write-Host "" -ForegroundColor $White
    Write-Host "Shortcuts Created:" -ForegroundColor $White
    Write-Host "  - Flutter Earth Desktop Application" -ForegroundColor $White
    Write-Host "  - Flutter Earth Web Application" -ForegroundColor $White
    Write-Host "  - Theme Showcase" -ForegroundColor $White
    Write-Host "  - Test Interface" -ForegroundColor $White
    Write-Host "  - Documentation" -ForegroundColor $White
}

# Function to validate project structure
function Test-ProjectStructure {
    Write-Status "Validating project structure..."
    
    $ProjectDir = Get-ProjectDirectory
    $RequiredFiles = @(
        "run_desktop.bat",
        "run_app.bat",
        "logo.ico",
        "frontend\theme_showcase.html",
        "frontend\satellite_info_test.html",
        "frontend\readme_page.html"
    )
    
    $MissingFiles = @()
    foreach ($File in $RequiredFiles) {
        $FilePath = Join-Path $ProjectDir $File
        if (-not (Test-Path $FilePath)) {
            $MissingFiles += $File
        }
    }
    
    if ($MissingFiles.Count -gt 0) {
        Write-Warning "Some required files are missing:"
        foreach ($File in $MissingFiles) {
            Write-Host "  - $File" -ForegroundColor $Yellow
        }
        Write-Warning "Some shortcuts may not be created properly"
    } else {
        Write-Success "Project structure validation passed"
    }
}

# Main function
function Main {
    Write-Status "Starting Flutter Earth Shortcut Creator"
    Write-Host "=========================================" -ForegroundColor $White
    
    # Show help if requested
    if ($Help) {
        Show-Help
        return
    }
    
    # Validate project structure
    Test-ProjectStructure
    
    # Determine what to create
    $CreateDesktop = $Desktop -or $All
    $CreateStartMenu = $StartMenu -or $All
    
    # If no options specified, create all
    if (-not $CreateDesktop -and -not $CreateStartMenu) {
        $CreateDesktop = $true
        $CreateStartMenu = $true
    }
    
    # Create shortcuts
    if ($CreateDesktop) {
        New-DesktopShortcuts
    }
    
    if ($CreateStartMenu) {
        New-StartMenuShortcuts
    }
    
    Write-Success "Shortcut creation completed!"
    Write-Status "You can now access Flutter Earth from your desktop or start menu"
}

# Handle script interruption
trap {
    Write-Error "Script interrupted"
    exit 1
}

# Run main function
Main 