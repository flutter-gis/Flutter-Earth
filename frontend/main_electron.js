const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 900,
    icon: path.join(__dirname, '..', 'logo.png'), // Use existing logo.png
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false,
      sandbox: false,
      webSecurity: false, // Allow local file access
      preload: path.join(__dirname, 'preload.js') // Add preload script
    }
  });
  
  mainWindow.setMenuBarVisibility(true);
  mainWindow.loadFile('flutter_earth.html');
}

// IPC handlers for Python communication
ipcMain.handle('python-init', async () => {
  console.log('Received python-init request');
  try {
    const result = await callPythonScript('init');
    console.log('Python init result:', result);
    return result;
  } catch (error) {
    console.error('Python init error:', error);
    return { status: 'error', message: error.message };
  }
});

ipcMain.handle('python-download', async (event, params) => {
  return await callPythonScript('download', JSON.stringify(params));
});

ipcMain.handle('python-progress', async () => {
  return await callPythonScript('progress');
});

ipcMain.handle('python-auth', async (event, keyFile, projectId) => {
  return await callPythonScript('auth', keyFile, projectId);
});

function callPythonScript(command, ...args) {
  return new Promise((resolve, reject) => {
    const pythonPath = 'python'; // or 'python3' depending on your system
    const scriptPath = path.join(__dirname, '..', 'backend', 'earth_engine_processor.py');
    
    const allArgs = [scriptPath, command, ...args];
    
    console.log(`Calling Python: ${pythonPath} ${allArgs.join(' ')}`);
    
    const pythonProcess = spawn(pythonPath, allArgs, {
      cwd: path.join(__dirname, '..') // Set working directory to project root
    });
    
    let stdout = '';
    let stderr = '';
    
    pythonProcess.stdout.on('data', (data) => {
      stdout += data.toString();
    });
    
    pythonProcess.stderr.on('data', (data) => {
      stderr += data.toString();
    });
    
    pythonProcess.on('close', (code) => {
      if (code === 0) {
        try {
          const result = JSON.parse(stdout);
          resolve(result);
        } catch (e) {
          reject(new Error(`Failed to parse Python output: ${e.message}`));
        }
      } else {
        reject(new Error(`Python script failed with code ${code}: ${stderr}`));
      }
    });
    
    pythonProcess.on('error', (error) => {
      reject(new Error(`Failed to start Python process: ${error.message}`));
    });
  });
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) createWindow();
});
// Suppress Electron security warnings for local/offline use
process.env['ELECTRON_DISABLE_SECURITY_WARNINGS'] = 'true'; 