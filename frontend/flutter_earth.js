// Flutter Earth JavaScript - Vanilla JS (No jQuery)

// Note: pako library is loaded via CDN in HTML if needed for gzip decompression

// The generated themes will be loaded via script tag in HTML
// import availableThemes from './generated_themes.js';

// Log all console output to file via Electron IPC
(function() {
    const origLog = console.log;
    const origError = console.error;
    const origWarn = console.warn;
    const origInfo = console.info;

    function sendToMain(level, args) {
        if (window.electronAPI && window.electronAPI.logToFile) {
            window.electronAPI.logToFile(level, Array.from(args).map(String).join(' '));
        }
    }

    console.log = function(...args) {
        origLog.apply(console, args);
        sendToMain('log', args);
    };
    console.error = function(...args) {
        origError.apply(console, args);
        sendToMain('error', args);
    };
    console.warn = function(...args) {
        origWarn.apply(console, args);
        sendToMain('warn', args);
    };
    console.info = function(...args) {
        origInfo.apply(console, args);
        sendToMain('info', args);
    };
})();

class FlutterEarth {
    constructor() {
        console.log('[DEBUG] FlutterEarth constructor called');
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
        
        console.log('[DEBUG] FlutterEarth constructor completed, calling init()');
        this.init();
        this.setDefaultTheme(); // Ensure a sensible default theme is set on load
    }

