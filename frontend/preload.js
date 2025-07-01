const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  // Python communication functions
  pythonInit: () => ipcRenderer.invoke('python-init'),
  pythonDownload: (params) => ipcRenderer.invoke('python-download', params),
  pythonProgress: () => ipcRenderer.invoke('python-progress'),
  pythonAuth: (keyFile, projectId) => ipcRenderer.invoke('python-auth', keyFile, projectId),
  pythonRunCrawler: () => ipcRenderer.invoke('python-run-crawler'),
  saveCrawlerData: (data) => ipcRenderer.invoke('save-crawler-data', data),
  tailCrawlerLog: (numLines = 50) => ipcRenderer.invoke('tail-crawler-log', numLines),
  
  // Utility functions
  showMessage: (message) => {
    // You can add native OS notifications here if needed
    console.log('Message from renderer:', message);
  }
}); 