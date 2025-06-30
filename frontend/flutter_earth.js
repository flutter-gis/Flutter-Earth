// Flutter Earth JavaScript - Converted from QML

class FlutterEarth {
    constructor() {
        this.currentView = 'welcome';
        this.connectionStatus = 'offline';
        this.statusBarText = 'Initializing...';
        this.currentDate = new Date();
        this.selectedDate = null;
        this.calendarTarget = null;
        this.downloadInProgress = false;
        this.isOfflineMode = false;
        
        this.init();
    }

    async init() {
        this.showThemeSplash();
        this.setupEventListeners();
        await this.initializeEarthEngine();
        this.hideThemeSplash();
        this.loadSensors();
        this.setupCalendar();
        this.initSettings();
        this.initSatelliteInfo();
        this.initAboutView();
        // Do NOT show help popup on startup
    }

    async initializeEarthEngine() {
        try {
            this.updateConnectionStatus('initializing');
            this.statusBarText = 'Initializing Earth Engine...';
            
            if (window.electronAPI) {
                const result = await window.electronAPI.pythonInit();
                console.log('[DEBUG] pythonInit result:', result);
                
                if (result.status === 'success' && result.initialized) {
                    this.updateConnectionStatus('online');
                    this.statusBarText = 'Earth Engine ready';
                    this.showNotification('Earth Engine initialized successfully', 'success');
                } else if (result.status === 'offline') {
                    this.updateConnectionStatus('offline');
                    this.statusBarText = 'Offline mode: ' + (result.message || 'No credentials');
                    this.showNotification('Offline mode: ' + (result.message || 'No credentials'), 'warning');
                    this.showAuthDialog();
                    this.isOfflineMode = true;
                    return;
                } else {
                    this.updateConnectionStatus('offline');
                    this.statusBarText = 'Earth Engine initialization failed';
                    this.showNotification('Earth Engine initialization failed', 'error');
                    this.showAuthDialog();
                    return;
                }
            } else {
                // Fallback for browser testing
                this.updateConnectionStatus('online');
                this.statusBarText = 'Running in browser mode';
            }
        } catch (error) {
            console.error('[DEBUG] Earth Engine initialization error:', error);
            this.updateConnectionStatus('offline');
            this.statusBarText = 'Initialization error';
            this.showNotification('Failed to initialize Earth Engine', 'error');
        }
    }

    async startDownload() {
        if (this.downloadInProgress) {
            this.showNotification('Download already in progress', 'warning');
            return;
        }

        try {
            // Gather form data
            const params = this.gatherDownloadParams();
            
            if (!params.aoi || !params.startDate || !params.endDate || !params.sensor) {
                this.showNotification('Please fill in all required fields', 'error');
                return;
            }

            this.downloadInProgress = true;
            this.updateDownloadStatus('Starting download...', 'info');
            
            if (window.electronAPI) {
                const result = await window.electronAPI.pythonDownload(params);
                
                if (result.status === 'success') {
                    this.updateDownloadStatus('Download started successfully', 'success');
                    this.showNotification('Download started', 'success');
                    this.startProgressPolling();
                } else {
                    this.updateDownloadStatus('Download failed: ' + result.message, 'error');
                    this.showNotification('Download failed: ' + result.message, 'error');
                    this.downloadInProgress = false;
                }
            } else {
                // Fallback for browser testing
                this.simulateDownloadProgress();
            }
        } catch (error) {
            console.error('Download error:', error);
            this.updateDownloadStatus('Download error: ' + error.message, 'error');
            this.showNotification('Download failed', 'error');
            this.downloadInProgress = false;
        }
    }

    gatherDownloadParams() {
        return {
            aoi: document.getElementById('aoi-input').value,
            startDate: document.getElementById('start-date').value,
            endDate: document.getElementById('end-date').value,
            sensor: document.getElementById('sensor-select').value,
            outputDir: document.getElementById('output-dir').value,
            cloudMask: document.getElementById('cloud-mask').checked,
            cloudCover: parseInt(document.getElementById('cloud-cover').value),
            bestRes: document.getElementById('best-res').checked,
            targetRes: parseInt(document.getElementById('target-res').value),
            tilingMethod: document.getElementById('tiling-method').value,
            numSubsections: parseInt(document.getElementById('num-subsections').value),
            overwriteExisting: document.getElementById('overwrite-existing').checked,
            cleanupTiles: document.getElementById('cleanup-tiles').checked
        };
    }

    updateDownloadLog(message) {
        const logElement = document.getElementById('download-log');
        if (logElement) {
            const timestamp = new Date().toLocaleTimeString();
            logElement.value += `[${timestamp}] ${message}\n`;
            logElement.scrollTop = logElement.scrollHeight;
        }
    }

    async startProgressPolling() {
        if (!window.electronAPI) return;
        
        this.updateDownloadLog('Starting progress monitoring...');
        
        const pollInterval = setInterval(async () => {
            try {
                const result = await window.electronAPI.pythonProgress();
                
                if (result.status === 'success') {
                    const progress = result.progress;
                    this.updateProgressDisplay(progress);
                    
                    if (progress.message) {
                        this.updateDownloadLog(progress.message);
                    }
                    
                    if (progress.completed || progress.error) {
                        clearInterval(pollInterval);
                        this.downloadInProgress = false;
                        
                        if (progress.error) {
                            this.updateDownloadStatus('Download failed: ' + progress.error, 'error');
                            this.updateDownloadLog('ERROR: ' + progress.error);
                        } else {
                            this.updateDownloadStatus('Download completed', 'success');
                            this.updateDownloadLog('Download completed successfully');
                        }
                    }
                }
            } catch (error) {
                console.error('Progress polling error:', error);
                this.updateDownloadLog('ERROR: Progress polling failed - ' + error.message);
                clearInterval(pollInterval);
                this.downloadInProgress = false;
            }
        }, 1000);
    }

    updateProgressDisplay(progress) {
        const progressElement = document.getElementById('download-progress');
        const statusElement = document.getElementById('download-status');
        const currentProgressElement = document.getElementById('current-progress');
        const currentStatusElement = document.getElementById('current-status-text');
        const cancelButton = document.getElementById('cancel-current-download');
        
        if (progressElement) {
            progressElement.style.width = `${progress.percentage || 0}%`;
        }
        
        if (statusElement) {
            statusElement.textContent = progress.message || 'Downloading...';
        }

        if (currentProgressElement) {
            currentProgressElement.style.width = `${progress.percentage || 0}%`;
        }

        if (currentStatusElement) {
            currentStatusElement.textContent = progress.message || 'No active downloads';
        }

        if (cancelButton) {
            cancelButton.disabled = !(progress.percentage > 0 && progress.percentage < 100);
        }
    }

    async submitAuth() {
        const keyFileInput = document.getElementById('auth-key-file');
        const projectId = document.getElementById('auth-project-id').value;
        
        if (!keyFileInput.files[0] || !projectId) {
            this.showNotification('Please provide both key file and project ID', 'error');
            return;
        }

        const keyFile = keyFileInput.files[0].path || keyFileInput.files[0].name;

        try {
            if (window.electronAPI) {
                const result = await window.electronAPI.pythonAuth(keyFile, projectId);
                
                if (result.status === 'success') {
                    this.showNotification('Authentication successful', 'success');
                    this.hideAuthDialog();
                    await this.initializeEarthEngine();
                } else {
                    this.showNotification('Authentication failed: ' + result.message, 'error');
                }
            } else {
                // Fallback for browser testing
                this.showNotification('Authentication (browser mode)', 'info');
                this.hideAuthDialog();
            }
        } catch (error) {
            console.error('Authentication error:', error);
            this.showNotification('Authentication failed', 'error');
        }
    }

    updateDownloadStatus(message, type = 'info') {
        const statusElement = document.getElementById('download-status');
        if (statusElement) {
            statusElement.textContent = message;
            statusElement.className = `status-text ${type}`;
        }
    }

