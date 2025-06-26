const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld('electronAPI', {
  // Example: expose a function to send a message to the main process
  // sendMessage: (message) => ipcRenderer.send('message-from-renderer', message),

  // Example: expose a function to receive messages from the main process
  // onMessage: (callback) => ipcRenderer.on('message-from-main', (event, ...args) => callback(...args)),

  // Settings related (keep specific ones if preferred, or use invokePython for all)
  // getSettings: () => ipcRenderer.invoke('get-all-settings'), // Example if you had specific one
  // setSetting: (key, value) => ipcRenderer.invoke('set-setting', key, value),
  // getThemes: () => ipcRenderer.invoke('get-available-themes'),
  // setTheme: (themeName) => ipcRenderer.invoke('set-theme', themeName),
  // getCurrentTheme: () => ipcRenderer.invoke('get-current-theme-data'),


  // Generic Python call (used by settings.js and about.js)
  invokePython: (channel, ...args) => ipcRenderer.invoke(channel, ...args),

  // --- IPC Listeners for backend signals ---
  // (Main process will send messages to renderer using these channels)
  onConnectionStatusChanged: (callback) => {
    ipcRenderer.on('connection-status-changed', (event, status) => callback(status));
  },

  onThemeChanged: (callback) => {
    ipcRenderer.on('theme-changed', (event, themeName, themeData) => callback(themeName, themeData));
  },

  onStatusMessageUpdate: (callback) => { // For general status text updates
    ipcRenderer.on('status-message-update', (event, message) => callback(message));
  },

  onDownloadStatusUpdate: (callback) => {
    ipcRenderer.on('download-status-update', (event, downloadStatus) => callback(downloadStatus));
  }
  // Add more listeners for other signals from backend as needed
});

console.log('Preload script loaded.');