    async init() {
        console.log('[DEBUG] FlutterEarth.init() started');
        
        try {
            // Wait for DOM to be fully loaded
            if (document.readyState === 'loading') {
                console.log('[DEBUG] DOM still loading, waiting...');
                await new Promise(resolve => {
                    document.addEventListener('DOMContentLoaded', resolve);
                });
            } else {
                console.log('[DEBUG] DOM already loaded');
            }
            
            // Log initial DOM state
            console.log('[DEBUG] DOM ready, checking elements...');
            const toolbarItems = document.querySelectorAll('.toolbar-item');
            const viewElements = document.querySelectorAll('.view-content');
            console.log(`[DEBUG] Found ${toolbarItems.length} toolbar items and ${viewElements.length} view elements`);
            
            // Initialize views first - ensure welcome view is visible
            this.initializeViews();
            console.log('[DEBUG] Views initialized');
            
            // Setup event listeners immediately
            this.setupEventListeners();
            console.log('[DEBUG] Event listeners setup');
            
            // Verify initialization worked
            setTimeout(() => {
                const activeView = document.querySelector('.view-content.active');
                const activeToolbar = document.querySelector('.toolbar-item.active');
                console.log('[DEBUG] Post-init check:', {
                    activeView: activeView ? activeView.id : 'none',
                    activeToolbar: activeToolbar ? activeToolbar.dataset.view : 'none',
                    welcomeViewDisplay: document.getElementById('welcome-view')?.style.display,
                    welcomeViewActive: document.getElementById('welcome-view')?.classList.contains('active')
                });
            }, 100);
            
            // Initialize other components
            this.loadSensors();
            this.setupCalendar();
            
            // Try to load themes (but don't block)
            console.log('[DEBUG] Attempting to load themes...');
            const themesLoaded = await this.waitForThemes(10, 50); // Reduced wait time
            if (!themesLoaded) {
                console.warn('[DEBUG] No availableThemes found, continuing without themes');
                console.warn('[DEBUG] window.availableThemes:', window.availableThemes);
                console.warn('[DEBUG] typeof window.availableThemes:', typeof window.availableThemes);
            } else {
                console.log('[DEBUG] Themes loaded successfully:', window.availableThemes.length, 'themes found');
                // Initialize settings only after themes are loaded
                this.initSettings();
            }
            
            this.initSatelliteInfo();
            this.initAboutView();
            
            // Try to initialize Earth Engine (but don't block the UI)
            this.initializeEarthEngineAsync();
            
            // Show a simple notification that the app is ready
            setTimeout(() => {
                this.showNotification('Flutter Earth is ready!', 'success');
            }, 1000);
            
            console.log('[DEBUG] FlutterEarth.init() completed successfully');
        } catch (error) {
            console.error('[DEBUG] Error in FlutterEarth.init():', error);
            // Even if there's an error, make sure the basic UI is functional
            this.initializeViews();
            this.setupEventListeners();
        }
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

    // ===== CLEAN TAB SYSTEM INTEGRATION =====
    
    initializeViews() {
        console.log('[MAIN] Initializing views with clean tab system...');
        
        // The clean tab system handles all view initialization
        if (window.tabSystem) {
            console.log('[MAIN] Clean tab system is available');
            this.currentView = window.tabSystem.getCurrentTab();
        } else {
            console.log('[MAIN] Clean tab system not available, using fallback');
            this.currentView = 'welcome';
        }
        
        console.log('[MAIN] Views initialization complete');
    }

        async initializeEarthEngineAsync() {
        console.log('[DEBUG] initializeEarthEngineAsync called');
        // Run Earth Engine initialization in background
        setTimeout(async () => {
        try {
            this.updateConnectionStatus('initializing');
            this.updateStatusText('Status: Checking authentication...');
            
            if (window.electronAPI) {
                console.log('[DEBUG] window.electronAPI is available');
                // First check if authentication is needed
                const authCheck = await window.electronAPI.pythonAuthCheck();
                console.log('[DEBUG] Auth check result:', authCheck);
                
                if (authCheck && authCheck.needs_auth) {
                    this.updateConnectionStatus('offline');
                    this.updateStatusText('Status: Authentication required');
                    this.showNotification('Please set up Earth Engine authentication', 'warning');
                    console.log('[DEBUG] Showing auth dialog (needs_auth true)');
                    this.showAuthDialog();
                    return;
                }
            } else {
                console.warn('[DEBUG] window.electronAPI is NOT available');
                // Fallback for browser testing
                this.updateConnectionStatus('online');
                this.updateStatusText('Status: Running in browser mode');
                return;
            }
            
            this.updateStatusText('Status: Initializing Earth Engine...');
            const result = await window.electronAPI.pythonInit();
            console.log('[DEBUG] pythonInit result:', result);
            
            if (result.status === 'success' && result.initialized) {
                this.updateConnectionStatus('online');
                this.updateStatusText('Status: Earth Engine ready');
                this.showNotification('Earth Engine initialized successfully', 'success');
            } else if (result.status === 'offline') {
                this.updateConnectionStatus('offline');
                this.updateStatusText('Status: Offline mode - ' + (result.message || 'No credentials'));
                this.showNotification('Offline mode: ' + (result.message || 'No credentials'), 'warning');
                this.isOfflineMode = true;
            } else {
                this.updateConnectionStatus('offline');
                this.updateStatusText('Status: Earth Engine initialization failed');
                this.showNotification('Earth Engine initialization failed', 'error');
            }
        } catch (error) {
            console.error('[DEBUG] Earth Engine initialization error:', error);
            this.updateConnectionStatus('offline');
            this.updateStatusText('Status: Initialization error');
            this.showNotification('Failed to initialize Earth Engine', 'error');
        }
        }, 100);
    }

    async startDownload() {
        console.log('[DEBUG] startDownload() called');
        if (this.downloadInProgress) {
            this.showNotification('Download already in progress', 'warning');
            return;
        }
        try {
            // Gather form data
            const params = this.gatherDownloadParams();
            console.log('[DEBUG] Download params:', params);
            if (!params.area_of_interest || !params.start_date || !params.end_date || !params.sensor_name) {
                this.showNotification('Please fill in all required fields', 'error');
                return;
            }
            this.downloadInProgress = true;
            // --- Spinner and status highlight logic ---
            const spinner = document.getElementById('download-spinner');
            const btnSpinner = document.getElementById('button-download-spinner');
            const startBtn = document.getElementById('start-download');
            const statusDiv = document.getElementById('download-status');
            if (spinner) spinner.style.display = 'inline-block';
            if (btnSpinner) btnSpinner.style.display = 'inline-block';
            if (startBtn) startBtn.disabled = true;
            if (statusDiv) statusDiv.classList.add('in-progress');
            this.updateDownloadLog('Download started, waiting for crawler...');
            // --- End spinner logic ---
            this.updateDownloadStatus('Starting download...', 'info');
            console.log('[DEBUG] About to call electronAPI.pythonDownload');
            if (window.electronAPI) {
                console.log('[DEBUG] electronAPI available, calling pythonDownload');
                const result = await window.electronAPI.pythonDownload(params);
                console.log('[DEBUG] pythonDownload result:', result);
                if (result.status === 'success') {
                    this.updateDownloadStatus('Download started successfully', 'success');
                    this.showNotification('Download started', 'success');
                    this.startProgressPolling();
                } else {
                    this.updateDownloadStatus('Download failed: ' + result.message, 'error');
                    this.showNotification('Download failed: ' + result.message, 'error');
                    this.downloadInProgress = false;
                    // --- Hide spinner and restore button ---
                    if (spinner) spinner.style.display = 'none';
                    if (btnSpinner) btnSpinner.style.display = 'none';
                    if (startBtn) startBtn.disabled = false;
                    if (statusDiv) statusDiv.classList.remove('in-progress');
                }
            } else {
                console.log('[DEBUG] electronAPI not available, using fallback');
                // Fallback for browser testing
                this.simulateDownloadProgress();
            }
        } catch (error) {
            console.error('[DEBUG] Download error:', error);
            this.updateDownloadStatus('Download error: ' + error.message, 'error');
            this.showNotification('Download failed', 'error');
            this.downloadInProgress = false;
            // --- Hide spinner and restore button ---
            const spinner = document.getElementById('download-spinner');
            const btnSpinner = document.getElementById('button-download-spinner');
            const startBtn = document.getElementById('start-download');
            const statusDiv = document.getElementById('download-status');
            if (spinner) spinner.style.display = 'none';
            if (btnSpinner) btnSpinner.style.display = 'none';
            if (startBtn) startBtn.disabled = false;
            if (statusDiv) statusDiv.classList.remove('in-progress');
        }
    }

    gatherDownloadParams() {
        const params = {
            area_of_interest: document.getElementById('aoi-input').value,
            start_date: document.getElementById('start-date').value,
            end_date: document.getElementById('end-date').value,
            sensor_name: document.getElementById('sensor-select').value,
            output_dir: document.getElementById('output-dir').value,
            cloud_mask: document.getElementById('cloud-mask').checked,
            max_cloud_cover: parseInt(document.getElementById('cloud-cover').value),
            use_best_resolution: document.getElementById('best-res').checked,
            target_resolution: parseInt(document.getElementById('target-res').value),
            tiling_method: document.getElementById('tiling-method').value,
            num_subsections: parseInt(document.getElementById('num-subsections').value),
            overwrite_existing: document.getElementById('overwrite-existing').checked,
            cleanup_tiles: document.getElementById('cleanup-tiles').checked
        };

        // Add code snippet from web scraped data if available
        if (this.crawlerData && this.crawlerData.satellites && params.sensor_name) {
            const satelliteName = params.sensor_name.charAt(0).toUpperCase() + params.sensor_name.slice(1);
            const satelliteData = this.crawlerData.satellites[satelliteName];
            if (satelliteData && satelliteData[0]?.code_snippet) {
                params.code_snippet = satelliteData[0].code_snippet;
                params.satellite_info = {
                    name: satelliteName,
                    resolution: satelliteData[0].resolution,
                    data_type: satelliteData[0].data_type,
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
        const spinner = document.getElementById('download-spinner');
        const btnSpinner = document.getElementById('button-download-spinner');
        const startBtn = document.getElementById('start-download');
        const statusDiv = document.getElementById('download-status');
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
                        // --- Hide spinner and restore button ---
                        if (spinner) spinner.style.display = 'none';
                        if (btnSpinner) btnSpinner.style.display = 'none';
                        if (startBtn) startBtn.disabled = false;
                        if (statusDiv) statusDiv.classList.remove('in-progress');
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
                // --- Hide spinner and restore button ---
                if (spinner) spinner.style.display = 'none';
                if (btnSpinner) btnSpinner.style.display = 'none';
                if (startBtn) startBtn.disabled = false;
                if (statusDiv) statusDiv.classList.remove('in-progress');
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
            statusElement.textContent = '';
            const spinner = document.getElementById('download-spinner');
            if (spinner && this.downloadInProgress) {
                spinner.style.display = 'inline-block';
                statusElement.appendChild(spinner);
            }
            statusElement.appendChild(document.createTextNode(message));
        }
    }

    simulateDownloadProgress() {
        console.log('[DEBUG] Simulating download progress');
        let progress = 0;
        const interval = setInterval(() => {
            progress += 10;
            this.updateProgressDisplay({
                percentage: progress,
                message: `Simulated download progress: ${progress}%`,
                completed: progress >= 100
            });
            
            if (progress >= 100) {
                clearInterval(interval);
                this.downloadInProgress = false;
                this.updateDownloadStatus('Simulated download completed', 'success');
                this.showNotification('Simulated download completed', 'success');
            }
        }, 1000);
    }

    setupEventListeners() {
        console.log('[MAIN] Setting up event listeners with clean tab system...');
        
        // The clean tab system handles all tab switching
        if (window.tabSystem) {
            console.log('[MAIN] Clean tab system handles tab switching');
        } else {
            console.log('[MAIN] Clean tab system not available, using fallback');
        }
        
        // ===== OTHER EVENT LISTENERS =====
        this.setupOtherEventListeners();
        
        console.log('[MAIN] Event listeners setup complete');
    }
    
    setupOtherEventListeners() {
        // Help button
        const helpBtn = document.getElementById('help-button');
        if (helpBtn) {
            helpBtn.addEventListener('click', () => this.showHelpPopup());
        }
        
        // App title easter egg
        const appTitle = document.querySelector('.app-title');
        if (appTitle) {
            appTitle.addEventListener('click', () => this.triggerEasterEgg());
        }
        
        // Welcome logo effect
        const welcomeLogo = document.querySelector('.welcome-logo');
        if (welcomeLogo) {
            welcomeLogo.addEventListener('click', () => this.createLogoEffect(welcomeLogo));
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
        
        const authSettingsBtn = document.getElementById('auth-settings-btn');
        if (authSettingsBtn) authSettingsBtn.addEventListener('click', () => this.showAuthDialog());
        
        // Settings key file upload
        const settingsKeyFile = document.getElementById('settings-key-file');
        if (settingsKeyFile) {
            settingsKeyFile.addEventListener('change', (e) => {
                const fileInput = document.getElementById('auth-key-file');
                if (fileInput && e.target.files && e.target.files.length > 0) {
                    fileInput.files = e.target.files;
                }
            });
        }
        
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
        
        // Data viewer controls
        const loadRasterBtn = document.getElementById('load-raster-btn');
        if (loadRasterBtn) loadRasterBtn.addEventListener('click', () => this.loadRasterData());
        
        const loadVectorBtn = document.getElementById('load-vector-btn');
        if (loadVectorBtn) loadVectorBtn.addEventListener('click', () => this.loadVectorData());
        
        const clearDataBtn = document.getElementById('clear-data-btn');
        if (clearDataBtn) clearDataBtn.addEventListener('click', () => this.clearAllData());
        
        // About view
        const visitWebsiteBtn = document.getElementById('visit-website-btn');
        if (visitWebsiteBtn) visitWebsiteBtn.addEventListener('click', () => this.visitProjectWebsite());
        
        // Help popup backdrop
        const helpPopup = document.getElementById('help-popup');
        if (helpPopup) {
            helpPopup.addEventListener('click', (e) => {
                if (e.target === helpPopup) {
                    this.hideHelpPopup();
                }
            });
        }
        
        // Toolbar animation dropdown
        const animationSelect = document.getElementById('toolbar-animation-select');
        if (animationSelect) {
            animationSelect.addEventListener('change', () => {
                this.setToolbarAnimation(animationSelect.value);
            });
            this.setToolbarAnimation(animationSelect.value);
        }
    }
    
    switchToView(viewName) {
        console.log(`[MAIN] Switching to view: ${viewName}`);
        
        // Use the clean tab system if available
        if (window.tabSystem) {
            window.tabSystem.switchTab(viewName);
            this.currentView = viewName;
            this.updateStatusText(`View: ${this.getViewTitle(viewName)}`);
            this.handleViewSpecificLogic(viewName);
        } else {
            console.error('[MAIN] Clean tab system not available');
        }
    }
    
    updateToolbarActiveState(viewName) {
        // Remove active class from all toolbar items
        const allToolbarItems = document.querySelectorAll('.toolbar-item');
        allToolbarItems.forEach(item => {
            item.classList.remove('active');
        });
        
        // Add active class to current view's toolbar item
        const activeToolbarItem = document.querySelector(`.toolbar-item[data-view="${viewName}"]`);
        if (activeToolbarItem) {
            activeToolbarItem.classList.add('active');
            console.log(`[TAB] Set toolbar active: ${viewName}`);
        } else {
            console.warn(`[TAB] Toolbar item not found for: ${viewName}`);
        }
    }
    
    handleViewSpecificLogic(viewName) {
        console.log(`[TAB] Handling specific logic for: ${viewName}`);
        
        switch (viewName) {
            case 'settings':
                console.log('[TAB] Initializing settings view');
                this.waitForThemes().then(themesLoaded => {
                    if (themesLoaded) {
                        this.initializeThemeTabs();
                        this.updateThemeGrid('all');
                    } else {
                        console.error('[TAB] No themes found for settings view');
                        const grid = document.getElementById('theme-grid');
                        if (grid) grid.innerHTML = '<div style="color:red">No themes found. Check generated_themes.js loading.</div>';
                    }
                });
                break;
                
            case 'satelliteInfo':
                console.log('[TAB] Initializing satellite info view');
                this.setupWebCrawlerEvents();
                this.initSatelliteInfo();
                break;
                
            case 'welcome':
                console.log('[TAB] Welcome view activated');
                // Show top bar only on welcome view
                const topBar = document.getElementById('top-bar');
                if (topBar) topBar.style.display = '';
                break;
                
            default:
                // Hide top bar on other views
                const topBarDefault = document.getElementById('top-bar');
                if (topBarDefault) topBarDefault.style.display = 'none';
                break;
        }
        
        // Hide satellite thumbnail/modal if not in satelliteInfo view
        if (viewName !== 'satelliteInfo') {
            const thumbModal = document.getElementById('satellite-thumbnail-modal');
            if (thumbModal) thumbModal.style.display = 'none';
            const thumbImg = document.getElementById('thumbnail-img');
            if (thumbImg) thumbImg.style.display = 'none';
            const thumbPlaceholder = document.querySelector('.thumbnail-placeholder');
            if (thumbPlaceholder) thumbPlaceholder.style.display = 'none';
        }
    }
    
    // Legacy function for backward compatibility
    switchView(viewName) {
        console.log(`[TAB] Legacy switchView called for: ${viewName}`);
        this.switchToView(viewName);
    }
    
    // Legacy function for backward compatibility
    showPanel(panelType) {
        console.log(`[TAB] Legacy showPanel called for: ${panelType}`);
        this.showNotification(`Panel ${panelType} opened`);
    }

    moveToolbarIndicator(item) {
        const indicator = document.getElementById('toolbar-indicator');
        if (!indicator || !item) {
            console.log('[DEBUG] moveToolbarIndicator: indicator or item not found', { indicator: !!indicator, item: !!item });
            return;
        }
        const rect = item.getBoundingClientRect();
        const parentRect = item.parentElement.getBoundingClientRect();
        indicator.style.left = (rect.left - parentRect.left) + 'px';
        indicator.style.width = rect.width + 'px';
        // Set active class
        document.querySelectorAll('.toolbar-item').forEach(i => i.classList.remove('active'));
        item.classList.add('active');
        console.log('[DEBUG] moveToolbarIndicator: moved indicator to', item.dataset.view);
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

    // OLD switchView function removed - replaced by switchToView

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

    // OLD showPanel function removed - replaced by new implementation

    updateConnectionStatus(status) {
        this.connectionStatus = status;
        const statusElement = document.getElementById('connection-status');
        const statusBar = document.getElementById('status-bar');
        
        if (status === 'online') {
            statusElement.textContent = 'Status: Online';
            statusElement.className = 'status-text online';
            statusBar.style.backgroundColor = 'var(--success)';
            this.statusBarText = 'Online';
        } else if (status === 'initializing') {
            statusElement.textContent = 'Status: Initializing...';
            statusElement.className = 'status-text initializing';
            statusBar.style.backgroundColor = 'var(--warning)';
            this.statusBarText = 'Initializing...';
        } else {
            statusElement.textContent = 'Status: Offline';
            statusElement.className = 'status-text offline';
            statusBar.style.backgroundColor = 'var(--error)';
            this.statusBarText = 'Offline';
        }
    }

    showAuthDialog() {
        console.log('[DEBUG] showAuthDialog called');
        const authDialog = document.getElementById('auth-dialog');
        if (authDialog) {
            authDialog.style.display = 'flex';
            authDialog.classList.add('show');
            console.log('[DEBUG] auth-dialog element set to display flex and show class added');
        } else {
            console.warn('[DEBUG] auth-dialog element not found');
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
        this.initializeThemeTabs();
        this.updateThemeGrid('all');
    }

    // --- Enhanced updateThemeGrid with better previews ---
    updateThemeGrid(category = 'all') {
        const grid = document.getElementById('theme-grid');
        if (!grid) return;
        let themesToShow = window.availableThemes;
        if (category && category !== 'all') {
            themesToShow = window.availableThemes.filter(t => t.category === category);
        }
        console.log('[DEBUG] Updating theme grid for category:', category, 'Themes:', themesToShow.map(t => t.name));
        grid.innerHTML = '';
        themesToShow.forEach(theme => {
            const card = document.createElement('div');
            card.className = 'theme-card';
            card.innerHTML = `
                <div class="theme-card-icon">${theme.icon || theme.emoji}</div>
                <div class="theme-card-title">${theme.display_name}</div>
            `;
            card.addEventListener('click', () => this.applyTheme(theme.name));
            grid.appendChild(card);
        });
    }

    selectTheme(themeName) {
        console.log('[DEBUG] Selecting theme:', themeName);
        this.applyTheme(themeName);
    }

    applyTheme(themeName) {
        const theme = window.availableThemes.find(t => t.name === themeName);
        if (!theme) return;
        this.currentTheme = themeName;
        document.documentElement.setAttribute('data-theme', themeName);
        // Set all theme colors as CSS variables
        if (theme.colors) {
            Object.entries(theme.colors).forEach(([key, value]) => {
                document.documentElement.style.setProperty(`--${key.replace(/_/g, '-')}`, value);
            });
        }
        // Conditionally apply enhanced-theme class
        const advancedThemes = [
            'unity_pride', 'cyberpunk', 'ocean_depths', 'sunset_vibes',
            'forest_mist', 'neon_dreams', 'aurora_borealis'
        ].concat(window.availableThemes.filter(t => t.category === 'mlp').map(t => t.name));
        if (advancedThemes.includes(themeName)) {
            document.documentElement.classList.add('enhanced-theme');
        } else {
            document.documentElement.classList.remove('enhanced-theme');
        }
        
        console.log('[DEBUG] Applying theme:', themeName);
        
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
        const theme = window.availableThemes.find(t => t.name === themeName);
        return theme ? theme.notificationMessage : `Theme ${themeName} applied!`;
    }

    // --- Robust initSettings ---
    _settingsInitialized = false;
    initSettings(force = false) {
        console.log('[DEBUG] Initializing settings (all themes grid)');
        
        // Check if themes are available
        if (!window.availableThemes || !Array.isArray(window.availableThemes) || window.availableThemes.length === 0) {
            console.error('[DEBUG] No themes available for settings initialization!');
            console.error('[DEBUG] window.availableThemes:', window.availableThemes);
            return;
        }
        
        console.log('[DEBUG] Found', window.availableThemes.length, 'themes for initialization');
        
        // Try to find theme grid, but don't fail if not found
        const themeGrid = document.getElementById('theme-grid');
        if (!themeGrid) {
            console.warn('[Theme] theme-grid element not found, but continuing with settings initialization');
        } else {
            console.log('[DEBUG] Found theme-grid element, updating grid');
            this.updateThemeGrid();
        }
        
        this.loadCurrentSettings();
        this.initializeThemeTabs();
        this.updateThemeGrid('all');
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
            'gaming': '🎮 Gaming',
            'nature': '🌿 Nature',
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
        console.log('[DEBUG] setupWebCrawlerEvents() called');
        
        const runCrawlerBtn = document.getElementById('run-web-crawler');
        const cancelCrawlerBtn = document.getElementById('cancel-web-crawler');
        const refreshDataBtn = document.getElementById('refresh-crawler-data');
        const viewLogBtn = document.getElementById('view-crawler-log');
        
        console.log('[DEBUG] Setting up crawler events...');
        console.log('[DEBUG] Run button found:', !!runCrawlerBtn);
        console.log('[DEBUG] Run button element:', runCrawlerBtn);
        
        if (runCrawlerBtn) {
            console.log('[DEBUG] Run button text:', runCrawlerBtn.textContent);
            console.log('[DEBUG] Run button classes:', runCrawlerBtn.className);
        }
        
        if (runCrawlerBtn) {
            // Add visual feedback for testing
            runCrawlerBtn.style.position = 'relative';
            runCrawlerBtn.style.zIndex = '1000';
            
            runCrawlerBtn.addEventListener('click', (e) => {
                console.log('Run crawler button clicked!');
                e.preventDefault();
                e.stopPropagation();
                
                // Add immediate visual feedback
                runCrawlerBtn.style.transform = 'scale(0.95)';
                setTimeout(() => {
                    runCrawlerBtn.style.transform = '';
                }, 150);
                
                this.runWebCrawler();
            });
            
            // Also add mousedown/mouseup for better feedback
            runCrawlerBtn.addEventListener('mousedown', () => {
                runCrawlerBtn.style.transform = 'scale(0.95)';
            });
            
            runCrawlerBtn.addEventListener('mouseup', () => {
                runCrawlerBtn.style.transform = '';
            });
        }
        if (cancelCrawlerBtn) {
            cancelCrawlerBtn.addEventListener('click', () => this.cancelWebCrawler());
        }
        if (refreshDataBtn) {
            refreshDataBtn.addEventListener('click', () => this.refreshCrawlerData());
        }
        if (viewLogBtn) {
            viewLogBtn.addEventListener('click', () => this.viewCrawlerLog());
        }
        
        // Add test button handler
        const testBtn = document.getElementById('test-crawler-btn');
        if (testBtn) {
            testBtn.addEventListener('click', () => {
                console.log('Test button clicked!');
                alert('Test button works! The click event is functioning.');
            });
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
        console.log('[DEBUG] runWebCrawler() called');
        
        const progressDiv = document.getElementById('crawler-progress');
        const progressFill = document.getElementById('crawler-progress-fill');
        const messageDiv = document.getElementById('crawler-message');
        const progressTime = document.getElementById('progress-time');
        const runBtn = document.getElementById('run-web-crawler');
        const cancelBtn = document.getElementById('cancel-web-crawler');

        console.log('[DEBUG] UI elements found:', {
            progressDiv: !!progressDiv,
            progressFill: !!progressFill,
            messageDiv: !!messageDiv,
            progressTime: !!progressTime,
            runBtn: !!runBtn,
            cancelBtn: !!cancelBtn
        });

        if (this.crawlerRunning) {
            this.showNotification('Data collection is already running', 'warning');
            return;
        }

        // Show confirmation dialog
        const confirmed = confirm(
            '🕷️ Start Data Collection\n\n' +
            'This will collect satellite data from Google Earth Engine.\n' +
            '• Takes 2-5 minutes depending on connection\n' +
            '• Downloads comprehensive dataset information\n' +
            '• Generates ready-to-use Earth Engine code\n\n' +
            'Click OK to start the data collection process.'
        );

        if (!confirmed) {
            return;
        }

        this.crawlerRunning = true;
        this.updateCrawlerStatus('Starting data collection...', 'running');
        
        // Show progress UI
        if (progressDiv) {
            progressDiv.style.display = 'block';
            console.log('[DEBUG] Progress div shown');
        }
        
        if (runBtn) runBtn.disabled = true;
        if (cancelBtn) cancelBtn.disabled = false;
        if (messageDiv) messageDiv.textContent = 'Initializing data collection...';
        if (progressTime) progressTime.textContent = 'Starting...';
        this.setCrawlerBottomBar(true, 0);
        
        const consoleEl = document.getElementById('crawler-console');
        if (consoleEl) consoleEl.textContent = '';
        this.logCrawlerMessage('🕷️ Data collection started at ' + new Date().toLocaleTimeString());
        this.logCrawlerMessage('📡 Connecting to Google Earth Engine...');

        // Reset all steps
        document.querySelectorAll('.step').forEach(step => {
            step.className = 'step';
        });

        // Update first step
        this.updateCrawlerStep('init', 'active');

        // Start crawler in background
        let pollInterval = null;
        let startTime = Date.now();
        
        try {
            // Call the real backend crawler
            if (window.electronAPI) {
                console.log('[DEBUG] Electron API available, calling pythonRunCrawler');
                const result = await window.electronAPI.pythonRunCrawler();
                console.log('[DEBUG] Crawler result:', result);
                
                if (result.status === 'started') {
                    console.log('[DEBUG] Crawler started successfully, beginning progress polling');
                    // Start polling for progress
                    this.startCrawlerLogPolling();
                    
                    // Start progress monitoring
                    pollInterval = setInterval(async () => {
                        try {
                            console.log('[DEBUG] Polling for crawler progress...');
                            // Use the specific crawler progress API
                            const progressResult = await window.electronAPI.pythonCrawlerProgress();
                            console.log('[DEBUG] Progress result:', progressResult);
                            
                            if (progressResult.status === 'success' && progressResult.progress) {
                                const progress = progressResult.progress;
                                
                                // Update progress bar
                                if (progressFill) {
                                    const percent = progress.percentage || progress.percent || 0;
                                    progressFill.style.width = percent + '%';
                                    console.log('[DEBUG] Updated progress bar to:', percent + '%');
                                }
                                
                                // Update message
                                if (messageDiv) {
                                    messageDiv.textContent = progress.message || 'Collecting data...';
                                }
                                
                                // Update percentage display
                                const percentageElement = document.getElementById('progress-percentage');
                                if (percentageElement) {
                                    percentageElement.textContent = Math.round(progress.percentage || progress.percent || 0) + '%';
                                }
                                
                                // Update progress steps based on percentage
                                this.updateCrawlerStepsFromProgress(progress.percentage || progress.percent || 0);
                                
                                // Update time display
                                if (progressTime && startTime) {
                                    const elapsed = Math.floor((Date.now() - startTime) / 1000);
                                    const elapsedText = this.formatTime(elapsed);
                                    progressTime.textContent = `Elapsed: ${elapsedText}`;
                                }
                                
                                // Update bottom progress bar
                                this.setCrawlerBottomBar(true, progress.percentage || progress.percent || 0);
                                
                                // Log progress
                                this.logCrawlerMessage(`[${new Date().toLocaleTimeString()}] ${progress.message}`);
                                
                                // Update satellite counts if available
                                if (progress.datasets_found !== undefined) {
                                    const totalDatasets = document.getElementById('total-datasets');
                                    if (totalDatasets) totalDatasets.textContent = progress.datasets_found;
                                }
                                if (progress.satellites_found !== undefined) {
                                    const totalSatellites = document.getElementById('total-satellites');
                                    if (totalSatellites) totalSatellites.textContent = progress.satellites_found;
                                }
                                
                                // Check if completed
                                if (progress.status === 'completed' || (progress.percentage || progress.percent) >= 100) {
                                    console.log('[DEBUG] Crawler completed');
                                    clearInterval(pollInterval);
                                    this.crawlerRunning = false;
                                    if (runBtn) runBtn.disabled = false;
                                    if (cancelBtn) cancelBtn.disabled = true;
                                    
                                    this.updateCrawlerStatus('Data collection completed', 'ready');
                                    this.showNotification('Data collection completed successfully!', 'success');
                                    
                                    // Hide bottom progress bar after a delay
                                    setTimeout(() => this.setCrawlerBottomBar(false, 0), 3000);
                                    
                                    // Refresh data
                                    setTimeout(() => {
                                        this.refreshCrawlerData();
                                    }, 1000);
                                }
                            }
                        } catch (error) {
                            console.error('[DEBUG] Progress polling error:', error);
                        }
                    }, 1000);
                    
                } else {
                    throw new Error(result.message || 'Failed to start crawler');
                }
            } else {
                // Fallback to simulation if Electron API not available
                console.log('[DEBUG] Electron API not available, using simulation');
                await this.simulateWebCrawler(progressFill, messageDiv, progressTime, startTime);
                
                // Reset UI state
                this.crawlerRunning = false;
                if (runBtn) runBtn.disabled = false;
                if (cancelBtn) cancelBtn.disabled = true;
                
                this.updateCrawlerStatus('Data collection completed', 'ready');
                this.showNotification('Data collection completed successfully!', 'success');
                
                // Hide bottom progress bar after a delay
                setTimeout(() => this.setCrawlerBottomBar(false, 0), 3000);
                
                // Simulate loading some data
                setTimeout(() => {
                    this.refreshCrawlerData();
                }, 1000);
            }
            
        } catch (error) {
            console.error('[DEBUG] Crawler error:', error);
            if (pollInterval) clearInterval(pollInterval);
            this.crawlerRunning = false;
            if (runBtn) runBtn.disabled = false;
            if (cancelBtn) cancelBtn.disabled = true;
            if (messageDiv) messageDiv.textContent = 'Error: ' + error.message;
            this.updateCrawlerStatus('Error', 'error');
            this.showNotification('Data collection failed: ' + error.message, 'error');
            this.logCrawlerMessage('Error: ' + error.message);
            setTimeout(() => this.setCrawlerBottomBar(false, 0), 2000);
            this.stopCrawlerLogPolling();
        }
    }

    // Optionally, add a cancel button handler
    async cancelWebCrawler() {
        if (window.electronAPI) {
            await window.electronAPI.pythonCancelCrawler();
            this.showNotification('Crawler cancelled', 'warning');
        }
    }

    async simulateWebCrawler(progressFill, messageDiv, progressTime, startTime) {
        const steps = [
            { name: 'init', message: 'Initializing data collection system...', duration: 1500 },
            { name: 'connect', message: 'Connecting to Google Earth Engine catalog...', duration: 2000 },
            { name: 'fetch', message: 'Fetching satellite dataset information...', duration: 3000 },
            { name: 'process', message: 'Processing satellite details and capabilities...', duration: 2500 },
            { name: 'download', message: 'Downloading satellite thumbnails and metadata...', duration: 3500 },
            { name: 'save', message: 'Saving data to local storage...', duration: 1500 }
        ];

        for (let i = 0; i < steps.length; i++) {
            const step = steps[i];
            
            // Update step status
            this.updateCrawlerStep(step.name, 'active');
            
            // Update message and progress
            messageDiv.textContent = step.message;
            const progress = ((i + 1) / steps.length) * 100;
            if (progressFill) progressFill.style.width = progress + '%';
            
            // Update percentage display
            const percentageElement = document.getElementById('progress-percentage');
            if (percentageElement) {
                percentageElement.textContent = Math.round(progress) + '%';
            }
            
            // Update time display
            if (progressTime && startTime) {
                const elapsed = Math.floor((Date.now() - startTime) / 1000);
                const elapsedText = this.formatTime(elapsed);
                progressTime.textContent = `Elapsed: ${elapsedText}`;
            }
            
            // Update bottom progress bar
            this.setCrawlerBottomBar(true, progress);
            
            // Log with timestamp
            const elapsed = startTime ? Math.floor((Date.now() - startTime) / 1000) : 0;
            const elapsedText = this.formatTime(elapsed);
            this.logCrawlerMessage(`[${elapsedText}] ${step.message}`);
            
            // Simulate some satellite data updates
            if (i === 2) { // During fetch step
                setTimeout(() => {
                    const totalSatellites = document.getElementById('total-satellites');
                    const totalDatasets = document.getElementById('total-datasets');
                    if (totalSatellites) totalSatellites.textContent = '12';
                    if (totalDatasets) totalDatasets.textContent = '156';
                }, 1000);
            }
            
            if (i === 3) { // During process step
                setTimeout(() => {
                    const totalSatellites = document.getElementById('total-satellites');
                    const totalDatasets = document.getElementById('total-datasets');
                    if (totalSatellites) totalSatellites.textContent = '24';
                    if (totalDatasets) totalDatasets.textContent = '342';
                }, 1000);
            }
            
            // Wait for step duration
            await new Promise(resolve => setTimeout(resolve, step.duration));
            
            // Mark step as completed
            this.updateCrawlerStep(step.name, 'completed');
        }
        
        // Final completion message
        const totalTime = startTime ? Math.floor((Date.now() - startTime) / 1000) : 0;
        const totalTimeText = this.formatTime(totalTime);
        this.logCrawlerMessage(`✅ Data collection completed successfully in ${totalTimeText}`);
        
        if (progressTime) {
            progressTime.textContent = `Completed in ${totalTimeText}`;
        }
        
        // Update final stats
        const totalSatellites = document.getElementById('total-satellites');
        const totalDatasets = document.getElementById('total-datasets');
        if (totalSatellites) totalSatellites.textContent = '32';
        if (totalDatasets) totalDatasets.textContent = '487';
    }

    updateCrawlerStep(stepName, status) {
        const stepElement = document.querySelector(`[data-step="${stepName}"]`);
        if (stepElement) {
            stepElement.className = `step ${status}`;
        }
    }
    
    updateCrawlerStepsFromProgress(percent) {
        // Map percentage to steps
        const steps = [
            { name: 'init', threshold: 10 },
            { name: 'connect', threshold: 25 },
            { name: 'fetch', threshold: 50 },
            { name: 'process', threshold: 75 },
            { name: 'download', threshold: 90 },
            { name: 'save', threshold: 100 }
        ];
        
        steps.forEach((step, index) => {
            if (percent >= step.threshold) {
                // Mark this step and all previous steps as completed
                for (let i = 0; i <= index; i++) {
                    this.updateCrawlerStep(steps[i].name, 'completed');
                }
                // Mark next step as active if not at the end
                if (index < steps.length - 1 && percent < steps[index + 1].threshold) {
                    this.updateCrawlerStep(steps[index + 1].name, 'active');
                }
            }
        });
        
        // If at 100%, ensure all steps are completed
        if (percent >= 100) {
            steps.forEach(step => {
                this.updateCrawlerStep(step.name, 'completed');
            });
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
    }

    // --- THEME TABS & GRID LOGIC ---
    // Dynamically generate theme tabs from availableThemes categories
    getUniqueThemeCategories() {
        if (!window.availableThemes || !Array.isArray(window.availableThemes)) {
            console.error('[DEBUG] No themes available for category extraction!');
            return ['all'];
        }
        
        const categories = new Set(window.availableThemes.map(t => t.category));
        return ['all', ...Array.from(categories)];
    }

    initializeThemeTabs() {
        if (!window.availableThemes || !Array.isArray(window.availableThemes)) {
            console.error('[DEBUG] No themes available for tab initialization!');
            return;
        }
        
        const categories = this.getUniqueThemeCategories();
        const tabContainer = document.getElementById('theme-tab-container');
        if (!tabContainer) {
            console.warn('[DEBUG] Theme tab container not found');
            return;
        }
        
        tabContainer.innerHTML = '';
        console.log('[DEBUG] Creating theme tabs for categories:', categories);
        categories.forEach(category => {
            const tab = document.createElement('button');
            tab.className = 'theme-tab';
            tab.dataset.category = category;
            tab.textContent = category === 'all' ? 'All Themes' : this.getCategoryDisplayName(category);
            tab.addEventListener('click', () => {
                console.log('[DEBUG] Tab clicked:', category);
                this.switchThemeCategory(category);
            });
            tabContainer.appendChild(tab);
        });
    }

    switchThemeCategory(category) {
        console.log('[DEBUG] Switching theme category to:', category);
        document.querySelectorAll('.theme-tab').forEach(tab => {
            tab.classList.toggle('active', tab.dataset.category === category);
        });
        this.updateThemeGrid(category);
    }

    updateThemeGrid(category = 'all') {
        const grid = document.getElementById('theme-grid');
        if (!grid) {
            console.warn('[DEBUG] Theme grid element not found');
            return;
        }
        
        if (!window.availableThemes || !Array.isArray(window.availableThemes)) {
            console.error('[DEBUG] No themes available for grid update!');
            grid.innerHTML = '<div class="theme-error">No themes found. Check generated_themes.js loading.</div>';
            return;
        }
        
        let themesToShow = window.availableThemes;
        if (category && category !== 'all') {
            themesToShow = window.availableThemes.filter(t => t.category === category);
        }
        
        console.log('[DEBUG] Updating theme grid for category:', category, 'Themes:', themesToShow.length, 'themes');
        
        if (themesToShow.length === 0) {
            grid.innerHTML = '<div class="theme-error">No themes found for category: ' + category + '</div>';
            return;
        }
        
        grid.innerHTML = '';
        themesToShow.forEach(theme => {
            const card = document.createElement('div');
            card.className = 'theme-card';
            card.innerHTML = `
                <div class="theme-card-icon">${theme.icon || theme.emoji}</div>
                <div class="theme-card-title">${theme.display_name}</div>
            `;
            card.addEventListener('click', () => this.applyTheme(theme.name));
            grid.appendChild(card);
        });
    }

    // On app load, set a sensible default theme
    setDefaultTheme() {
        const currentTheme = this.currentTheme || 'default_dark';
        
        // Set the theme attribute
        document.documentElement.setAttribute('data-theme', currentTheme);
        
        // Apply theme colors to CSS variables
        this.applyThemeColors(currentTheme);
        
        console.log('[THEME] Set default theme:', currentTheme);
    }
    
    applyThemeColors(themeName) {
        if (!window.availableThemes) {
            console.warn('[THEME] No themes available');
            return;
        }
        
        const theme = window.availableThemes.find(t => t.name === themeName);
        if (!theme) {
            console.warn(`[THEME] Theme not found: ${themeName}`);
            return;
        }
        
        // Apply CSS variables
        const root = document.documentElement;
        if (theme.colors) {
            Object.entries(theme.colors).forEach(([key, value]) => {
                const cssVar = key.replace(/_/g, '-');
                root.style.setProperty(`--${cssVar}`, value);
            });
        }
        
        console.log(`[THEME] Applied theme colors: ${themeName}`);
    }

    // Call setDefaultTheme in the constructor or init method

    // Add this function to FlutterEarth class:
    async waitForThemes(maxRetries = 10, delayMs = 100) {
        for (let i = 0; i < maxRetries; i++) {
            if (window.availableThemes && window.availableThemes.length > 0) return true;
            await new Promise(res => setTimeout(res, delayMs));
        }
        return false;
    }

    setToolbarAnimation(style) {
        const toolbarItems = document.querySelectorAll('.toolbar-item');
        toolbarItems.forEach(item => {
            item.classList.remove('glow', 'bounce', 'slide', 'pulse', 'spin', 'flip', 'shake', 'wiggle', 'color', 'fade', 'pop', 'rubber', 'swing', 'rotate', 'none');
            item.classList.add(style);
        });
    }

    animateToolbarItem(item) {
        const animationSelect = document.getElementById('toolbar-animation-select');
        const style = animationSelect ? animationSelect.value : 'glow';
        item.classList.remove('glow', 'bounce', 'slide', 'pulse', 'spin', 'flip', 'shake', 'wiggle', 'color', 'fade', 'pop', 'rubber', 'swing', 'rotate', 'none');
        void item.offsetWidth; // force reflow for animation restart
        item.classList.add(style);
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('[DEBUG] DOM loaded, initializing FlutterEarth...');
    try {
        window.flutterEarth = new FlutterEarth();
        console.log('[DEBUG] FlutterEarth instance created:', window.flutterEarth);
        window.flutterEarth.init().then(() => {
            console.log('[DEBUG] FlutterEarth initialization completed');
        }).catch(error => {
            console.error('[DEBUG] FlutterEarth initialization failed:', error);
        });
    } catch (error) {
        console.error('[DEBUG] Error creating FlutterEarth instance:', error);
    }
});

// Debug functions - call these from browser console to test tab switching
window.testTabSwitching = function() {
    console.log('=== TAB SWITCHING DEBUG TEST ===');
    
    // Check if FlutterEarth instance exists
    if (!window.flutterEarth) {
        console.error('FlutterEarth instance not found!');
        return;
    }
    
    // Check toolbar items
    const toolbarItems = document.querySelectorAll('.toolbar-item');
    console.log(`Found ${toolbarItems.length} toolbar items`);
    
    // Check view elements
    const viewElements = document.querySelectorAll('.view-content');
    console.log(`Found ${viewElements.length} view elements`);
    
    // Test switching to map view
    console.log('Testing switch to map view...');
    window.flutterEarth.switchView('map');
    
    // Check if map view is now active
    setTimeout(() => {
        const mapView = document.getElementById('map-view');
        const isActive = mapView && mapView.classList.contains('active');
        const display = mapView ? getComputedStyle(mapView).display : 'not found';
        console.log(`Map view active: ${isActive}, display: ${display}`);
    }, 100);
};

// Quick test function
window.quickTest = function() {
    const welcomeView = document.getElementById('welcome-view');
    const mapView = document.getElementById('map-view');
    
    console.log('Welcome view:', welcomeView ? 'found' : 'not found');
    console.log('Map view:', mapView ? 'found' : 'not found');
    
    if (welcomeView) {
        console.log('Welcome view classes:', welcomeView.className);
        console.log('Welcome view display:', getComputedStyle(welcomeView).display);
    }
    
    if (mapView) {
        console.log('Map view classes:', mapView.className);
        console.log('Map view display:', getComputedStyle(mapView).display);
    }
};

// Manual tab switch function
window.manualSwitch = function(viewName) {
    console.log(`Manually switching to: ${viewName}`);
    if (window.flutterEarth) {
        window.flutterEarth.switchView(viewName);
    } else {
        console.error('FlutterEarth not available');
    }
};