const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let pythonProcess = null;

function createWindow() {
  // Start the Python backend as a child process
  if (!pythonProcess) {
    const pythonPath = 'python';
    const scriptPath = path.join(__dirname, '..', 'backend', 'earth_engine_processor.py');
    pythonProcess = spawn(pythonPath, [scriptPath, 'get_crawler_progress'], {
      cwd: path.join(__dirname, '..'),
      stdio: ['ignore', 'pipe', 'pipe'] // Pipe stdout and stderr
    });
    pythonProcess.stdout.on('data', (data) => {
      process.stdout.write(`[PYTHON] ${data}`);
    });
    pythonProcess.stderr.on('data', (data) => {
      process.stderr.write(`[PYTHON ERROR] ${data}`);
    });
    pythonProcess.on('close', (code) => {
      console.log(`[PYTHON] Backend process exited with code ${code}`);
    });
  }

  const win = new BrowserWindow({
    width: 1280,
    height: 900,
    minWidth: 900,
    minHeight: 700,
    icon: path.join(__dirname, '../logo.ico'), // Use app icon if available
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    }
  });

  // Load the enhanced HTML UI directly (offline mode)
  win.loadFile('flutter_earth_enhanced_v2.html').catch(err => {
    console.error('Failed to load HTML:', err);
  });

  // Optionally open DevTools for debugging
  // win.webContents.openDevTools();
  
  // Setup IPC handlers for Python communication
  setupIPCHandlers(win);
}

// Setup IPC handlers for Python backend communication
function setupIPCHandlers(mainWindow) {
  // Handle crawler status requests
  ipcMain.handle('get-crawler-status', async () => {
    return callPythonScript('get_crawler_progress');
  });

  // Handle starting crawler
  ipcMain.handle('start-crawler', async () => {
    return callPythonScript('run_web_crawler');
  });

  // Handle getting datasets
  ipcMain.handle('get-datasets', async () => {
    return callPythonScript('get_datasets');
  });

  // Handle getting satellites
  ipcMain.handle('get-satellites', async () => {
    return callPythonScript('get_satellites');
  });

  // Handle starting download
  ipcMain.handle('start-download', async (event, params) => {
    return callPythonScript('start_download', JSON.stringify(params));
  });

  // Handle getting download progress
  ipcMain.handle('get-download-progress', async () => {
    return callPythonScript('get_progress');
  });

  // Handle authentication test
  ipcMain.handle('test-auth', async () => {
    return callPythonScript('test_auth');
  });

  // Handle getting satellite list
  ipcMain.handle('get-satellite-list', async () => {
    return callPythonScript('get_satellite_list');
  });

  // Handle reading auth files
  ipcMain.handle('read-auth-files', async () => {
    const fs = require('fs');
    const authDir = 'C:\\FE Auth';
    
    try {
      const authConfigPath = path.join(authDir, 'auth_config.json');
      const keyFilePath = path.join(authDir, 'service_account_key.json');
      
      const files = {};
      
      if (fs.existsSync(authConfigPath)) {
        files.authConfig = JSON.parse(fs.readFileSync(authConfigPath, 'utf8'));
      }
      
      if (fs.existsSync(keyFilePath)) {
        files.keyFile = JSON.parse(fs.readFileSync(keyFilePath, 'utf8'));
      }
      
      return {
        success: true,
        files: files
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  });

  // Handle saving crawler data
  ipcMain.handle('save-crawler-data', async (event, data) => {
    const fs = require('fs');
    const gzip = require('zlib').gzip;
    
    try {
      const dataDir = path.join(__dirname, '..', 'backend', 'crawler_data');
      if (!fs.existsSync(dataDir)) {
        fs.mkdirSync(dataDir, { recursive: true });
      }
      
      const outputPath = path.join(dataDir, 'gee_catalog_data_enhanced.json.gz');
      const compressedData = await new Promise((resolve, reject) => {
        gzip(JSON.stringify(data), (err, result) => {
          if (err) reject(err);
          else resolve(result);
        });
      });
      
      fs.writeFileSync(outputPath, compressedData);
      
      return {
        status: 'success',
        message: 'Crawler data saved successfully'
      };
    } catch (error) {
      return {
        status: 'error',
        message: error.message
      };
    }
  });

  // Handle checking auth status
  ipcMain.handle('check-auth-status', async () => {
    return callPythonScript('test_auth');
  });
}

// Function to call Python scripts
function callPythonScript(command, ...args) {
  return new Promise((resolve, reject) => {
    const pythonPath = 'python';
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
  if (pythonProcess) {
    pythonProcess.kill();
    pythonProcess = null;
  }
  if (process.platform !== 'darwin') app.quit();
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) createWindow();
}); 