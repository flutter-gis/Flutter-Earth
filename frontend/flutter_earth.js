// Flutter Earth JavaScript - Vanilla JS (No jQuery)

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
        console.log('[DEBUG] FlutterEarth.init() started');
        
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
        document.querySelectorAll('.sidebar-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                
                try {
                const view = item.dataset.view;
                const panel = item.dataset.panel;
                console.log(`[DEBUG] Sidebar item clicked:`, { view, panel, item: item.textContent.trim() });
                
                if (view) {
                    this.switchView(view);
                } else if (panel) {
                    this.showPanel(panel);
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

        // Theme tabs
        document.querySelectorAll('.theme-tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                document.querySelectorAll('.theme-tab').forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                this.switchThemeCategory(tab.dataset.category);
            });
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
            targetView.classList.add('active');
                targetView.style.display = 'block';
            console.log(`[DEBUG] Successfully switched to ${viewName}-view`);
        } else {
            console.warn(`[DEBUG] View not found: ${viewName}-view`);
            // Fallback: show welcome view if target missing
            const fallback = document.getElementById('welcome-view');
            if (fallback) {
                fallback.classList.add('active');
                    fallback.style.display = 'block';
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
                this.initSettings(true); // force re-init
                // Set the correct theme tab active
                const currentTheme = this.currentTheme || 'default';
                let currentCategory = 'default';
                const theme = this.availableThemes.find(t => t.name === currentTheme);
                if (theme) currentCategory = theme.category;
                document.querySelectorAll('.theme-tab').forEach(tab => {
                    if (tab.dataset.category === currentCategory) {
                        tab.classList.add('active');
                    } else {
                        tab.classList.remove('active');
                    }
                });
                // Populate the theme grid for the current category
                this.updateThemeGrid(currentCategory);
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
        const mapModal = document.getElementById('map-modal');
        if (mapModal) {
            mapModal.style.display = 'flex';
            mapModal.classList.add('show');
        }
    }

    hideMapSelector() {
        const mapModal = document.getElementById('map-modal');
        if (mapModal) {
            mapModal.style.display = 'none';
            mapModal.classList.remove('show');
        }
    }

    confirmMapSelection() {
        // Simplified map selection confirmation
        this.showNotification('Map selection confirmed', 'success');
        this.hideMapSelector();
    }

    loadSensors() {
        console.log('[DEBUG] Loading sensors...');
        // Placeholder for sensor loading
        const sensorSelect = document.getElementById('sensor-select');
        if (sensorSelect) {
            sensorSelect.innerHTML = `
                <option value="">Choose a sensor...</option>
                <option value="sentinel-2">Sentinel-2</option>
                <option value="landsat-8">Landsat 8</option>
                <option value="landsat-9">Landsat 9</option>
            `;
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

    // Theme Methods
    availableThemes = [
        { name: 'default', display_name: 'Default', category: 'default', background: '#f0f0f0', primary: '#e91e63', emoji: '🌍', icon: '🌍', splashEffect: 'fade', uiEffect: 'none', welcomeMessage: 'Welcome to Flutter Earth!', splashText: "Let's explore the world!" },
        { name: 'dark', display_name: 'Dark Theme', category: 'dark', background: '#2d2d2d', primary: '#4fc3f7', emoji: '🌑', icon: '🌑', splashEffect: 'stars', uiEffect: 'nightGlow', welcomeMessage: 'Welcome to the Dark Side!', splashText: 'Embrace the night.' },
        { name: 'light', display_name: 'Light Theme', category: 'light', background: '#ffffff', primary: '#2196f3', emoji: '🌞', icon: '🌞', splashEffect: 'sunbeams', uiEffect: 'sunshine', welcomeMessage: 'Bright and Light!', splashText: 'Shine bright!' },
        { name: 'twilight_sparkle', display_name: 'Twilight Sparkle', category: 'mlp', background: '#f8c5f8', primary: '#9c27b0', emoji: '📚', icon: '🦄', splashEffect: 'magic', uiEffect: 'magicSparkle', welcomeMessage: 'Magic of Friendship!', splashText: 'Friendship is Magic!' },
        { name: 'rainbow_dash', display_name: 'Rainbow Dash', category: 'mlp', background: '#e3f2fd', primary: '#00bcd4', emoji: '🌈', icon: '🌈', splashEffect: 'rainbow', uiEffect: 'rainbowTrail', welcomeMessage: '20% Cooler!', splashText: 'Speed and color!' },
        { name: 'pinkie_pie', display_name: 'Pinkie Pie', category: 'mlp', background: '#ffe0f7', primary: '#ff69b4', emoji: '🎉', icon: '🎂', splashEffect: 'confetti', uiEffect: 'partyConfetti', welcomeMessage: 'Smile! Smile! Smile!', splashText: 'Party time!' },
        { name: 'applejack', display_name: 'Applejack', category: 'mlp', background: '#ffe5b4', primary: '#ffb347', emoji: '🍏', icon: '🍎', splashEffect: 'sunbeams', uiEffect: 'sunshine', welcomeMessage: 'Honest and True!', splashText: 'Yeehaw!' },
        { name: 'rarity', display_name: 'Rarity', category: 'mlp', background: '#f8f6ff', primary: '#b39ddb', emoji: '💎', icon: '💎', splashEffect: 'magic', uiEffect: 'magicSparkle', welcomeMessage: 'So fabulous!', splashText: 'Shine bright!' },
        { name: 'fluttershy', display_name: 'Fluttershy', category: 'mlp', background: '#fffde4', primary: '#ffd6e0', emoji: '🦋', icon: '🐰', splashEffect: 'butterflies', uiEffect: 'sunshine', welcomeMessage: 'Kindness everywhere!', splashText: 'Be gentle.' },
        { name: 'derpy', display_name: 'Derpy Hooves', category: 'mlp', background: '#e0e7ef', primary: '#b0c4de', emoji: '🧁', icon: '🦉', splashEffect: 'muffins', uiEffect: 'partyConfetti', welcomeMessage: 'Muffins!', splashText: 'Whoops! Something silly happened.' },
        { name: 'luna', display_name: 'Princess Luna', category: 'mlp', background: '#232946', primary: '#5f6caf', emoji: '🌙', icon: '🌙', splashEffect: 'stars', uiEffect: 'nightGlow', welcomeMessage: 'Dreams and Night!', splashText: 'Good night, dreamer!' },
        { name: 'celestia', display_name: 'Princess Celestia', category: 'mlp', background: '#fff8e1', primary: '#ffd54f', emoji: '☀️', icon: '👑', splashEffect: 'sunbeams', uiEffect: 'sunshine', welcomeMessage: 'Sunshine and Harmony!', splashText: 'Rise and shine, my little pony!' },
        { name: 'cadence', display_name: 'Princess Cadence', category: 'mlp', background: '#ffe0f0', primary: '#f06292', emoji: '💖', icon: '👑', splashEffect: 'hearts', uiEffect: 'magicSparkle', welcomeMessage: 'Love and Light!', splashText: 'Spread love everywhere!' },
        { name: 'sunset_shimmer', display_name: 'Sunset Shimmer', category: 'mlp', background: '#ffecb3', primary: '#ff7043', emoji: '🌅', icon: '🔥', splashEffect: 'sunset', uiEffect: 'sunshine', welcomeMessage: 'Shimmer and Shine!', splashText: 'Shine on, sunset style!' },
        { name: 'starlight_glimmer', display_name: 'Starlight Glimmer', category: 'mlp', background: '#e1bee7', primary: '#ba68c8', emoji: '⭐', icon: '✨', splashEffect: 'magic', uiEffect: 'magicSparkle', welcomeMessage: 'Equality for all!', splashText: 'Shine bright, everypony!' },
        { name: 'trixie', display_name: 'Trixie', category: 'mlp', background: '#b3e5fc', primary: '#0288d1', emoji: '🎩', icon: '🪄', splashEffect: 'fireworks', uiEffect: 'magicSparkle', welcomeMessage: 'The Great and Powerful!', splashText: 'Prepare to be amazed!' },
        { name: 'steve', display_name: 'Steve', category: 'minecraft', background: '#7ec850', primary: '#3c763d', emoji: '🧑‍🌾', icon: '⛏️', splashEffect: 'blocky', uiEffect: 'blockyOverlay', welcomeMessage: "Let's Mine!", splashText: 'Ready to build?' },
        { name: 'alex', display_name: 'Alex', category: 'minecraft', background: '#f4e2d8', primary: '#e67e22', emoji: '🧑‍🦰', icon: '🪓', splashEffect: 'blocky', uiEffect: 'blockyOverlay', welcomeMessage: 'Adventure awaits!', splashText: 'Let's craft something new!' },
        { name: 'enderman', display_name: 'Enderman', category: 'minecraft', background: '#1a1a2e', primary: '#9d00ff', emoji: '👾', icon: '👾', splashEffect: 'portal', uiEffect: 'nightGlow', welcomeMessage: '... ... ...', splashText: 'Don't look directly at them!' },
        { name: 'skeleton', display_name: 'Skeleton', category: 'minecraft', background: '#e0e0e0', primary: '#757575', emoji: '💀', icon: '🏹', splashEffect: 'arrows', uiEffect: 'nightGlow', welcomeMessage: 'Rattle rattle!', splashText: 'Watch your back!' },
        { name: 'zombie', display_name: 'Zombie', category: 'minecraft', background: '#4caf50', primary: '#1b5e20', emoji: '🧟', icon: '🧟', splashEffect: 'blocky', uiEffect: 'blockyOverlay', welcomeMessage: 'Brains...', splashText: 'Grrr! Stay safe!' },
        { name: 'creeper', display_name: 'Creeper', category: 'minecraft', background: '#3fa63f', primary: '#1a4d1a', emoji: '💣', icon: '💣', splashEffect: 'explode', uiEffect: 'creeperShake', welcomeMessage: "That's a nice app you have...", splashText: 'Sssss... Boom!' },
        { name: 'wlw', display_name: 'WLW Pride', category: 'pride', background: '#d52d00', primary: '#a30262', emoji: '👭', icon: '👭', splashEffect: 'rainbow', uiEffect: 'rainbowTrail', welcomeMessage: 'WLW Pride!', splashText: 'Love wins! Celebrate love!' },
        { name: 'mlm', display_name: 'MLM Pride', category: 'pride', background: '#078d70', primary: '#26ceaa', emoji: '👬', icon: '👬', splashEffect: 'rainbow', uiEffect: 'rainbowTrail', welcomeMessage: 'MLM Pride!', splashText: 'Love wins! Celebrate love!' },
        { name: 'nonbinary', display_name: 'Nonbinary Pride', category: 'pride', background: '#fff430', primary: '#9c59d1', emoji: '⚧️', icon: '⚧️', splashEffect: 'trans', uiEffect: 'transWave', welcomeMessage: 'Nonbinary and proud!', splashText: 'Be you, be bright!' },
        { name: 'genderqueer', display_name: 'Genderqueer Pride', category: 'pride', background: '#b57edc', primary: '#4a8123', emoji: '🏳️‍🌈', icon: '🏳️‍🌈', splashEffect: 'rainbow', uiEffect: 'rainbowTrail', welcomeMessage: 'Genderqueer and proud!', splashText: 'Be yourself, always!' },
        { name: 'pan', display_name: 'Pan Pride', category: 'pride', background: '#ff218c', primary: '#ffd800', emoji: '💖💛💙', icon: '💖', splashEffect: 'rainbow', uiEffect: 'rainbowTrail', welcomeMessage: 'Pan and proud!', splashText: 'All the love, all the colors!' },
        { name: 'ace', display_name: 'Ace Pride', category: 'pride', background: '#a3a3a3', primary: '#000000', emoji: '🖤', icon: '🤍', splashEffect: 'stars', uiEffect: 'nightGlow', welcomeMessage: 'Ace and proud!', splashText: 'You are valid and awesome!' },
        { name: 'aro', display_name: 'Aro Pride', category: 'pride', background: '#3da542', primary: '#a8d47a', emoji: '💚', icon: '💚', splashEffect: 'rainbow', uiEffect: 'rainbowTrail', welcomeMessage: 'Aro and proud!', splashText: 'Aromantic joy for all!' },
        { name: 'black_pride', display_name: 'Black Pride', category: 'pride', background: '#000000', primary: '#f9d71c', emoji: '✊🏿', icon: '✊🏿', splashEffect: 'fade', uiEffect: 'nightGlow', welcomeMessage: 'Black Pride!', splashText: 'Unity and strength always!' },
        { name: 'unity', display_name: 'Unity Pride', category: 'pride', background: '#262626', primary: '#f9d71c', emoji: '🤝', icon: '🤝', splashEffect: 'rainbow', uiEffect: 'rainbowTrail', welcomeMessage: 'Unity for all!', splashText: 'Together we rise, together we shine!' },
    ];

    currentThemeData = { options: {} };
    currentTheme = 'default';

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

    // --- Robust updateThemeGrid ---
    updateThemeGrid(category = null) {
        const themeGrid = document.getElementById('theme-grid');
        if (!themeGrid) {
            console.error('[Theme] theme-grid element not found!');
            return;
        }
        themeGrid.innerHTML = '';
        let rendered = 0;
        try {
            // Filter themes by category if specified, otherwise show all
            const themesToShow = category ? 
                this.availableThemes.filter(theme => theme.category === category) : 
                this.availableThemes;
            
            themesToShow.forEach(theme => {
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
                themeItem.style.background = cardBg;
                themeItem.style.color = textColor;
                themeItem.innerHTML = `
                    <div class="theme-icon-foreground" style="font-size:2.5em;line-height:1.2;">${theme.icon || theme.emoji}</div>
                    <div class="theme-preview" style="background: linear-gradient(45deg, ${theme.background} 0%, ${theme.primary} 100%);"></div>
                <div class="theme-info">
                    <div class="theme-name">${theme.display_name}</div>
                        <div class="theme-category">${this.getCategoryDisplayName(theme.category)}</div>
                </div>
                `;
                themeItem.addEventListener('click', () => this.selectTheme(theme.name));
                if (theme.name === this.currentTheme) {
                    themeItem.classList.add('selected');
                }
                themeGrid.appendChild(themeItem);
                rendered++;
            });
        } catch (err) {
            console.error('[Theme] Error rendering theme grid:', err);
            themeGrid.innerHTML = `<div style="color:red;padding:2em;text-align:center;">Theme grid error: ${err.message}</div>`;
            return;
        }
        if (rendered === 0) {
            themeGrid.innerHTML = '<div style="color:red;padding:2em;text-align:center;">No themes could be rendered. Check console for errors.</div>';
        } else {
            console.log(`[Theme] Rendered ${rendered} theme(s) in grid (${category ? 'category: ' + category : 'all themes'})`);
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
        splash.innerHTML = `
            <div class="theme-splash-content">
                <div class="theme-splash-emoji">${theme.emoji}</div>
                <div class="theme-splash-text">${theme.display_name}</div>
                <div class="theme-splash-message">${theme.welcomeMessage}</div>
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
        
        const content = splash.querySelector('.theme-splash-content');
        content.style.cssText = `
            text-align: center;
            color: white;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        `;
        
        const emoji = splash.querySelector('.theme-splash-emoji');
        emoji.style.cssText = `
            font-size: 120px;
            margin-bottom: 20px;
            animation: bounce 1s ease infinite;
        `;
        
        const text = splash.querySelector('.theme-splash-text');
        text.style.cssText = `
            font-size: 48px;
            font-weight: bold;
            margin-bottom: 16px;
            animation: slideInUp 0.6s ease 0.2s both;
        `;
        
        const message = splash.querySelector('.theme-splash-message');
        message.style.cssText = `
            font-size: 24px;
            opacity: 0.9;
            animation: slideInUp 0.6s ease 0.4s both;
        `;
        
        // Add CSS animations
        const style = document.createElement('style');
        style.textContent = `
            @keyframes bounce {
                0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
                40% { transform: translateY(-20px); }
                60% { transform: translateY(-10px); }
            }
            @keyframes slideInUp {
                from {
                    opacity: 0;
                    transform: translateY(30px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
        `;
        document.head.appendChild(style);
        
        document.body.appendChild(splash);
        
        // Animate in
        setTimeout(() => {
            splash.style.opacity = '1';
            splash.style.transform = 'scale(1)';
        }, 100);
        
        // Hide after 3 seconds
        setTimeout(() => {
            splash.style.opacity = '0';
            splash.style.transform = 'scale(1.1)';
            setTimeout(() => {
                if (splash.parentNode) splash.parentNode.removeChild(splash);
                if (style.parentNode) style.parentNode.removeChild(style);
            }, 500);
        }, 3000);
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
        // Always rebuild the grid for debug
        console.log('[DEBUG] Initializing settings (all themes grid)');
        const themeGrid = document.getElementById('theme-grid');
        if (!themeGrid) {
            console.error('[Theme] theme-grid element not found!');
            return;
        }
        this.updateThemeGrid();
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
            'default': '🌍 Default',
            'dark': '🌑 Dark',
            'light': '🌞 Light',
            'mlp': '🦄 MLP',
            'pride': '🏳️‍🌈 Pride',
            'special': '✨ Special',
            'minecraft': '⛏️ Minecraft',
            'other': '⭐ Other',
        };
        return map[category] || (category ? category.charAt(0).toUpperCase() + category.slice(1) : '');
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
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('[DEBUG] DOM Content Loaded - Initializing FlutterEarth');
    window.flutterEarth = new FlutterEarth();
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = FlutterEarth;
}

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

// Simplified error handling
function showLatexErrorBox() {
    const latexBox = document.createElement('div');
    latexBox.style.cssText = `
        background: #fffbe6;
        border: 2px solid #e0c200;
        padding: 24px;
        margin: 32px auto;
        max-width: 600px;
        font-family: serif;
        font-size: 1.1em;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    `;
    latexBox.innerHTML = `
        <b style="font-size:1.2em;">Electron/Node.js Not Detected</b><br><br>
        The application could not detect Electron (Node.js) running.<br>
        This usually means the Electron dependencies are missing or failed to install.<br><br>
        <strong>Manual Fix:</strong><br>
        1. Download Electron from:<br>
        &nbsp;&nbsp;&nbsp;&nbsp;https://github.com/electron/electron/releases<br>
        2. Extract the ZIP and place it in:<br>
        &nbsp;&nbsp;&nbsp;&nbsp;frontend/node_modules/electron<br>
        3. Try running the app again.<br><br>
        See the README for full instructions.
    `;
    document.body.prepend(latexBox);
}

// Check for Electron on page load
window.addEventListener('DOMContentLoaded', function() {
    if (!isElectron()) {
        console.warn('[DEBUG] Electron not detected - showing error box');
        showLatexErrorBox();
    }
}); 