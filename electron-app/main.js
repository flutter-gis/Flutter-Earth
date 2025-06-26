const { app, BrowserWindow, ipcMain, dialog, shell } = require('electron')
const path = require('path')
const { spawn } = require('child_process')

// --- Python Bridge ---
// Adjust the path to your Python executable and script as necessary
const PYTHON_EXECUTABLE = process.platform === 'win32' ? 'python' : 'python3'; // Or absolute path
const PYTHON_SCRIPT_PATH = path.join(__dirname, '..', 'flutter_earth_pkg', 'flutter_earth', 'electron_bridge.py'); // Adjust if bridge is elsewhere

function callPython(action, args = {}) {
    return new Promise((resolve, reject) => {
        const argsArray = [PYTHON_SCRIPT_PATH, action];
        for (const key in args) {
            argsArray.push(`--${key}`);
            // Ensure arguments are strings for spawn
            argsArray.push(String(args[key]));
        }

        console.log(`Spawning Python: ${PYTHON_EXECUTABLE} ${argsArray.join(' ')}`);
        const pythonProcess = spawn(PYTHON_EXECUTABLE, argsArray);

        let stdoutData = '';
        let stderrData = '';

        pythonProcess.stdout.on('data', (data) => {
            stdoutData += data.toString();
        });

        pythonProcess.stderr.on('data', (data) => {
            stderrData += data.toString();
        });

        pythonProcess.on('close', (code) => {
            console.log(`Python process for action "${action}" exited with code ${code}`);
            if (stderrData) {
                console.error(`Python stderr for "${action}":\n${stderrData}`);
            }
            if (code === 0) {
                try {
                    // Handle cases where Python might not return JSON (e.g. simple success message)
                    if (stdoutData.trim() === "" && (action === "open_external_url" || action === "some_action_with_no_json_return")) {
                        resolve({ success: true, message: "Action completed without JSON output." });
                        return;
                    }
                    const result = JSON.parse(stdoutData);
                    resolve(result);
                } catch (e) {
                    console.error("Error parsing Python output:", e);
                    console.error("Python stdout was:", stdoutData);
                    reject(new Error('Failed to parse Python output. ' + stdoutData));
                }
            } else {
                reject(new Error(`Python script error for action "${action}" (code ${code}): ${stderrData || stdoutData}`));
            }
        });

        pythonProcess.on('error', (err) => {
            console.error(`Failed to start Python process for action "${action}":`, err);
            reject(err);
        });
    });
}


function createWindow () {
  mainWindow = new BrowserWindow({ // Assign to global mainWindow
    width: 1200, // Increased width
    height: 800,  // Increased height
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      enableRemoteModule: false, // Best practice
      nodeIntegration: false,    // Best practice
      // sandbox: true, // Consider for enhanced security, might need adjustments
    }
  })

  mainWindow.loadFile('index.html') // Load the main page first

  // Optionally open DevTools:
  // mainWindow.webContents.openDevTools();
}