    setupEventListeners() {
        // Sidebar navigation
        document.querySelectorAll('.sidebar-item').forEach(item => {
            item.addEventListener('click', (e) => {
                const view = item.dataset.view;
                const panel = item.dataset.panel;
                if (view) {
                    this.switchView(view);
                } else if (panel) {
                    this.showPanel(panel);
                }
                document.querySelectorAll('.sidebar-item').forEach(i => i.classList.remove('active'));
                item.classList.add('active');
            });
        });

        // Help button opens help popup
        const helpBtn = document.getElementById('help-button');
        if (helpBtn) {
            helpBtn.addEventListener('click', () => this.showHelpPopup());
        }

        // Auth dialog
        const authSubmit = document.getElementById('auth-submit');
        if (authSubmit) authSubmit.addEventListener('click', () => this.submitAuth());
        const authHelp = document.getElementById('auth-help');
        if (authHelp) authHelp.addEventListener('click', () => this.showHelpPopup());
        const authCancel = document.getElementById('auth-cancel');
        if (authCancel) authCancel.addEventListener('click', () => this.hideAuthDialog());
        const authOffline = document.getElementById('auth-offline');
        if (authOffline) authOffline.addEventListener('click', () => this.hideAuthDialog());

        // Help popup close
        const helpClose = document.getElementById('help-close');
        if (helpClose) helpClose.addEventListener('click', () => this.hideHelpPopup());

        // Calendar buttons
        const calPrev = document.getElementById('calendar-prev');
        if (calPrev) calPrev.addEventListener('click', () => this.previousMonth());
        const calNext = document.getElementById('calendar-next');
        if (calNext) calNext.addEventListener('click', () => this.nextMonth());

        // Map selector
        const mapSelectorBtn = document.getElementById('map-selector-btn');
        if (mapSelectorBtn) mapSelectorBtn.addEventListener('click', () => this.showMapSelector());
        const mapConfirm = document.getElementById('map-confirm');
        if (mapConfirm) mapConfirm.addEventListener('click', () => this.confirmMapSelection());
        const mapCancel = document.getElementById('map-cancel');
        if (mapCancel) mapCancel.addEventListener('click', () => this.hideMapSelector());

        // Calendar buttons
        document.querySelectorAll('.calendar-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.calendarTarget = e.target.dataset.target;
                this.showCalendar();
            });
        });

        // Download controls
        const startDownload = document.getElementById('start-download');
        if (startDownload) startDownload.addEventListener('click', () => this.startDownload());
        const cancelDownload = document.getElementById('cancel-download');
        if (cancelDownload) cancelDownload.addEventListener('click', () => this.cancelDownload());

        // Browse button
        const browseBtn = document.getElementById('browse-btn');
        if (browseBtn) browseBtn.addEventListener('click', () => this.browseOutputDirectory());

        // Best resolution checkbox
        const bestRes = document.getElementById('best-res');
        if (bestRes) bestRes.addEventListener('change', (e) => {
            const targetResInput = document.getElementById('target-res');
            if (targetResInput) targetResInput.disabled = e.target.checked;
        });

        // Tiling method
        const tilingMethod = document.getElementById('tiling-method');
        if (tilingMethod) tilingMethod.addEventListener('change', (e) => {
            const numSubsectionsInput = document.getElementById('num-subsections');
            if (numSubsectionsInput) numSubsectionsInput.disabled = e.target.value !== 'pixel';
        });

        // Theme selector
        const themeSelect = document.getElementById('theme-select');
        if (themeSelect) themeSelect.addEventListener('change', (e) => this.changeTheme(e.target.value));

        // Modal backdrop clicks
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', (e) => {
                // Prevent closing auth modal by clicking backdrop
                if (e.target === modal && modal.id !== 'auth-dialog') {
                    modal.style.display = 'none';
                }
            });
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => this.handleKeyboardShortcuts(e));

        // Progress view controls
        const cancelCurrentDownload = document.getElementById('cancel-current-download');
        if (cancelCurrentDownload) cancelCurrentDownload.addEventListener('click', () => this.cancelDownload());
        const clearCacheLogs = document.getElementById('clear-cache-logs');
        if (clearCacheLogs) clearCacheLogs.addEventListener('click', () => this.clearCacheAndLogs());
        const reloadSettings = document.getElementById('reload-settings');
        if (reloadSettings) reloadSettings.addEventListener('click', () => this.reloadSettings());
        const clearHistory = document.getElementById('clear-history');
        if (clearHistory) clearHistory.addEventListener('click', () => this.clearHistory());

        // Index analysis controls
        const addRasterFiles = document.getElementById('add-raster-files');
        if (addRasterFiles) addRasterFiles.addEventListener('click', () => this.addRasterFiles());
        const clearRasterFiles = document.getElementById('clear-raster-files');
        if (clearRasterFiles) clearRasterFiles.addEventListener('click', () => this.clearRasterFiles());
        const browseAnalysisOutput = document.getElementById('browse-analysis-output');
        if (browseAnalysisOutput) browseAnalysisOutput.addEventListener('click', () => this.browseAnalysisOutputDirectory());
        const startAnalysis = document.getElementById('start-analysis');
        if (startAnalysis) startAnalysis.addEventListener('click', () => this.startIndexAnalysis());
        const cancelAnalysis = document.getElementById('cancel-analysis');
        if (cancelAnalysis) cancelAnalysis.addEventListener('click', () => this.cancelIndexAnalysis());

        // Index selection checkboxes
        document.querySelectorAll('input[id^="index-"]').forEach(checkbox => {
            checkbox.addEventListener('change', () => this.updateAnalysisButtonState());
        });

        // Settings controls
        const browseSettingsOutput = document.getElementById('browse-settings-output');
        if (browseSettingsOutput) browseSettingsOutput.addEventListener('click', () => this.browseSettingsOutputDirectory());
        const reloadSettingsBtn = document.getElementById('reload-settings-btn');
        if (reloadSettingsBtn) reloadSettingsBtn.addEventListener('click', () => this.reloadSettings());
        const clearCacheSettingsBtn = document.getElementById('clear-cache-settings-btn');
        if (clearCacheSettingsBtn) clearCacheSettingsBtn.addEventListener('click', () => this.clearCacheAndLogs());

        // Theme tabs
        document.querySelectorAll('.theme-tab').forEach(tab => {
            tab.addEventListener('click', (e) => this.switchThemeCategory(e.target.dataset.category));
        });

        // Theme options
        const useCharacterCatchphrases = document.getElementById('use-character-catchphrases');
        if (useCharacterCatchphrases) useCharacterCatchphrases.addEventListener('change', () => this.saveThemeSubOptions());
        const showSpecialIcons = document.getElementById('show-special-icons');
        if (showSpecialIcons) showSpecialIcons.addEventListener('change', () => this.saveThemeSubOptions());
        const enableAnimatedBackground = document.getElementById('enable-animated-background');
        if (enableAnimatedBackground) enableAnimatedBackground.addEventListener('change', () => this.saveThemeSubOptions());

        // Vector download controls
        const loadExampleQuery = document.getElementById('load-example-query');
        if (loadExampleQuery) loadExampleQuery.addEventListener('click', () => this.loadExampleVectorQuery());
        const clearVectorQuery = document.getElementById('clear-vector-query');
        if (clearVectorQuery) clearVectorQuery.addEventListener('click', () => this.clearVectorQuery());
        const selectVectorAoi = document.getElementById('select-vector-aoi');
        if (selectVectorAoi) selectVectorAoi.addEventListener('click', () => this.selectVectorAOI());
        const browseVectorOutput = document.getElementById('browse-vector-output');
        if (browseVectorOutput) browseVectorOutput.addEventListener('click', () => this.browseVectorOutputDirectory());
        const startVectorDownload = document.getElementById('start-vector-download');
        if (startVectorDownload) startVectorDownload.addEventListener('click', () => this.startVectorDownload());
        const cancelVectorDownload = document.getElementById('cancel-vector-download');
        if (cancelVectorDownload) cancelVectorDownload.addEventListener('click', () => this.cancelVectorDownload());

        // Vector data source selection
        const vectorDataSource = document.getElementById('vector-data-source');
        if (vectorDataSource) vectorDataSource.addEventListener('change', (e) => this.updateVectorDataSourceDescription(e.target.value));

        // Data viewer controls
        const loadRasterBtn = document.getElementById('load-raster-btn');
        if (loadRasterBtn) loadRasterBtn.addEventListener('click', () => this.loadRasterData());

        // Help popup close button is already wired in HTML
        // Add Escape key to close help popup
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.hideHelpPopup();
            }
        });
        // Clicking outside modal-content closes help popup
        const helpPopup = document.getElementById('help-popup');
        if (helpPopup) {
            helpPopup.addEventListener('click', (e) => {
                if (e.target === helpPopup) {
                    this.hideHelpPopup();
                }
            });
        }
    }

    switchView(viewName) {
        // Hide all views
        document.querySelectorAll('.view-content').forEach(view => {
            view.classList.remove('active');
        });

        // Show selected view
        const targetView = document.getElementById(`${viewName}-view`);
        if (targetView) {
            targetView.classList.add('active');
            this.currentView = viewName;
        }

        // Update page title
        document.title = `Flutter Earth - ${this.getViewTitle(viewName)}`;
    }

    getViewTitle(viewName) {
        const titles = {
            'welcome': 'Home',
            'map': 'Map',
            'download': 'Download',
            'satelliteInfo': 'Satellite Info',
            'indexAnalysis': 'Index Analysis',
            'vectorDownload': 'Vector Download',
            'dataViewer': 'Data Viewer',
            'progress': 'Progress',
            'settings': 'Settings',
            'about': 'About'
        };
        return titles[viewName] || 'Flutter Earth';
    }

    showPanel(panelType) {
        // This would show dockable panels like toolbox, bookmarks, etc.
        console.log(`Showing panel: ${panelType}`);
        this.showNotification(`Panel ${panelType} opened`);
    }

    updateConnectionStatus(status) {
        this.connectionStatus = status;
        const statusElement = document.getElementById('connection-status');
        const statusBar = document.getElementById('status-bar');
        
        if (status === 'online') {
            statusElement.textContent = 'Status: Online';
            statusElement.className = 'status-text online';
            statusBar.style.backgroundColor = 'var(--success)';
            this.statusBarText = 'Online';
        } else {
            statusElement.textContent = 'Status: Offline';
            statusElement.className = 'status-text offline';
            statusBar.style.backgroundColor = 'var(--error)';
            this.statusBarText = 'Offline';
        }
    }

    showAuthDialog() {
        document.getElementById('auth-dialog').style.display = 'flex';
    }

    hideAuthDialog() {
        document.getElementById('auth-dialog').style.display = 'none';
    }

    showHelpPopup() {
        document.getElementById('help-popup').style.display = 'flex';
    }

    hideHelpPopup() {
        document.getElementById('help-popup').style.display = 'none';
    }

    showCalendar() {
        this.renderCalendar();
        document.getElementById('calendar-modal').style.display = 'flex';
    }

    hideCalendar() {
        document.getElementById('calendar-modal').style.display = 'none';
    }

    renderCalendar() {
        const year = this.currentDate.getFullYear();
        const month = this.currentDate.getMonth();
        
        const firstDay = new Date(year, month, 1);
        const lastDay = new Date(year, month + 1, 0);
        const startDate = new Date(firstDay);
        startDate.setDate(startDate.getDate() - firstDay.getDay());
        
        const calendarGrid = document.getElementById('calendar-grid');
        const calendarTitle = document.getElementById('calendar-title');
        
        calendarTitle.textContent = `${this.getMonthName(month)} ${year}`;
        calendarGrid.innerHTML = '';

        // Add day headers
        const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
        days.forEach(day => {
            const dayHeader = document.createElement('div');
            dayHeader.className = 'calendar-day-header';
            dayHeader.textContent = day;
            calendarGrid.appendChild(dayHeader);
        });

        // Add calendar days
        for (let i = 0; i < 42; i++) {
            const date = new Date(startDate);
            date.setDate(startDate.getDate() + i);
            
            const dayElement = document.createElement('div');
            dayElement.className = 'calendar-day';
            dayElement.textContent = date.getDate();
            
            if (date.getMonth() !== month) {
                dayElement.classList.add('other-month');
            }
            
            if (this.isSameDate(date, this.selectedDate)) {
                dayElement.classList.add('selected');
            }
            
            dayElement.addEventListener('click', () => {
                this.selectDate(date);
            });
            
            calendarGrid.appendChild(dayElement);
        }
    }

    selectDate(date) {
        this.selectedDate = date;
        if (this.calendarTarget) {
            const input = document.querySelector(this.calendarTarget);
            if (input) {
                input.value = this.formatDate(date);
            }
        }
        this.hideCalendar();
    }

    formatDate(date) {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    }

    isSameDate(date1, date2) {
        if (!date1 || !date2) return false;
        return date1.getFullYear() === date2.getFullYear() &&
               date1.getMonth() === date2.getMonth() &&
               date1.getDate() === date2.getDate();
    }

    getMonthName(month) {
        const months = [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ];
        return months[month];
    }

    previousMonth() {
        this.currentDate.setMonth(this.currentDate.getMonth() - 1);
        this.renderCalendar();
    }

    nextMonth() {
        this.currentDate.setMonth(this.currentDate.getMonth() + 1);
        this.renderCalendar();
    }

    showMapSelector() {
        document.getElementById('map-modal').style.display = 'flex';
    }

    hideMapSelector() {
        document.getElementById('map-modal').style.display = 'none';
    }

    confirmMapSelection() {
        // This would get the selected coordinates from the map iframe
        this.showNotification('Map selection confirmed');
        this.hideMapSelector();
    }

    loadSensors() {
        const sensorSelect = document.getElementById('sensor-select');
        const sensors = [
            { value: 'landsat8', label: 'Landsat 8' },
            { value: 'sentinel2', label: 'Sentinel-2' },
            { value: 'modis', label: 'MODIS' },
            { value: 'aster', label: 'ASTER' }
        ];

        sensors.forEach(sensor => {
            const option = document.createElement('option');
            option.value = sensor.value;
            option.textContent = sensor.label;
            sensorSelect.appendChild(option);
        });
    }

    cancelDownload() {
        this.showNotification('Download cancelled');
    }

    browseOutputDirectory() {
        // In a real implementation, this would open a file dialog
        // For now, we'll simulate it
        const outputDir = document.getElementById('output-dir');
        outputDir.value = '/path/to/output/directory';
        this.showNotification('Output directory selected');
    }

    changeTheme(themeName) {
        document.documentElement.setAttribute('data-theme', themeName);
        this.showNotification(`Theme changed to ${themeName}`);
    }

    showNotification(message, type = 'success') {
        const notification = document.getElementById('notification-popup');
        const notificationText = document.getElementById('notification-text');
        const notificationContent = notification.querySelector('.notification-content');
        
        notificationText.textContent = message;
        
        // Update notification style based on type
        notificationContent.className = 'notification-content';
        if (type === 'error') {
            notificationContent.style.background = 'var(--error)';
        } else if (type === 'warning') {
            notificationContent.style.background = 'var(--warning)';
        } else {
            notificationContent.style.background = 'var(--success)';
        }
        
        notification.style.display = 'block';
        
        // Auto-hide after 3 seconds
        setTimeout(() => {
            notification.style.display = 'none';
        }, 3000);
    }

    handleKeyboardShortcuts(e) {
        // Ctrl/Cmd + key shortcuts
        if (e.ctrlKey || e.metaKey) {
            switch (e.key) {
                case '1':
                    e.preventDefault();
                    this.switchView('welcome');
                    break;
                case '2':
                    e.preventDefault();
                    this.switchView('download');
                    break;
                case '3':
                    e.preventDefault();
                    this.switchView('map');
                    break;
                case '4':
                    e.preventDefault();
                    this.switchView('settings');
                    break;
                case 'h':
                    e.preventDefault();
                    this.showHelpPopup();
                    break;
                case 'q':
                    e.preventDefault();
                    this.showAuthDialog();
                    break;
            }
        }

        // Escape key to close modals, but not auth modal
        if (e.key === 'Escape') {
            document.querySelectorAll('.modal').forEach(modal => {
                if (modal.style.display === 'flex' && modal.id !== 'auth-dialog') {
                    modal.style.display = 'none';
                }
            });
        }
    }

    // Utility methods
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }

    async clearCacheAndLogs() {
        try {
            if (window.electronAPI) {
                // This would need to be implemented in the Python backend
                this.showNotification('Cache and logs cleared', 'success');
                this.updateStatusText('Cache and logs cleared');
            } else {
                this.showNotification('Cache clearing (browser mode)', 'info');
            }
        } catch (error) {
            console.error('Clear cache error:', error);
            this.showNotification('Failed to clear cache', 'error');
        }
    }

    async reloadSettings() {
        try {
            if (window.electronAPI) {
                // This would need to be implemented in the Python backend
                this.showNotification('Settings reloaded', 'success');
                this.updateStatusText('Settings reloaded');
            } else {
                this.showNotification('Settings reload (browser mode)', 'info');
            }
        } catch (error) {
            console.error('Reload settings error:', error);
            this.showNotification('Failed to reload settings', 'error');
        }
    }

    async clearHistory() {
        try {
            if (window.electronAPI) {
                // This would need to be implemented in the Python backend
                this.showNotification('Download history cleared', 'success');
                this.updateStatusText('Download history cleared');
                this.updateHistoryList([]);
            } else {
                this.showNotification('History clear (browser mode)', 'info');
            }
        } catch (error) {
            console.error('Clear history error:', error);
            this.showNotification('Failed to clear history', 'error');
        }
    }

    updateStatusText(message) {
        const statusElement = document.getElementById('current-status-text');
        if (statusElement) {
            statusElement.textContent = message;
        }
    }

    updateHistoryList(history) {
        const historyList = document.getElementById('history-list');
        if (!historyList) return;

        if (history.length === 0) {
            historyList.innerHTML = `
                <div class="history-item">
                    <div class="history-header">
                        <span class="history-title">No download history</span>
                        <span class="history-status">-</span>
                    </div>
                    <div class="history-details">
                        <span>No downloads completed yet</span>
                    </div>
                </div>
            `;
            return;
        }

        historyList.innerHTML = history.map(item => `
            <div class="history-item">
                <div class="history-header">
                    <span class="history-title">${item.title || 'Download'}</span>
                    <span class="history-status">${item.status || 'Completed'}</span>
                </div>
                <div class="history-details">
                    <span>${item.date || ''}</span>
                    <span>${item.size || ''}</span>
                </div>
            </div>
        `).join('');
    }

    // Index Analysis Functions
    selectedRasterFiles = [];

    addRasterFiles() {
        // In a real implementation, this would open a file dialog
        // For now, we'll simulate adding files
        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.multiple = true;
        fileInput.accept = '.tif,.tiff,.img,.hdr';
        
        fileInput.onchange = (e) => {
            const files = Array.from(e.target.files);
            this.selectedRasterFiles.push(...files.map(f => f.name));
            this.updateRasterFilesList();
            this.updateAnalysisButtonState();
        };
        
        fileInput.click();
    }

    clearRasterFiles() {
        this.selectedRasterFiles = [];
        this.updateRasterFilesList();
        this.updateAnalysisButtonState();
    }

    updateRasterFilesList() {
        const listElement = document.getElementById('raster-files-list');
        const clearButton = document.getElementById('clear-raster-files');
        
        if (this.selectedRasterFiles.length === 0) {
            listElement.innerHTML = '<div class="no-files">No raster files selected</div>';
            clearButton.disabled = true;
        } else {
            listElement.innerHTML = this.selectedRasterFiles.map((file, index) => `
                <div class="file-item">
                    <span class="file-name">${file}</span>
                    <button class="remove-file" onclick="app.removeRasterFile(${index})">Remove</button>
                </div>
            `).join('');
            clearButton.disabled = false;
        }
    }

    removeRasterFile(index) {
        this.selectedRasterFiles.splice(index, 1);
        this.updateRasterFilesList();
        this.updateAnalysisButtonState();
    }

    updateAnalysisButtonState() {
        const startButton = document.getElementById('start-analysis');
        const hasFiles = this.selectedRasterFiles.length > 0;
        const hasIndices = this.getSelectedIndices().length > 0;
        const hasOutputDir = document.getElementById('analysis-output-dir').value.trim() !== '';
        
        startButton.disabled = !(hasFiles && hasIndices && hasOutputDir);
    }

    getSelectedIndices() {
        const indices = [];
        document.querySelectorAll('input[id^="index-"]:checked').forEach(checkbox => {
            indices.push(checkbox.id.replace('index-', ''));
        });
        return indices;
    }

    browseAnalysisOutputDirectory() {
        // In a real implementation, this would open a directory dialog
        // For now, we'll use a simple prompt
        const dir = prompt('Enter output directory path:');
        if (dir) {
            document.getElementById('analysis-output-dir').value = dir;
            this.updateAnalysisButtonState();
        }
    }

    async startIndexAnalysis() {
        const files = this.selectedRasterFiles;
        const indices = this.getSelectedIndices();
        const outputDir = document.getElementById('analysis-output-dir').value;
        
        if (!files.length || !indices.length || !outputDir) {
            this.showNotification('Please select files, indices, and output directory', 'error');
            return;
        }

        try {
            const startButton = document.getElementById('start-analysis');
            const cancelButton = document.getElementById('cancel-analysis');
            const statusElement = document.getElementById('analysis-status');
            
            startButton.disabled = true;
            cancelButton.disabled = false;
            statusElement.textContent = 'Starting analysis...';
            
            // Simulate analysis progress
            this.simulateAnalysisProgress();
            
            this.showNotification('Index analysis started', 'success');
        } catch (error) {
            console.error('Analysis error:', error);
            this.showNotification('Analysis failed', 'error');
        }
    }

    cancelIndexAnalysis() {
        const startButton = document.getElementById('start-analysis');
        const cancelButton = document.getElementById('cancel-analysis');
        const statusElement = document.getElementById('analysis-status');
        
        startButton.disabled = false;
        cancelButton.disabled = true;
        statusElement.textContent = 'Analysis cancelled';
        
        this.showNotification('Analysis cancelled', 'info');
    }

    simulateAnalysisProgress() {
        const progressElement = document.getElementById('analysis-progress');
        const statusElement = document.getElementById('analysis-status');
        const cancelButton = document.getElementById('cancel-analysis');
        
        let progress = 0;
        const interval = setInterval(() => {
            progress += Math.random() * 10;
            if (progress >= 100) {
                progress = 100;
                clearInterval(interval);
                statusElement.textContent = 'Analysis completed';
                cancelButton.disabled = true;
                document.getElementById('start-analysis').disabled = false;
                this.showNotification('Index analysis completed', 'success');
            }
            
            progressElement.style.width = `${progress}%`;
            statusElement.textContent = `Processing... ${Math.round(progress)}%`;
        }, 500);
    }

    // Settings Functions
    availableThemes = [
        // Default themes
        { name: 'default', display_name: 'Default', category: 'default', background: '#f0f0f0', primary: '#e91e63', emoji: '🌍', welcomeMessage: 'Welcome to Flutter Earth!', notificationMessage: 'Theme changed to Default 🌍' },
        { name: 'dark', display_name: 'Dark Theme', category: 'dark', background: '#2d2d2d', primary: '#4fc3f7', emoji: '🌑', welcomeMessage: 'Welcome to the Dark Side!', notificationMessage: 'Theme changed to Dark 🌑' },
        { name: 'light', display_name: 'Light Theme', category: 'light', background: '#ffffff', primary: '#2196f3', emoji: '🌞', welcomeMessage: 'Bright and Light!', notificationMessage: 'Theme changed to Light 🌞' },
        // Mane 6
        { name: 'twilight_sparkle', display_name: 'Twilight Sparkle', category: 'mlp', background: '#f8c5f8', primary: '#9c27b0', emoji: '📚', welcomeMessage: 'Magic of Friendship!', notificationMessage: 'Twilight Sparkle magic! 📚' },
        { name: 'rainbow_dash', display_name: 'Rainbow Dash', category: 'mlp', background: '#e3f2fd', primary: '#00bcd4', emoji: '🌈', welcomeMessage: '20% Cooler!', notificationMessage: 'Rainbow Dash zoom! 🌈' },
        { name: 'applejack', display_name: 'Applejack', category: 'mlp', background: '#fff3e0', primary: '#ff9800', emoji: '🍏', welcomeMessage: 'Honest to the Core!', notificationMessage: 'Applejack style! 🍏' },
        { name: 'pinkie_pie', display_name: 'Pinkie Pie', category: 'mlp', background: '#ffe0f7', primary: '#ff69b4', emoji: '🎉', welcomeMessage: 'Smile! Smile! Smile!', notificationMessage: 'Pinkie Pie party! 🎉' },
        { name: 'rarity', display_name: 'Rarity', category: 'mlp', background: '#f3e6ff', primary: '#b39ddb', emoji: '💎', welcomeMessage: 'Simply Fabulous!', notificationMessage: 'Rarity glam! 💎' },
        { name: 'fluttershy', display_name: 'Fluttershy', category: 'mlp', background: '#f0fff0', primary: '#aed581', emoji: '🦋', welcomeMessage: 'Kindness is Magic!', notificationMessage: 'Fluttershy gentle! 🦋' },
        // Pride
        { name: 'trans_pride', display_name: 'Trans Pride', category: 'pride', background: '#55cdfc', primary: '#f7a8b8', emoji: '🏳️‍⚧️', welcomeMessage: 'Trans Rights are Human Rights!', notificationMessage: 'Trans Pride! 🏳️‍⚧️' },
        { name: 'bi_pride', display_name: 'Bi Pride', category: 'pride', background: '#d60270', primary: '#0038a8', emoji: '💖💜💙', welcomeMessage: 'Proud to be Bi!', notificationMessage: 'Bi Pride! 💖💜💙' },
        { name: 'mlm_pride', display_name: 'MLM Pride', category: 'pride', background: '#78dbe2', primary: '#078d70', emoji: '🏳️‍🌈♂️', welcomeMessage: 'MLM Pride!', notificationMessage: 'MLM Pride! 🏳️‍🌈♂️' },
        { name: 'wlw_pride', display_name: 'WLW Pride', category: 'pride', background: '#d162a4', primary: '#a349a4', emoji: '🏳️‍🌈♀️', welcomeMessage: 'WLW Pride!', notificationMessage: 'WLW Pride! 🏳️‍🌈♀️' },
        { name: 'nonbinary_pride', display_name: 'Nonbinary Pride', category: 'pride', background: '#fff430', primary: '#9c59d1', emoji: '⚧️', welcomeMessage: 'Nonbinary and Proud!', notificationMessage: 'Nonbinary Pride! ⚧️' },
        { name: 'ace_pride', display_name: 'Ace Pride', category: 'pride', background: '#a3a3a3', primary: '#810081', emoji: '🖤🤍💜', welcomeMessage: 'Asexual Pride!', notificationMessage: 'Ace Pride! 🖤🤍💜' },
        { name: 'pan_pride', display_name: 'Pan Pride', category: 'pride', background: '#ff218c', primary: '#ffd800', emoji: '💗💛💙', welcomeMessage: 'Pan and Proud!', notificationMessage: 'Pan Pride! 💗💛💙' },
        { name: 'genderqueer_pride', display_name: 'Genderqueer Pride', category: 'pride', background: '#b57edc', primary: '#4a8123', emoji: '🏳️‍🌈', welcomeMessage: 'Genderqueer and Proud!', notificationMessage: 'Genderqueer Pride! 🏳️‍🌈' },
        // Unity & Black History
        { name: 'unity_pride', display_name: 'Unity Pride', category: 'special', background: '#ffffff', primary: '#000000', emoji: '🤝', welcomeMessage: 'Unity in Diversity!', notificationMessage: 'Unity Pride! 🤝' },
        { name: 'black_history', display_name: 'Black History', category: 'special', background: '#232323', primary: '#ffbe00', emoji: '✊🏿', welcomeMessage: 'Celebrating Black Excellence!', notificationMessage: 'Black History! ✊🏿' },
        // MLP Characters
        { name: 'trixie', display_name: 'Trixie', category: 'mlp', background: '#d0e6ff', primary: '#5e92f3', emoji: '🔮', welcomeMessage: 'The Great and Powerful Trixie!', notificationMessage: 'Trixie magic! 🔮' },
        { name: 'celestia', display_name: 'Celestia', category: 'mlp', background: '#fff8e1', primary: '#ffd600', emoji: '☀️', welcomeMessage: 'Let the Sun Shine!', notificationMessage: 'Celestia shines! ☀️' },
        { name: 'luna', display_name: 'Luna', category: 'mlp', background: '#232946', primary: '#5a4fcf', emoji: '🌙', welcomeMessage: 'Embrace the Night!', notificationMessage: 'Luna glows! 🌙' },
        { name: 'derpy', display_name: 'Derpy', category: 'mlp', background: '#e0e7ef', primary: '#b0c4de', emoji: '🧁', welcomeMessage: 'Muffins for All!', notificationMessage: 'Derpy delivers! 🧁' },
        { name: 'cadence', display_name: 'Cadence', category: 'mlp', background: '#ffe0f0', primary: '#f06292', emoji: '💖', welcomeMessage: 'Love is Magic!', notificationMessage: 'Cadence love! 💖' },
        { name: 'starlight_glimmer', display_name: 'Starlight Glimmer', category: 'mlp', background: '#e1f5fe', primary: '#ba68c8', emoji: '✨', welcomeMessage: 'Equality for All!', notificationMessage: 'Starlight Glimmer! ✨' },
        { name: 'sunset_shimmer', display_name: 'Sunset Shimmer', category: 'mlp', background: '#fff3e0', primary: '#ff7043', emoji: '🌅', welcomeMessage: 'Shimmer and Shine!', notificationMessage: 'Sunset Shimmer! 🌅' },
        // Minecraft
        { name: 'steve', display_name: 'Steve', category: 'minecraft', background: '#7ec850', primary: '#3c763d', emoji: '🧑‍🌾', welcomeMessage: "Let's Mine!", notificationMessage: 'Steve is ready! 🧑‍🌾' },
        { name: 'alex', display_name: 'Alex', category: 'minecraft', background: '#f7a35c', primary: '#e67e22', emoji: '🧑‍🔧', welcomeMessage: "Let's Build!", notificationMessage: 'Alex is ready! 🧑‍🔧' },
        { name: 'enderman', display_name: 'Enderman', category: 'minecraft', background: '#1a1a2e', primary: '#8f00ff', emoji: '👾', welcomeMessage: '... ... ...', notificationMessage: 'Enderman stares! 👾' },
        { name: 'creeper', display_name: 'Creeper', category: 'minecraft', background: '#3fa63f', primary: '#1a4d1a', emoji: '💣', welcomeMessage: "That's a nice app you have...", notificationMessage: 'Creeper hisses! 💣' },
        { name: 'zombie', display_name: 'Zombie', category: 'minecraft', background: '#4e944f', primary: '#2e7d32', emoji: '🧟', welcomeMessage: 'Brains...', notificationMessage: 'Zombie groans! 🧟' },
        { name: 'skeleton', display_name: 'Skeleton', category: 'minecraft', background: '#e0e0e0', primary: '#bdbdbd', emoji: '💀', welcomeMessage: 'Rattle Rattle!', notificationMessage: 'Skeleton rattles! 💀' }
    ];

    currentThemeData = { options: {} };

    switchThemeCategory(category) {
        // Update active tab
        document.querySelectorAll('.theme-tab').forEach(tab => {
            tab.classList.remove('active');
        });
        document.querySelector(`[data-category="${category}"]`).classList.add('active');
        
        // Update theme grid
        this.updateThemeGrid(category);
    }

    updateThemeGrid(category) {
        const gridElement = document.getElementById('theme-grid');
        const themesInCategory = this.availableThemes.filter(theme => theme.category === category);
        
        gridElement.innerHTML = themesInCategory.map(theme => `
            <div class="theme-item ${this.currentThemeData.name === theme.name ? 'selected' : ''}" data-theme="${theme.name}">
                <div class="theme-preview" style="background-color: ${theme.background}; border-color: ${theme.primary}"></div>
                <div class="theme-info">
                    <div class="theme-name">${theme.display_name}</div>
                    <div class="theme-category">${theme.category}</div>
                </div>
            </div>
        `).join('');

        // Add click handlers
        gridElement.querySelectorAll('.theme-item').forEach(item => {
            item.addEventListener('click', () => {
                this.selectTheme(item.dataset.theme);
            });
        });
    }

    selectTheme(themeName) {
        if (this.currentThemeData.name === themeName) return;
        // Update visual selection
        document.querySelectorAll('.theme-item').forEach(item => {
            item.classList.remove('selected');
        });
        document.querySelector(`[data-theme="${themeName}"]`).classList.add('selected');
        // Apply theme
        this.applyTheme(themeName);
        // Update splash and welcome view immediately
        this.showThemeSplash();
        setTimeout(() => this.hideThemeSplash(), 1200);
        this.updateWelcomeView();
        // Save setting
        if (window.electronAPI) {
            // This would call the Python backend to save the theme
            console.log('Theme selected:', themeName);
        }
        this.showNotification(this.getThemeNotification(themeName), 'success');
    }

    applyTheme(themeName) {
        const theme = this.availableThemes.find(t => t.name === themeName);
        if (!theme) return;
        // Update current theme data
        this.currentThemeData.name = themeName;
        // Apply CSS variables (simplified theme application)
        document.documentElement.style.setProperty('--primary-color', theme.primary);
        document.documentElement.style.setProperty('--background-color', theme.background);
        // Update theme options based on new theme
        this.updateThemeOptions();
        // Update welcome view
        this.updateWelcomeView();
    }

    updateThemeOptions() {
        // Update checkboxes based on current theme options
        const options = this.currentThemeData.options || {};
        
        document.getElementById('use-character-catchphrases').checked = options.use_character_catchphrases || false;
        document.getElementById('show-special-icons').checked = options.show_special_icons || false;
        document.getElementById('enable-animated-background').checked = options.enable_animated_background || false;
    }

    saveThemeSubOptions() {
        const subOptions = {
            use_character_catchphrases: document.getElementById('use-character-catchphrases').checked,
            show_special_icons: document.getElementById('show-special-icons').checked,
            enable_animated_background: document.getElementById('enable-animated-background').checked
        };
        
        // Update current theme data
        this.currentThemeData.options = subOptions;
        
        // Save to backend
        if (window.electronAPI) {
            // This would call the Python backend to save theme sub-options
            console.log('Theme sub-options saved:', subOptions);
        }
    }

    browseSettingsOutputDirectory() {
        const dir = prompt('Enter output directory path:');
        if (dir) {
            document.getElementById('settings-output-dir').value = dir;
            // Save setting
            if (window.electronAPI) {
                // This would call the Python backend to save the setting
                console.log('Output directory set:', dir);
            }
        }
    }

    initSettings() {
        // Initialize theme grid with default category
        this.updateThemeGrid('default');
        
        // Load current settings
        this.loadCurrentSettings();
    }

    loadCurrentSettings() {
        // Load current theme and settings
        // This would typically come from the backend
        this.currentThemeData = {
            name: 'default',
            options: {
                use_character_catchphrases: false,
                show_special_icons: false,
                enable_animated_background: false
            }
        };
        
        this.updateThemeOptions();
    }

    // Vector Download Functions
    vectorDownloadInProgress = false;

    loadExampleVectorQuery() {
        const exampleQuery = `[out:json][timeout:25];
(
  node["amenity"="restaurant"]({{bbox}});
  way["amenity"="restaurant"]({{bbox}});
  relation["amenity"="restaurant"]({{bbox}});
);
out body;
>;
out skel qt;`;
        
        document.getElementById('vector-query').value = exampleQuery;
        this.showNotification('Example query loaded', 'info');
    }

    clearVectorQuery() {
        document.getElementById('vector-query').value = '';
        this.showNotification('Query cleared', 'info');
    }

    selectVectorAOI() {
        // This would integrate with the map view
        // For now, we'll use a simple prompt
        const aoi = prompt('Enter AOI coordinates (minLon,minLat,maxLon,maxLat) or GeoJSON:');
        if (aoi) {
            document.getElementById('vector-aoi').value = aoi;
            this.showNotification('AOI set', 'success');
        }
    }

    browseVectorOutputDirectory() {
        const dir = prompt('Enter output directory path:');
        if (dir) {
            document.getElementById('vector-output-dir').value = dir;
        }
    }

    updateVectorDataSourceDescription(source) {
        const descriptions = {
            'overpass': 'Download vector data from OpenStreetMap using Overpass API queries.',
            'natural-earth': 'Download natural Earth vector data including countries, states, and physical features.',
            'openstreetmap': 'Download data directly from OpenStreetMap using various APIs.',
            'custom': 'Use a custom API endpoint for vector data download.'
        };
        
        const descriptionElement = document.getElementById('data-source-description');
        if (descriptionElement) {
            descriptionElement.textContent = descriptions[source] || 'Select a data source to get started.';
        }
    }

    async startVectorDownload() {
        const dataSource = document.getElementById('vector-data-source').value;
        const query = document.getElementById('vector-query').value;
        const aoi = document.getElementById('vector-aoi').value;
        const outputFormat = document.getElementById('vector-output-format').value;
        const outputDir = document.getElementById('vector-output-dir').value;
        
        if (!query.trim()) {
            this.showNotification('Please enter a query', 'error');
            return;
        }
        
        if (!outputDir.trim()) {
            this.showNotification('Please select an output directory', 'error');
            return;
        }

        try {
            this.vectorDownloadInProgress = true;
            const startButton = document.getElementById('start-vector-download');
            const cancelButton = document.getElementById('cancel-vector-download');
            const statusElement = document.getElementById('vector-download-status');
            
            startButton.disabled = true;
            cancelButton.disabled = false;
            statusElement.textContent = 'Starting vector download...';
            
            // Simulate vector download progress
            this.simulateVectorDownloadProgress();
            
            this.showNotification('Vector download started', 'success');
        } catch (error) {
            console.error('Vector download error:', error);
            this.showNotification('Vector download failed', 'error');
            this.vectorDownloadInProgress = false;
        }
    }

    cancelVectorDownload() {
        const startButton = document.getElementById('start-vector-download');
        const cancelButton = document.getElementById('cancel-vector-download');
        const statusElement = document.getElementById('vector-download-status');
        
        startButton.disabled = false;
        cancelButton.disabled = true;
        statusElement.textContent = 'Vector download cancelled';
        
        this.vectorDownloadInProgress = false;
        this.showNotification('Vector download cancelled', 'info');
    }

    simulateVectorDownloadProgress() {
        const progressElement = document.getElementById('vector-download-progress');
        const statusElement = document.getElementById('vector-download-status');
        const cancelButton = document.getElementById('cancel-vector-download');
        
        let progress = 0;
        const interval = setInterval(() => {
            if (!this.vectorDownloadInProgress) {
                clearInterval(interval);
                return;
            }
            
            progress += Math.random() * 8;
            if (progress >= 100) {
                progress = 100;
                clearInterval(interval);
                statusElement.textContent = 'Vector download completed';
                cancelButton.disabled = true;
                document.getElementById('start-vector-download').disabled = false;
                this.vectorDownloadInProgress = false;
                this.showNotification('Vector download completed', 'success');
            }
            
            progressElement.style.width = `${progress}%`;
            statusElement.textContent = `Downloading vector data... ${Math.round(progress)}%`;
        }, 800);
    }

    // Data Viewer Functions
    loadedRasterData = {};
    loadedVectorData = {};
    currentRasterFile = "";
    currentVectorFile = "";

    loadRasterData() {
        // In a real implementation, this would open a file dialog
        // For now, we'll simulate loading a raster file
        const filePath = prompt('Enter raster file path (e.g., /path/to/raster.tif):');
        if (!filePath) return;
        
        // Simulate raster data loading
        this.currentRasterFile = filePath;
        this.loadedRasterData = {
            width: 1024,
            height: 1024,
            bands: 3,
            crs: 'EPSG:4326',
            dtype: 'uint8',
            nodata: 0,
            bounds: {
                left: -180.0,
                bottom: -90.0,
                right: 180.0,
                top: 90.0
            }
        };
        
        this.updateRasterDataDisplay();
        this.updateDataViewerState();
        this.showNotification('Raster data loaded successfully', 'success');
    }

    loadVectorData() {
        // In a real implementation, this would open a file dialog
        // For now, we'll simulate loading a vector file
        const filePath = prompt('Enter vector file path (e.g., /path/to/vector.geojson):');
        if (!filePath) return;
        
        // Simulate vector data loading
        this.currentVectorFile = filePath;
        this.loadedVectorData = {
            feature_count: 1250,
            geometry_types: ['Point', 'LineString', 'Polygon'],
            crs: 'EPSG:4326',
            bounds: {
                left: -122.5,
                bottom: 37.5,
                right: -122.0,
                top: 38.0
            }
        };
        
        this.updateVectorDataDisplay();
        this.updateDataViewerState();
        this.showNotification('Vector data loaded successfully', 'success');
    }

    clearAllData() {
        this.loadedRasterData = {};
        this.loadedVectorData = {};
        this.currentRasterFile = "";
        this.currentVectorFile = "";
        
        this.updateDataViewerState();
        this.showNotification('All data cleared', 'info');
    }

    updateRasterDataDisplay() {
        const data = this.loadedRasterData;
        const bounds = data.bounds;
        
        document.getElementById('raster-file-path').textContent = this.currentRasterFile;
        document.getElementById('raster-dimensions').textContent = `${data.width} x ${data.height}`;
        document.getElementById('raster-bands').textContent = data.bands || 'N/A';
        document.getElementById('raster-crs').textContent = data.crs || 'N/A';
        document.getElementById('raster-dtype').textContent = data.dtype || 'N/A';
        document.getElementById('raster-nodata').textContent = data.nodata !== undefined ? data.nodata : 'N/A';
        document.getElementById('raster-bounds').textContent = bounds ? 
            `(${bounds.left.toFixed(4)}, ${bounds.bottom.toFixed(4)}) to (${bounds.right.toFixed(4)}, ${bounds.top.toFixed(4)})` : 'N/A';
        
        document.getElementById('raster-data-section').style.display = 'block';
    }

    updateVectorDataDisplay() {
        const data = this.loadedVectorData;
        const bounds = data.bounds;
        
        document.getElementById('vector-file-path').textContent = this.currentVectorFile;
        document.getElementById('vector-features').textContent = data.feature_count || 'N/A';
        document.getElementById('vector-geometry-types').textContent = data.geometry_types ? data.geometry_types.join(', ') : 'N/A';
        document.getElementById('vector-crs').textContent = data.crs || 'N/A';
        document.getElementById('vector-bounds').textContent = bounds ? 
            `(${bounds.left.toFixed(4)}, ${bounds.bottom.toFixed(4)}) to (${bounds.right.toFixed(4)}, ${bounds.top.toFixed(4)})` : 'N/A';
        
        document.getElementById('vector-data-section').style.display = 'block';
    }

    updateDataViewerState() {
        const hasData = this.currentRasterFile !== "" || this.currentVectorFile !== "";
        const clearButton = document.getElementById('clear-data-btn');
        const noDataMessage = document.getElementById('no-data-message');
        
        clearButton.disabled = !hasData;
        noDataMessage.style.display = hasData ? 'none' : 'block';
    }

    // Satellite Info Functions
    satelliteCategories = {
        optical: [
            { id: 'Landsat8_OLI', type: 'Optical', resolution: 30, swath: 185, revisit: 16, launch: '2013-02-11', status: 'Active' },
            { id: 'Sentinel2_MSI', type: 'Optical', resolution: 10, swath: 290, revisit: 5, launch: '2015-06-23', status: 'Active' },
            { id: 'PlanetScope', type: 'Optical', resolution: 3, swath: 24, revisit: 1, launch: '2016-01-01', status: 'Active' }
        ],
        radar: [
            { id: 'Sentinel1_SAR', type: 'Radar', resolution: 5, swath: 250, revisit: 6, launch: '2014-04-03', status: 'Active' },
            { id: 'ALOS_PALSAR', type: 'Radar', resolution: 10, swath: 70, revisit: 46, launch: '2006-01-24', status: 'Inactive' }
        ],
        thermal: [
            { id: 'Landsat8_TIRS', type: 'Thermal', resolution: 100, swath: 185, revisit: 16, launch: '2013-02-11', status: 'Active' },
            { id: 'ASTER_TIR', type: 'Thermal', resolution: 90, swath: 60, revisit: 16, launch: '1999-12-18', status: 'Active' }
        ],
        multispectral: [
            { id: 'MODIS', type: 'Multispectral', resolution: 250, swath: 2330, revisit: 1, launch: '1999-12-18', status: 'Active' },
            { id: 'VIIRS', type: 'Multispectral', resolution: 375, swath: 3060, revisit: 1, launch: '2011-10-28', status: 'Active' }
        ]
    };

    selectedSensor = "";

    updateSatelliteCategory(category) {
        const sensors = this.satelliteCategories[category] || [];
        this.updateSensorList(sensors);
    }

    updateSensorList(sensors) {
        const container = document.getElementById('sensor-list-container');
        
        if (sensors.length === 0) {
            container.innerHTML = '<p>No sensors available in this category.</p>';
            return;
        }
        
        container.innerHTML = sensors.map((sensor, index) => `
            <div class="sensor-item ${this.selectedSensor === sensor.id ? 'selected' : ''}" data-sensor="${sensor.id}">
                <div class="sensor-item-content">
                    <div class="sensor-name">${sensor.id}</div>
                    <div class="sensor-type">${sensor.type}</div>
                    <div class="sensor-resolution">${sensor.resolution}m</div>
                </div>
            </div>
        `).join('');
        
        // Add click handlers
        container.querySelectorAll('.sensor-item').forEach(item => {
            item.addEventListener('click', () => {
                this.selectSensor(item.dataset.sensor);
            });
        });
    }

    selectSensor(sensorId) {
        this.selectedSensor = sensorId;
        
        // Update visual selection
        document.querySelectorAll('.sensor-item').forEach(item => {
            item.classList.remove('selected');
        });
        document.querySelector(`[data-sensor="${sensorId}"]`).classList.add('selected');
        
        // Load sensor details
        this.loadSensorDetails(sensorId);
    }

    loadSensorDetails(sensorId) {
        // Find sensor in all categories
        let sensor = null;
        for (const category in this.satelliteCategories) {
            sensor = this.satelliteCategories[category].find(s => s.id === sensorId);
            if (sensor) break;
        }
        
        if (!sensor) return;
        
        // Update sensor details display
        document.getElementById('sensor-name').textContent = sensor.id;
        document.getElementById('sensor-type').textContent = sensor.type;
        document.getElementById('sensor-resolution').textContent = `${sensor.resolution}m`;
        document.getElementById('sensor-swath').textContent = `${sensor.swath}km`;
        document.getElementById('sensor-revisit').textContent = `${sensor.revisit} days`;
        document.getElementById('sensor-launch').textContent = sensor.launch;
        document.getElementById('sensor-status').textContent = sensor.status;
        
        // Update description
        this.updateSensorDescription(sensorId);
        
        // Update bands
        this.updateSensorBands(sensorId);
        
        // Update applications
        this.updateSensorApplications(sensorId);
    }

    updateSensorDescription(sensorId) {
        const descriptions = {
            'Landsat8_OLI': 'The Operational Land Imager (OLI) is a multispectral radiometer that collects image data for nine spectral bands with a spatial resolution of 30 meters for most bands.',
            'Sentinel2_MSI': 'The MultiSpectral Instrument (MSI) provides 13 spectral bands ranging from 10 to 60 meter spatial resolution, designed to provide continuity of SPOT- and Landsat-type data.',
            'PlanetScope': 'PlanetScope provides daily global coverage with 3-5 meter resolution, enabling monitoring of rapid changes on Earth\'s surface.',
            'Sentinel1_SAR': 'The Synthetic Aperture Radar (SAR) operates in C-band and provides all-weather, day-and-night imagery for land and ocean services.',
            'Landsat8_TIRS': 'The Thermal Infrared Sensor (TIRS) measures land surface temperature in two thermal bands with 100 meter spatial resolution.',
            'MODIS': 'The Moderate Resolution Imaging Spectroradiometer provides daily global coverage with 36 spectral bands for monitoring Earth\'s atmosphere, oceans, and land surface.'
        };
        
        const description = descriptions[sensorId] || 'Detailed description not available for this sensor.';
        document.getElementById('sensor-description').textContent = description;
    }

    updateSensorBands(sensorId) {
        const bands = {
            'Landsat8_OLI': ['Band 1: Coastal/Aerosol (0.43-0.45 μm)', 'Band 2: Blue (0.45-0.51 μm)', 'Band 3: Green (0.53-0.59 μm)', 'Band 4: Red (0.64-0.67 μm)', 'Band 5: NIR (0.85-0.88 μm)', 'Band 6: SWIR1 (1.57-1.65 μm)', 'Band 7: SWIR2 (2.11-2.29 μm)', 'Band 8: Panchromatic (0.50-0.68 μm)', 'Band 9: Cirrus (1.36-1.38 μm)'],
            'Sentinel2_MSI': ['Band 1: Coastal aerosol (0.443 μm)', 'Band 2: Blue (0.490 μm)', 'Band 3: Green (0.560 μm)', 'Band 4: Red (0.665 μm)', 'Band 5: Vegetation red edge (0.705 μm)', 'Band 6: Vegetation red edge (0.740 μm)', 'Band 7: Vegetation red edge (0.783 μm)', 'Band 8: NIR (0.842 μm)', 'Band 8A: Vegetation red edge (0.865 μm)', 'Band 9: Water vapour (0.945 μm)', 'Band 10: SWIR - Cirrus (1.375 μm)', 'Band 11: SWIR (1.610 μm)', 'Band 12: SWIR (2.190 μm)'],
            'PlanetScope': ['Blue (0.455-0.515 μm)', 'Green (0.500-0.590 μm)', 'Red (0.590-0.670 μm)', 'NIR (0.780-0.860 μm)'],
            'Sentinel1_SAR': ['C-band (5.405 GHz)'],
            'Landsat8_TIRS': ['Band 10: TIRS-1 (10.6-11.19 μm)', 'Band 11: TIRS-2 (11.50-12.51 μm)'],
            'MODIS': ['36 spectral bands from 0.405 to 14.385 μm']
        };
        
        const sensorBands = bands[sensorId] || ['Band information not available'];
        const bandsList = document.getElementById('sensor-bands-list');
        bandsList.innerHTML = sensorBands.map(band => `<div class="band-item">${band}</div>`).join('');
    }

    updateSensorApplications(sensorId) {
        const applications = {
            'Landsat8_OLI': ['Land cover classification', 'Vegetation monitoring', 'Urban development', 'Water quality assessment', 'Agricultural monitoring'],
            'Sentinel2_MSI': ['Agriculture monitoring', 'Forest monitoring', 'Land cover mapping', 'Disaster management', 'Water quality monitoring'],
            'PlanetScope': ['Change detection', 'Urban monitoring', 'Agricultural monitoring', 'Infrastructure monitoring', 'Environmental assessment'],
            'Sentinel1_SAR': ['Disaster monitoring', 'Sea ice monitoring', 'Land subsidence', 'Forest monitoring', 'Ship detection'],
            'Landsat8_TIRS': ['Surface temperature mapping', 'Thermal anomaly detection', 'Urban heat island analysis', 'Volcanic monitoring', 'Fire detection'],
            'MODIS': ['Global vegetation monitoring', 'Atmospheric monitoring', 'Ocean color monitoring', 'Snow and ice monitoring', 'Fire detection']
        };
        
        const sensorApplications = applications[sensorId] || ['Application information not available'];
        const applicationsList = document.getElementById('sensor-applications-list');
        applicationsList.innerHTML = sensorApplications.map(app => `<div class="application-item">${app}</div>`).join('');
    }

    initSatelliteInfo() {
        // Initialize with optical category
        this.updateSatelliteCategory('optical');
    }

    // About View Functions
    userName = "";
    namePrompted = false;

    visitProjectWebsite() {
        // Open the project website in the default browser
        if (window.electronAPI) {
            window.electronAPI.openExternal('https://github.com/jakobnewman/Flutter-Earth');
        } else {
            // Fallback for web version
            window.open('https://github.com/jakobnewman/Flutter-Earth', '_blank');
        }
    }

    initAboutView() {
        // Check if user name is set
        this.userName = localStorage.getItem('user_name') || "";
        
        if (!this.userName && !this.namePrompted) {
            this.promptForUserName();
            this.namePrompted = true;
        } else {
            this.updateAboutGreeting();
        }
    }

    promptForUserName() {
        const name = prompt('Please enter your name:');
        if (name && name.trim()) {
            this.userName = name.trim();
            localStorage.setItem('user_name', this.userName);
            this.updateAboutGreeting();
        }
    }

    updateAboutGreeting() {
        const greetingElement = document.getElementById('about-greeting');
        if (greetingElement) {
            greetingElement.textContent = this.userName ? `Hello ${this.userName}!` : 'Hello!';
        }
    }

    // Help Popup Functions
    switchHelpTab(tabName) {
        // Update navigation buttons
        document.querySelectorAll('.help-nav-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
        
        // Update content tabs
        document.querySelectorAll('.help-tab').forEach(tab => {
            tab.classList.remove('active');
        });
        document.getElementById(tabName).classList.add('active');
    }

    updateWelcomeView() {
        const theme = this.availableThemes.find(t => t.name === (this.currentThemeData?.name || 'default')) || this.availableThemes[0];
        const logo = document.querySelector('.welcome-logo-img');
        const welcomeTitle = document.querySelector('#welcome-view h1');
        const welcomeMsg = document.querySelector('#welcome-view p');
        if (logo) logo.alt = theme.display_name + ' Logo';
        if (welcomeTitle) welcomeTitle.innerHTML = `${theme.emoji || ''} ${theme.display_name}`;
        if (welcomeMsg) welcomeMsg.textContent = theme.welcomeMessage;
    }

    getThemeNotification(themeName) {
        const theme = this.availableThemes.find(t => t.name === themeName);
        return theme && theme.notificationMessage ? theme.notificationMessage : `Theme changed to ${themeName}`;
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.flutterEarth = new FlutterEarth();
    
    // Set default active sidebar item
    document.querySelector('.sidebar-item[data-view="welcome"]').classList.add('active');
    
    // Add some CSS for calendar day headers
    const style = document.createElement('style');
    style.textContent = `
        .calendar-day-header {
            aspect-ratio: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
            color: var(--text-subtle);
            font-size: var(--font-size-small);
        }
    `;
    document.head.appendChild(style);
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = FlutterEarth;
}

$(document).ready(function() {
    // Splash screen fade in
    $('#splash-screen').hide().fadeIn(800);

    // Sidebar item hover pop
    $('.sidebar-item').hover(
        function() { $(this).stop().animate({ scale: 1.08 }, { step: function(now) { $(this).css('transform', 'scale(' + now + ')'); }, duration: 180 }); },
        function() { $(this).stop().animate({ scale: 1 }, { step: function(now) { $(this).css('transform', 'scale(' + now + ')'); }, duration: 180 }); }
    );

    // Button click pop
    $(document).on('mousedown', '.btn-primary, .btn-secondary', function() {
        $(this).stop().animate({ scale: 1.12 }, { step: function(now) { $(this).css('transform', 'scale(' + now + ')'); }, duration: 80 });
    });
    $(document).on('mouseup mouseleave', '.btn-primary, .btn-secondary', function() {
        $(this).stop().animate({ scale: 1 }, { step: function(now) { $(this).css('transform', 'scale(' + now + ')'); }, duration: 120 });
    });
});

// Override showAuthDialog to pop in the modal
FlutterEarth.prototype.showAuthDialog = function() {
    const $modal = $('#auth-dialog');
    $modal.css({ display: 'flex', opacity: 0 });
    $modal.find('.modal-content').css({ transform: 'scale(0.8)' });
    $modal.animate({ opacity: 1 }, 180, function() {
        $modal.find('.modal-content').animate({ scale: 1.08 }, {
            step: function(now) { $(this).css('transform', 'scale(' + now + ')'); },
            duration: 120,
            complete: function() {
                $(this).animate({ scale: 1 }, {
                    step: function(now) { $(this).css('transform', 'scale(' + now + ')'); },
                    duration: 100
                });
            }
        });
    });
};

// Override hideSplashScreen to fade out
FlutterEarth.prototype.hideSplashScreen = function() {
    $('#splash-screen').fadeOut(500);
};

// Override showNotification to pop/fade
FlutterEarth.prototype.showNotification = function(message, type = 'success') {
    const $notification = $('#notification-popup');
    const $notificationText = $('#notification-text');
    const $notificationContent = $notification.find('.notification-content');
    $notificationText.text(message);
    $notificationContent.removeClass('success error warning');
    if (type === 'error') $notificationContent.addClass('error');
    else if (type === 'warning') $notificationContent.addClass('warning');
    else $notificationContent.addClass('success');
    $notification.stop(true, true).css({ display: 'block', opacity: 0 });
    $notificationContent.css({ transform: 'scale(0.8)' });
    $notification.animate({ opacity: 1 }, 180, function() {
        $notificationContent.animate({ scale: 1.08 }, {
            step: function(now) { $(this).css('transform', 'scale(' + now + ')'); },
            duration: 120,
            complete: function() {
                $(this).animate({ scale: 1 }, {
                    step: function(now) { $(this).css('transform', 'scale(' + now + ')'); },
                    duration: 100
                });
            }
        });
    });
    setTimeout(() => {
        $notification.fadeOut(400);
    }, 3000);
};

// Check if running in Electron (Node.js) environment
function isElectron() {
    // Renderer process
    if (typeof window !== 'undefined' && typeof window.process === 'object' && window.process.type === 'renderer') {
        return true;
    }
    // Main process
    if (typeof process !== 'undefined' && typeof process.versions === 'object' && !!process.versions.electron) {
        return true;
    }
    // User agent
    if (typeof navigator === 'object' && typeof navigator.userAgent === 'string' && navigator.userAgent.indexOf('Electron') >= 0) {
        return true;
    }
    return false;
}

function showLatexErrorBox() {
    const latexBox = document.createElement('div');
    latexBox.style.background = '#fffbe6';
    latexBox.style.border = '2px solid #e0c200';
    latexBox.style.padding = '24px';
    latexBox.style.margin = '32px auto';
    latexBox.style.maxWidth = '600px';
    latexBox.style.fontFamily = 'serif';
    latexBox.style.fontSize = '1.1em';
    latexBox.style.boxShadow = '0 2px 8px rgba(0,0,0,0.08)';
    latexBox.innerHTML = `
        <b style="font-size:1.2em;">\(\text{Electron/Node.js Not Detected}\)</b><br><br>
        \(
          \begin{array}{l}
            \text{The application could not detect Electron (Node.js) running.} \\
            \text{This usually means the Electron dependencies are missing or failed to install.} \\
            \\
            \text{\textbf{Manual Fix:}} \\
            \text{1. Download Electron from:} \\
            \text{\quad \texttt{https://github.com/electron/electron/releases}} \\
            \text{2. Extract the ZIP and place it in:} \\
            \text{\quad frontend/node\_modules/electron} \\
            \text{3. Try running the app again.} \\
            \\
            \text{See the README for full instructions.}
          \end{array}
        \)
    `;
    document.body.prepend(latexBox);
    // Optionally, load MathJax for LaTeX rendering
    if (!window.MathJax) {
        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js';
        script.async = true;
        document.head.appendChild(script);
    } else {
        window.MathJax.typesetPromise();
    }
}

// Helper: Copy Electron folder from user-provided path
async function copyElectronFromUserPath() {
    // Prompt user for folder path
    const userPath = prompt('Electron not found. Please provide the full path to your electron folder (e.g., C:/path/to/electron):');
    if (!userPath) return;

    // Call backend to copy the folder (requires a backend endpoint)
    try {
        const response = await fetch('/copy-electron', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ source: userPath })
        });
        const result = await response.json();
        if (result.success) {
            alert('Electron copied successfully! Please restart the app.');
            location.reload();
        } else {
            alert('Failed to copy Electron: ' + (result.error || 'Unknown error'));
        }
    } catch (err) {
        alert('Error communicating with backend: ' + err.message);
    }
}

function showLatexErrorBoxWithButton() {
    showLatexErrorBox();
    // Add a button for user to provide Electron folder
    const latexBox = document.body.querySelector('div');
    if (latexBox) {
        const btn = document.createElement('button');
        btn.textContent = 'Provide Electron Folder';
        btn.style.marginTop = '16px';
        btn.onclick = copyElectronFromUserPath;
        latexBox.appendChild(btn);
    }
}

window.addEventListener('DOMContentLoaded', function() {
    if (!isElectron()) {
        showLatexErrorBoxWithButton();
    }
}); 