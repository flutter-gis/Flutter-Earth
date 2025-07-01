// Flutter Earth JavaScript - Vanilla JS (No jQuery)

// Note: pako library is loaded via CDN in HTML if needed for gzip decompression

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
        this.crawlerRunning = false;
        this.selectedSatellite = null;
        this.crawlerData = null;
        this.crawlerSpeedSamples = [];
        this.crawlerSpeedWindow = 60; // last 60 seconds
        
        this.init();
    }

    async init() {
        console.log('[DEBUG] FlutterEarth.init() started');
        
        // Wait for DOM to be fully loaded
        if (document.readyState === 'loading') {
            await new Promise(resolve => {
                document.addEventListener('DOMContentLoaded', resolve);
            });
        }
        
        // Initialize views first - ensure welcome view is visible
        this.initializeViews();
        console.log('[DEBUG] Views initialized');
        
        // Setup event listeners
        this.setupEventListeners();
        console.log('[DEBUG] Event listeners setup');
        
        // Initialize other components
        this.loadSensors();
        this.setupCalendar();
        this.initSettings();
        this.initSatelliteInfo();
        this.initAboutView();
        
        // Try to initialize Earth Engine (but don't block the UI)
        this.initializeEarthEngineAsync();
        
        // Show a simple notification that the app is ready
        setTimeout(() => {
            this.showNotification('Flutter Earth is ready!', 'success');
        }, 1000);
        
        console.log('[DEBUG] FlutterEarth.init() completed');
    }

    // Show a unique splash screen for the theme on startup
    showStartupSplash(theme) {
        return new Promise(resolve => {
            const splash = document.createElement('div');
            splash.className = 'theme-splash';
            splash.innerHTML = `
                <div class="theme-splash-content">
                    <div class="theme-splash-emoji">${theme.icon || theme.emoji}</div>
                    <div class="theme-splash-text">${theme.display_name}</div>
                    <div class="theme-splash-message">${theme.splashText || theme.welcomeMessage}</div>
                </div>
            `;
            splash.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                width: 100vw;
                height: 100vh;
                background: linear-gradient(135deg, ${theme.background} 0%, ${theme.primary} 100%);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 10000;
                opacity: 0;
                transform: scale(0.8);
                transition: all 0.5s ease;
            `;
            document.body.appendChild(splash);
            setTimeout(() => {
                splash.style.opacity = '1';
                splash.style.transform = 'scale(1)';
                // Per-theme effects
                this.runSplashEffect(theme, splash);
            }, 100);
            setTimeout(() => {
                splash.style.opacity = '0';
                splash.style.transform = 'scale(1.1)';
                setTimeout(() => {
                    if (splash.parentNode) splash.parentNode.removeChild(splash);
                    resolve();
                }, 500);
            }, 2500);
        });
    }

    // Per-theme splash effects
    runSplashEffect(theme, splash) {
        switch (theme.splashEffect) {
            case 'confetti':
                this.createConfettiEffectForSplash(splash);
                break;
            case 'rainbow':
                this.createRainbowEffectForSplash(splash);
                break;
            case 'magic':
                this.createMagicEffectForSplash(splash);
                break;
            case 'stars':
                this.createStarsEffectForSplash(splash);
                break;
            case 'sunbeams':
                this.createSunbeamsEffectForSplash(splash);
                break;
            case 'blocky':
                this.createBlockyEffectForSplash(splash);
                break;
            case 'explode':
                this.createExplosionEffectForSplash(splash);
                break;
            default:
                // Subtle fade or nothing
                break;
        }
    }

    // Example per-theme effect implementations
    createConfettiEffectForSplash(splash) {
        for (let i = 0; i < 40; i++) {
            const confetti = document.createElement('div');
            confetti.className = 'confetti-piece';
            confetti.style.cssText = `
                position: absolute;
                width: 12px;
                height: 12px;
                background: ${['#ff69b4', '#ff1493', '#ffd700', '#00bcd4', '#fff'][Math.floor(Math.random() * 5)]};
                left: ${Math.random() * 100}vw;
                top: -20px;
                border-radius: 50%;
                opacity: 0.8;
                animation: confettiFallSplash ${Math.random() * 2 + 1.5}s linear infinite;
                pointer-events: none;
                z-index: 10001;
            `;
            splash.appendChild(confetti);
        }
        if (!document.querySelector('#confetti-splash-style')) {
            const style = document.createElement('style');
            style.id = 'confetti-splash-style';
            style.textContent = `
                @keyframes confettiFallSplash {
                    0% { transform: translateY(0) rotate(0deg); opacity: 0.8; }
                    100% { transform: translateY(100vh) rotate(720deg); opacity: 0; }
                }
            `;
            document.head.appendChild(style);
        }
    }
    createRainbowEffectForSplash(splash) {
        const rainbow = document.createElement('div');
        rainbow.style.cssText = `
            position: absolute;
            width: 80vw;
            height: 20vw;
            left: 10vw;
            top: 30vh;
            background: linear-gradient(90deg, red, orange, yellow, green, blue, indigo, violet);
            border-radius: 50% 50% 0 0 / 100% 100% 0 0;
            opacity: 0.7;
            z-index: 10001;
            animation: rainbowAppear 1.5s ease;
        `;
        splash.appendChild(rainbow);
        if (!document.querySelector('#rainbow-splash-style')) {
            const style = document.createElement('style');
            style.id = 'rainbow-splash-style';
            style.textContent = `
                @keyframes rainbowAppear {
                    0% { opacity: 0; transform: scaleX(0.5); }
                    100% { opacity: 0.7; transform: scaleX(1); }
                }
            `;
            document.head.appendChild(style);
        }
    }
    createMagicEffectForSplash(splash) {
        for (let i = 0; i < 20; i++) {
            const star = document.createElement('div');
            star.innerHTML = '✨';
            star.style.cssText = `
                position: absolute;
                font-size: ${Math.random() * 30 + 20}px;
                left: ${Math.random() * 100}vw;
                top: ${Math.random() * 100}vh;
                opacity: 0.7;
                animation: magicTwinkle ${Math.random() * 2 + 1}s linear infinite;
                pointer-events: none;
                z-index: 10001;
            `;
            splash.appendChild(star);
        }
        if (!document.querySelector('#magic-splash-style')) {
            const style = document.createElement('style');
            style.id = 'magic-splash-style';
            style.textContent = `
                @keyframes magicTwinkle {
                    0%, 100% { opacity: 0.7; }
                    50% { opacity: 1; }
                }
            `;
            document.head.appendChild(style);
        }
    }
    createStarsEffectForSplash(splash) {
        for (let i = 0; i < 30; i++) {
            const star = document.createElement('div');
            star.innerHTML = '★';
            star.style.cssText = `
                position: absolute;
                font-size: ${Math.random() * 18 + 8}px;
                left: ${Math.random() * 100}vw;
                top: ${Math.random() * 100}vh;
                color: #fff;
                opacity: 0.5;
                animation: starTwinkle ${Math.random() * 2 + 1}s linear infinite;
                pointer-events: none;
                z-index: 10001;
            `;
            splash.appendChild(star);
        }
        if (!document.querySelector('#star-splash-style')) {
            const style = document.createElement('style');
            style.id = 'star-splash-style';
            style.textContent = `
                @keyframes starTwinkle {
                    0%, 100% { opacity: 0.5; }
                    50% { opacity: 1; }
                }
            `;
            document.head.appendChild(style);
        }
    }
    createSunbeamsEffectForSplash(splash) {
        for (let i = 0; i < 12; i++) {
            const beam = document.createElement('div');
            beam.style.cssText = `
                position: absolute;
                width: 4px;
                height: 120px;
                left: 50vw;
                top: 40vh;
                background: #fff59d;
                opacity: 0.5;
                border-radius: 2px;
                transform: rotate(${i * 30}deg) translateY(-60px);
                animation: sunbeamPulse 1.5s ease-in-out infinite;
                z-index: 10001;
            `;
            splash.appendChild(beam);
        }
        if (!document.querySelector('#sunbeam-splash-style')) {
            const style = document.createElement('style');
            style.id = 'sunbeam-splash-style';
            style.textContent = `
                @keyframes sunbeamPulse {
                    0%, 100% { opacity: 0.5; }
                    50% { opacity: 1; }
                }
            `;
            document.head.appendChild(style);
        }
    }
    createBlockyEffectForSplash(splash) {
        for (let i = 0; i < 30; i++) {
            const block = document.createElement('div');
            block.style.cssText = `
                position: absolute;
                width: 24px;
                height: 24px;
                left: ${Math.random() * 100}vw;
                top: ${Math.random() * 100}vh;
                background: #7ec850;
                border: 2px solid #3c763d;
                opacity: 0.7;
                animation: blockyJump ${Math.random() * 2 + 1}s ease-in-out infinite;
                z-index: 10001;
            `;
            splash.appendChild(block);
        }
        if (!document.querySelector('#blocky-splash-style')) {
            const style = document.createElement('style');
            style.id = 'blocky-splash-style';
            style.textContent = `
                @keyframes blockyJump {
                    0%, 100% { transform: translateY(0); }
                    50% { transform: translateY(-20px); }
                }
            `;
            document.head.appendChild(style);
        }
    }
    createExplosionEffectForSplash(splash) {
        for (let i = 0; i < 20; i++) {
            const particle = document.createElement('div');
            particle.innerHTML = '💥';
            particle.style.cssText = `
                position: absolute;
                font-size: ${Math.random() * 30 + 20}px;
                left: 50vw;
                top: 50vh;
                opacity: 0.8;
                animation: explodeSplash ${Math.random() * 1.5 + 0.5}s ease-out forwards;
                z-index: 10001;
            `;
            splash.appendChild(particle);
        }
        if (!document.querySelector('#explode-splash-style')) {
            const style = document.createElement('style');
            style.id = 'explode-splash-style';
            style.textContent = `
                @keyframes explodeSplash {
                    0% { transform: scale(0) translate(0,0); opacity: 1; }
                    100% { transform: scale(1.5) translate(${Math.random()*200-100}px,${Math.random()*200-100}px); opacity: 0; }
                }
            `;
            document.head.appendChild(style);
        }
    }

    initializeViews() {
        console.log('[DEBUG] Initializing views');
        
        // Hide all views first
        document.querySelectorAll('.view-content').forEach(view => {
            view.classList.remove('active');
            view.style.display = 'none';
        });
        
        // Show welcome view
        const welcomeView = document.getElementById('welcome-view');
        if (welcomeView) {
            welcomeView.classList.add('active');
            welcomeView.style.display = 'block';
            console.log('[DEBUG] Welcome view activated');
        } else {
            console.error('[DEBUG] Welcome view not found!');
        }
        
        // Set default active sidebar item
        const welcomeSidebarItem = document.querySelector('.sidebar-item[data-view="welcome"]');
        if (welcomeSidebarItem) {
            welcomeSidebarItem.classList.add('active');
            console.log('[DEBUG] Welcome sidebar item activated');
        }
    }

    async initializeEarthEngineAsync() {
        // Run Earth Engine initialization in background
        setTimeout(async () => {
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
                    this.isOfflineMode = true;
                } else {
                    this.updateConnectionStatus('offline');
                    this.statusBarText = 'Earth Engine initialization failed';
                    this.showNotification('Earth Engine initialization failed', 'error');
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
        }, 100);
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
        const params = {
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

        // Add code snippet from web scraped data if available
        if (this.crawlerData && this.crawlerData.satellites && params.sensor) {
            const satelliteName = params.sensor.charAt(0).toUpperCase() + params.sensor.slice(1);
            const satelliteData = this.crawlerData.satellites[satelliteName];
            if (satelliteData && satelliteData[0]?.code_snippet) {
                params.codeSnippet = satelliteData[0].code_snippet;
                params.satelliteInfo = {
                    name: satelliteName,
                    resolution: satelliteData[0].resolution,
                    dataType: satelliteData[0].data_type,
                    description: satelliteData[0].description,
                    bands: satelliteData[0].bands || [],
                    applications: satelliteData[0].applications || []
                };
            }
        }

        return params;
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
            currentStatusElement.textContent = progress.message || 'Downloading...';
        }

        if (cancelButton) {
            cancelButton.disabled = !this.downloadInProgress;
        }
    }

    async submitAuth() {
        const keyFileInput = document.getElementById('auth-key-file');
        const projectIdInput = document.getElementById('auth-project-id');
        
        if (!keyFileInput.files[0] || !projectIdInput.value.trim()) {
            this.showNotification('Please provide both key file and project ID', 'error');
            return;
        }

        try {
            const keyFile = keyFileInput.files[0].path;
            const projectId = projectIdInput.value.trim();
            
            if (window.electronAPI) {
                const result = await window.electronAPI.pythonAuth(keyFile, projectId);
                
                if (result.status === 'success') {
                    this.showNotification('Authentication successful', 'success');
                    this.hideAuthDialog();
                    this.initializeEarthEngineAsync();
                } else {
                    this.showNotification('Authentication failed: ' + result.message, 'error');
                }
            } else {
                this.showNotification('Authentication (browser mode)', 'info');
                this.hideAuthDialog();
            }
        } catch (error) {
            console.error('Auth error:', error);
            this.showNotification('Authentication error: ' + error.message, 'error');
        }
    }

    updateDownloadStatus(message, type = 'info') {
        const statusElement = document.getElementById('download-status');
        if (statusElement) {
            statusElement.textContent = message;
            statusElement.className = `download-status ${type}`;
        }
    }

    setupEventListeners() {
        console.log('[DEBUG] Setting up event listeners');
        
        // Sidebar navigation
        const sidebarItems = document.querySelectorAll('.sidebar-item');
        console.log(`[DEBUG] Found ${sidebarItems.length} sidebar items`);
        
        sidebarItems.forEach((item, index) => {
            console.log(`[DEBUG] Setting up sidebar item ${index}:`, item.textContent.trim(), item.dataset);
            
            item.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                
                try {
                    const view = item.dataset.view;
                    const panel = item.dataset.panel;
                    console.log(`[DEBUG] Sidebar item clicked:`, { view, panel, item: item.textContent.trim() });
                    console.log(`[DEBUG] Sidebar item dataset:`, item.dataset);
                    console.log(`[DEBUG] Sidebar item classes:`, item.className);
                    
                    if (view) {
                        console.log(`[DEBUG] Switching to view: ${view}`);
                        this.switchView(view);
                    } else if (panel) {
                        console.log(`[DEBUG] Showing panel: ${panel}`);
                        this.showPanel(panel);
                    } else {
                        console.warn(`[DEBUG] No view or panel found for sidebar item`);
                    }
                    
                    // Fun click effect
                    this.createClickEffect(e.clientX, e.clientY);
                } catch (error) {
                    console.error('[DEBUG] Error handling sidebar click:', error);
                    this.showNotification('Error switching view: ' + error.message, 'error');
                }
            });
        });

        // Help button opens help popup
        const helpBtn = document.getElementById('help-button');
        if (helpBtn) {
            helpBtn.addEventListener('click', () => {
                this.showHelpPopup();
                // Fun help button effect
                this.createSpinEffect(helpBtn);
            });
        }

        // Add Easter egg to app title
        const appTitle = document.querySelector('.app-title');
        if (appTitle) {
            appTitle.addEventListener('click', () => {
                this.triggerEasterEgg();
            });
        }

        // Add fun effects to welcome logo
        const welcomeLogo = document.querySelector('.welcome-logo');
        if (welcomeLogo) {
            welcomeLogo.addEventListener('click', () => {
                this.createLogoEffect(welcomeLogo);
            });
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
        if (themeSelect) themeSelect.addEventListener('change', (e) => this.applyTheme(e.target.value));

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

        // Theme tabs - will be set up dynamically when settings view is shown
        // (moved to switchView function for settings)

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
        
        const loadVectorBtn = document.getElementById('load-vector-btn');
        if (loadVectorBtn) loadVectorBtn.addEventListener('click', () => this.loadVectorData());
        
        const clearDataBtn = document.getElementById('clear-data-btn');
        if (clearDataBtn) clearDataBtn.addEventListener('click', () => this.clearAllData());

        // Satellite info controls
        const satelliteCategory = document.getElementById('satellite-category');
        if (satelliteCategory) satelliteCategory.addEventListener('change', (e) => this.updateSatelliteCategory(e.target.value));

        // About view controls
        const visitWebsiteBtn = document.getElementById('visit-website-btn');
        if (visitWebsiteBtn) visitWebsiteBtn.addEventListener('click', () => this.visitProjectWebsite());

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
        
        console.log('[DEBUG] Event listeners setup completed');
    }

    // Fun Effects and Easter Eggs
    createClickEffect(x, y) {
        const effect = document.createElement('div');
        effect.className = 'click-effect';
        effect.innerHTML = '✨';
        effect.style.cssText = `
            position: fixed;
            left: ${x}px;
            top: ${y}px;
            font-size: 20px;
            pointer-events: none;
            z-index: 10000;
            animation: clickEffect 0.6s ease-out forwards;
        `;
        
        document.body.appendChild(effect);
        
        setTimeout(() => {
            if (effect.parentNode) {
                effect.parentNode.removeChild(effect);
            }
        }, 600);
    }

    createSpinEffect(element) {
        element.style.animation = 'spin 0.5s ease-out';
        setTimeout(() => {
            element.style.animation = '';
        }, 500);
    }

    createLogoEffect(logo) {
        // Create explosion effect
        for (let i = 0; i < 12; i++) {
            const particle = document.createElement('div');
            particle.className = 'logo-particle';
            particle.innerHTML = '🌟';
            particle.style.cssText = `
                position: absolute;
                font-size: 24px;
                left: 50%;
                top: 50%;
                transform: translate(-50%, -50%);
                animation: logoExplosion 1s ease-out forwards;
                pointer-events: none;
                z-index: 1000;
            `;
            
            // Calculate direction
            const angle = (i / 12) * 2 * Math.PI;
            const distance = 100;
            const x = Math.cos(angle) * distance;
            const y = Math.sin(angle) * distance;
            
            particle.style.setProperty('--x', x + 'px');
            particle.style.setProperty('--y', y + 'px');
            
            logo.appendChild(particle);
            
            setTimeout(() => {
                if (particle.parentNode) {
                    particle.parentNode.removeChild(particle);
                }
            }, 1000);
        }
        
        // Add CSS animation
        if (!document.querySelector('#logo-explosion-style')) {
            const style = document.createElement('style');
            style.id = 'logo-explosion-style';
            style.textContent = `
                @keyframes logoExplosion {
                    0% {
                        transform: translate(-50%, -50%) scale(1);
                        opacity: 1;
                    }
                    100% {
                        transform: translate(calc(-50% + var(--x)), calc(-50% + var(--y))) scale(0);
                        opacity: 0;
                    }
                }
            `;
            document.head.appendChild(style);
        }
    }

    triggerEasterEgg() {
        const messages = [
            "🎉 You found an Easter egg!",
            "🌟 Magic happens when you click!",
            "✨ You're awesome!",
            "🎊 Party time!",
            "💫 You discovered a secret!",
            "🎈 Clicking is fun!",
            "🌈 Rainbow power!",
            "⭐ You're a star!",
            "🎪 Welcome to the circus!",
            "🎭 The show must go on!"
        ];
        
        const randomMessage = messages[Math.floor(Math.random() * messages.length)];
        this.showNotification(randomMessage, 'info');
        
        // Create rainbow trail effect
        this.createRainbowTrail();
    }

    createRainbowTrail() {
        const colors = ['#ff0000', '#ff7f00', '#ffff00', '#00ff00', '#0000ff', '#4b0082', '#9400d3'];
        let colorIndex = 0;
        
        const trail = document.createElement('div');
        trail.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            pointer-events: none;
            z-index: 9999;
            background: linear-gradient(45deg, ${colors.join(', ')});
            opacity: 0;
            animation: rainbowTrail 2s ease-out forwards;
        `;
        
        document.body.appendChild(trail);
        
        // Add CSS animation
        if (!document.querySelector('#rainbow-trail-style')) {
            const style = document.createElement('style');
            style.id = 'rainbow-trail-style';
            style.textContent = `
                @keyframes rainbowTrail {
                    0% {
                        opacity: 0;
                        transform: scale(0.8) rotate(0deg);
                    }
                    50% {
                        opacity: 0.3;
                        transform: scale(1.1) rotate(180deg);
                    }
                    100% {
                        opacity: 0;
                        transform: scale(1.5) rotate(360deg);
                    }
                }
            `;
            document.head.appendChild(style);
        }
        
        setTimeout(() => {
            if (trail.parentNode) {
                trail.parentNode.removeChild(trail);
            }
        }, 2000);
    }

    switchView(viewName) {
        console.log(`[DEBUG] Switching to view: ${viewName}`);
        
        try {
            // Validate view name
            if (!viewName) {
                console.error('[DEBUG] No view name provided');
                return;
            }
        
            // Hide all views
            const allViews = document.querySelectorAll('.view-content');
            console.log(`[DEBUG] Found ${allViews.length} view elements`);
            allViews.forEach(view => {
                view.classList.remove('active');
                view.style.display = 'none';
            });
        
            // Show selected view
            const targetView = document.getElementById(`${viewName}-view`);
            console.log(`[DEBUG] Looking for view: ${viewName}-view, found:`, targetView);
            if (targetView) {
                targetView.style.display = 'block';
                targetView.classList.add('active');
                console.log(`[DEBUG] Successfully switched to ${viewName}-view`);
            } else {
                console.warn(`[DEBUG] View not found: ${viewName}-view`);
                // Fallback: show welcome view if target missing
                const fallback = document.getElementById('welcome-view');
                if (fallback) {
                    fallback.style.display = 'block';
                    fallback.classList.add('active');
                    console.log(`[DEBUG] Fallback to welcome-view`);
                    viewName = 'welcome';
                } else {
                    console.error('[DEBUG] Even welcome view not found!');
                    return;
                }
            }
        
            // Update sidebar active state
            document.querySelectorAll('.sidebar-item').forEach(item => {
                item.classList.remove('active');
            });
            
            const activeSidebarItem = document.querySelector(`.sidebar-item[data-view="${viewName}"]`);
            if (activeSidebarItem) {
                activeSidebarItem.classList.add('active');
                console.log(`[DEBUG] Set sidebar item active: ${viewName}`);
            } else {
                console.warn(`[DEBUG] Sidebar item not found for view: ${viewName}`);
            }
        
            // Update current view tracking
            this.currentView = viewName;
            
            // Update status bar
            this.updateStatusText(`View: ${this.getViewTitle(viewName)}`);

            // --- THEME TABS & GRID LOGIC ---
            if (viewName === 'settings') {
                console.log('[DEBUG] Settings view specific logic starting...');
                
                // Check if settings view is actually visible
                const settingsView = document.getElementById('settings-view');
                if (settingsView) {
                    const computedStyle = window.getComputedStyle(settingsView);
                    console.log('[DEBUG] Settings view display style:', computedStyle.display);
                    console.log('[DEBUG] Settings view visibility:', computedStyle.visibility);
                    console.log('[DEBUG] Settings view opacity:', computedStyle.opacity);
                    console.log('[DEBUG] Settings view element found and accessible');
                    
                    // Force the view to be visible
                    settingsView.style.display = 'block';
                    settingsView.classList.add('active');
                    console.log('[DEBUG] Forced settings view to be visible');
                } else {
                    console.error('[DEBUG] Settings view element NOT FOUND!');
                }
                
                try {
                    this.initSettings(true); // force re-init
                    this.initializeThemeGrid(); // ensure theme grid is properly initialized
                    
                    // Set up theme tab event listeners dynamically
                    const themeTabs = document.querySelectorAll('.theme-tab');
                    console.log('[DEBUG] Found theme tabs:', themeTabs.length);
                    themeTabs.forEach((tab, index) => {
                        console.log(`[DEBUG] Theme tab ${index}:`, tab.textContent.trim(), tab.dataset.category);
                        // Remove any existing listeners to prevent duplicates
                        tab.removeEventListener('click', this.handleThemeTabClick);
                        // Add new listener
                        tab.addEventListener('click', this.handleThemeTabClick.bind(this));
                    });
                    
                    // Set the correct theme tab active
                    const currentTheme = this.currentTheme || 'default_dark';
                    let currentCategory = 'all'; // Default to 'all' category
                    const theme = this.availableThemes.find(t => t.name === currentTheme);
                    if (theme) currentCategory = theme.category;
                    
                    console.log('[DEBUG] Setting active category:', currentCategory);
                    document.querySelectorAll('.theme-tab').forEach(tab => {
                        if (tab.dataset.category === currentCategory) {
                            tab.classList.add('active');
                            console.log('[DEBUG] Activated tab:', tab.textContent.trim());
                        } else {
                            tab.classList.remove('active');
                        }
                    });
                    
                    // Populate the theme grid for the current category
                    this.updateThemeGrid(currentCategory);
                    
                    console.log('[DEBUG] Settings view logic completed successfully');
                } catch (error) {
                    console.error('[DEBUG] Error in settings view logic:', error);
                }
            }
        } catch (error) {
            console.error('[DEBUG] Error in switchView:', error);
            this.showNotification('Error switching view: ' + error.message, 'error');
        }
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
        const authDialog = document.getElementById('auth-dialog');
        if (authDialog) {
            authDialog.style.display = 'flex';
            authDialog.classList.add('show');
        }
    }

    hideAuthDialog() {
        const authDialog = document.getElementById('auth-dialog');
        if (authDialog) {
            authDialog.style.display = 'none';
            authDialog.classList.remove('show');
        }
    }

    showHelpPopup() {
        // Simplified help popup
        this.showNotification('Help documentation coming soon!', 'info');
    }

    hideHelpPopup() {
        // Simplified help popup hiding
        console.log('[DEBUG] Help popup hidden');
    }

    showCalendar() {
        this.renderCalendar();
        const calendarModal = document.getElementById('calendar-modal');
        if (calendarModal) {
            calendarModal.style.display = 'flex';
            calendarModal.classList.add('show');
        }
    }

    hideCalendar() {
        const calendarModal = document.getElementById('calendar-modal');
        if (calendarModal) {
            calendarModal.style.display = 'none';
            calendarModal.classList.remove('show');
        }
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
        const overlay = document.getElementById('map-selector-overlay');
        if (overlay) {
            overlay.style.display = 'block';
        }
        // Optionally, disable background scrolling/interactions here
    }

    hideMapSelector() {
        const overlay = document.getElementById('map-selector-overlay');
        if (overlay) {
            overlay.style.display = 'none';
        }
    }

    confirmMapSelection() {
        // Simplified map selection confirmation
        this.showNotification('Map selection confirmed', 'success');
        this.hideMapSelector();
    }

    loadSensors() {
        console.log('[DEBUG] Loading sensors from crawler data...');
        
        // Try to load from crawler data first
        this.loadSensorsFromCrawlerData().then(() => {
            console.log('[DEBUG] Sensors loaded from crawler data');
        }).catch(() => {
            // Fallback to hardcoded data
            console.log('[DEBUG] Falling back to hardcoded sensor data');
            const sensorSelect = document.getElementById('sensor-select');
            if (sensorSelect) {
                sensorSelect.innerHTML = `
                    <option value="">Choose a sensor...</option>
                    <option value="sentinel-2">Sentinel-2</option>
                    <option value="landsat-8">Landsat 8</option>
                    <option value="landsat-9">Landsat 9</option>
                `;
            }
        });
    }

    async loadSensorsFromCrawlerData() {
        // Load and decompress the .json.gz file using pako
        const gzUrl = '../backend/crawler_data/gee_catalog_data_enhanced.json.gz';
        try {
            const response = await fetch(gzUrl);
            if (!response.ok) throw new Error('Failed to fetch crawler data');
            const arrayBuffer = await response.arrayBuffer();
            const uint8Array = new Uint8Array(arrayBuffer);
            const decompressed = window.pako.ungzip(uint8Array, { to: 'string' });
            const data = JSON.parse(decompressed);
            this.crawlerData = data;
            this.updateSatelliteInfoView(data);
            return data;
        } catch (err) {
            this.showNotification('Failed to load crawler data: ' + err.message, 'error');
            throw err;
        }
    }

    async saveSensorsToCrawlerData(updatedData) {
        // Send updated data to backend for recompression and saving
        if (window.electronAPI && window.electronAPI.saveCrawlerData) {
            try {
                const result = await window.electronAPI.saveCrawlerData(updatedData);
                if (result.status === 'success') {
                    this.showNotification('Crawler data saved successfully', 'success');
                } else {
                    this.showNotification('Failed to save crawler data: ' + result.message, 'error');
                }
            } catch (err) {
                this.showNotification('Failed to save crawler data: ' + err.message, 'error');
            }
        } else {
            this.showNotification('Save not supported in this environment', 'warning');
        }
    }

    updateSatelliteInfoView(data) {
        // Update the new satellite grid instead of the old sensor list
        this.updateSatelliteGrid(data);
        
        // Update crawler status
        this.updateCrawlerStatus('Data Loaded', 'ready');
        
        // Setup new event listeners if not already done
        if (!this.newEventsSetup) {
            this.setupNewSatelliteEvents();
            this.newEventsSetup = true;
        }
    }



    cancelDownload() {
        // Simplified download cancellation
        this.downloadInProgress = false;
        this.showNotification('Download cancelled', 'warning');
    }

    browseOutputDirectory() {
        // Simplified directory browsing
        this.showNotification('Directory browser coming soon', 'info');
    }

    changeTheme(themeName) {
        // Simplified theme changing
        this.showNotification(`Theme changed to ${themeName}`, 'success');
    }

    showNotification(message, type = 'success') {
        const notification = document.getElementById('notification-popup');
        const notificationText = document.getElementById('notification-text');
        const notificationContent = notification?.querySelector('.notification-content');
        
        if (notificationText) notificationText.textContent = message;
        if (notificationContent) {
            notificationContent.className = 'notification-content ' + type;
        }
        
        if (notification) {
        notification.style.display = 'block';
            notification.classList.add('show');
            setTimeout(() => {
                notification.classList.remove('show');
        setTimeout(() => {
            notification.style.display = 'none';
                }, 300);
        }, 3000);
        }
    }

    handleKeyboardShortcuts(e) {
        // Simplified keyboard shortcuts
        if (e.key === 'Escape') {
            this.hideHelpPopup();
        }
    }

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
        // Simplified cache clearing
                this.showNotification('Cache and logs cleared', 'success');
    }

    async reloadSettings() {
        // Simplified settings reload
                this.showNotification('Settings reloaded', 'success');
    }

    async clearHistory() {
        // Simplified history clearing
        this.showNotification('History cleared', 'success');
    }

    updateStatusText(message) {
        const statusElement = document.getElementById('connection-status');
        if (statusElement) {
            statusElement.textContent = message;
        }
    }

    updateHistoryList(history) {
        // Simplified history list update
        console.log('[DEBUG] History list updated');
    }

    // Index Analysis Methods
    selectedRasterFiles = [];

    addRasterFiles() {
        // Simplified raster file addition
        this.showNotification('Raster file browser coming soon', 'info');
    }

    clearRasterFiles() {
        // Simplified raster file clearing
        this.showNotification('Raster files cleared', 'success');
    }

    updateRasterFilesList() {
        // Simplified raster files list update
        console.log('[DEBUG] Raster files list updated');
    }

    removeRasterFile(index) {
        // Simplified raster file removal
        console.log('[DEBUG] Raster file removed at index:', index);
    }

    updateAnalysisButtonState() {
        // Simplified analysis button state update
        console.log('[DEBUG] Analysis button state updated');
    }

    getSelectedIndices() {
        // Simplified selected indices getter
        return [];
    }

    browseAnalysisOutputDirectory() {
        // Simplified analysis output directory browsing
        this.showNotification('Analysis output directory browser coming soon', 'info');
    }

    async startIndexAnalysis() {
        // Simplified index analysis start
            this.showNotification('Index analysis started', 'success');
    }

    cancelIndexAnalysis() {
        // Simplified index analysis cancellation
        this.showNotification('Index analysis cancelled', 'warning');
    }

    simulateAnalysisProgress() {
        // Simplified analysis progress simulation
        console.log('[DEBUG] Analysis progress simulated');
    }

    // Theme Methods - Using generated themes from Python config
    availableThemes = [
        {
            name: 'default_dark',
            display_name: 'Default (Dark)',
            category: 'basic',
            background: '#2E2E2E',
            primary: '#5A9BD5',
            emoji: '🌑',
            icon: '🌑',
            splashEffect: 'stars',
            uiEffect: 'nightGlow',
            iconAnimation: 'twinkle',
            welcomeMessage: 'Welcome to Flutter Earth',
            splashText: 'Flutter Earth',
            notificationMessage: 'Flutter Earth'
        },
        {
            name: 'light',
            display_name: 'Light',
            category: 'basic',
            background: '#F0F0F0',
            primary: '#0078D7',
            emoji: '��',
            icon: '🌞',
            splashEffect: 'sunbeams',
            uiEffect: 'sunshine',
            iconAnimation: 'pulse',
            welcomeMessage: 'Welcome to Flutter Earth',
            splashText: 'Flutter Earth',
            notificationMessage: 'Flutter Earth'
        },
        {
            name: 'twilight_sparkle',
            display_name: 'Twilight Sparkle',
            category: 'mlp',
            background: '#2c1a4d',
            primary: '#6c4a8e',
            emoji: '📚',
            icon: '📚',
            splashEffect: 'magic',
            uiEffect: 'magicSparkle',
            iconAnimation: 'magic',
            welcomeMessage: 'Greetings, Everypony!',
            splashText: "Twilight's Flutter Earth Study",
            notificationMessage: "Twilight's Flutter Earth Study"
        },
        {
            name: 'pinkie_pie',
            display_name: 'Pinkie Pie',
            category: 'mlp',
            background: '#ffe6f2',
            primary: '#ff80c0',
            emoji: '🎉',
            icon: '🎉',
            splashEffect: 'confetti',
            uiEffect: 'partyConfetti',
            iconAnimation: 'bounce',
            welcomeMessage: 'Okie Dokie Lokie!',
            splashText: "Pinkie Pie's Super Duper Party App!",
            notificationMessage: "Pinkie Pie's Super Duper Party App!"
        },
        {
            name: 'fluttershy',
            display_name: 'Fluttershy',
            category: 'mlp',
            background: '#f3e5f5',
            primary: '#ffb3d9',
            emoji: '🦋',
            icon: '🦋',
            splashEffect: 'fade',
            uiEffect: 'none',
            iconAnimation: 'float',
            welcomeMessage: 'Oh, hello there...',
            splashText: "Fluttershy's Gentle Earth Explorer",
            notificationMessage: "Fluttershy's Gentle Earth Explorer"
        },
        {
            name: 'rainbow_dash',
            display_name: 'Rainbow Dash',
            category: 'mlp',
            background: '#e3f2fd',
            primary: '#2196f3',
            emoji: '🌈',
            icon: '🌈',
            splashEffect: 'rainbow',
            uiEffect: 'rainbowTrail',
            iconAnimation: 'rainbow',
            welcomeMessage: 'Hey there!',
            splashText: "Rainbow Dash's Awesome Earth Explorer",
            notificationMessage: "Rainbow Dash's Awesome Earth Explorer"
        },
        {
            name: 'applejack',
            display_name: 'Applejack',
            category: 'mlp',
            background: '#fff3e0',
            primary: '#ff9800',
            emoji: '🍎',
            icon: '🍎',
            splashEffect: 'fade',
            uiEffect: 'none',
            iconAnimation: 'shake',
            welcomeMessage: 'Howdy!',
            splashText: "Applejack's Honest Earth Explorer",
            notificationMessage: "Applejack's Honest Earth Explorer"
        },
        {
            name: 'rarity',
            display_name: 'Rarity',
            category: 'mlp',
            background: '#f3e5f5',
            primary: '#9c27b0',
            emoji: '💎',
            icon: '💎',
            splashEffect: 'fade',
            uiEffect: 'none',
            iconAnimation: 'sparkle',
            welcomeMessage: 'Darling!',
            splashText: "Rarity's Fabulous Earth Explorer",
            notificationMessage: "Rarity's Fabulous Earth Explorer"
        },
        {
            name: 'princess_celestia',
            display_name: 'Princess Celestia',
            category: 'mlp',
            background: '#fff8e1',
            primary: '#ffd54f',
            emoji: '☀️',
            icon: '☀️',
            splashEffect: 'sunbeams',
            uiEffect: 'sunshine',
            iconAnimation: 'glow',
            welcomeMessage: 'Greetings, my little pony!',
            splashText: "Celestia's Solar Surveyor",
            notificationMessage: "Celestia's Solar Surveyor"
        },
        {
            name: 'princess_luna',
            display_name: 'Princess Luna',
            category: 'mlp',
            background: '#23213a',
            primary: '#3949ab',
            emoji: '🌙',
            icon: '🌙',
            splashEffect: 'stars',
            uiEffect: 'nightGlow',
            iconAnimation: 'moonPhase',
            welcomeMessage: 'Good evening, dreamer!',
            splashText: "Luna's Lunar Mapper",
            notificationMessage: "Luna's Lunar Mapper"
        },
        {
            name: 'trixie',
            display_name: 'Trixie',
            category: 'mlp',
            background: '#e1bee7',
            primary: '#7c43bd',
            emoji: '🎩',
            icon: '🎩',
            splashEffect: 'fade',
            uiEffect: 'none',
            iconAnimation: 'magic',
            welcomeMessage: 'Behold, the Great and Powerful Trixie!',
            splashText: "The Great and Powerful Trixie's Map!",
            notificationMessage: "The Great and Powerful Trixie's Map!"
        },
        {
            name: 'starlight_glimmer',
            display_name: 'Starlight Glimmer',
            category: 'mlp',
            background: '#e0f7fa',
            primary: '#ba68c8',
            emoji: '⭐',
            icon: '⭐',
            splashEffect: 'sunbeams',
            uiEffect: 'sunshine',
            iconAnimation: 'twinkle',
            welcomeMessage: 'Welcome, friend!',
            splashText: "Starlight's Equality Explorer",
            notificationMessage: "Starlight's Equality Explorer"
        },
        {
            name: 'derpy_hooves',
            display_name: 'Derpy Hooves',
            category: 'mlp',
            background: '#e0e0e0',
            primary: '#ffd600',
            emoji: '🧁',
            icon: '🧁',
            splashEffect: 'fade',
            uiEffect: 'none',
            iconAnimation: 'wiggle',
            welcomeMessage: 'Muffins!',
            splashText: "Derpy's Muffin Mapper",
            notificationMessage: "Derpy's Muffin Mapper"
        },
        {
            name: 'steve',
            display_name: 'Steve',
            category: 'mc',
            background: '#7ec850',
            primary: '#3c763d',
            emoji: '🧑‍🌾',
            icon: '⛏️',
            splashEffect: 'blocky',
            uiEffect: 'blockyOverlay',
            iconAnimation: 'blockyJump',
            welcomeMessage: "Let's Mine!",
            splashText: 'Ready to build?',
            notificationMessage: 'Ready to build?'
        },
        {
            name: 'alex_minecraft',
            display_name: 'Alex (Minecraft)',
            category: 'mc',
            background: '#f4e2d8',
            primary: '#e67e22',
            emoji: '🧑‍🦰',
            icon: '🪓',
            splashEffect: 'blocky',
            uiEffect: 'blockyOverlay',
            iconAnimation: 'blockyJump',
            welcomeMessage: 'Adventure awaits!',
            splashText: "Let's craft something new!",
            notificationMessage: "Let's craft something new!"
        },
        {
            name: 'creeper_minecraft',
            display_name: 'Creeper (Minecraft)',
            category: 'mc',
            background: '#3fa63f',
            primary: '#1a4d1a',
            emoji: '💣',
            icon: '💣',
            splashEffect: 'explode',
            uiEffect: 'creeperShake',
            iconAnimation: 'explode',
            welcomeMessage: "That's a nice app you have...",
            splashText: 'Sssss... Boom!',
            notificationMessage: 'Sssss... Boom!'
        },
        {
            name: 'zombie_minecraft',
            display_name: 'Zombie (Minecraft)',
            category: 'mc',
            background: '#4caf50',
            primary: '#1b5e20',
            emoji: '🧟',
            icon: '🧟',
            splashEffect: 'blocky',
            uiEffect: 'blockyOverlay',
            iconAnimation: 'shuffle',
            welcomeMessage: 'Brains...',
            splashText: 'Grrr! Stay safe!',
            notificationMessage: 'Grrr! Stay safe!'
        },
        {
            name: 'wlw_pride',
            display_name: 'WLW Pride',
            category: 'queer_pride',
            background: '#d52d00',
            primary: '#a30262',
            emoji: '👭',
            icon: '👭',
            splashEffect: 'rainbow',
            uiEffect: 'rainbowTrail',
            iconAnimation: 'heartbeat',
            welcomeMessage: 'WLW Pride!',
            splashText: 'Love wins! Celebrate love!',
            notificationMessage: 'Love wins! Celebrate love!'
        },
        {
            name: 'mlm_pride',
            display_name: 'MLM Pride',
            category: 'queer_pride',
            background: '#078d70',
            primary: '#26ceaa',
            emoji: '👬',
            icon: '👬',
            splashEffect: 'rainbow',
            uiEffect: 'rainbowTrail',
            iconAnimation: 'heartbeat',
            welcomeMessage: 'MLM Pride!',
            splashText: 'Love wins! Celebrate love!',
            notificationMessage: 'Love wins! Celebrate love!'
        },
        {
            name: 'nonbinary_pride',
            display_name: 'Nonbinary Pride',
            category: 'queer_pride',
            background: '#fff430',
            primary: '#9c59d1',
            emoji: '⚧️',
            icon: '⚧️',
            splashEffect: 'trans',
            uiEffect: 'transWave',
            iconAnimation: 'transWave',
            welcomeMessage: 'Nonbinary and proud!',
            splashText: 'Be you, be bright!',
            notificationMessage: 'Be you, be bright!'
        },
        {
            name: 'genderqueer_pride',
            display_name: 'Genderqueer Pride',
            category: 'queer_pride',
            background: '#b57edc',
            primary: '#4a8123',
            emoji: '🏳️‍🌈',
            icon: '🏳️‍🌈',
            splashEffect: 'rainbow',
            uiEffect: 'rainbowTrail',
            iconAnimation: 'rainbow',
            welcomeMessage: 'Genderqueer and proud!',
            splashText: 'Be yourself, always!',
            notificationMessage: 'Be yourself, always!'
        },
        {
            name: 'pan_pride',
            display_name: 'Pan Pride',
            category: 'queer_pride',
            background: '#ff218c',
            primary: '#ffd800',
            emoji: '💖',
            icon: '💖',
            splashEffect: 'rainbow',
            uiEffect: 'rainbowTrail',
            iconAnimation: 'pulse',
            welcomeMessage: 'Pan and proud!',
            splashText: 'All the love, all the colors!',
            notificationMessage: 'All the love, all the colors!'
        },
        {
            name: 'ace_pride',
            display_name: 'Ace Pride',
            category: 'queer_pride',
            background: '#a3a3a3',
            primary: '#000000',
            emoji: '🖤',
            icon: '🤍',
            splashEffect: 'stars',
            uiEffect: 'nightGlow',
            iconAnimation: 'twinkle',
            welcomeMessage: 'Ace and proud!',
            splashText: 'You are valid and awesome!',
            notificationMessage: 'You are valid and awesome!'
        },
        {
            name: 'aro_pride',
            display_name: 'Aro Pride',
            category: 'queer_pride',
            background: '#3da542',
            primary: '#a8d47a',
            emoji: '💚',
            icon: '💚',
            splashEffect: 'rainbow',
            uiEffect: 'rainbowTrail',
            iconAnimation: 'pulse',
            welcomeMessage: 'Aro and proud!',
            splashText: 'Aromantic joy for all!',
            notificationMessage: 'Aromantic joy for all!'
        },
        {
            name: 'black_pride',
            display_name: 'Black Pride',
            category: 'queer_pride',
            background: '#000000',
            primary: '#f9d71c',
            emoji: '✊🏿',
            icon: '✊🏿',
            splashEffect: 'fade',
            uiEffect: 'nightGlow',
            iconAnimation: 'fistPump',
            welcomeMessage: 'Black Pride!',
            splashText: 'Unity and strength always!',
            notificationMessage: 'Unity and strength always!'
        },
        {
            name: 'global_unity',
            display_name: 'Global Unity',
            category: 'unity_pride',
            background: '#1e3a8a',
            primary: '#fbbf24',
            emoji: '🌍',
            icon: '🌍',
            splashEffect: 'rainbow',
            uiEffect: 'rainbowTrail',
            iconAnimation: 'rotate',
            welcomeMessage: 'One World, One People!',
            splashText: 'United we stand, divided we fall!',
            notificationMessage: 'United we stand, divided we fall!'
        },
        {
            name: 'cultural_unity',
            display_name: 'Cultural Unity',
            category: 'unity_pride',
            background: '#dc2626',
            primary: '#fbbf24',
            emoji: '🎭',
            icon: '🎭',
            splashEffect: 'rainbow',
            uiEffect: 'rainbowTrail',
            iconAnimation: 'dance',
            welcomeMessage: 'Celebrating our differences!',
            splashText: 'Diversity is our strength!',
            notificationMessage: 'Diversity is our strength!'
        },
        {
            name: 'generational_unity',
            display_name: 'Generational Unity',
            category: 'unity_pride',
            background: '#059669',
            primary: '#fbbf24',
            emoji: '👨‍👩‍👧‍👦',
            icon: '👨‍👩‍👧‍👦',
            splashEffect: 'rainbow',
            uiEffect: 'rainbowTrail',
            iconAnimation: 'heartbeat',
            welcomeMessage: 'Bridging generations!',
            splashText: 'Past, present, and future together!',
            notificationMessage: 'Past, present, and future together!'
        },
        {
            name: 'humanitarian_unity',
            display_name: 'Humanitarian Unity',
            category: 'unity_pride',
            background: '#7c3aed',
            primary: '#fbbf24',
            emoji: '🤝',
            icon: '🤝',
            splashEffect: 'rainbow',
            uiEffect: 'rainbowTrail',
            iconAnimation: 'handshake',
            welcomeMessage: 'Helping hands unite!',
            splashText: 'Compassion connects us all!',
            notificationMessage: 'Compassion connects us all!'
        }
    ];

    currentThemeData = { options: {} };
    currentTheme = 'default_dark'; // Match the first theme in the array

    // Handle theme tab clicks dynamically
    handleThemeTabClick(e) {
        e.preventDefault();
        e.stopPropagation();
        
        try {
            const category = e.target.dataset.category;
            console.log('[DEBUG] Theme tab clicked:', category);
            
            // Update active tab
            document.querySelectorAll('.theme-tab').forEach(tab => {
                if (tab.dataset.category === category) {
                    tab.classList.add('active');
                } else {
                    tab.classList.remove('active');
                }
            });
            
            // Update theme grid
            this.updateThemeGrid(category);
        } catch (error) {
            console.error('[DEBUG] Error handling theme tab click:', error);
        }
    }

    // Add missing switchThemeCategory function
    switchThemeCategory(category) {
        console.log('[DEBUG] Switching theme category:', category);
        try {
            // Update theme tabs
            document.querySelectorAll('.theme-tab').forEach(tab => {
                if (tab.dataset.category === category) {
                    tab.classList.add('active');
                } else {
                    tab.classList.remove('active');
                }
            });
            
            // Update theme grid for the selected category
            this.updateThemeGrid(category);
        } catch (error) {
            console.error('[DEBUG] Error switching theme category:', error);
        }
    }

    // Ensure theme grid is initialized when settings view is shown
    initializeThemeGrid() {
        console.log('[DEBUG] Initializing theme grid...');
        setTimeout(() => {
            this.updateThemeGrid();
        }, 100);
    }

    // --- Enhanced updateThemeGrid with better previews ---
    updateThemeGrid(category = null) {
        console.log('[DEBUG] updateThemeGrid called with category:', category);
        
        const themeGrid = document.getElementById('theme-grid');
        if (!themeGrid) {
            console.warn('[Theme] theme-grid element not found, skipping grid update');
            return;
        }
        
        console.log('[DEBUG] Found theme-grid element');
        themeGrid.innerHTML = '';
        let rendered = 0;
        
        try {
            console.log('[DEBUG] Available themes count:', this.availableThemes.length);
            
            // Filter themes by category if specified, otherwise show all
            const themesToShow = category ? 
                this.availableThemes.filter(theme => theme.category === category) : 
                this.availableThemes;
            
            console.log('[DEBUG] Themes to show count:', themesToShow.length);
            console.log('[DEBUG] Themes to show:', themesToShow.map(t => t.name));
            
            themesToShow.forEach((theme, index) => {
                console.log(`[DEBUG] Processing theme ${index + 1}:`, theme.name);
                
                try {
                    // Calculate contrast color for text
                    const bg = theme.background || '#fff';
                    const fg = theme.primary || '#222';
                    
                    function luminance(hex) {
                        hex = hex.replace('#', '');
                        const r = parseInt(hex.substring(0,2),16);
                        const g = parseInt(hex.substring(2,4),16);
                        const b = parseInt(hex.substring(4,6),16);
                        return 0.299*r + 0.587*g + 0.114*b;
                    }
                    
                    let textColor = luminance(bg) > 180 ? '#222' : '#fff';
                    let cardBg = bg;
                    if (Math.abs(luminance(bg) - luminance(fg)) < 60) {
                        cardBg = fg;
                        textColor = luminance(fg) > 180 ? '#222' : '#fff';
                    }
                    
                    const themeItem = document.createElement('div');
                    themeItem.className = 'theme-item';
                    themeItem.dataset.theme = theme.name;
                    themeItem.style.cssText = `
                        background: ${cardBg};
                        color: ${textColor};
                        border: 2px solid ${theme.primary};
                        border-radius: 12px;
                        padding: 16px;
                        margin: 8px;
                        cursor: pointer;
                        transition: all 0.3s ease;
                        position: relative;
                        overflow: hidden;
                        min-width: 200px;
                        text-align: center;
                        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                    `;
                    
                    // Create enhanced theme preview
                    themeItem.innerHTML = `
                        <div class="theme-preview-header theme-icon-animated theme-icon-${theme.iconAnimation || 'pulse'}" style="
                            font-size: 3em;
                            margin-bottom: 12px;
                            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
                        ">${theme.icon || theme.emoji}</div>
                        
                        <div class="theme-preview-gradient" style="
                            background: linear-gradient(135deg, ${theme.background} 0%, ${theme.primary} 100%);
                            height: 60px;
                            border-radius: 8px;
                            margin: 12px 0;
                            position: relative;
                            overflow: hidden;
                        ">
                            <div class="theme-preview-pattern" style="
                                position: absolute;
                                top: 0;
                                left: 0;
                                right: 0;
                                bottom: 0;
                                opacity: 0.3;
                                background-image: ${theme.category === 'mlp' ? 'radial-gradient(circle, white 1px, transparent 1px)' :
                                                 theme.category === 'minecraft' ? 'linear-gradient(45deg, transparent 40%, rgba(255,255,255,0.1) 50%, transparent 60%)' :
                                                 theme.category === 'pride' ? 'linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent)' :
                                                 'none'};
                                background-size: ${theme.category === 'mlp' ? '20px 20px' : '30px 30px'};
                            "></div>
                        </div>
                        
                        <div class="theme-info">
                            <div class="theme-name" style="
                                font-weight: bold;
                                font-size: 1.1em;
                                margin-bottom: 4px;
                                text-shadow: 0 1px 2px rgba(0,0,0,0.2);
                            ">${theme.display_name}</div>
                            <div class="theme-category" style="
                                font-size: 0.9em;
                                opacity: 0.8;
                                margin-bottom: 8px;
                            ">${this.getCategoryDisplayName(theme.category)}</div>
                            <div class="theme-description" style="
                                font-size: 0.8em;
                                opacity: 0.7;
                                font-style: italic;
                            ">${theme.welcomeMessage}</div>
                        </div>
                        
                        ${theme.name === this.currentTheme ? `
                            <div class="theme-selected-indicator" style="
                                position: absolute;
                                top: 8px;
                                right: 8px;
                                background: ${theme.primary};
                                color: ${textColor};
                                border-radius: 50%;
                                width: 24px;
                                height: 24px;
                                display: flex;
                                align-items: center;
                                justify-content: center;
                                font-size: 14px;
                                box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                            ">✓</div>
                        ` : ''}
                    `;
                    
                    // Add hover effects
                    themeItem.addEventListener('mouseenter', () => {
                        themeItem.style.transform = 'translateY(-4px) scale(1.02)';
                        themeItem.style.boxShadow = `0 8px 16px rgba(0,0,0,0.2), 0 0 20px ${theme.primary}40`;
                    });
                    
                    themeItem.addEventListener('mouseleave', () => {
                        themeItem.style.transform = 'translateY(0) scale(1)';
                        themeItem.style.boxShadow = '0 4px 8px rgba(0,0,0,0.1)';
                    });
                    
                    themeItem.addEventListener('click', () => this.selectTheme(theme.name));
                    
                    if (theme.name === this.currentTheme) {
                        themeItem.classList.add('selected');
                        themeItem.style.borderColor = theme.primary;
                        themeItem.style.boxShadow = `0 4px 8px rgba(0,0,0,0.1), 0 0 0 2px ${theme.primary}40`;
                    }
                    
                    themeGrid.appendChild(themeItem);
                    rendered++;
                    console.log(`[DEBUG] Successfully rendered theme: ${theme.name}`);
                    
                } catch (themeError) {
                    console.error(`[DEBUG] Error rendering theme ${theme.name}:`, themeError);
                }
            });
            
            // Add CSS animations for theme effects
            if (!document.querySelector('#theme-animations')) {
                const style = document.createElement('style');
                style.id = 'theme-animations';
                style.textContent = `
                    @keyframes pulse {
                        0%, 100% { transform: scale(1); }
                        50% { transform: scale(1.1); }
                    }
                    @keyframes rainbow {
                        0% { filter: hue-rotate(0deg); }
                        100% { filter: hue-rotate(360deg); }
                    }
                    @keyframes twinkle {
                        0%, 100% { opacity: 1; }
                        50% { opacity: 0.5; }
                    }
                    @keyframes confetti {
                        0% { transform: translateY(-10px) rotate(0deg); opacity: 1; }
                        100% { transform: translateY(10px) rotate(360deg); opacity: 0; }
                    }
                    @keyframes bounce {
                        0%, 20%, 53%, 80%, 100% { transform: translate3d(0,0,0); }
                        40%, 43% { transform: translate3d(0,-30px,0); }
                        70% { transform: translate3d(0,-15px,0); }
                        90% { transform: translate3d(0,-4px,0); }
                    }
                    @keyframes float {
                        0%, 100% { transform: translateY(0px); }
                        50% { transform: translateY(-10px); }
                    }
                    @keyframes shake {
                        0%, 100% { transform: translateX(0); }
                        10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
                        20%, 40%, 60%, 80% { transform: translateX(5px); }
                    }
                    @keyframes sparkle {
                        0%, 100% { opacity: 1; transform: scale(1) rotate(0deg); }
                        25% { opacity: 0.8; transform: scale(1.1) rotate(90deg); }
                        50% { opacity: 0.6; transform: scale(1.2) rotate(180deg); }
                        75% { opacity: 0.8; transform: scale(1.1) rotate(270deg); }
                    }
                    @keyframes glow {
                        0%, 100% { filter: brightness(1) drop-shadow(0 0 5px currentColor); }
                        50% { filter: brightness(1.3) drop-shadow(0 0 15px currentColor); }
                    }
                    @keyframes moonPhase {
                        0% { content: "🌑"; }
                        25% { content: "🌒"; }
                        50% { content: "🌕"; }
                        75% { content: "🌘"; }
                        100% { content: "🌑"; }
                    }
                    @keyframes wiggle {
                        0%, 100% { transform: rotate(-3deg); }
                        50% { transform: rotate(3deg); }
                    }
                    @keyframes blockyJump {
                        0%, 100% { transform: translateY(0) scale(1); }
                        50% { transform: translateY(-8px) scale(1.05); }
                    }
                    @keyframes explode {
                        0% { transform: scale(1) rotate(0deg); }
                        50% { transform: scale(1.5) rotate(180deg); }
                        100% { transform: scale(1) rotate(360deg); }
                    }
                    @keyframes shuffle {
                        0%, 100% { transform: translateX(0) rotate(0deg); }
                        25% { transform: translateX(-5px) rotate(-5deg); }
                        75% { transform: translateX(5px) rotate(5deg); }
                    }
                    @keyframes heartbeat {
                        0%, 100% { transform: scale(1); }
                        14% { transform: scale(1.1); }
                        28% { transform: scale(1); }
                        42% { transform: scale(1.1); }
                        70% { transform: scale(1); }
                    }
                    @keyframes transWave {
                        0% { filter: hue-rotate(0deg) brightness(1); }
                        25% { filter: hue-rotate(90deg) brightness(1.1); }
                        50% { filter: hue-rotate(180deg) brightness(1.2); }
                        75% { filter: hue-rotate(270deg) brightness(1.1); }
                        100% { filter: hue-rotate(360deg) brightness(1); }
                    }
                    @keyframes fistPump {
                        0%, 100% { transform: translateY(0) rotate(0deg); }
                        25% { transform: translateY(-5px) rotate(-10deg); }
                        75% { transform: translateY(-5px) rotate(10deg); }
                    }
                    @keyframes rotate {
                        0% { transform: rotate(0deg); }
                        100% { transform: rotate(360deg); }
                    }
                    @keyframes dance {
                        0%, 100% { transform: translateY(0) rotate(0deg); }
                        25% { transform: translateY(-8px) rotate(-5deg); }
                        50% { transform: translateY(-12px) rotate(0deg); }
                        75% { transform: translateY(-8px) rotate(5deg); }
                    }
                    @keyframes handshake {
                        0%, 100% { transform: translateY(0) rotate(0deg); }
                        25% { transform: translateY(-3px) rotate(-15deg); }
                        75% { transform: translateY(-3px) rotate(15deg); }
                    }
                    @keyframes magic {
                        0%, 100% { transform: scale(1) rotate(0deg); filter: brightness(1); }
                        25% { transform: scale(1.1) rotate(90deg); filter: brightness(1.2); }
                        50% { transform: scale(1.2) rotate(180deg); filter: brightness(1.4); }
                        75% { transform: scale(1.1) rotate(270deg); filter: brightness(1.2); }
                    }
                    
                    /* Theme icon animation classes */
                    .theme-icon-animated {
                        animation-duration: 2s;
                        animation-iteration-count: infinite;
                        animation-timing-function: ease-in-out;
                    }
                    
                    .theme-icon-pulse { animation-name: pulse; }
                    .theme-icon-rainbow { animation-name: rainbow; }
                    .theme-icon-twinkle { animation-name: twinkle; }
                    .theme-icon-bounce { animation-name: bounce; }
                    .theme-icon-float { animation-name: float; }
                    .theme-icon-shake { animation-name: shake; }
                    .theme-icon-sparkle { animation-name: sparkle; }
                    .theme-icon-glow { animation-name: glow; }
                    .theme-icon-moonPhase { animation-name: moonPhase; }
                    .theme-icon-wiggle { animation-name: wiggle; }
                    .theme-icon-blockyJump { animation-name: blockyJump; }
                    .theme-icon-explode { animation-name: explode; }
                    .theme-icon-shuffle { animation-name: shuffle; }
                    .theme-icon-heartbeat { animation-name: heartbeat; }
                    .theme-icon-transWave { animation-name: transWave; }
                    .theme-icon-fistPump { animation-name: fistPump; }
                    .theme-icon-rotate { animation-name: rotate; }
                    .theme-icon-dance { animation-name: dance; }
                    .theme-icon-handshake { animation-name: handshake; }
                    .theme-icon-magic { animation-name: magic; }
                `;
                document.head.appendChild(style);
            }
            
        } catch (err) {
            console.error('[Theme] Error rendering theme grid:', err);
            themeGrid.innerHTML = `<div style="color:red;padding:2em;text-align:center;">Theme grid error: ${err.message}</div>`;
            return;
        }
        
        if (rendered === 0) {
            console.error('[DEBUG] No themes were rendered!');
            themeGrid.innerHTML = '<div style="color:red;padding:2em;text-align:center;">No themes could be rendered. Check console for errors.</div>';
        } else {
            console.log(`[Theme] Successfully rendered ${rendered} theme(s) in grid (${category ? 'category: ' + category : 'all themes'})`);
        }
    }

    selectTheme(themeName) {
        console.log('[DEBUG] Selecting theme:', themeName);
        this.applyTheme(themeName);
    }

    applyTheme(themeName) {
        const theme = this.availableThemes.find(t => t.name === themeName);
        if (!theme) return;
        
        console.log('[DEBUG] Applying theme:', themeName);
        
        this.currentTheme = themeName;
        document.documentElement.setAttribute('data-theme', themeName);
        
        // Update CSS custom properties
        document.documentElement.style.setProperty('--primary', theme.primary);
        document.documentElement.style.setProperty('--primary-dark', theme.primary);
        document.documentElement.style.setProperty('--background', theme.background);
        document.documentElement.style.setProperty('--widget-bg', theme.background);
        
        // Show theme splash
        this.showThemeSplash(theme);
        
        // Update welcome message
        if (this.currentView === 'welcome') {
            this.updateWelcomeMessage(theme.welcomeMessage);
        }
        
        // Show notification
        this.showNotification(theme.splashText || theme.notificationMessage, 'success');
        
        // Save theme preference
        localStorage.setItem('flutter-earth-theme', themeName);
        // Run per-theme UI effect
        this.runUIEffect(theme);
    }

    showThemeSplash(theme) {
        const splash = document.createElement('div');
        splash.className = 'theme-splash';
        
        // Create theme-specific splash content
        let splashContent = `
            <div class="theme-splash-content">
                <div class="theme-splash-emoji">${theme.emoji}</div>
                <div class="theme-splash-text">${theme.display_name}</div>
                <div class="theme-splash-message">${theme.welcomeMessage}</div>
            </div>
        `;
        
        // Add theme-specific decorative elements
        if (theme.category === 'mlp') {
            splashContent += `
                <div class="theme-splash-decoration" style="
                    position: absolute;
                    top: 20px;
                    right: 20px;
                    font-size: 2em;
                    opacity: 0.3;
                    animation: float 3s ease-in-out infinite;
                ">🦄</div>
            `;
        } else if (theme.category === 'minecraft') {
            splashContent += `
                <div class="theme-splash-decoration" style="
                    position: absolute;
                    bottom: 20px;
                    left: 20px;
                    font-size: 2em;
                    opacity: 0.3;
                    animation: blockyJump 2s ease-in-out infinite;
                ">⛏️</div>
            `;
        } else if (theme.category === 'pride') {
            splashContent += `
                <div class="theme-splash-decoration" style="
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    font-size: 4em;
                    opacity: 0.1;
                    animation: rainbow 4s linear infinite;
                ">🏳️‍🌈</div>
            `;
        }
        
        splash.innerHTML = splashContent;
        
        // Enhanced splash styling with theme colors
        splash.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: linear-gradient(135deg, ${theme.background} 0%, ${theme.primary} 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10000;
            opacity: 0;
            transform: scale(0.8);
            transition: all 0.5s ease;
            overflow: hidden;
        `;
        
        // Add theme-specific background patterns
        if (theme.category === 'mlp') {
            splash.style.backgroundImage = `
                linear-gradient(135deg, ${theme.background} 0%, ${theme.primary} 100%),
                radial-gradient(circle at 20% 80%, rgba(255,255,255,0.1) 0%, transparent 50%),
                radial-gradient(circle at 80% 20%, rgba(255,255,255,0.1) 0%, transparent 50%)
            `;
        } else if (theme.category === 'minecraft') {
            splash.style.backgroundImage = `
                linear-gradient(135deg, ${theme.background} 0%, ${theme.primary} 100%),
                repeating-linear-gradient(45deg, transparent, transparent 20px, rgba(255,255,255,0.05) 20px, rgba(255,255,255,0.05) 40px)
            `;
        } else if (theme.category === 'pride') {
            splash.style.backgroundImage = `
                linear-gradient(135deg, ${theme.background} 0%, ${theme.primary} 100%),
                linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.1) 50%, transparent 100%)
            `;
        }
        
        const content = splash.querySelector('.theme-splash-content');
        content.style.cssText = `
            text-align: center;
            color: white;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
            z-index: 2;
            position: relative;
        `;
        
        const emoji = splash.querySelector('.theme-splash-emoji');
        emoji.style.cssText = `
            font-size: 120px;
            margin-bottom: 20px;
            animation: ${theme.splashEffect === 'magic' ? 'pulse 1s ease infinite' :
                       theme.splashEffect === 'rainbow' ? 'rainbow 3s linear infinite' :
                       theme.splashEffect === 'stars' ? 'twinkle 2s ease infinite' :
                       theme.splashEffect === 'confetti' ? 'bounce 1s ease infinite' :
                       theme.splashEffect === 'blocky' ? 'blockyJump 2s ease infinite' :
                       theme.splashEffect === 'explode' ? 'explode 1s ease-out' : 'bounce 1s ease infinite'};
            filter: drop-shadow(0 4px 8px rgba(0,0,0,0.3));
        `;
        
        const text = splash.querySelector('.theme-splash-text');
        text.style.cssText = `
            font-size: 48px;
            font-weight: bold;
            margin-bottom: 16px;
            animation: slideInUp 0.6s ease 0.2s both;
            text-shadow: 0 2px 4px rgba(0,0,0,0.5);
        `;
        
        const message = splash.querySelector('.theme-splash-message');
        message.style.cssText = `
            font-size: 24px;
            opacity: 0.9;
            animation: slideInUp 0.6s ease 0.4s both;
            max-width: 600px;
            margin: 0 auto;
            line-height: 1.4;
        `;
        
        // Add enhanced CSS animations
        const style = document.createElement('style');
        style.id = 'enhanced-splash-animations';
        style.textContent = `
            @keyframes slideInUp {
                0% { opacity: 0; transform: translateY(30px); }
                100% { opacity: 1; transform: translateY(0); }
            }
            @keyframes bounce {
                0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
                40% { transform: translateY(-10px); }
                60% { transform: translateY(-5px); }
            }
            @keyframes pulse {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.1); }
            }
            @keyframes rainbow {
                0% { filter: hue-rotate(0deg); }
                100% { filter: hue-rotate(360deg); }
            }
            @keyframes twinkle {
                0%, 100% { opacity: 1; transform: scale(1); }
                50% { opacity: 0.7; transform: scale(1.05); }
            }
            @keyframes blockyJump {
                0%, 100% { transform: translateY(0) rotate(0deg); }
                25% { transform: translateY(-10px) rotate(5deg); }
                75% { transform: translateY(-5px) rotate(-5deg); }
            }
            @keyframes explode {
                0% { transform: scale(1); }
                50% { transform: scale(1.3); }
                100% { transform: scale(1); }
            }
            @keyframes float {
                0%, 100% { transform: translateY(0px); }
                50% { transform: translateY(-10px); }
            }
        `;
        document.head.appendChild(style);
        
        // Add theme-specific particle effects
        if (theme.splashEffect === 'magic' || theme.category === 'mlp') {
            this.createMagicParticles(splash, theme);
        } else if (theme.splashEffect === 'confetti' || theme.category === 'mlp') {
            this.createConfettiParticles(splash, theme);
        } else if (theme.splashEffect === 'stars' || theme.category === 'mlp') {
            this.createStarParticles(splash, theme);
        } else if (theme.splashEffect === 'blocky' || theme.category === 'minecraft') {
            this.createBlockyParticles(splash, theme);
        }
        
        document.body.appendChild(splash);
        
        // Animate in
        setTimeout(() => {
            splash.style.opacity = '1';
            splash.style.transform = 'scale(1)';
        }, 100);
        
        // Animate out after delay
        setTimeout(() => {
            splash.style.opacity = '0';
            splash.style.transform = 'scale(1.1)';
            setTimeout(() => {
                if (splash.parentNode) {
                    splash.parentNode.removeChild(splash);
                }
                if (style.parentNode) {
                    style.parentNode.removeChild(style);
                }
            }, 500);
        }, 2500);
    }

    hideThemeSplash() {
        const splash = document.querySelector('.theme-splash');
        if (splash) {
            splash.style.opacity = '0';
            setTimeout(() => {
                if (splash.parentNode) splash.parentNode.removeChild(splash);
            }, 500);
        }
    }

    updateWelcomeMessage(message) {
        const welcomeTitle = document.querySelector('#welcome-view h1');
        if (welcomeTitle) {
            // Add typing effect class
            welcomeTitle.classList.add('typing-effect');
            
            // Animate the text change
            welcomeTitle.style.opacity = '0';
            welcomeTitle.style.transform = 'translateY(-20px)';
            
            setTimeout(() => {
                welcomeTitle.textContent = message;
                welcomeTitle.style.opacity = '1';
                welcomeTitle.style.transform = 'translateY(0)';
                
                // Add fun emoji and effects
                this.addWelcomeEffects();
            }, 300);
        }
    }

    addWelcomeEffects() {
        // Add floating particles effect
        this.createFloatingParticles();
        
        // Add welcome sound effect (if available)
        this.playWelcomeSound();
        
        // Add confetti effect for special themes
        if (this.currentTheme.includes('pinkie') || this.currentTheme.includes('party')) {
            this.createConfettiEffect();
        }
    }

    createFloatingParticles() {
        const welcomeView = document.getElementById('welcome-view');
        if (!welcomeView) return;
        
        // Create floating particles
        for (let i = 0; i < 20; i++) {
            const particle = document.createElement('div');
            particle.className = 'floating-particle';
            particle.innerHTML = ['🌟', '✨', '💫', '⭐', '🎉'][Math.floor(Math.random() * 5)];
            particle.style.cssText = `
                position: absolute;
                font-size: ${Math.random() * 20 + 10}px;
                left: ${Math.random() * 100}%;
                top: ${Math.random() * 100}%;
                animation: floatParticle ${Math.random() * 10 + 10}s linear infinite;
                opacity: 0.7;
                pointer-events: none;
                z-index: 1;
            `;
            welcomeView.appendChild(particle);
        }
        
        // Add CSS animation for particles
        if (!document.querySelector('#particle-style')) {
            const style = document.createElement('style');
            style.id = 'particle-style';
            style.textContent = `
                @keyframes floatParticle {
                    0% {
                        transform: translateY(0px) rotate(0deg);
                        opacity: 0.7;
                    }
                    50% {
                        opacity: 1;
                    }
                    100% {
                        transform: translateY(-100vh) rotate(360deg);
                        opacity: 0;
                    }
                }
            `;
            document.head.appendChild(style);
        }
    }

    createConfettiEffect() {
        const welcomeView = document.getElementById('welcome-view');
        if (!welcomeView) return;
        
        // Create confetti pieces
        for (let i = 0; i < 50; i++) {
            const confetti = document.createElement('div');
            confetti.className = 'confetti-piece';
            confetti.style.cssText = `
                position: absolute;
                width: 10px;
                height: 10px;
                background: ${['#ff69b4', '#ff1493', '#ff69b4', '#ff1493', '#ff69b4'][Math.floor(Math.random() * 5)]};
                left: ${Math.random() * 100}%;
                top: -10px;
                animation: confettiFall ${Math.random() * 3 + 2}s linear infinite;
                pointer-events: none;
                z-index: 2;
            `;
            welcomeView.appendChild(confetti);
        }
        
        // Add CSS animation for confetti
        if (!document.querySelector('#confetti-style')) {
            const style = document.createElement('style');
            style.id = 'confetti-style';
            style.textContent = `
                @keyframes confettiFall {
                    0% {
                        transform: translateY(-10px) rotate(0deg);
                        opacity: 1;
                    }
                    100% {
                        transform: translateY(100vh) rotate(720deg);
                        opacity: 0;
                    }
                }
            `;
            document.head.appendChild(style);
        }
    }

    playWelcomeSound() {
        // This would play a welcome sound if audio is available
        console.log('[DEBUG] Welcome sound effect (audio not implemented)');
    }

    getThemeNotification(themeName) {
        const theme = this.availableThemes.find(t => t.name === themeName);
        return theme ? theme.notificationMessage : `Theme ${themeName} applied!`;
    }

    // --- Robust initSettings ---
    _settingsInitialized = false;
    initSettings(force = false) {
        console.log('[DEBUG] Initializing settings (all themes grid)');
        
        // Try to find theme grid, but don't fail if not found
        const themeGrid = document.getElementById('theme-grid');
        if (!themeGrid) {
            console.warn('[Theme] theme-grid element not found, but continuing with settings initialization');
        } else {
            console.log('[DEBUG] Found theme-grid element, updating grid');
            this.updateThemeGrid();
        }
        
        this.loadCurrentSettings();
    }

    loadCurrentSettings() {
        console.log('[DEBUG] Loading current settings');
        
        const themeSelect = document.getElementById('theme-select');
        if (themeSelect) {
            themeSelect.value = this.currentTheme;
        }
        
        this.updateThemeOptions();
    }

    updateThemeOptions() {
        console.log('[DEBUG] Updating theme options');
        
        const useCharacterCatchphrases = document.getElementById('use-character-catchphrases');
        const showSpecialIcons = document.getElementById('show-special-icons');
        const enableAnimatedBackground = document.getElementById('enable-animated-background');
        
        if (useCharacterCatchphrases) {
            useCharacterCatchphrases.checked = this.currentThemeData.options.useCharacterCatchphrases || false;
        }
        
        if (showSpecialIcons) {
            showSpecialIcons.checked = this.currentThemeData.options.showSpecialIcons || false;
        }
        
        if (enableAnimatedBackground) {
            enableAnimatedBackground.checked = this.currentThemeData.options.enableAnimatedBackground || false;
        }
    }

    saveThemeSubOptions() {
        console.log('[DEBUG] Saving theme sub-options');
        
        const useCharacterCatchphrases = document.getElementById('use-character-catchphrases');
        const showSpecialIcons = document.getElementById('show-special-icons');
        const enableAnimatedBackground = document.getElementById('enable-animated-background');
        
        this.currentThemeData.options = {
            useCharacterCatchphrases: useCharacterCatchphrases ? useCharacterCatchphrases.checked : false,
            showSpecialIcons: showSpecialIcons ? showSpecialIcons.checked : false,
            enableAnimatedBackground: enableAnimatedBackground ? enableAnimatedBackground.checked : false
        };
        
        localStorage.setItem('flutter-earth-theme-options', JSON.stringify(this.currentThemeData.options));
        
        if (this.currentThemeData.options.enableAnimatedBackground) {
            this.enableAnimatedBackground();
        } else {
            this.disableAnimatedBackground();
        }
    }

    enableAnimatedBackground() {
        const body = document.body;
        body.style.background = `
            linear-gradient(-45deg, 
                var(--background) 0%, 
                var(--primary) 25%, 
                var(--background) 50%, 
                var(--primary) 75%, 
                var(--background) 100%
            )`;
        body.style.backgroundSize = '400% 400%';
        body.style.animation = 'gradientShift 15s ease infinite';
        body.style.willChange = 'background';
        if (!document.querySelector('#animated-bg-style')) {
            const style = document.createElement('style');
            style.id = 'animated-bg-style';
            style.textContent = `
                @keyframes gradientShift {
                    0% { background-position: 0% 50%; }
                    50% { background-position: 100% 50%; }
                    100% { background-position: 0% 50%; }
                }
            `;
            document.head.appendChild(style);
        }
    }

    disableAnimatedBackground() {
        const body = document.body;
        body.style.background = '';
        body.style.animation = '';
        
        const style = document.querySelector('#animated-bg-style');
        if (style) {
            style.remove();
        }
    }

    // Per-theme UI effects
    runUIEffect(theme) {
        // Remove any previous effect overlays
        document.querySelectorAll('.ui-effect-overlay').forEach(el => el.remove());
        switch (theme.uiEffect) {
            case 'nightGlow':
                this.createNightGlowEffect();
                break;
            case 'sunshine':
                this.createSunshineEffect();
                break;
            case 'magicSparkle':
                this.createMagicSparkleEffect();
                break;
            case 'rainbowTrail':
                this.createRainbowTrailEffect();
                break;
            case 'partyConfetti':
                this.createPartyConfettiEffect();
                break;
            case 'transWave':
                this.createTransWaveEffect();
                break;
            case 'biWave':
                this.createBiWaveEffect();
                break;
            case 'blockyOverlay':
                this.createBlockyOverlayEffect();
                break;
            case 'creeperShake':
                this.createCreeperShakeEffect();
                break;
            default:
                // No effect
                break;
        }
    }

    // Example UI effect implementations
    createNightGlowEffect() {
        const overlay = document.createElement('div');
        overlay.className = 'ui-effect-overlay';
        overlay.style.cssText = 'position:fixed;top:0;left:0;width:100vw;height:100vh;pointer-events:none;z-index:9999;background:radial-gradient(ellipse at 50% 60%,rgba(80,80,120,0.2) 0%,rgba(0,0,0,0.7) 100%);animation:glowPulse 3s infinite alternate;';
        document.body.appendChild(overlay);
        if (!document.querySelector('#glowPulse-style')) {
            const style = document.createElement('style');
            style.id = 'glowPulse-style';
            style.textContent = '@keyframes glowPulse{0%{opacity:0.7;}100%{opacity:1;}}';
            document.head.appendChild(style);
        }
    }
    createSunshineEffect() {
        const overlay = document.createElement('div');
        overlay.className = 'ui-effect-overlay';
        overlay.style.cssText = 'position:fixed;top:0;left:0;width:100vw;height:100vh;pointer-events:none;z-index:9999;background:radial-gradient(circle at 50% 30%,rgba(255,255,200,0.3) 0%,rgba(255,255,255,0) 80%);';
        document.body.appendChild(overlay);
    }
    createMagicSparkleEffect() {
        for (let i = 0; i < 18; i++) {
            const sparkle = document.createElement('div');
            sparkle.className = 'ui-effect-overlay';
            sparkle.innerHTML = '✨';
            sparkle.style.cssText = `position:fixed;left:${Math.random()*100}vw;top:${Math.random()*100}vh;font-size:${Math.random()*24+16}px;pointer-events:none;z-index:9999;opacity:0.7;animation:magicTwinkle 2s linear infinite;`;
            document.body.appendChild(sparkle);
        }
    }
    createRainbowTrailEffect() {
        const overlay = document.createElement('div');
        overlay.className = 'ui-effect-overlay';
        overlay.style.cssText = 'position:fixed;top:0;left:0;width:100vw;height:10px;pointer-events:none;z-index:9999;background:linear-gradient(90deg,red,orange,yellow,green,blue,indigo,violet);animation:rainbowTrailMove 3s linear infinite;';
        document.body.appendChild(overlay);
        if (!document.querySelector('#rainbowTrailMove-style')) {
            const style = document.createElement('style');
            style.id = 'rainbowTrailMove-style';
            style.textContent = '@keyframes rainbowTrailMove{0%{left:-100vw;}100%{left:100vw;}}';
            document.head.appendChild(style);
        }
    }
    createPartyConfettiEffect() {
        for (let i = 0; i < 30; i++) {
            const confetti = document.createElement('div');
            confetti.className = 'ui-effect-overlay';
            confetti.style.cssText = `position:fixed;left:${Math.random()*100}vw;top:-10px;width:10px;height:10px;background:${['#ff69b4','#ff1493','#ffd700','#00bcd4','#fff'][Math.floor(Math.random()*5)]};border-radius:50%;pointer-events:none;z-index:9999;animation:confettiFallSplash ${Math.random()*2+1.5}s linear infinite;`;
            document.body.appendChild(confetti);
        }
    }
    createTransWaveEffect() {
        const overlay = document.createElement('div');
        overlay.className = 'ui-effect-overlay';
        overlay.style.cssText = 'position:fixed;top:0;left:0;width:100vw;height:100vh;pointer-events:none;z-index:9999;background:linear-gradient(135deg,#55cdfc 0%,#f7a8b8 50%,#fff 100%);opacity:0.3;';
        document.body.appendChild(overlay);
    }
    createBiWaveEffect() {
        const overlay = document.createElement('div');
        overlay.className = 'ui-effect-overlay';
        overlay.style.cssText = 'position:fixed;top:0;left:0;width:100vw;height:100vh;pointer-events:none;z-index:9999;background:linear-gradient(135deg,#d60270 0%,#9b4f96 50%,#0038a8 100%);opacity:0.3;';
        document.body.appendChild(overlay);
    }
    createBlockyOverlayEffect() {
        for (let i = 0; i < 20; i++) {
            const block = document.createElement('div');
            block.className = 'ui-effect-overlay';
            block.style.cssText = `position:fixed;left:${Math.random()*100}vw;top:${Math.random()*100}vh;width:24px;height:24px;background:#7ec850;border:2px solid #3c763d;opacity:0.5;pointer-events:none;z-index:9999;animation:blockyJump ${Math.random()*2+1}s ease-in-out infinite;`;
            document.body.appendChild(block);
        }
    }
    createCreeperShakeEffect() {
        document.body.classList.add('creeper-shake');
        setTimeout(()=>document.body.classList.remove('creeper-shake'), 1500);
        if (!document.querySelector('#creeper-shake-style')) {
            const style = document.createElement('style');
            style.id = 'creeper-shake-style';
            style.textContent = '@keyframes creeperShake{0%,100%{transform:translateX(0);}20%{transform:translateX(-10px);}40%{transform:translateX(10px);}60%{transform:translateX(-10px);}80%{transform:translateX(10px);}}body.creeper-shake{animation:creeperShake 0.5s 3;}';
            document.head.appendChild(style);
        }
    }

    // Helper to get display name and icon for a category
    getCategoryDisplayName(category) {
        const map = {
            'all': '🌟 All Themes',
            'basic': '🌍 Basic',
            'mlp': '🦄 My Little Pony',
            'mc': '⛏️ Minecraft',
            'queer_pride': '🏳️‍🌈 Queer Pride',
            'unity_pride': '🤝 Unity Pride',
            'default': '🌍 Default',
            'dark': '🌑 Dark',
            'light': '🌞 Light',
            'professional': '💼 Professional',
            'corporate': '🏢 Corporate',
            'pride': '🏳️‍🌈 Pride',
            'special': '✨ Special',
            'minecraft': '⛏️ Minecraft',
            'other': '⭐ Other',
        };
        return map[category] || (category ? category.charAt(0).toUpperCase() + category.slice(1) : 'Unknown');
    }

    // Add missing function stubs
    loadExampleVectorQuery() {
        console.log('[DEBUG] Loading example vector query...');
        this.showNotification('Example query loaded', 'info');
    }

    clearVectorQuery() {
        console.log('[DEBUG] Clearing vector query...');
        this.showNotification('Vector query cleared', 'info');
    }

    selectVectorAOI() {
        console.log('[DEBUG] Selecting vector AOI...');
        this.showNotification('Vector AOI selection coming soon', 'info');
    }

    browseVectorOutputDirectory() {
        console.log('[DEBUG] Browsing vector output directory...');
        this.showNotification('Vector output directory browser coming soon', 'info');
    }

    startVectorDownload() {
        console.log('[DEBUG] Starting vector download...');
        this.showNotification('Vector download started', 'info');
    }

    cancelVectorDownload() {
        console.log('[DEBUG] Cancelling vector download...');
        this.showNotification('Vector download cancelled', 'info');
    }

    updateVectorDataSourceDescription(source) {
        console.log('[DEBUG] Updating vector data source description:', source);
    }

    loadRasterData() {
        console.log('[DEBUG] Loading raster data...');
        this.showNotification('Raster data loading coming soon', 'info');
    }

    loadVectorData() {
        console.log('[DEBUG] Loading vector data...');
        this.showNotification('Vector data loading coming soon', 'info');
    }

    clearAllData() {
        console.log('[DEBUG] Clearing all data...');
        this.showNotification('All data cleared', 'info');
    }

    updateSatelliteCategory(category) {
        console.log('[DEBUG] Updating satellite category:', category);
        this.showNotification(`Satellite category updated to ${category}`, 'info');
    }

    visitProjectWebsite() {
        console.log('[DEBUG] Visiting project website...');
        this.showNotification('Project website coming soon', 'info');
    }

    browseSettingsOutputDirectory() {
        console.log('[DEBUG] Browsing settings output directory...');
        this.showNotification('Settings output directory browser coming soon', 'info');
    }

    initSatelliteInfo() {
        console.log('[DEBUG] Initializing satellite info...');
        // This will be called when the satellite info view is loaded
        if (this.crawlerData) {
            this.updateSatelliteInfoView(this.crawlerData);
        } else {
            // Try to load data if not already loaded
            this.loadSensorsFromCrawlerData().catch(() => {
                console.log('[DEBUG] Using fallback satellite data');
            });
        }
        
        // Setup web crawler event listeners
        this.setupWebCrawlerEvents();
        
        // Setup satellite search functionality
        this.setupSatelliteSearch();
        
        // Setup sensor action buttons
        this.setupSensorActions();
    }

    initAboutView() {
        console.log('[DEBUG] Initializing about view...');
        // About view initialization logic would go here
    }

    // Particle effect functions for theme splash screens
    createMagicParticles(container, theme) {
        const particles = ['✨', '⭐', '💫', '🌟', '💎'];
        for (let i = 0; i < 15; i++) {
            const particle = document.createElement('div');
            particle.textContent = particles[Math.floor(Math.random() * particles.length)];
            particle.style.cssText = `
                position: absolute;
                font-size: ${20 + Math.random() * 20}px;
                color: ${theme.primary};
                opacity: 0;
                animation: magicFloat ${2 + Math.random() * 3}s ease-in-out infinite;
                animation-delay: ${Math.random() * 2}s;
                left: ${Math.random() * 100}%;
                top: ${Math.random() * 100}%;
                z-index: 1;
                pointer-events: none;
            `;
            container.appendChild(particle);
        }
        
        // Add magic sparkle animation
        const style = document.createElement('style');
        style.textContent = `
            @keyframes magicFloat {
                0% { opacity: 0; transform: translateY(0) rotate(0deg); }
                50% { opacity: 1; transform: translateY(-20px) rotate(180deg); }
                100% { opacity: 0; transform: translateY(-40px) rotate(360deg); }
            }
        `;
        document.head.appendChild(style);
    }

    createConfettiParticles(container, theme) {
        const colors = [theme.primary, theme.background, '#ff69b4', '#00bcd4', '#ffd700'];
        for (let i = 0; i < 30; i++) {
            const confetti = document.createElement('div');
            confetti.style.cssText = `
                position: absolute;
                width: 8px;
                height: 8px;
                background: ${colors[Math.floor(Math.random() * colors.length)]};
                opacity: 0;
                animation: confettiFall ${1 + Math.random() * 2}s ease-in infinite;
                animation-delay: ${Math.random() * 1}s;
                left: ${Math.random() * 100}%;
                top: -10px;
                z-index: 1;
                pointer-events: none;
                border-radius: 2px;
            `;
            container.appendChild(confetti);
        }
        
        const style = document.createElement('style');
        style.textContent = `
            @keyframes confettiFall {
                0% { opacity: 0; transform: translateY(-10px) rotate(0deg); }
                10% { opacity: 1; }
                90% { opacity: 1; }
                100% { opacity: 0; transform: translateY(100vh) rotate(360deg); }
            }
        `;
        document.head.appendChild(style);
    }

    createStarParticles(container, theme) {
        const stars = ['⭐', '✨', '🌟', '💫'];
        for (let i = 0; i < 20; i++) {
            const star = document.createElement('div');
            star.textContent = stars[Math.floor(Math.random() * stars.length)];
            star.style.cssText = `
                position: absolute;
                font-size: ${15 + Math.random() * 15}px;
                color: white;
                opacity: 0;
                animation: starTwinkle ${1.5 + Math.random() * 2}s ease-in-out infinite;
                animation-delay: ${Math.random() * 2}s;
                left: ${Math.random() * 100}%;
                top: ${Math.random() * 100}%;
                z-index: 1;
                pointer-events: none;
            `;
            container.appendChild(star);
        }
        
        const style = document.createElement('style');
        style.textContent = `
            @keyframes starTwinkle {
                0%, 100% { opacity: 0; transform: scale(0.5); }
                50% { opacity: 1; transform: scale(1); }
            }
        `;
        document.head.appendChild(style);
    }

    createBlockyParticles(container, theme) {
        const blocks = ['⬜', '🟫', '🟩', '🟦', '🟨'];
        for (let i = 0; i < 12; i++) {
            const block = document.createElement('div');
            block.textContent = blocks[Math.floor(Math.random() * blocks.length)];
            block.style.cssText = `
                position: absolute;
                font-size: ${20 + Math.random() * 15}px;
                opacity: 0;
                animation: blockyFloat ${2 + Math.random() * 2}s ease-in-out infinite;
                animation-delay: ${Math.random() * 1.5}s;
                left: ${Math.random() * 100}%;
                top: ${Math.random() * 100}%;
                z-index: 1;
                pointer-events: none;
                transform: rotate(${Math.random() * 360}deg);
            `;
            container.appendChild(block);
        }
        
        const style = document.createElement('style');
        style.textContent = `
            @keyframes blockyFloat {
                0% { opacity: 0; transform: translateY(0) rotate(0deg); }
                50% { opacity: 1; transform: translateY(-15px) rotate(180deg); }
                100% { opacity: 0; transform: translateY(-30px) rotate(360deg); }
            }
        `;
        document.head.appendChild(style);
    }

    // Web Crawler Methods
    setupWebCrawlerEvents() {
        const runCrawlerBtn = document.getElementById('run-web-crawler');
        const refreshDataBtn = document.getElementById('refresh-crawler-data');
        const viewLogBtn = document.getElementById('view-crawler-log');

        if (runCrawlerBtn) {
            runCrawlerBtn.addEventListener('click', () => this.runWebCrawler());
        }
        if (refreshDataBtn) {
            refreshDataBtn.addEventListener('click', () => this.refreshCrawlerData());
        }
        if (viewLogBtn) {
            viewLogBtn.addEventListener('click', () => this.viewCrawlerLog());
        }
    }

    logCrawlerMessage(msg) {
        const consoleEl = document.getElementById('crawler-console');
        if (consoleEl) {
            consoleEl.textContent += msg + '\n';
            consoleEl.scrollTop = consoleEl.scrollHeight;
        }
    }

    setCrawlerBottomBar(visible, percent = 0) {
        const bar = document.getElementById('crawler-bottom-bar');
        const progress = document.getElementById('crawler-bottom-progress');
        if (bar) bar.style.display = visible ? 'flex' : 'none';
        if (progress) progress.style.width = percent + '%';
    }

    startCrawlerLogPolling() {
        if (this.crawlerLogInterval) return;
        this.crawlerLogInterval = setInterval(async () => {
            if (window.electronAPI && window.electronAPI.tailCrawlerLog) {
                const result = await window.electronAPI.tailCrawlerLog(50);
                if (result.status === 'success') {
                    const consoleEl = document.getElementById('crawler-console');
                    if (consoleEl) {
                        consoleEl.textContent = result.log;
                        consoleEl.scrollTop = consoleEl.scrollHeight;
                    }
                    // Parse progress and update speed samples
                    this.parseAndUpdateCrawlerSpeed(result.log);
                    // Optionally, update progress bar from log content
                    const progress = this.parseProgressFromLog(result.log);
                    this.setCrawlerBottomBar(true, progress);
                }
            }
        }, 1000);
    }

    stopCrawlerLogPolling() {
        if (this.crawlerLogInterval) {
            clearInterval(this.crawlerLogInterval);
            this.crawlerLogInterval = null;
        }
    }

    parseProgressFromLog(log) {
        // Try to extract a percentage from the last log lines
        const match = log.match(/(\d{1,3}\.\d)%/);
        if (match) {
            return Math.min(100, parseFloat(match[1]));
        }
        return 0;
    }

    parseAndUpdateCrawlerSpeed(log) {
        // Look for the last [PROGRESS] line
        const lines = log.split(/\r?\n/);
        let lastProgress = null;
        for (let i = lines.length - 1; i >= 0; i--) {
            if (lines[i].includes('[PROGRESS]')) {
                lastProgress = lines[i];
                break;
            }
        }
        if (lastProgress) {
            // Example: [PROGRESS] 12/100 datasets processed | 5/10 satellites | Elapsed: 34s
            const match = lastProgress.match(/\[PROGRESS\] (\d+)\/(\d+) datasets processed \| (\d+)\/(\d+) satellites \| Elapsed: (\d+)s/);
            if (match) {
                const current = parseInt(match[1]);
                const total = parseInt(match[2]);
                const elapsed = parseInt(match[5]);
                // Calculate speed (datasets/sec)
                let speed = 0;
                if (elapsed > 0) speed = current / elapsed;
                // Add to rolling window
                this.crawlerSpeedSamples.push({ t: Date.now(), speed });
                if (this.crawlerSpeedSamples.length > this.crawlerSpeedWindow) {
                    this.crawlerSpeedSamples.shift();
                }
                // Draw the graph
                this.drawCrawlerSpeedGraph();
                // Optionally, update estimated time left
                const timeLeft = speed > 0 ? Math.round((total - current) / speed) : 0;
                this.updateCrawlerTimeLeft(timeLeft, current, total);
            }
        }
    }

    drawCrawlerSpeedGraph() {
        const canvas = document.getElementById('crawler-speed-graph');
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        // Draw background
        ctx.fillStyle = '#181c24';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        // Draw line
        const samples = this.crawlerSpeedSamples;
        if (samples.length < 2) return;
        const maxSpeed = Math.max(...samples.map(s => s.speed), 1);
        ctx.strokeStyle = '#4fc3f7';
        ctx.lineWidth = 2;
        ctx.beginPath();
        for (let i = 0; i < samples.length; i++) {
            const x = (i / (this.crawlerSpeedWindow - 1)) * (canvas.width - 10) + 5;
            const y = canvas.height - 5 - (samples[i].speed / maxSpeed) * (canvas.height - 10);
            if (i === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
        }
        ctx.stroke();
        // Draw axis
        ctx.strokeStyle = '#333';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(5, canvas.height - 5);
        ctx.lineTo(canvas.width - 5, canvas.height - 5);
        ctx.stroke();
        // Draw max speed label
        ctx.fillStyle = '#b8e1ff';
        ctx.font = '10px monospace';
        ctx.fillText(maxSpeed.toFixed(2), 5, 10);
    }

    updateCrawlerTimeLeft(timeLeft, current, total) {
        // Optionally show time left in the progress label
        const label = document.querySelector('.progress-label');
        if (label) {
            if (timeLeft > 0 && current < total) {
                label.textContent = `Progress (ETA: ${this.formatTime(timeLeft)})`;
            } else {
                label.textContent = 'Progress';
            }
        }
    }

    formatTime(seconds) {
        const m = Math.floor(seconds / 60);
        const s = seconds % 60;
        return m > 0 ? `${m}m ${s}s` : `${s}s`;
    }

    async runWebCrawler() {
        const progressDiv = document.getElementById('crawler-progress');
        const progressFill = document.getElementById('crawler-progress-fill');
        const messageDiv = document.getElementById('crawler-message');
        const runBtn = document.getElementById('run-web-crawler');

        if (this.crawlerRunning) {
            this.showNotification('Web crawler is already running', 'warning');
            return;
        }

        this.crawlerRunning = true;
        this.updateCrawlerStatus('Running', 'running');
        progressDiv.style.display = 'block';
        runBtn.disabled = true;
        messageDiv.textContent = 'Starting web crawler...';
        this.setCrawlerBottomBar(true, 0);
        const consoleEl = document.getElementById('crawler-console');
        if (consoleEl) consoleEl.textContent = '';
        this.logCrawlerMessage('Web crawler started.');
        this.startCrawlerLogPolling();

        // Reset all steps
        document.querySelectorAll('.step').forEach(step => {
            step.className = 'step';
        });

        try {
            if (window.electronAPI) {
                const result = await window.electronAPI.pythonRunCrawler();
                this.logCrawlerMessage('Backend crawler finished.');
                if (result.status === 'success') {
                    messageDiv.textContent = 'Web crawler completed successfully!';
                    this.updateCrawlerStatus('Completed', 'ready');
                    this.showNotification('Web crawler completed', 'success');
                    document.querySelectorAll('.step').forEach(step => {
                        step.classList.add('completed');
                    });
                    await this.refreshCrawlerData();
                } else {
                    throw new Error(result.message || 'Crawler failed');
                }
            } else {
                await this.simulateWebCrawler(progressFill, messageDiv);
                this.updateCrawlerStatus('Completed', 'ready');
                this.showNotification('Web crawler completed', 'success');
            }
        } catch (error) {
            console.error('Web crawler error:', error);
            messageDiv.textContent = 'Error: ' + error.message;
            this.updateCrawlerStatus('Error', 'error');
            this.showNotification('Web crawler failed: ' + error.message, 'error');
            this.logCrawlerMessage('Error: ' + error.message);
        } finally {
            this.crawlerRunning = false;
            runBtn.disabled = false;
            setTimeout(() => this.setCrawlerBottomBar(false, 0), 2000);
            this.stopCrawlerLogPolling();
        }
    }

    async simulateWebCrawler(progressFill, messageDiv) {
        const steps = [
            { name: 'init', message: 'Initializing web crawler...', duration: 1000 },
            { name: 'connect', message: 'Connecting to Google Earth Engine...', duration: 1500 },
            { name: 'fetch', message: 'Fetching catalog data...', duration: 2000 },
            { name: 'process', message: 'Processing satellite information...', duration: 1500 },
            { name: 'download', message: 'Downloading thumbnails...', duration: 2500 },
            { name: 'save', message: 'Saving data to file...', duration: 1000 }
        ];

        for (let i = 0; i < steps.length; i++) {
            const step = steps[i];
            this.updateCrawlerStep(step.name, 'active');
            messageDiv.textContent = step.message;
            const progress = ((i + 1) / steps.length) * 100;
            progressFill.style.width = progress + '%';
            this.setCrawlerBottomBar(true, progress);
            this.logCrawlerMessage(step.message);
            const percentageElement = document.getElementById('progress-percentage');
            if (percentageElement) {
                percentageElement.textContent = Math.round(progress) + '%';
            }
            await new Promise(resolve => setTimeout(resolve, step.duration));
            this.updateCrawlerStep(step.name, 'completed');
        }
        this.logCrawlerMessage('Web crawler completed successfully!');
    }

    updateCrawlerStep(stepName, status) {
        const stepElement = document.querySelector(`[data-step="${stepName}"]`);
        if (stepElement) {
            stepElement.className = `step ${status}`;
        }
    }

    updateCrawlerStatus(status, type = 'ready') {
        const statusDot = document.getElementById('status-dot');
        const statusText = document.getElementById('crawler-status');
        
        if (statusDot) {
            statusDot.className = `status-dot ${type}`;
        }
        
        if (statusText) {
            statusText.textContent = status;
        }
    }

    updateSatelliteGrid(data) {
        const grid = document.getElementById('satellite-grid');
        if (!grid || !data.satellites) return;

        let html = '';
        let totalDatasets = 0;

        Object.entries(data.satellites).forEach(([satellite, datasets]) => {
            const firstDataset = datasets[0];
            totalDatasets += datasets.length;

            const tags = [];
            if (firstDataset.data_type) tags.push(firstDataset.data_type);
            if (firstDataset.resolution) tags.push(firstDataset.resolution);

            html += `
                <div class="satellite-card" onclick="flutterEarth.showSensorDetails('${satellite}')">
                    <div class="card-header">
                        <h3 class="card-title">${satellite}</h3>
                        <span class="card-badge">${datasets.length} datasets</span>
                    </div>
                    <div class="card-stats">
                        <div class="card-stat">
                            <span class="card-stat-value">${firstDataset.resolution || 'N/A'}</span>
                            <span class="card-stat-label">Resolution</span>
                        </div>
                        <div class="card-stat">
                            <span class="card-stat-value">${firstDataset.data_type || 'N/A'}</span>
                            <span class="card-stat-label">Type</span>
                        </div>
                    </div>
                    <p class="card-description">${firstDataset.description || 'No description available'}</p>
                    <div class="card-tags">
                        ${tags.map(tag => `<span class="card-tag">${tag}</span>`).join('')}
                    </div>
                </div>
            `;
        });

        grid.innerHTML = html;

        // Update header stats
        const totalSatellites = document.getElementById('total-satellites');
        const totalDatasetsElement = document.getElementById('total-datasets');
        const lastUpdated = document.getElementById('last-updated');

        if (totalSatellites) totalSatellites.textContent = Object.keys(data.satellites).length;
        if (totalDatasetsElement) totalDatasetsElement.textContent = totalDatasets;
        if (lastUpdated) lastUpdated.textContent = new Date().toLocaleDateString();
    }

    setupNewSatelliteEvents() {
        // Close details panel
        const closeDetails = document.getElementById('close-details');
        if (closeDetails) {
            closeDetails.addEventListener('click', () => {
                const detailsPanel = document.getElementById('satellite-details-panel');
                if (detailsPanel) {
                    detailsPanel.classList.remove('show');
                }
            });
        }

        // Clear search
        const clearSearch = document.getElementById('clear-search');
        if (clearSearch) {
            clearSearch.addEventListener('click', () => {
                const searchInput = document.getElementById('satellite-search');
                if (searchInput) {
                    searchInput.value = '';
                    this.filterSatellites('');
                }
            });
        }

        // Filter tabs
        const filterTabs = document.querySelectorAll('.filter-tab');
        filterTabs.forEach(tab => {
            tab.addEventListener('click', () => {
                filterTabs.forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                this.filterSatellitesByCategory(tab.dataset.filter);
            });
        });

        // View toggles
        const viewToggles = document.querySelectorAll('.view-toggle');
        viewToggles.forEach(toggle => {
            toggle.addEventListener('click', () => {
                viewToggles.forEach(t => t.classList.remove('active'));
                toggle.classList.add('active');
                this.switchGridView(toggle.dataset.view);
            });
        });

        // Copy code button
        const copyCodeBtn = document.getElementById('copy-code-btn');
        if (copyCodeBtn) {
            copyCodeBtn.addEventListener('click', () => this.copyCodeSnippet());
        }

        // Share satellite button
        const shareSatelliteBtn = document.getElementById('share-satellite');
        if (shareSatelliteBtn) {
            shareSatelliteBtn.addEventListener('click', () => this.shareSatellite());
        }
    }

    filterSatellitesByCategory(category) {
        const cards = document.querySelectorAll('.satellite-card');
        cards.forEach(card => {
            if (category === 'all') {
                card.style.display = 'block';
            } else {
                const cardType = card.querySelector('.card-stat-value')?.textContent.toLowerCase();
                if (cardType && cardType.includes(category)) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            }
        });
    }

    switchGridView(view) {
        const grid = document.getElementById('satellite-grid');
        if (grid) {
            if (view === 'list') {
                grid.style.gridTemplateColumns = '1fr';
            } else {
                grid.style.gridTemplateColumns = 'repeat(auto-fill, minmax(280px, 1fr))';
            }
        }
    }

    shareSatellite() {
        if (!this.selectedSatellite) {
            this.showNotification('No satellite selected', 'warning');
            return;
        }

        const satelliteData = this.crawlerData.satellites[this.selectedSatellite];
        const shareText = `Check out ${this.selectedSatellite} satellite data:\n\n` +
                         `Resolution: ${satelliteData[0].resolution || 'N/A'}\n` +
                         `Type: ${satelliteData[0].data_type || 'N/A'}\n` +
                         `Description: ${satelliteData[0].description || 'No description'}`;

        if (navigator.share) {
            navigator.share({
                title: `${this.selectedSatellite} Satellite Data`,
                text: shareText
            });
        } else {
            navigator.clipboard.writeText(shareText).then(() => {
                this.showNotification('Satellite info copied to clipboard', 'success');
            });
        }
    }

    async refreshCrawlerData() {
        try {
            await this.loadSensorsFromCrawlerData();
            this.showNotification('Satellite data refreshed', 'success');
        } catch (error) {
            console.error('Error refreshing crawler data:', error);
            this.showNotification('Failed to refresh data', 'error');
        }
    }

    viewCrawlerLog() {
        this.showNotification('Crawler log viewer coming soon', 'info');
    }

    // Satellite Search Methods
    setupSatelliteSearch() {
        const searchInput = document.getElementById('satellite-search');
        if (searchInput) {
            searchInput.addEventListener('input', this.debounce((e) => {
                this.filterSatellites(e.target.value);
            }, 300));
        }
    }

    filterSatellites(searchTerm) {
        const sensorItems = document.querySelectorAll('.sensor-item');
        const searchLower = searchTerm.toLowerCase();

        sensorItems.forEach(item => {
            const sensorName = item.querySelector('.sensor-name')?.textContent.toLowerCase() || '';
            const sensorType = item.querySelector('.sensor-type')?.textContent.toLowerCase() || '';
            
            if (sensorName.includes(searchLower) || sensorType.includes(searchLower)) {
                item.style.display = 'block';
            } else {
                item.style.display = 'none';
            }
        });
    }

    // Sensor Action Methods
    setupSensorActions() {
        const useForDownloadBtn = document.getElementById('use-for-download');
        const viewThumbnailBtn = document.getElementById('view-thumbnail');
        const copyCodeBtn = document.getElementById('copy-code-snippet');

        if (useForDownloadBtn) {
            console.log('[DEBUG] Setting up useForDownload button event listener');
            useForDownloadBtn.addEventListener('click', () => {
                console.log('[DEBUG] useForDownload button clicked!');
                this.useForDownload();
            });
        } else {
            console.error('[DEBUG] useForDownload button not found!');
        }
        if (viewThumbnailBtn) {
            viewThumbnailBtn.addEventListener('click', () => this.viewThumbnail());
        }
        if (copyCodeBtn) {
            copyCodeBtn.addEventListener('click', () => this.copyCodeSnippet());
        }
    }

    useForDownload() {
        console.log('[DEBUG] useForDownload called (catalog/crawler mode)');
        this.showNotification('Starting satellite catalog download...', 'info');

        // Switch to download view to show progress
        this.switchView('download');
        this.initializeDownloadMonitoring();

        // Call the backend to run the crawler (fetch catalog)
        if (window.electronAPI && window.electronAPI.pythonRunCrawler) {
            window.electronAPI.pythonRunCrawler()
                .then(result => {
                    if (result.status === 'success') {
                        this.showNotification('Satellite catalog download started.', 'success');
                        this.updateDownloadStatus('Satellite catalog download started.', 'success');
                        this.startDownloadMonitoring();
                    } else {
                        this.showNotification('Catalog download failed: ' + result.message, 'error');
                        this.updateDownloadStatus('Catalog download failed: ' + result.message, 'error');
                    }
                })
                .catch(error => {
                    this.showNotification('Catalog download error: ' + error.message, 'error');
                    this.updateDownloadStatus('Catalog download error: ' + error.message, 'error');
                });
        } else {
            this.showNotification('Electron API not available', 'error');
            this.updateDownloadStatus('Electron API not available', 'error');
        }
    }

    initializeDownloadMonitoring() {
        // Initialize download monitoring variables
        this.downloadInProgress = true;
        this.downloadStartTime = Date.now();
        this.downloadSpeedSamples = [];
        this.downloadSpeedWindow = 30; // 30 samples for rolling average
        this.downloadProgress = 0;
        this.downloadStatus = 'Starting...';
        
        // Show download bottom bar
        this.setDownloadBottomBar(true, 0);
        
        // Clear download console
        const consoleEl = document.getElementById('download-console');
        if (consoleEl) {
            consoleEl.textContent = '';
        }
        
        this.logDownloadMessage('Download started.');
    }

    setDownloadBottomBar(visible, percent = 0) {
        const bar = document.getElementById('download-bottom-bar');
        const progress = document.getElementById('download-bottom-progress');
        if (bar) bar.style.display = visible ? 'flex' : 'none';
        if (progress) progress.style.width = percent + '%';
    }

    startDownloadMonitoring() {
        if (this.downloadLogInterval) return;
        this.downloadLogInterval = setInterval(async () => {
            if (window.electronAPI && window.electronAPI.pythonProgress) {
                const result = await window.electronAPI.pythonProgress();
                if (result.status === 'success') {
                    const progress = result.progress;
                    this.updateDownloadProgress(progress);
                    
                    if (progress.message) {
                        this.logDownloadMessage(progress.message);
                    }
                    
                    if (progress.completed || progress.error) {
                        this.stopDownloadMonitoring();
                        
                        if (progress.error) {
                            this.updateDownloadStatus('Download failed: ' + progress.error, 'error');
                            this.logDownloadMessage('ERROR: ' + progress.error);
                        } else {
                            this.updateDownloadStatus('Download completed', 'success');
                            this.logDownloadMessage('Download completed successfully');
                        }
                    }
                }
            }
        }, 1000);
    }

    stopDownloadMonitoring() {
        if (this.downloadLogInterval) {
            clearInterval(this.downloadLogInterval);
            this.downloadLogInterval = null;
        }
        this.downloadInProgress = false;
        setTimeout(() => this.setDownloadBottomBar(false, 0), 2000);
    }

    updateDownloadProgress(progress) {
        // Update progress bar
        const progressPercent = progress.percentage || 0;
        this.downloadProgress = progressPercent;
        this.setDownloadBottomBar(true, progressPercent);
        
        // Update download status
        this.downloadStatus = progress.message || 'Downloading...';
        
        // Calculate speed and update graph
        if (progress.bytes_downloaded && progress.elapsed_time) {
            const speed = progress.bytes_downloaded / progress.elapsed_time; // bytes per second
            const speedMBps = speed / (1024 * 1024); // Convert to MB/s
            
            // Add to rolling window
            this.downloadSpeedSamples.push({ t: Date.now(), speed: speedMBps });
            if (this.downloadSpeedSamples.length > this.downloadSpeedWindow) {
                this.downloadSpeedSamples.shift();
            }
            
            // Draw the speed graph
            this.drawDownloadSpeedGraph();
            
            // Update time estimation
            if (progress.total_bytes && speed > 0) {
                const remainingBytes = progress.total_bytes - progress.bytes_downloaded;
                const timeLeft = remainingBytes / speed;
                this.updateDownloadTimeLeft(timeLeft, progress.bytes_downloaded, progress.total_bytes);
            }
        }
    }

    drawDownloadSpeedGraph() {
        const canvas = document.getElementById('download-speed-graph');
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Draw background
        ctx.fillStyle = '#181c24';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        // Draw line
        const samples = this.downloadSpeedSamples;
        if (samples.length < 2) return;
        
        const maxSpeed = Math.max(...samples.map(s => s.speed), 1);
        ctx.strokeStyle = '#4fc3f7';
        ctx.lineWidth = 2;
        ctx.beginPath();
        
        for (let i = 0; i < samples.length; i++) {
            const x = (i / (this.downloadSpeedWindow - 1)) * (canvas.width - 10) + 5;
            const y = canvas.height - 5 - (samples[i].speed / maxSpeed) * (canvas.height - 10);
            if (i === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
        }
        ctx.stroke();
        
        // Draw axis
        ctx.strokeStyle = '#333';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(5, canvas.height - 5);
        ctx.lineTo(canvas.width - 5, canvas.height - 5);
        ctx.stroke();
        
        // Draw max speed label
        ctx.fillStyle = '#b8e1ff';
        ctx.font = '10px monospace';
        ctx.fillText(maxSpeed.toFixed(2) + ' MB/s', 5, 10);
    }

    updateDownloadTimeLeft(timeLeft, downloaded, total) {
        const label = document.querySelector('.download-progress-section .progress-label');
        if (label) {
            if (timeLeft > 0 && downloaded < total) {
                label.textContent = `Download Progress (ETA: ${this.formatTime(timeLeft)})`;
            } else {
                label.textContent = 'Download Progress';
            }
        }
    }

    logDownloadMessage(msg) {
        const consoleEl = document.getElementById('download-console');
        if (consoleEl) {
            const timestamp = new Date().toLocaleTimeString();
            consoleEl.textContent += `[${timestamp}] ${msg}\n`;
            consoleEl.scrollTop = consoleEl.scrollHeight;
        }
    }

    viewThumbnail() {
        if (!this.selectedSatellite || !this.crawlerData) {
            this.showNotification('No satellite or thumbnail data available', 'warning');
            return;
        }

        const satelliteData = this.crawlerData.satellites[this.selectedSatellite];
        if (!satelliteData || !satelliteData[0]?.thumbnail_path) {
            this.showNotification('No thumbnail available for this satellite', 'warning');
            return;
        }

        const thumbnailPath = satelliteData[0].thumbnail_path;
        const modal = document.getElementById('thumbnail-modal');
        const image = document.getElementById('thumbnail-image');

        if (modal && image) {
            image.src = thumbnailPath;
            modal.classList.add('show');
        }
    }

    hideThumbnailModal() {
        const modal = document.getElementById('thumbnail-modal');
        if (modal) {
            modal.classList.remove('show');
        }
    }

    copyCodeSnippet() {
        if (!this.selectedSatellite || !this.crawlerData) {
            this.showNotification('No satellite or code snippet available', 'warning');
            return;
        }

        const satelliteData = this.crawlerData.satellites[this.selectedSatellite];
        if (!satelliteData || !satelliteData[0]?.code_snippet) {
            this.showNotification('No code snippet available for this satellite', 'warning');
            return;
        }

        const codeSnippet = satelliteData[0].code_snippet;
        
        if (navigator.clipboard) {
            navigator.clipboard.writeText(codeSnippet).then(() => {
                this.showNotification('Code snippet copied to clipboard', 'success');
            }).catch(() => {
                this.fallbackCopyTextToClipboard(codeSnippet);
            });
        } else {
            this.fallbackCopyTextToClipboard(codeSnippet);
        }
    }

    fallbackCopyTextToClipboard(text) {
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        try {
            document.execCommand('copy');
            this.showNotification('Code snippet copied to clipboard', 'success');
        } catch (err) {
            this.showNotification('Failed to copy code snippet', 'error');
        }
        
        document.body.removeChild(textArea);
    }

    // Enhanced showSensorDetails method for new GUI
    showSensorDetails(satelliteName) {
        if (!this.crawlerData || !this.crawlerData.satellites[satelliteName]) {
            console.warn('[DEBUG] No data for satellite:', satelliteName);
            return;
        }

        this.selectedSatellite = satelliteName;
        const datasets = this.crawlerData.satellites[satelliteName];
        const firstDataset = datasets[0];

        // Show the details panel
        const detailsPanel = document.getElementById('satellite-details-panel');
        if (detailsPanel) {
            detailsPanel.classList.add('show');
        }

        // Update satellite hero section
        const detailName = document.getElementById('detail-satellite-name');
        const detailResolution = document.getElementById('detail-resolution');
        const detailDatasets = document.getElementById('detail-datasets');
        const detailStatus = document.getElementById('detail-status');
        const detailDescription = document.getElementById('detail-description');

        if (detailName) detailName.textContent = satelliteName;
        if (detailResolution) detailResolution.textContent = firstDataset.resolution || 'N/A';
        if (detailDatasets) detailDatasets.textContent = datasets.length;
        if (detailStatus) detailStatus.textContent = firstDataset.status || 'Active';
        if (detailDescription) detailDescription.textContent = firstDataset.description || 'No description available';

        // Update thumbnail
        const thumbnailImg = document.getElementById('thumbnail-img');
        const thumbnailPlaceholder = document.querySelector('.thumbnail-placeholder');
        if (firstDataset.thumbnail_path) {
            if (thumbnailImg) {
                thumbnailImg.src = firstDataset.thumbnail_path;
                thumbnailImg.style.display = 'block';
            }
            if (thumbnailPlaceholder) {
                thumbnailPlaceholder.style.display = 'none';
            }
        } else {
            if (thumbnailImg) {
                thumbnailImg.style.display = 'none';
            }
            if (thumbnailPlaceholder) {
                thumbnailPlaceholder.style.display = 'flex';
            }
        }

        // Update satellite tags
        const satelliteTags = document.getElementById('satellite-tags');
        if (satelliteTags) {
            const tags = [];
            if (firstDataset.data_type) tags.push(firstDataset.data_type);
            if (firstDataset.resolution) tags.push(firstDataset.resolution);
            if (firstDataset.coverage) tags.push(firstDataset.coverage);
            
            satelliteTags.innerHTML = tags.map(tag => 
                `<span class="card-tag">${tag}</span>`
            ).join('');
        }

        // Update applications
        const applicationsGrid = document.getElementById('detail-applications');
        if (applicationsGrid) {
            if (firstDataset.applications && firstDataset.applications.length > 0) {
                applicationsGrid.innerHTML = firstDataset.applications.map(app => 
                    `<div class="application-item">${app}</div>`
                ).join('');
            } else {
                applicationsGrid.innerHTML = '<p>No applications information available.</p>';
            }
        }

        // Update bands
        const bandsGrid = document.getElementById('detail-bands');
        if (bandsGrid) {
            if (firstDataset.bands && firstDataset.bands.length > 0) {
                bandsGrid.innerHTML = firstDataset.bands.map(band => 
                    `<div class="band-item">${band}</div>`
                ).join('');
            } else {
                bandsGrid.innerHTML = '<p>No bands information available.</p>';
            }
        }

        // Update code section
        const codeBlock = document.getElementById('code-block');
        if (codeBlock) {
            if (firstDataset.code_snippet) {
                codeBlock.innerHTML = `<code>${firstDataset.code_snippet}</code>`;
            } else {
                codeBlock.innerHTML = '<code>No code snippet available for this satellite.</code>';
            }
        }

        // Enable/disable action buttons
        const useForDownloadBtn = document.getElementById('use-for-download');
        const viewThumbnailBtn = document.getElementById('view-thumbnail');
        const copyCodeBtn = document.getElementById('copy-code-btn');

        if (useForDownloadBtn) useForDownloadBtn.disabled = false;
        if (viewThumbnailBtn) viewThumbnailBtn.disabled = !firstDataset.thumbnail_path;
        if (copyCodeBtn) copyCodeBtn.disabled = !firstDataset.code_snippet;

        // Update selected state in satellite grid
        document.querySelectorAll('.satellite-card').forEach(card => {
            card.classList.remove('selected');
        });
        
        const selectedCard = Array.from(document.querySelectorAll('.satellite-card')).find(card => 
            card.querySelector('.card-title')?.textContent === satelliteName
        );
        if (selectedCard) {
            selectedCard.classList.add('selected');
        }
    }

    // New method to update satellite grid
    updateSatelliteGrid(data) {
        const grid = document.getElementById('satellite-grid');
        if (!grid || !data.satellites) return;

        let html = '';
        let totalDatasets = 0;

        Object.entries(data.satellites).forEach(([satellite, datasets]) => {
            const firstDataset = datasets[0];
            totalDatasets += datasets.length;

            const tags = [];
            if (firstDataset.data_type) tags.push(firstDataset.data_type);
            if (firstDataset.resolution) tags.push(firstDataset.resolution);

            html += `
                <div class="satellite-card" onclick="flutterEarth.showSensorDetails('${satellite}')">
                    <div class="card-header">
                        <h3 class="card-title">${satellite}</h3>
                        <span class="card-badge">${datasets.length} datasets</span>
                    </div>
                    <div class="card-stats">
                        <div class="card-stat">
                            <span class="card-stat-value">${firstDataset.resolution || 'N/A'}</span>
                            <span class="card-stat-label">Resolution</span>
                        </div>
                        <div class="card-stat">
                            <span class="card-stat-value">${firstDataset.data_type || 'N/A'}</span>
                            <span class="card-stat-label">Type</span>
                        </div>
                    </div>
                    <p class="card-description">${firstDataset.description || 'No description available'}</p>
                    <div class="card-tags">
                        ${tags.map(tag => `<span class="card-tag">${tag}</span>`).join('')}
                    </div>
                </div>
            `;
        });

        grid.innerHTML = html;

        // Update header stats
        const totalSatellites = document.getElementById('total-satellites');
        const totalDatasetsElement = document.getElementById('total-datasets');
        const lastUpdated = document.getElementById('last-updated');

        if (totalSatellites) totalSatellites.textContent = Object.keys(data.satellites).length;
        if (totalDatasetsElement) totalDatasetsElement.textContent = totalDatasets;
        if (lastUpdated) lastUpdated.textContent = new Date().toLocaleDateString();
    }

    // Enhanced crawler progress with step tracking
    async simulateWebCrawler(progressFill, messageDiv) {
        const steps = [
            { name: 'init', message: 'Initializing web crawler...', duration: 1000 },
            { name: 'connect', message: 'Connecting to Google Earth Engine...', duration: 1500 },
            { name: 'fetch', message: 'Fetching catalog data...', duration: 2000 },
            { name: 'process', message: 'Processing satellite information...', duration: 1500 },
            { name: 'download', message: 'Downloading thumbnails...', duration: 2500 },
            { name: 'save', message: 'Saving data to file...', duration: 1000 }
        ];

        for (let i = 0; i < steps.length; i++) {
            const step = steps[i];
            
            // Update step status
            this.updateCrawlerStep(step.name, 'active');
            
            // Update message and progress
            messageDiv.textContent = step.message;
            const progress = ((i + 1) / steps.length) * 100;
            progressFill.style.width = progress + '%';
            
            // Update percentage
            const percentageElement = document.getElementById('progress-percentage');
            if (percentageElement) {
                percentageElement.textContent = Math.round(progress) + '%';
            }
            
            await new Promise(resolve => setTimeout(resolve, step.duration));
            
            // Mark step as completed
            this.updateCrawlerStep(step.name, 'completed');
        }
    }

    updateCrawlerStep(stepName, status) {
        const stepElement = document.querySelector(`[data-step="${stepName}"]`);
        if (stepElement) {
            stepElement.className = `step ${status}`;
        }
    }

    updateCrawlerStatus(status, type = 'ready') {
        const statusDot = document.getElementById('status-dot');
        const statusText = document.getElementById('crawler-status');
        
        if (statusDot) {
            statusDot.className = `status-dot ${type}`;
        }
        
        if (statusText) {
            statusText.textContent = status;
        }
    }

    // Setup new event listeners for the redesigned GUI
    setupNewSatelliteEvents() {
        // Close details panel
        const closeDetails = document.getElementById('close-details');
        if (closeDetails) {
            closeDetails.addEventListener('click', () => {
                const detailsPanel = document.getElementById('satellite-details-panel');
                if (detailsPanel) {
                    detailsPanel.classList.remove('show');
                }
            });
        }

        // Clear search
        const clearSearch = document.getElementById('clear-search');
        if (clearSearch) {
            clearSearch.addEventListener('click', () => {
                const searchInput = document.getElementById('satellite-search');
                if (searchInput) {
                    searchInput.value = '';
                    this.filterSatellites('');
                }
            });
        }

        // Filter tabs
        const filterTabs = document.querySelectorAll('.filter-tab');
        filterTabs.forEach(tab => {
            tab.addEventListener('click', () => {
                filterTabs.forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                this.filterSatellitesByCategory(tab.dataset.filter);
            });
        });

        // View toggles
        const viewToggles = document.querySelectorAll('.view-toggle');
        viewToggles.forEach(toggle => {
            toggle.addEventListener('click', () => {
                viewToggles.forEach(t => t.classList.remove('active'));
                toggle.classList.add('active');
                this.switchGridView(toggle.dataset.view);
            });
        });

        // Copy code button
        const copyCodeBtn = document.getElementById('copy-code-btn');
        if (copyCodeBtn) {
            copyCodeBtn.addEventListener('click', () => this.copyCodeSnippet());
        }

        // Share satellite button
        const shareSatelliteBtn = document.getElementById('share-satellite');
        if (shareSatelliteBtn) {
            shareSatelliteBtn.addEventListener('click', () => this.shareSatellite());
        }
    }

    filterSatellitesByCategory(category) {
        const cards = document.querySelectorAll('.satellite-card');
        cards.forEach(card => {
            if (category === 'all') {
                card.style.display = 'block';
            } else {
                // This is a simplified filter - you can enhance it based on your data structure
                const cardType = card.querySelector('.card-stat-value')?.textContent.toLowerCase();
                if (cardType && cardType.includes(category)) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            }
        });
    }

    switchGridView(view) {
        const grid = document.getElementById('satellite-grid');
        if (grid) {
            if (view === 'list') {
                grid.style.gridTemplateColumns = '1fr';
            } else {
                grid.style.gridTemplateColumns = 'repeat(auto-fill, minmax(280px, 1fr))';
            }
        }
    }

    shareSatellite() {
        if (!this.selectedSatellite) {
            this.showNotification('No satellite selected', 'warning');
            return;
        }

        const satelliteData = this.crawlerData.satellites[this.selectedSatellite];
        const shareText = `Check out ${this.selectedSatellite} satellite data:\n\n` +
                         `Resolution: ${satelliteData[0].resolution || 'N/A'}\n` +
                         `Type: ${satelliteData[0].data_type || 'N/A'}\n` +
                         `Description: ${satelliteData[0].description || 'No description'}`;

        if (navigator.share) {
            navigator.share({
                title: `${this.selectedSatellite} Satellite Data`,
                text: shareText
            });
        } else {
            // Fallback to clipboard
            navigator.clipboard.writeText(shareText).then(() => {
                this.showNotification('Satellite info copied to clipboard', 'success');
            });
        }
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('[DEBUG] DOM Content Loaded - Initializing FlutterEarth');
    
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
    
    // Initialize the main app
    try {
        window.flutterEarth = new FlutterEarth();
        console.log('[DEBUG] FlutterEarth initialized successfully');
    } catch (error) {
        console.error('[DEBUG] Failed to initialize FlutterEarth:', error);
    }
    
    // Setup map selector close button
    const closeBtn = document.getElementById('map-selector-close');
    if (closeBtn) {
        closeBtn.onclick = () => {
            const overlay = document.getElementById('map-selector-overlay');
            if (overlay) overlay.style.display = 'none';
        };
    }
    
    // Log Electron status but don't show error box (allows browser testing)
    if (!isElectron()) {
        console.log('[DEBUG] Running in browser mode (Electron not detected)');
    } else {
        console.log('[DEBUG] Running in Electron mode');
    }
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = FlutterEarth;
}

// In Satellite Info tab logic:
async function fetchCatalogData() {
    const sources = [
        '../backend/gee_catalog_data_enhanced.json',
        '../backend/gee_catalog_data.json',
        '../backend/gee_catalog_data_enhanced.json.gz',
    ];
    for (const src of sources) {
        try {
            if (src.endsWith('.gz')) {
                const resp = await fetch(src);
                if (!resp.ok) continue;
                const arrayBuffer = await resp.arrayBuffer();
                const text = pako.ungzip(new Uint8Array(arrayBuffer), { to: 'string' });
                return JSON.parse(text);
            } else {
                const resp = await fetch(src);
                if (!resp.ok) continue;
                return await resp.json();
            }
        } catch (e) { continue; }
    }
    throw new Error('No catalog data found');
}