app.whenReady().then(() => {
  // --- IPC Handlers ---
  ipcMain.handle('get-all-settings', async () => {
    return callPython('get_all_settings');
  });

  ipcMain.handle('get-available-themes', async () => {
    return callPython('get_available_themes');
  });

  ipcMain.handle('get-current-theme-data', async () => {
    return callPython('get_current_theme_data');
  });

  ipcMain.handle('get-current-theme-name', async () => {
    return callPython('get_current_theme_name');
  });

  ipcMain.handle('set-theme', async (event, themeName) => {
    const result = await callPython('set_theme', { theme_name: themeName });
    if (result.success && mainWindow) {
        const newThemeData = await callPython('get_current_theme_data');
        const newThemeName = await callPython('get_current_theme_name');
        if (newThemeData) {
            mainWindow.webContents.send('theme-changed', newThemeName, newThemeData);
        }
    }
    return result;
  });

  // Specific handler for get-setting
  ipcMain.handle('get-setting', async(event, key) => {
    if (!key) return Promise.reject(new Error("Key not provided for get-setting"));
    return callPython('get_setting', { key: key });
  });

  ipcMain.handle('set-setting', async (event, key, value) => {
    // For theme_suboptions, Python might expect a JSON string if that's how it's stored
    let processedValue = value;
    if (key === 'theme_suboptions' && typeof value === 'object') {
        processedValue = JSON.stringify(value);
    }
    const result = await callPython('set_setting', { key: key, value: processedValue });
    if (result.success && (key === 'theme_suboptions' || key.startsWith("use_") || key.startsWith("show_") || key.startsWith("enable_")) && mainWindow) {
        const updatedThemeData = await callPython('get_current_theme_data');
        const currentThemeName = await callPython('get_current_theme_name');
         if (updatedThemeData) {
            mainWindow.webContents.send('theme-changed', currentThemeName, updatedThemeData);
        }
    }
    return result;
  });

  ipcMain.handle('reload-config', async () => {
    const result = await callPython('reload_config');
    if (result.success && mainWindow) {
        const newThemeData = await callPython('get_current_theme_data');
        const newThemeName = await callPython('get_current_theme_name');
        if (newThemeData) {
            mainWindow.webContents.send('theme-changed', newThemeName, newThemeData);
        }
        const connStatus = await callPython('get_connection_status');
        if (connStatus && connStatus.status) {
             mainWindow.webContents.send('connection-status-changed', connStatus.status);
        }
         mainWindow.webContents.send('status-message-update', "Configuration reloaded.");
    }
    return result;
  });

  ipcMain.handle('clear-cache-and-logs', async () => {
    const result = await callPython('clear_cache_and_logs');
    if (result.success && mainWindow) {
        mainWindow.webContents.send('status-message-update', result.message || "Cache and logs cleared.");
    }
    return result;
  });

  ipcMain.handle('select-directory-dialog', async () => {
    const focusedWindow = BrowserWindow.getFocusedWindow() || mainWindow; // Use global mainWindow as fallback
    if (!focusedWindow) {
        const allWindows = BrowserWindow.getAllWindows();
        if (allWindows.length > 0) {
            return dialog.showOpenDialog(allWindows[0], { properties: ['openDirectory'] });
        }
        return Promise.reject(new Error("No window available for dialog."));
    }
    return dialog.showOpenDialog(focusedWindow, { properties: ['openDirectory'] });
  });

  ipcMain.handle('get-changelog', async () => {
    return callPython('get_changelog');
  });

  ipcMain.handle('open-external-url', async (event, url) => {
    try {
        await shell.openExternal(url);
        return { success: true };
    } catch (error) {
        console.error('Failed to open external URL:', error);
        return { success: false, error: error.message };
    }
  });

  ipcMain.handle('get-connection-status', async () => {
    return callPython('get_connection_status');
  });

  ipcMain.handle('get-download-status', async () => {
    return callPython('get_download_status');
  });

  ipcMain.handle('get-all-sensors', async () => {
    return callPython('get_all_sensors');
  });

  ipcMain.handle('start-download-with-params', async (event, params) => {
    return callPython('start_download_with_params', params);
  });

  ipcMain.handle('cancel-download', async () => {
    return callPython('cancel_download');
  });

  ipcMain.handle('get-download-history', async () => {
    return callPython('get_download_history');
  });

  ipcMain.handle('clear-download-history', async () => {
    return callPython('clear_download_history');
  });

  ipcMain.handle('get-available-indices', async () => {
    return callPython('get_available_indices');
  });

  ipcMain.handle('start-index-analysis', async (event, params) => {
    return callPython('start_index_analysis', params);
  });

  ipcMain.handle('select-raster-files-dialog', async () => {
    const focusedWindow = BrowserWindow.getFocusedWindow() || mainWindow;
    if (!focusedWindow) {
        const allWindows = BrowserWindow.getAllWindows();
        if (allWindows.length > 0) {
            return dialog.showOpenDialog(allWindows[0], {
                properties: ['openFile', 'multiSelections'],
                filters: [
                    { name: 'GeoTIFF Files', extensions: ['tif', 'tiff'] },
                    { name: 'All Files', extensions: ['*'] }
                ]
            });
        }
        return Promise.reject(new Error("No window available for dialog."));
    }
    return dialog.showOpenDialog(focusedWindow, {
        properties: ['openFile', 'multiSelections'],
        filters: [
            { name: 'GeoTIFF Files', extensions: ['tif', 'tiff'] },
            { name: 'All Files', extensions: ['*'] }
        ]
    });
  });

  ipcMain.handle('get-vector-data-sources', async () => {
    return callPython('get_vector_data_sources');
  });

  ipcMain.handle('get-vector-output-formats', async () => {
    return callPython('get_vector_output_formats');
  });

  // get-current-aoi handler should already exist if map integration was planned
  // If not, it's:
  // ipcMain.handle('get-current-aoi', async () => {
  //   return callPython('get_current_aoi');
  // });

  ipcMain.handle('start-vector-download', async (event, params) => {
    return callPython('start_vector_download', params);
  });

  ipcMain.handle('select-file-dialog', async (event, options) => {
    const focusedWindow = BrowserWindow.getFocusedWindow() || mainWindow;
    const dialogOptions = {
        title: options?.title || 'Select File',
        properties: ['openFile'],
        filters: options?.filters || [{ name: 'All Files', extensions: ['*'] }]
    };
    if (!focusedWindow) {
        const allWindows = BrowserWindow.getAllWindows();
        if (allWindows.length > 0) return dialog.showOpenDialog(allWindows[0], dialogOptions);
        return Promise.reject(new Error("No window available for dialog."));
    }
    return dialog.showOpenDialog(focusedWindow, dialogOptions);
  });

  ipcMain.handle('load-raster-data', async (event, filePath) => {
    return callPython('load_raster_data', { file_path: filePath });
  });

  ipcMain.handle('load-vector-data', async (event, filePath) => {
    return callPython('load_vector_data', { file_path: filePath });
  });

  // Example: Simulate fetching connection and download status periodically
  // In a real app, Python might push updates, or this polling could be more intelligent.
  setInterval(async () => {
    if (mainWindow && !mainWindow.isDestroyed()) {
      try {
        const connStatus = await callPython('get_connection_status');
        if (connStatus && connStatus.status && mainWindow && !mainWindow.isDestroyed()) {
          mainWindow.webContents.send('connection-status-changed', connStatus.status);
          // mainWindow.webContents.send('status-message-update', connStatus.message); // Avoid too many status messages
        }
      } catch (error) {
        if (mainWindow && !mainWindow.isDestroyed()) {
          mainWindow.webContents.send('connection-status-changed', 'offline');
        }
        console.error("Error polling connection status:", error);
      }

      try {
        const dlStatus = await callPython('get_download_status');
        if (dlStatus && mainWindow && !mainWindow.isDestroyed()) {
          mainWindow.webContents.send('download-status-update', dlStatus); // Send the whole object
        }
      } catch (error) {
        console.error("Error polling download status:", error);
         if (mainWindow && !mainWindow.isDestroyed()) {
            // Optionally send a default/error download status
            // mainWindow.webContents.send('download-status-update', { status: 'error', message: 'Could not get status' });
         }
      }
    }
  }, 7000); // Poll every 7 seconds for example


  // Generic handler (renamed for clarity, ensure preload.js matches if used)
  ipcMain.handle('invoke-python-generic', async (event, pythonAction, ...pythonArgs) => {
    // This generic handler assumes 'pythonAction' is the direct name of the python function
    // and 'pythonArgs' is an object of arguments.
    // This is different from the previous 'invoke-python' which took 'channel'
    // that needed to be mapped.
    // For simplicity, we'll assume pythonArgs[0] is the arguments object if present.
    const argsObject = pythonArgs && pythonArgs.length > 0 ? pythonArgs[0] : {};
    if (typeof pythonAction !== 'string') {
        return Promise.reject(new Error('Python action name must be a string.'));
    }
    return callPython(pythonAction, argsObject);
  });


  createWindow()

  app.on('activate', function () {
    if (BrowserWindow.getAllWindows().length === 0) createWindow()
  })
})

app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') app.quit()
})
