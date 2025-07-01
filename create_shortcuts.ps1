# PowerShell script to create shortcuts with custom icons
# This script converts logo.png to ICO format and creates shortcuts for batch files

# Add Windows Forms for image conversion
Add-Type -AssemblyName System.Drawing

# Function to convert PNG to ICO
function Convert-PngToIco {
    param(
        [string]$PngPath,
        [string]$IcoPath
    )
    
    try {
        $image = [System.Drawing.Image]::FromFile($PngPath)
        $icon = [System.Drawing.Icon]::FromHandle($image.GetHicon())
        
        # Save as ICO
        $fileStream = [System.IO.File]::Create($IcoPath)
        $icon.Save($fileStream)
        $fileStream.Close()
        
        # Clean up
        $icon.Dispose()
        $image.Dispose()
        
        Write-Host "Successfully converted $PngPath to $IcoPath"
    }
    catch {
        Write-Host "Error converting image: $($_.Exception.Message)"
    }
}

# Function to create shortcut with custom icon
function Create-ShortcutWithIcon {
    param(
        [string]$TargetPath,
        [string]$ShortcutPath,
        [string]$IconPath
    )
    
    try {
        $WshShell = New-Object -comObject WScript.Shell
        $Shortcut = $WshShell.CreateShortcut($ShortcutPath)
        $Shortcut.TargetPath = $TargetPath
        $Shortcut.WorkingDirectory = Split-Path $TargetPath
        $Shortcut.IconLocation = $IconPath
        $Shortcut.Save()
        
        Write-Host "Created shortcut: $ShortcutPath"
    }
    catch {
        Write-Host "Error creating shortcut: $($_.Exception.Message)"
    }
}

# Main execution
Write-Host "Creating shortcuts with Flutter Earth logo..."

# Convert logo.png to logo.ico
$logoPng = "logo.png"
$logoIco = "logo.ico"

if (Test-Path $logoPng) {
    Convert-PngToIco -PngPath $logoPng -IcoPath $logoIco
    
    # Create shortcuts for main batch files
    $batchFiles = @(
        "run_app.bat",
        "run_desktop.bat", 
        "git_push_script.bat"
    )
    
    foreach ($batchFile in $batchFiles) {
        if (Test-Path $batchFile) {
            $shortcutName = $batchFile -replace '\.bat$', ' - Flutter Earth.lnk'
            Create-ShortcutWithIcon -TargetPath $batchFile -ShortcutPath $shortcutName -IconPath "$PWD\$logoIco"
        }
    }
    
    Write-Host "`nShortcuts created successfully!"
    Write-Host "You can now use the shortcuts with the Flutter Earth logo icon."
    Write-Host "The original batch files remain unchanged."
} else {
    Write-Host "Error: logo.png not found in current directory"
} 