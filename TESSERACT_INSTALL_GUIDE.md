# Tesseract OCR Installation Guide

## Manual Installation Steps

Since the automated installation scripts aren't working, please follow these manual steps:

### Step 1: Copy Files
1. Open File Explorer
2. Navigate to: `C:\Users\U1060469\Downloads\tesseract-5.5.1`
3. Select all files and folders
4. Copy them (Ctrl+C)

### Step 2: Create Installation Directory
1. Navigate to: `C:\Program Files\`
2. Create a new folder named: `Tesseract-OCR`
3. Paste the copied files into this folder

### Step 3: Add to PATH
1. Press `Win + R` to open Run dialog
2. Type `sysdm.cpl` and press Enter
3. Go to "Advanced" tab
4. Click "Environment Variables"
5. Under "System Variables", find "Path" and click "Edit"
6. Click "New" and add: `C:\Program Files\Tesseract-OCR`
7. Click "OK" on all dialogs

### Step 4: Test Installation
1. Open a new Command Prompt or PowerShell
2. Type: `tesseract --version`
3. You should see version information

### Alternative: Quick Test
If you want to test the crawler without installing Tesseract globally:

1. Copy `tesseract.exe` from your download folder to the `web_crawler` folder
2. The crawler will find it locally

## Verification
After installation, run:
```bash
tesseract --version
```

You should see output like:
```
tesseract 5.5.1
```

## Troubleshooting
- If you get "command not found", restart your terminal
- If you get permission errors, run as Administrator
- If the executable isn't found, check the file structure in your download folder 