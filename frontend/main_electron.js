// Suppress Electron security warnings for local/offline use
process.env['ELECTRON_DISABLE_SECURITY_WARNINGS'] = 'true';

const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');

let mainWindow;
let crawlerProcess = null;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 900,
    minWidth: 1024,
    minHeight: 700,
    icon: path.join(__dirname, '../logo.png'), // Set the window/taskbar icon
    fullscreen: true, // Open in fullscreen
    frame: false,     // Hide the Electron window bar
    autoHideMenuBar: true, // Hide the menu bar
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false,
      sandbox: false,
      webSecurity: false, // Allow local file access
      preload: path.join(__dirname, 'preload.js') // Add preload script
    }
  });
  
  mainWindow.setMenuBarVisibility(false);
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

ipcMain.handle('python-auth-check', async () => {
  console.log('Received python-auth-check request');
  try {
    const result = await callPythonScript('auth-check');
    console.log('Python auth-check result:', result);
    return result;
  } catch (error) {
    console.error('Python auth-check error:', error);
    return { status: 'error', needs_auth: true, message: error.message };
  }
});

ipcMain.handle('python-auth', async (event, keyFile, projectId) => {
  return await callPythonScript('auth', keyFile, projectId);
});

ipcMain.handle('python-run-crawler', async () => {
  if (crawlerProcess && !crawlerProcess.killed) {
    return { status: 'error', message: 'Crawler is already running' };
  }
  try {
    const scriptPath = path.join(__dirname, '../backend/earth_engine_processor.py');
    crawlerProcess = spawn('python', [scriptPath, 'run-crawler'], { shell: true });
    crawlerProcess.on('close', (code) => {
      console.log('Crawler process exited with code', code);
      crawlerProcess = null;
    });
    crawlerProcess.on('error', (err) => {
      console.error('Crawler process error:', err);
      crawlerProcess = null;
    });
    return { status: 'started', message: 'Crawler started in background' };
  } catch (error) {
    return { status: 'error', message: error.message };
  }
});

ipcMain.handle('python-crawler-progress', async () => {
  try {
    const progressPath = path.join(__dirname, '../backend/crawler_data/crawler_progress.json');
    if (!fs.existsSync(progressPath)) {
      return { status: 'pending', message: 'No progress yet' };
    }
    const data = fs.readFileSync(progressPath, 'utf-8');
    return { status: 'success', progress: JSON.parse(data) };
  } catch (err) {
    return { status: 'error', message: err.message };
  }
});

ipcMain.handle('python-cancel-crawler', async () => {
  if (crawlerProcess && !crawlerProcess.killed) {
    crawlerProcess.kill();
    crawlerProcess = null;
    return { status: 'cancelled', message: 'Crawler cancelled' };
  }
  return { status: 'error', message: 'No crawler running' };
});

ipcMain.handle('save-crawler-data', async (event, data) => {
  try {
    // Write the updated data to a temp file
    const tempPath = path.join(__dirname, '../backend/crawler_data/gee_catalog_data_enhanced_tmp.json');
    fs.writeFileSync(tempPath, JSON.stringify(data, null, 2), 'utf-8');
    // Call the backend Python script to compress and save
    const scriptPath = path.join(__dirname, '../backend/earth_engine_processor.py');
    return await new Promise((resolve) => {
      const proc = spawn('python', [scriptPath, 'compress-crawler-data', tempPath], { shell: true });
      let output = '';
      let error = '';
      proc.stdout.on('data', (data) => { output += data.toString(); });
      proc.stderr.on('data', (data) => { error += data.toString(); });
      proc.on('close', (code) => {
        fs.unlinkSync(tempPath);
        if (code === 0) {
          resolve({ status: 'success', message: output });
        } else {
          resolve({ status: 'error', message: error || output });
        }
      });
    });
  } catch (err) {
    return { status: 'error', message: err.message };
  }
});

const getLatestCrawlerLogFile = () => {
  const logsDir = path.join(__dirname, '../logs');
  const files = fs.readdirSync(logsDir)
    .filter(f => f.startsWith('gee_catalog_crawler_') && f.endsWith('.log'))
    .map(f => ({
      name: f,
      time: fs.statSync(path.join(logsDir, f)).mtime.getTime()
    }))
    .sort((a, b) => b.time - a.time);
  return files.length > 0 ? path.join(logsDir, files[0].name) : null;
};

ipcMain.handle('tail-crawler-log', async (event, numLines = 50) => {
  try {
    const logFile = getLatestCrawlerLogFile();
    if (!logFile) return { status: 'error', message: 'No log file found' };
    const data = fs.readFileSync(logFile, 'utf-8');
    const lines = data.trim().split(/\r?\n/);
    const lastLines = lines.slice(-numLines).join('\n');
    return { status: 'success', log: lastLines };
  } catch (err) {
    return { status: 'error', message: err.message };
  }
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

ipcMain.on('log-to-file', (event, level, message) => {
    const logPath = path.join(__dirname, '..', 'console_log.txt');
    const timestamp = new Date().toISOString();
    fs.appendFileSync(logPath, `[${timestamp}] [${level.toUpperCase()}] ${message}\n`);
});

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) createWindow();
}); 