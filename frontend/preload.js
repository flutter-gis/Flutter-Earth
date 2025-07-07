const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
    // Crawler functions
    getCrawlerStatus: () => ipcRenderer.invoke('get-crawler-status'),
    startCrawler: () => ipcRenderer.invoke('start-crawler'),
    
    // Dataset functions
    getDatasets: () => ipcRenderer.invoke('get-datasets'),
    getSatellites: () => ipcRenderer.invoke('get-satellites'),
    
    // Download functions
    startDownload: (params) => ipcRenderer.invoke('start-download', params),
    getDownloadProgress: () => ipcRenderer.invoke('get-download-progress'),
    
    // Authentication functions
    testAuth: () => ipcRenderer.invoke('test-auth'),
    getSatelliteList: () => ipcRenderer.invoke('get-satellite-list'),
    
    // File system functions (for auth files)
    readAuthFiles: () => ipcRenderer.invoke('read-auth-files'),
    saveCrawlerData: (data) => ipcRenderer.invoke('save-crawler-data', data),
    checkAuthStatus: () => ipcRenderer.invoke('check-auth-status')
}); 