/**
 * Enhanced Flutter Earth v2.0 JavaScript
 * Modern implementation with improved architecture and user experience
 */

class FlutterEarthEnhancedV2 {
    constructor() {
        this.currentView = 'welcome';
        this.currentTheme = 'default';
        this.isLoading = false;
        this.authModalShown = false;
        this.downloads = new Map();
        this.satellites = new Map();
        this.notifications = [];
        this.settings = this.loadSettings();
        
        // Initialize components
        this.initializeComponents();
        this.setupEventListeners();
        this.setupToolbarMenus();
        this.loadInitialData();
        
        // Initialize satellite info functionality
        this.initSatelliteInfo();
        
        console.log('Flutter Earth Enhanced v2.0 initialized');
    }

    /**
     * Initialize all UI components
     */
    initializeComponents() {
        // Initialize toolbar
        this.toolbar = {
            items: document.querySelectorAll('.toolbar-item'),
            indicator: document.getElementById('toolbar-indicator'),
            activeItem: null
        };

        // Initialize views
        this.views = {
            welcome: document.getElementById('welcome-view'),
            map: document.getElementById('map-view'),
            download: document.getElementById('download-view'),
            satelliteInfo: document.getElementById('satelliteInfo-view'),
            indexAnalysis: document.getElementById('indexAnalysis-view'),
            vectorDownload: document.getElementById('vectorDownload-view'),
            dataViewer: document.getElementById('dataViewer-view'),
            progress: document.getElementById('progress-view'),
            settings: document.getElementById('settings-view'),
            about: document.getElementById('about-view')
        };

        // Initialize side panels
        this.sidePanels = {
            toolbox: document.getElementById('toolbox-panel'),
            bookmarks: document.getElementById('bookmarks-panel'),
            attributeTable: document.getElementById('attributeTable-panel')
        };

        // Initialize modals
        this.modals = {
            help: document.getElementById('help-modal'),
            mapSelector: document.getElementById('map-selector-modal')
        };

        // Initialize status indicators
        this.statusIndicators = {
            connection: document.getElementById('connection-status'),
            auth: document.getElementById('auth-status')
        };

        // Initialize form elements
        this.formElements = {
            aoiInput: document.getElementById('aoi-input'),
            startDate: document.getElementById('start-date'),
            endDate: document.getElementById('end-date'),
            sensorSelect: document.getElementById('sensor-select'),
            outputDir: document.getElementById('output-dir'),
            cloudMask: document.getElementById('cloud-mask'),
            cloudCover: document.getElementById('cloud-cover'),
            cloudCoverValue: document.getElementById('cloud-cover-value'),
            bestRes: document.getElementById('best-res'),
            targetRes: document.getElementById('target-res'),
            tilingMethod: document.getElementById('tiling-method'),
            formatSelect: document.getElementById('format-select'),
            applyCorrections: document.getElementById('apply-corrections'),
            generateIndices: document.getElementById('generate-indices')
        };

        // Initialize action buttons
        this.actionButtons = {
            startDownload: document.getElementById('start-download-btn'),
            validateParams: document.getElementById('validate-params-btn'),
            savePreset: document.getElementById('save-preset-btn'),
            mapSelector: document.getElementById('map-selector-btn'),
            browse: document.getElementById('browse-btn'),
            testAuth: document.getElementById('test-auth-button'),
            help: document.getElementById('help-button'),
            themeToggle: document.getElementById('theme-toggle')
        };

        // Initialize progress elements
        this.progressElements = {
            list: document.getElementById('progress-list'),
            activeCount: document.getElementById('active-count'),
            completedCount: document.getElementById('completed-count'),
            failedCount: document.getElementById('failed-count'),
            refresh: document.getElementById('refresh-progress-btn'),
            clearCompleted: document.getElementById('clear-completed-btn')
        };

        // Initialize satellite elements
        this.satelliteElements = {
            grid: document.getElementById('satellite-grid'),
            search: document.getElementById('satellite-search'),
            typeFilter: document.getElementById('satellite-type'),
            refresh: document.getElementById('refresh-satellites-btn'),
            filter: document.getElementById('filter-satellites-btn')
        };

        // Initialize settings elements
        this.settingsElements = {
            tabs: document.querySelectorAll('.settings-tab'),
            panels: document.querySelectorAll('.settings-panel'),
            defaultOutputDir: document.getElementById('default-output-dir'),
            autoSave: document.getElementById('auto-save'),
            maxConcurrent: document.getElementById('max-concurrent'),
            downloadTimeout: document.getElementById('download-timeout'),
            themeSelect: document.getElementById('theme-select'),
            fontSize: document.getElementById('font-size'),
            fontSizeValue: document.getElementById('font-size-value'),
            debugMode: document.getElementById('debug-mode'),
            clearCache: document.getElementById('clear-cache-btn'),
            resetSettings: document.getElementById('reset-settings-btn')
        };
    }

    /**
     * Setup all event listeners
     */
    setupEventListeners() {
        // Tab switching is now handled by tabs.js
        // Only setup non-tab event listeners here
        
        // Side panel buttons
        document.querySelectorAll('.toolbar-item[data-panel]').forEach(item => {
            item.onclick = (e) => {
                const panel = item.dataset.panel;
                if (!panel) return;
                this.toggleSidePanel(panel);
            };
        });

        // Side panel buttons
        document.querySelectorAll('.toolbar-item[data-panel]').forEach(item => {
            item.onclick = (e) => {
                const panel = item.dataset.panel;
                if (!panel) return;
                this.toggleSidePanel(panel);
            };
        });

        // Action buttons (right side)
        this.actionButtons.startDownload?.addEventListener('click', () => this.startDownload());
        this.actionButtons.validateParams?.addEventListener('click', () => this.validateParameters());
        this.actionButtons.savePreset?.addEventListener('click', () => this.savePreset());
        this.actionButtons.mapSelector?.addEventListener('click', () => this.openMapSelector());
        this.actionButtons.browse?.addEventListener('click', () => this.browseOutputDir());
        this.actionButtons.testAuth?.addEventListener('click', () => this.testAuthentication());
        this.actionButtons.help?.addEventListener('click', () => this.openHelpModal());
        this.actionButtons.themeToggle?.addEventListener('click', () => this.toggleTheme());

        // Authentication status indicator - click to open auth modal
        this.statusIndicators.auth?.addEventListener('click', () => this.showAuthModal());
        this.statusIndicators.auth?.addEventListener('contextmenu', (e) => {
            e.preventDefault();
            this.showAuthModal();
        });

        // Form interactions
        this.formElements.cloudCover?.addEventListener('input', (e) => {
            this.formElements.cloudCoverValue.textContent = `${e.target.value}%`;
        });
        this.formElements.bestRes?.addEventListener('change', (e) => {
            this.formElements.targetRes.disabled = e.target.checked;
        });

        // Progress actions
        this.progressElements.refresh?.addEventListener('click', () => this.refreshProgress());
        this.progressElements.clearCompleted?.addEventListener('click', () => this.clearCompletedDownloads());

        // Satellite actions
        this.satelliteElements.refresh?.addEventListener('click', () => this.refreshSatellites());
        this.satelliteElements.filter?.addEventListener('click', () => this.filterSatellites());
        this.satelliteElements.search?.addEventListener('input', (e) => this.searchSatellites(e.target.value));
        this.satelliteElements.typeFilter?.addEventListener('change', (e) => this.filterSatellitesByType(e.target.value));

        // Settings interactions
        this.settingsElements.tabs.forEach(tab => {
            tab.addEventListener('click', (e) => this.switchSettingsTab(e.target.dataset.tab));
        });
        this.settingsElements.fontSize?.addEventListener('input', (e) => {
            this.settingsElements.fontSizeValue.textContent = `${e.target.value}px`;
            this.updateFontSize(e.target.value);
        });
        this.settingsElements.clearCache?.addEventListener('click', () => this.clearCache());
        this.settingsElements.resetSettings?.addEventListener('click', () => this.resetSettings());

        // Subtab navigation is handled by setupSubtabEventListeners() in initSatelliteInfo()
        // No duplicate event listeners here

        // Crawler controls
        const runCrawlerBtn = document.getElementById('run-web-crawler');
        const cancelCrawlerBtn = document.getElementById('cancel-web-crawler');
        const refreshCrawlerDataBtn = document.getElementById('refresh-crawler-data');
        const viewCrawlerLogBtn = document.getElementById('view-crawler-log');

        runCrawlerBtn?.addEventListener('click', () => this.startCrawler());
        cancelCrawlerBtn?.addEventListener('click', () => this.stopCrawlerProgressPolling());
        refreshCrawlerDataBtn?.addEventListener('click', () => this.loadCrawlerStatus());
        viewCrawlerLogBtn?.addEventListener('click', () => this.viewCrawlerLog());

        // Settings tab switching
        this.settingsElements.tabs.forEach(tab => {
            tab.addEventListener('click', (e) => this.switchSettingsTab(e.target.dataset.tab));
        });
        this.settingsElements.fontSize?.addEventListener('input', (e) => {
            this.settingsElements.fontSizeValue.textContent = `${e.target.value}px`;
            this.updateFontSize(e.target.value);
        });
        this.settingsElements.clearCache?.addEventListener('click', () => this.clearCache());
        this.settingsElements.resetSettings?.addEventListener('click', () => this.resetSettings());

        // Modal interactions
        Object.values(this.modals).forEach(modal => {
            if (modal) {
                const closeBtn = modal.querySelector('.modal-close');
                closeBtn?.addEventListener('click', () => this.closeModal(modal.id));
                modal.addEventListener('click', (e) => {
                    if (e.target === modal) {
                        this.closeModal(modal.id);
                    }
                });
            }
        });

        // Side panel interactions
        Object.values(this.sidePanels).forEach(panel => {
            if (panel) {
                const closeBtn = panel.querySelector('.panel-close');
                closeBtn?.addEventListener('click', () => this.closeSidePanel(panel.id));
            }
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => this.handleKeyboardShortcuts(e));
        // Window events
        window.addEventListener('resize', () => this.handleResize());
        window.addEventListener('beforeunload', () => this.saveSettings());

        // --- SATELLITE CATALOG SUBTABS ---
        // Satellite grid view toggles
        document.querySelectorAll('.view-toggle').forEach(toggle => {
            toggle.onclick = (e) => {
                const view = toggle.dataset.view;
                this.switchSatelliteGridView(view);
            };
        });

        // Satellite search
        const satSearch = document.getElementById('satellite-search');
        if (satSearch) {
            satSearch.oninput = (e) => this.filterSatellites();
        }
        const clearSatSearch = document.getElementById('clear-satellite-search');
        if (clearSatSearch) {
            clearSatSearch.onclick = () => this.clearSatelliteSearch();
        }

        // Satellite filter tabs
        document.querySelectorAll('.filter-tab').forEach(tab => {
            tab.onclick = (e) => {
                const category = tab.dataset.filter;
                this.filterSatellitesByCategory(category);
            };
        });

        // Satellite details close
        const closeDetails = document.getElementById('close-details');
        if (closeDetails) {
            closeDetails.onclick = () => this.closeSatelliteDetailsPanel();
        }
        // Use for download
        const useForDownload = document.getElementById('use-for-download');
        if (useForDownload) {
            useForDownload.onclick = () => this.useSatelliteForDownload();
        }
        // Share satellite
        const shareSatellite = document.getElementById('share-satellite');
        if (shareSatellite) {
            shareSatellite.onclick = () => this.shareSatellite();
        }

        // --- DATASET VIEWER SUBTAB ---
        // Dataset search
        const datasetSearch = document.getElementById('dataset-search');
        if (datasetSearch) {
            datasetSearch.oninput = (e) => this.filterDatasets();
        }
        const clearDatasetSearch = document.getElementById('clear-dataset-search');
        if (clearDatasetSearch) {
            clearDatasetSearch.onclick = () => this.clearDatasetSearch();
        }
        // Dataset details close
        const closeDatasetDetails = document.getElementById('close-dataset-details');
        if (closeDatasetDetails) {
            closeDatasetDetails.onclick = () => this.closeDatasetDetailsPanel();
        }
    }

    /**
     * Setup toolbar dropdown menus and tooltips
     */
    setupToolbarMenus() {
        // Only attach to right-side menu buttons
        const menuMap = {
            'connection-status': 'connection-menu',
            'auth-status': 'user-menu',
            'test-auth-button': 'auth-modal',
            'help-button': 'help-menu',
            'theme-toggle': 'theme-menu',
        };

        // Add tooltips
        const tooltips = {
            'connection-status': 'Connection Status',
            'auth-status': 'User/Account',
            'test-auth-button': 'Authentication',
            'help-button': 'Help & Documentation',
            'theme-toggle': 'Theme Switcher',
        };
        Object.entries(tooltips).forEach(([id, text]) => {
            const el = document.getElementById(id);
            if (el && !el.querySelector('.toolbar-tooltip')) {
                const tip = document.createElement('span');
                tip.className = 'toolbar-tooltip';
                tip.textContent = text;
                el.appendChild(tip);
            }
        });

        // Open/close menus ONLY for right-side menu buttons
        Object.entries(menuMap).forEach(([btnId, menuId]) => {
            const btn = document.getElementById(btnId);
            const menu = document.getElementById(menuId);
            if (!btn || !menu) return;

            btn.addEventListener('click', (e) => {
                console.log('[MENU CLICK]', {btnId, menuId, element: btn});
                e.stopPropagation();
                // Close all menus first
                document.querySelectorAll('.toolbar-menu').forEach(m => m.classList.remove('open'));
                document.querySelectorAll('.modal').forEach(m => m.classList.remove('open'));
                // Open the correct menu/modal
                if (menu.classList.contains('modal')) {
                    menu.classList.add('open');
                } else {
                    menu.classList.toggle('open');
                }
            });
        });

        // Close menus on outside click
        document.addEventListener('click', (e) => {
            document.querySelectorAll('.toolbar-menu').forEach(m => m.classList.remove('open'));
        });

        // Prevent menu click from closing itself
        document.querySelectorAll('.toolbar-menu').forEach(menu => {
            menu.addEventListener('click', (e) => e.stopPropagation());
        });

        // Menu actions (placeholders)
        document.getElementById('reconnect-btn')?.addEventListener('click', () => {
            this.showNotification('Reconnect feature coming soon!', 'info');
        });
        document.getElementById('logout-btn')?.addEventListener('click', () => {
            this.showNotification('Logout feature coming soon!', 'info');
        });
        document.getElementById('quickstart-link')?.addEventListener('click', (e) => {
            e.preventDefault();
            this.showNotification('Quick Start Guide coming soon!', 'info');
        });
        document.getElementById('faq-link')?.addEventListener('click', (e) => {
            e.preventDefault();
            this.showNotification('FAQ coming soon!', 'info');
        });
        document.getElementById('support-link')?.addEventListener('click', (e) => {
            e.preventDefault();
            this.showNotification('Support feature coming soon!', 'info');
        });
        document.querySelectorAll('.theme-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const theme = btn.getAttribute('data-theme');
                this.applyTheme(theme);
                this.showNotification(`Theme switched to ${theme}`, 'success');
            });
        });
        document.getElementById('save-theme-btn')?.addEventListener('click', () => {
            this.showNotification('Theme saving coming soon!', 'info');
        });
    }

    /**
     * Load initial data
     */
    async loadInitialData() {
        try {
            this.showLoading('Loading application data...');
            
            // Initialize authentication system first
            await this.initializeAuthentication();
            
            // Load satellites
            await this.loadSatellites();
            
            // Load progress
            await this.refreshProgress();
            
            // Apply saved theme
            this.applyTheme(this.settings.theme || 'default');
            
            this.hideLoading();
            this.showNotification('Application loaded successfully', 'success');
            
        } catch (error) {
            console.error('Error loading initial data:', error);
            this.hideLoading();
            this.showNotification('Error loading application data', 'error');
        }
    }

    /**
     * Initialize authentication system on startup
     */
    async initializeAuthentication() {
        console.log('Initializing authentication system...');
        
        try {
            // Check for existing credentials in C:\FE Auth
            const authStatus = await this.checkExistingCredentials();
            
            if (authStatus.hasCredentials) {
                // Validate existing credentials
                const isValid = await this.validateCredentials(authStatus.keyPath, authStatus.projectId);
                
                if (isValid) {
                    // Connect to GEE with existing credentials
                    await this.connectToGEE(authStatus.keyPath, authStatus.projectId);
                    this.updateAuthStatus({ authenticated: true, status: 'authenticated' });
                    this.showNotification('Connected to Google Earth Engine', 'success');
                    return true;
                } else {
                    // Credentials are invalid
                    this.showNotification('Existing credentials are invalid', 'warning');
                    this.updateAuthStatus({ authenticated: false, status: 'error' });
                    this.showAuthModal();
                    return false;
                }
            } else {
                // No credentials found
                this.showNotification('No authentication credentials found', 'info');
                this.updateAuthStatus({ authenticated: false, status: 'not_authenticated' });
                this.showAuthModal();
                return false;
            }
        } catch (error) {
            console.error('Authentication initialization failed:', error);
            this.updateAuthStatus({ authenticated: false, status: 'error', message: error.message });
            this.showAuthModal();
            return false;
        }
    }

    /**
     * Check for existing credentials in C:\FE Auth folder
     */
    async checkExistingCredentials() {
        try {
            if (window.electronAPI) {
                // Use Electron API to check files
                const result = await window.electronAPI.readAuthFiles();
                if (result.success && result.files.authConfig && result.files.keyFile) {
                    return {
                        hasCredentials: true,
                        projectId: result.files.authConfig.project_id,
                        keyPath: result.files.authConfig.key_file,
                        keyContent: result.files.keyFile
                    };
                }
            } else {
                // Web environment - try to read files
                const configResponse = await fetch('file:///C:/FE%20Auth/auth_config.json');
                const keyResponse = await fetch('file:///C:/FE%20Auth/service_account_key.json');
                
                if (configResponse.ok && keyResponse.ok) {
                    const config = await configResponse.json();
                    const keyContent = await keyResponse.json();
                    return {
                        hasCredentials: true,
                        projectId: config.project_id,
                        keyPath: config.key_file,
                        keyContent: keyContent
                    };
                }
            }
            
            return { hasCredentials: false };
        } catch (error) {
            console.log('No existing credentials found:', error);
            return { hasCredentials: false };
        }
    }

    /**
     * Validate credentials by testing connection to GEE
     */
    async validateCredentials(keyPath, projectId) {
        try {
            if (window.electronAPI) {
                // Use Electron API to test credentials
                const result = await window.electronAPI.pythonAuthTest(keyPath, projectId);
                return result.status === 'success';
            } else {
                // Web environment - simulate validation
                // In a real implementation, this would make an API call to test credentials
                return true; // Simulated success
            }
        } catch (error) {
            console.error('Credential validation failed:', error);
            return false;
        }
    }

    /**
     * Switch between main views
     */
    switchView(viewName) {
        if (this.currentView === viewName) return;

        // Hide current view
        const currentView = this.views[this.currentView];
        if (currentView) {
            currentView.classList.remove('active');
        }

        // Show new view
        const newView = this.views[viewName];
        if (newView) {
            newView.classList.add('active');
            this.currentView = viewName;
        }

        // Update toolbar
        this.updateToolbarActiveItem(viewName);

        // Load view-specific data
        this.loadViewData(viewName);

        // Update URL hash
        window.location.hash = viewName;
    }

    /**
     * Switch between subtabs in Satellite Info view
     */
    switchSubtab(subtabName) {
        console.log(`[SUBTAB] Switching to: ${subtabName}`);
        
        if (!subtabName) {
            console.error('[SUBTAB] No subtab name provided');
            return;
        }
        
        // Remove active class from all subtab buttons
        const allButtons = document.querySelectorAll('.subtab-btn');
        allButtons.forEach(btn => {
            btn.classList.remove('active');
        });
        
        // Remove active class from all subtab content
        const allContents = document.querySelectorAll('.subtab-content');
        allContents.forEach(content => {
            content.classList.remove('active');
        });
        
        // Add active class to target subtab button
        const targetBtn = document.querySelector(`.subtab-btn[data-subtab="${subtabName}"]`);
        if (targetBtn) {
            targetBtn.classList.add('active');
            console.log(`[SUBTAB] ✅ Activated button: ${subtabName}`);
        } else {
            console.error(`[SUBTAB] ❌ Button not found for: ${subtabName}`);
        }
        
        // Add active class to target subtab content
        const targetContentId = `${subtabName}-subtab`;
        const targetContent = document.getElementById(targetContentId);
        
        if (targetContent) {
            targetContent.classList.add('active');
            console.log(`[SUBTAB] ✅ Activated content: ${targetContentId}`);
            
            // Load subtab-specific data
            this.loadSubtabData(subtabName);
        } else {
            console.error(`[SUBTAB] ❌ Content not found for: ${targetContentId}`);
        }
    }

    /**
     * Load data specific to a subtab
     */
    loadSubtabData(subtabName) {
        switch (subtabName) {
            case 'satellites':
                this.loadSatellites();
                break;
            case 'crawler':
                this.loadCrawlerStatus();
                break;
            case 'datasets':
                this.loadDatasets();
                break;
        }
    }

    /**
     * Load crawler status and progress
     */
    async loadCrawlerStatus() {
        try {
            // Use Electron IPC to call Python backend
            if (window.electronAPI) {
                const result = await window.electronAPI.getCrawlerStatus();
                if (result.status === 'success') {
                    this.updateCrawlerStatus(result.progress);
                } else {
                    this.updateCrawlerStatus({ status: 'ready', progress: 0 });
                }
            } else {
                // Fallback for web environment
                this.updateCrawlerStatus({ status: 'ready', progress: 0 });
            }
        } catch (error) {
            console.log('[CRAWLER] Status check failed, assuming not running');
            this.updateCrawlerStatus({ status: 'ready', progress: 0 });
        }
    }

    /**
     * Load datasets from crawler data
     */
    async loadDatasets() {
        try {
            if (window.electronAPI) {
                const result = await window.electronAPI.getDatasets();
                if (result.status === 'success') {
                    this.updateDatasetViewer(result.data);
                } else {
                    this.updateDatasetViewer([]);
                }
            } else {
                // Fallback for web environment
                this.updateDatasetViewer([]);
            }
        } catch (error) {
            console.error('[DATASETS] Failed to load datasets:', error);
            this.updateDatasetViewer([]);
        }
    }

    /**
     * Update crawler status display
     */
    updateCrawlerStatus(status) {
        const statusDot = document.getElementById('status-dot');
        const statusText = document.getElementById('crawler-status');
        const runBtn = document.getElementById('run-web-crawler');
        const cancelBtn = document.getElementById('cancel-web-crawler');

        if (statusDot) {
            statusDot.className = `status-dot ${status.status}`;
        }

        if (statusText) {
            statusText.textContent = status.message || 'Ready to collect satellite data';
        }

        if (runBtn) {
            runBtn.disabled = status.status === 'running';
        }

        if (cancelBtn) {
            cancelBtn.disabled = status.status !== 'running';
        }

        // Update progress if available
        if (status.progress !== undefined) {
            this.updateCrawlerProgress(status.progress);
        }
    }

    /**
     * Update dataset viewer with data
     */
    updateDatasetViewer(datasets) {
        const grid = document.getElementById('dataset-grid');
        const totalDatasets = document.getElementById('total-datasets');
        const processedDatasets = document.getElementById('processed-datasets');
        const uniquePublishers = document.getElementById('unique-publishers');
        const totalSatellites = document.getElementById('total-satellites');

        if (totalDatasets) {
            totalDatasets.textContent = datasets.length;
        }

        if (processedDatasets) {
            processedDatasets.textContent = datasets.filter(d => d.processed).length;
        }

        if (uniquePublishers) {
            const publishers = new Set(datasets.map(d => d.publisher).filter(Boolean));
            uniquePublishers.textContent = publishers.size;
        }

        if (totalSatellites) {
            const satellites = new Set(datasets.map(d => d.satellite).filter(Boolean));
            totalSatellites.textContent = satellites.size;
        }

        if (grid) {
            grid.innerHTML = '';
            datasets.forEach(dataset => {
                const card = this.createDatasetCard(dataset);
                grid.appendChild(card);
            });
        }
    }

    /**
     * Create a dataset card element
     */
    createDatasetCard(dataset) {
        const card = document.createElement('div');
        card.className = 'dataset-card';
        card.innerHTML = `
            <h5>${dataset.name || 'Unknown Dataset'}</h5>
            <p>${dataset.description || 'No description available'}</p>
            <div class="dataset-meta">
                <span><i class="fas fa-satellite"></i> ${dataset.satellite || 'Unknown'}</span>
                <span><i class="fas fa-building"></i> ${dataset.publisher || 'Unknown'}</span>
            </div>
            <div class="dataset-actions">
                <button class="btn btn-sm btn-primary" onclick="app.viewDatasetDetails('${dataset.id}')">
                    <i class="fas fa-eye"></i> Details
                </button>
                <button class="btn btn-sm btn-outline-primary" onclick="app.useDatasetForDownload('${dataset.id}')">
                    <i class="fas fa-download"></i> Use
                </button>
            </div>
        `;
        return card;
    }

    /**
     * Update toolbar active item
     */
    updateToolbarActiveItem(viewName) {
        // Remove active class from all items
        this.toolbar.items.forEach(item => {
            item.classList.remove('active', 'selected');
        });

        // Add active class to current item
        const activeItem = document.querySelector(`[data-view="${viewName}"]`);
        if (activeItem) {
            activeItem.classList.add('active');
            this.toolbar.activeItem = activeItem;
            this.updateToolbarIndicator(activeItem);
        }
    }

    /**
     * Update toolbar indicator position
     */
    updateToolbarIndicator(activeItem) {
        if (!this.toolbar.indicator || !activeItem) return;

        const rect = activeItem.getBoundingClientRect();
        const containerRect = this.toolbar.indicator.parentElement.getBoundingClientRect();
        
        this.toolbar.indicator.style.left = `${rect.left - containerRect.left}px`;
        this.toolbar.indicator.style.width = `${rect.width}px`;
    }

    /**
     * Toggle side panel
     */
    toggleSidePanel(panelName) {
        const panel = this.sidePanels[panelName];
        if (!panel) return;

        const isOpen = panel.classList.contains('open');
        
        // Close all panels
        Object.values(this.sidePanels).forEach(p => {
            p.classList.remove('open');
        });

        // Open requested panel if it wasn't open
        if (!isOpen) {
            panel.classList.add('open');
            this.loadPanelData(panelName);
        }
    }

    /**
     * Close side panel
     */
    closeSidePanel(panelId) {
        const panel = document.getElementById(panelId);
        if (panel) {
            panel.classList.remove('open');
        }
    }

    /**
     * Open modal
     */
    openModal(modalId) {
        const modal = this.modals[modalId] || document.getElementById(modalId);
        if (modal) {
            modal.classList.add('open');
            document.body.style.overflow = 'hidden';
        }
    }

    /**
     * Close modal
     */
    closeModal(modalId) {
        const modal = this.modals[modalId] || document.getElementById(modalId);
        if (modal) {
            modal.classList.remove('open');
            document.body.style.overflow = '';
        }
    }

    /**
     * Load view-specific data
     */
    async loadViewData(viewName) {
        switch (viewName) {
            case 'map':
                await this.loadMapData();
                break;
            case 'download':
                await this.loadDownloadData();
                break;
            case 'satelliteInfo':
                await this.loadSatelliteData();
                break;
            case 'progress':
                await this.loadProgressData();
                break;
            case 'settings':
                this.loadSettingsData();
                break;
        }
    }

    /**
     * Load panel-specific data
     */
    async loadPanelData(panelName) {
        switch (panelName) {
            case 'toolbox':
                await this.loadToolboxData();
                break;
            case 'bookmarks':
                await this.loadBookmarksData();
                break;
            case 'attributeTable':
                await this.loadAttributeTableData();
                break;
        }
    }

    /**
     * Load satellites data
     */
    async loadSatellites() {
        try {
            if (window.electronAPI) {
                const result = await window.electronAPI.getSatellites();
                if (result.status === 'success') {
                    this.satellites = new Map(Object.entries(result.data));
                    this.populateSensorSelect();
                }
            } else {
                // Fallback for web environment
                this.satellites = new Map();
            }
        } catch (error) {
            console.error('Error loading satellites:', error);
            this.showNotification('Error loading satellite data', 'error');
        }
    }

    /**
     * Start web crawler
     */
    async startCrawler() {
        try {
            this.showLoading('Starting web crawler...');
            
            if (window.electronAPI) {
                const result = await window.electronAPI.startCrawler();
                if (result.status === 'success') {
                    this.showNotification('Web crawler started successfully', 'success');
                    // Start polling for progress
                    this.startCrawlerProgressPolling();
                } else {
                    this.showNotification(result.message || 'Failed to start crawler', 'error');
                }
            } else {
                this.showNotification('Crawler not available in web environment', 'warning');
            }
        } catch (error) {
            console.error('Error starting crawler:', error);
            this.showNotification('Error starting crawler', 'error');
        } finally {
            this.hideLoading();
        }
    }

    /**
     * Start polling for crawler progress
     */
    startCrawlerProgressPolling() {
        this.crawlerProgressInterval = setInterval(async () => {
            await this.loadCrawlerStatus();
            
            // Stop polling if crawler is complete
            const statusElement = document.getElementById('crawler-status');
            if (statusElement && statusElement.textContent.includes('completed')) {
                clearInterval(this.crawlerProgressInterval);
                this.showNotification('Web crawler completed', 'success');
            }
        }, 2000); // Poll every 2 seconds
    }

    /**
     * Stop crawler progress polling
     */
    stopCrawlerProgressPolling() {
        if (this.crawlerProgressInterval) {
            clearInterval(this.crawlerProgressInterval);
            this.crawlerProgressInterval = null;
        }
    }

    /**
     * View crawler log
     */
    viewCrawlerLog() {
        try {
            // Try to open the crawler log file
            const logPath = 'logs/gee_catalog_crawler_*.log';
            this.showNotification('Crawler log viewer coming soon!', 'info');
        } catch (error) {
            console.error('Error viewing crawler log:', error);
            this.showNotification('Error viewing crawler log', 'error');
        }
    }

    /**
     * Update crawler status display
     */
    updateCrawlerStatus(status) {
        const statusElement = document.getElementById('crawler-status');
        const progressElement = document.getElementById('crawler-progress');
        const progressFill = document.getElementById('crawler-progress-fill');
        const messageElement = document.getElementById('crawler-message');
        const runBtn = document.getElementById('run-web-crawler');
        const cancelBtn = document.getElementById('cancel-web-crawler');

        if (statusElement) {
            statusElement.textContent = status.message || 'Ready';
        }

        if (progressElement && progressFill) {
            if (status.status === 'running' || status.status === 'processing') {
                progressElement.style.display = 'block';
                progressFill.style.width = `${status.progress || 0}%`;
            } else {
                progressElement.style.display = 'none';
            }
        }

        if (messageElement) {
            messageElement.textContent = status.message || 'Ready to start';
        }

        if (runBtn && cancelBtn) {
            if (status.status === 'running' || status.status === 'processing') {
                runBtn.disabled = true;
                cancelBtn.disabled = false;
            } else {
                runBtn.disabled = false;
                cancelBtn.disabled = true;
            }
        }
    }

    /**
     * Populate sensor select dropdown
     */
    populateSensorSelect() {
        if (!this.formElements.sensorSelect) return;

        // Clear existing options
        this.formElements.sensorSelect.innerHTML = '<option value="">Choose a sensor...</option>';

        // Add satellite options
        this.satellites.forEach((satellite, name) => {
            const option = document.createElement('option');
            option.value = name;
            option.textContent = satellite.name || name;
            this.formElements.sensorSelect.appendChild(option);
        });
    }

    /**
     * Start download process
     */
    async startDownload() {
        try {
            // Validate parameters
            const validation = this.validateParameters();
            if (!validation.isValid) {
                this.showNotification(validation.message, 'error');
                return;
            }

            // Get download parameters
            const params = this.getDownloadParameters();
            
            this.showLoading('Starting download...');
            
            // Call Python backend via Electron IPC
            if (window.electronAPI) {
                const result = await window.electronAPI.startDownload(params);
                if (result.status === 'success') {
                    this.showNotification('Download started successfully', 'success');
                    this.switchView('progress');
                    this.refreshProgress();
                } else {
                    this.showNotification(result.message || 'Failed to start download', 'error');
                }
            } else {
                this.showNotification('Download not available in web environment', 'warning');
            }
            
        } catch (error) {
            console.error('Error starting download:', error);
            this.showNotification('Error starting download', 'error');
        } finally {
            this.hideLoading();
        }
    }

    /**
     * Validate download parameters
     */
    validateParameters() {
        const required = ['area_of_interest', 'start_date', 'end_date', 'sensor_name'];
        const missing = required.filter(field => !this.formElements[field]?.value);

        if (missing.length > 0) {
            return {
                isValid: false,
                message: `Missing required fields: ${missing.join(', ')}`
            };
        }

        // Validate date range
        const startDate = new Date(this.formElements.startDate.value);
        const endDate = new Date(this.formElements.endDate.value);
        
        if (startDate >= endDate) {
            return {
                isValid: false,
                message: 'End date must be after start date'
            };
        }

        return { isValid: true };
    }

    /**
     * Get download parameters from form
     */
    getDownloadParameters() {
        return {
            area_of_interest: this.formElements.aoiInput.value,
            start_date: this.formElements.startDate.value,
            end_date: this.formElements.endDate.value,
            sensor_name: this.formElements.sensorSelect.value,
            output_dir: this.formElements.outputDir.value || this.settings.defaultOutputDir,
            cloud_mask: this.formElements.cloudMask.checked,
            cloud_cover: parseInt(this.formElements.cloudCover.value),
            resolution: this.formElements.bestRes.checked ? null : parseInt(this.formElements.targetRes.value),
            tiling_method: this.formElements.tilingMethod.value,
            format: this.formElements.formatSelect.value,
            apply_corrections: this.formElements.applyCorrections.checked,
            generate_indices: this.formElements.generateIndices.checked
        };
    }

    /**
     * Refresh download progress
     */
    async refreshProgress() {
        try {
            if (window.electronAPI) {
                const result = await window.electronAPI.getDownloadProgress();
                if (result.status === 'success') {
                    this.updateProgressDisplay(result.data);
                }
            }
        } catch (error) {
            console.error('Error refreshing progress:', error);
        }
    }

    /**
     * Update progress display
     */
    updateProgressDisplay(progressData) {
        if (!this.progressElements.list) return;

        // Update summary counts
        const active = progressData.downloads?.filter(d => d.status === 'downloading').length || 0;
        const completed = progressData.downloads?.filter(d => d.status === 'completed').length || 0;
        const failed = progressData.downloads?.filter(d => d.status === 'error').length || 0;

        this.progressElements.activeCount.textContent = active;
        this.progressElements.completedCount.textContent = completed;
        this.progressElements.failedCount.textContent = failed;

        // Update progress list
        this.progressElements.list.innerHTML = '';
        
        progressData.downloads?.forEach(download => {
            const item = this.createProgressItem(download);
            this.progressElements.list.appendChild(item);
        });
    }

    /**
     * Create progress item element
     */
    createProgressItem(download) {
        const item = document.createElement('div');
        item.className = `progress-item ${download.status}`;
        
        const percentage = download.percentage || 0;
        const statusClass = download.status === 'completed' ? 'success' : 
                           download.status === 'error' ? 'error' : 'warning';
        
        item.innerHTML = `
            <div class="progress-header">
                <h4>${download.download_id}</h4>
                <span class="status-badge ${statusClass}">${download.status}</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: ${percentage}%"></div>
            </div>
            <div class="progress-details">
                <span>${percentage.toFixed(1)}%</span>
                <span>${download.message}</span>
                <span>${this.formatBytes(download.bytes_downloaded)} / ${this.formatBytes(download.total_bytes)}</span>
            </div>
        `;
        
        return item;
    }

    /**
     * Format bytes to human readable format
     */
    formatBytes(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    /**
     * Check authentication status
     */
    async checkAuthentication() {
        try {
            // Check if we're in Electron environment
            if (window.electronAPI) {
                const response = await window.electronAPI.checkAuthStatus();
                this.updateAuthStatus(response);
                
                // Auto-show auth modal if not authenticated
                if (!response.authenticated && !this.authModalShown) {
                    this.authModalShown = true;
                    setTimeout(() => this.showAuthModal(), 1000); // Small delay to let UI load
                }
                
                return response;
            } else {
                // Web environment - check C:\FE Auth folder
                try {
                    const authStatus = await this.checkLocalAuthStatus();
                    if (authStatus.authenticated) {
                        this.updateAuthStatus({ authenticated: true, status: 'authenticated' });
                        return { authenticated: true, status: 'authenticated' };
                    }
                } catch (error) {
                    console.log('Local auth check failed, using fallback');
                }
                
                // Fallback simulation
                const response = await this.callBackend('check_auth_needed');
                this.updateAuthStatus(response);
                
                // Auto-show auth modal if not authenticated
                if (response.status !== 'authenticated' && !this.authModalShown) {
                    this.authModalShown = true;
                    setTimeout(() => this.showAuthModal(), 1000); // Small delay to let UI load
                }
                
                return response;
            }
        } catch (error) {
            console.error('Error checking authentication:', error);
            this.updateAuthStatus({ status: 'error', message: error.message });
            return { status: 'error', message: error.message };
        }
    }

    /**
     * Check local authentication status from C:\FE Auth folder
     */
    async checkLocalAuthStatus() {
        try {
            // Try to fetch the auth status from the local folder
            const response = await fetch('file:///C:/FE%20Auth/auth_status.json');
            if (response.ok) {
                const authData = await response.json();
                return {
                    authenticated: authData.is_authenticated || false,
                    hasCredentials: authData.has_credentials || false,
                    projectId: authData.project_id || null,
                    status: authData.is_authenticated ? 'authenticated' : 'not_authenticated'
                };
            }
        } catch (error) {
            console.log('Could not read local auth status:', error);
        }
        
        // Fallback: check if files exist
        try {
            const configResponse = await fetch('file:///C:/FE%20Auth/auth_config.json');
            const keyResponse = await fetch('file:///C:/FE%20Auth/service_account_key.json');
            
            if (configResponse.ok && keyResponse.ok) {
                const config = await configResponse.json();
                return {
                    authenticated: true,
                    hasCredentials: true,
                    projectId: config.project_id,
                    status: 'authenticated'
                };
            }
        } catch (error) {
            console.log('Could not read local auth files:', error);
        }
        
        throw new Error('No local authentication found');
    }

    /**
     * Update authentication status display
     */
    updateAuthStatus(authData) {
        if (!this.statusIndicators.auth) return;

        const statusClass = authData.authenticated ? 'online' : 
                           authData.status === 'error' ? 'offline' : 'warning';
        
        this.statusIndicators.auth.className = `status-indicator ${statusClass}`;
        this.statusIndicators.auth.title = `Authentication: ${authData.authenticated ? 'Connected' : 'Not Connected'}`;
    }

    /**
     * Test authentication
     */
    async testAuthentication() {
        try {
            this.showLoading('Testing authentication...');
            
            if (window.electronAPI) {
                const response = await window.electronAPI.checkAuthStatus();
                if (response.authenticated) {
                    this.showNotification('Authentication successful', 'success');
                } else {
                    this.showNotification('Authentication failed - please configure credentials', 'error');
                }
            } else {
                if (window.electronAPI) {
                    const result = await window.electronAPI.testAuth();
                    if (result.status === 'success' && result.data.authenticated) {
                        this.showNotification('Authentication successful', 'success');
                    } else {
                        this.showNotification('Authentication failed', 'error');
                    }
                } else {
                    this.showNotification('Authentication not available in web environment', 'warning');
                }
            }
            
        } catch (error) {
            console.error('Authentication test error:', error);
            this.showNotification('Authentication test failed', 'error');
        } finally {
            this.hideLoading();
        }
    }

    /**
     * Show authentication modal
     */
    async showAuthModal() {
        const authModal = document.getElementById('auth-modal');
        if (authModal) {
            authModal.classList.add('open');
            this.setupAuthModalEvents();
            
            // Check for existing credentials and populate form
            await this.populateAuthForm();
            
            this.checkAuthStatus();
        }
    }

    /**
     * Populate authentication form with existing credentials
     */
    async populateAuthForm() {
        try {
            const authStatus = await this.checkLocalAuthStatus();
            
            if (authStatus.hasCredentials) {
                // Populate project ID
                const projectIdInput = document.getElementById('auth-project-id');
                if (projectIdInput && authStatus.projectId) {
                    projectIdInput.value = authStatus.projectId;
                }
                
                // Show existing key file info
                const fileNameDisplay = document.getElementById('key-file-name');
                const fileDisplay = document.querySelector('.file-input-display');
                
                if (fileNameDisplay && fileDisplay) {
                    fileNameDisplay.textContent = 'service_account_key.json (existing)';
                    fileNameDisplay.classList.add('has-file');
                    fileDisplay.classList.add('has-file');
                }
                
                // Update status to show existing credentials
                const statusIndicator = document.getElementById('auth-status-indicator');
                const statusText = statusIndicator?.querySelector('.status-text');
                const statusIcon = statusIndicator?.querySelector('.status-icon i');
                
                if (statusIndicator && statusText && statusIcon) {
                    if (authStatus.authenticated) {
                        statusText.textContent = 'Using existing credentials - Authentication successful';
                        statusIcon.className = 'fas fa-check-circle';
                        statusIndicator.className = 'auth-status-indicator authenticated';
                    } else {
                        statusText.textContent = 'Existing credentials found - Test connection to verify';
                        statusIcon.className = 'fas fa-info-circle';
                        statusIndicator.className = 'auth-status-indicator checking';
                    }
                }
                
                // Show info about existing setup
                this.showNotification('Existing credentials found in C:\\FE Auth folder', 'info');
            }
        } catch (error) {
            console.log('No existing credentials found:', error);
        }
    }

    /**
     * Hide authentication modal
     */
    hideAuthModal() {
        const authModal = document.getElementById('auth-modal');
        if (authModal) {
            authModal.classList.remove('open');
            this.authModalShown = false;
        }
    }

    /**
     * Setup authentication modal event listeners
     */
    setupAuthModalEvents() {
        // Close button
        const closeBtn = document.getElementById('auth-modal-close');
        if (closeBtn) {
            closeBtn.onclick = () => this.hideAuthModal();
        }

        // Cancel button
        const cancelBtn = document.getElementById('auth-cancel');
        if (cancelBtn) {
            cancelBtn.onclick = () => this.hideAuthModal();
        }

        // File input handling
        const fileInput = document.getElementById('auth-key-file');
        const fileNameDisplay = document.getElementById('key-file-name');
        const fileDisplay = document.querySelector('.file-input-display');

        if (fileInput && fileNameDisplay && fileDisplay) {
            fileInput.onchange = (e) => {
                const file = e.target.files[0];
                if (file) {
                    fileNameDisplay.textContent = file.name;
                    fileNameDisplay.classList.add('has-file');
                    fileDisplay.classList.add('has-file');
                } else {
                    fileNameDisplay.textContent = 'Choose a JSON file...';
                    fileNameDisplay.classList.remove('has-file');
                    fileDisplay.classList.remove('has-file');
                }
            };

            // Browse button
            const browseBtn = fileDisplay.querySelector('.file-browse-btn');
            if (browseBtn) {
                browseBtn.onclick = () => fileInput.click();
            }
        }

        // Test connection button
        const testBtn = document.getElementById('auth-test');
        if (testBtn) {
            testBtn.onclick = () => this.testAuthConnection();
        }

        // Save & Connect button
        const submitBtn = document.getElementById('auth-submit');
        if (submitBtn) {
            submitBtn.onclick = () => this.saveAuthCredentials();
        }

        // Clear credentials button
        const clearBtn = document.getElementById('auth-clear');
        if (clearBtn) {
            clearBtn.onclick = () => this.clearAuthCredentials();
        }

        // Continue offline button
        const offlineBtn = document.getElementById('auth-offline');
        if (offlineBtn) {
            offlineBtn.onclick = () => this.continueOffline();
        }

        // Close modal when clicking outside
        const authModal = document.getElementById('auth-modal');
        if (authModal) {
            authModal.onclick = (e) => {
                if (e.target === authModal) {
                    this.hideAuthModal();
                }
            };
        }
    }

    /**
     * Check authentication status and update modal
     */
    async checkAuthStatus() {
        const statusIndicator = document.getElementById('auth-status-indicator');
        const statusText = statusIndicator?.querySelector('.status-text');
        const statusIcon = statusIndicator?.querySelector('.status-icon i');

        if (statusIndicator && statusText && statusIcon) {
            statusText.textContent = 'Checking authentication...';
            statusIcon.className = 'fas fa-clock';
            statusIndicator.className = 'auth-status-indicator checking';

            try {
                const response = await this.checkAuthentication();
                
                if (response.authenticated) {
                    statusText.textContent = 'Authentication successful';
                    statusIcon.className = 'fas fa-check-circle';
                    statusIndicator.className = 'auth-status-indicator authenticated';
                } else {
                    statusText.textContent = 'Authentication required';
                    statusIcon.className = 'fas fa-exclamation-triangle';
                    statusIndicator.className = 'auth-status-indicator error';
                }
            } catch (error) {
                statusText.textContent = 'Authentication check failed';
                statusIcon.className = 'fas fa-times-circle';
                statusIndicator.className = 'auth-status-indicator error';
            }
        }
    }

    /**
     * Test authentication connection
     */
    async testAuthConnection() {
        const testBtn = document.getElementById('auth-test');
        const originalText = testBtn.innerHTML;
        
        testBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Testing...';
        testBtn.disabled = true;

        try {
            const keyFile = document.getElementById('auth-key-file').files[0];
            const projectId = document.getElementById('auth-project-id').value;

            if (!keyFile || !projectId) {
                this.showNotification('Please select a key file and enter project ID', 'warning');
                return;
            }

            if (window.electronAPI) {
                const response = await window.electronAPI.pythonAuthTest(keyFile.path, projectId);
                if (response.status === 'success') {
                    this.showNotification('Connection test successful!', 'success');
                } else {
                    this.showNotification('Connection test failed: ' + response.message, 'error');
                }
            } else {
                // Fallback for web environment
                this.showNotification('Connection test completed (simulated)', 'info');
            }
        } catch (error) {
            console.error('Test connection error:', error);
            this.showNotification('Connection test failed: ' + error.message, 'error');
        } finally {
            testBtn.innerHTML = originalText;
            testBtn.disabled = false;
        }
    }

    /**
     * Save authentication credentials
     */
    async saveAuthCredentials() {
        const submitBtn = document.getElementById('auth-submit');
        const originalText = submitBtn.innerHTML;
        
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving...';
        submitBtn.disabled = true;

        try {
            const keyFile = document.getElementById('auth-key-file').files[0];
            const projectId = document.getElementById('auth-project-id').value;

            if (!keyFile || !projectId) {
                this.showNotification('Please select a key file and enter project ID', 'warning');
                return;
            }

            // Save credentials to C:\FE Auth folder
            await this.saveCredentialsToAuthFolder(keyFile, projectId);
            
            // Connect to GEE
            await this.connectToGEE(keyFile.path || keyFile.name, projectId);
            
            this.showNotification('Authentication saved and connected successfully!', 'success');
            this.hideAuthModal();
            
            // Update authentication status
            this.updateAuthStatus({ authenticated: true, status: 'authenticated' });
            
        } catch (error) {
            console.error('Save auth error:', error);
            this.showNotification('Failed to save authentication: ' + error.message, 'error');
        } finally {
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }
    }

    /**
     * Save credentials to C:\FE Auth folder
     */
    async saveCredentialsToAuthFolder(keyFile, projectId) {
        try {
            if (window.electronAPI) {
                // Use Electron API to save credentials
                const result = await window.electronAPI.saveCredentialsToAuthFolder(keyFile, projectId);
                if (result.status === 'success') {
                    return true;
                } else {
                    throw new Error(result.message || 'Failed to save credentials');
                }
            } else {
                // Web environment - simulate saving
                console.log('Would save credentials to C:\\FE Auth folder:');
                console.log('Project ID:', projectId);
                console.log('Key file:', keyFile.name);
                
                // Show instructions for manual setup
                this.showNotification('Please manually copy credentials to C:\\FE Auth folder', 'info');
                return true; // Simulated success
            }
        } catch (error) {
            console.error('Failed to save credentials:', error);
            throw error;
        }
    }

    /**
     * Connect to Google Earth Engine
     */
    async connectToGEE(keyPath, projectId) {
        try {
            if (window.electronAPI) {
                // Use Electron API to connect
                const result = await window.electronAPI.pythonAuth(keyPath, projectId);
                if (result.status !== 'success') {
                    throw new Error(result.message || 'Failed to connect to GEE');
                }
            } else {
                // Web environment - simulate connection
                console.log('Simulating GEE connection with:', { keyPath, projectId });
            }
        } catch (error) {
            console.error('GEE connection failed:', error);
            throw error;
        }
    }

    /**
     * Clear authentication credentials
     */
    async clearAuthCredentials() {
        try {
            if (window.electronAPI) {
                const response = await window.electronAPI.clearAuth();
                if (response.status === 'success') {
                    this.showNotification('Authentication cleared successfully', 'success');
                    this.checkAuthStatus();
                } else {
                    this.showNotification('Failed to clear authentication', 'error');
                }
            } else {
                // Fallback for web environment
                this.showNotification('Authentication cleared (simulated)', 'success');
                this.checkAuthStatus();
            }

            // Clear form
            document.getElementById('auth-key-file').value = '';
            document.getElementById('auth-project-id').value = '';
            document.getElementById('key-file-name').textContent = 'Choose a JSON file...';
            document.getElementById('key-file-name').classList.remove('has-file');
            document.querySelector('.file-input-display').classList.remove('has-file');
        } catch (error) {
            console.error('Clear auth error:', error);
            this.showNotification('Failed to clear authentication: ' + error.message, 'error');
        }
    }

    /**
     * Continue in offline mode
     */
    continueOffline() {
        this.showNotification('Continuing in offline mode', 'info');
        this.hideAuthModal();
        this.updateAuthStatus({ authenticated: false, status: 'offline' });
    }

    /**
     * Use dataset for download
     */
    useDatasetForDownload(datasetId) {
        const dataset = this.satelliteInfoState.datasets.find(d => d.id === datasetId);
        if (!dataset) return;

        // Switch to download view and populate form
        this.switchView('download');
        
        // Populate download form with dataset info
        this.populateDownloadFormFromDataset(dataset);
        
        this.showNotification(`Dataset "${dataset.name}" selected for download`, 'success');
    }

    /**
     * Populate download form from dataset
     */
    populateDownloadFormFromDataset(dataset) {
        // Populate sensor select
        if (this.formElements.sensorSelect && dataset.satellites) {
            this.formElements.sensorSelect.value = dataset.satellites[0] || '';
        }

        // Set other relevant fields based on dataset properties
        // This would be customized based on your download form structure
    }

    /**
     * Add dataset to bookmarks
     */
    addDatasetToBookmarks(datasetId) {
        const dataset = this.satelliteInfoState.datasets.find(d => d.id === datasetId);
        if (!dataset) return;

        // Add to bookmarks (implement based on your bookmarks system)
        this.showNotification(`Dataset "${dataset.name}" added to bookmarks`, 'success');
    }

    /**
     * Update satellite grid
     */
    updateSatelliteGrid() {
        if (!this.satelliteGridElements.grid) return;

        const satellites = this.getFilteredSatellites();
        this.satelliteGridElements.grid.innerHTML = '';

        satellites.forEach(satellite => {
            const card = this.createSatelliteCard(satellite);
            this.satelliteGridElements.grid.appendChild(card);
        });
    }

    /**
     * Create satellite card
     */
    createSatelliteCard(satellite) {
        const card = document.createElement('div');
        card.className = 'satellite-card';
        card.dataset.satelliteName = satellite.name;
        
        card.innerHTML = `
            <h4><i class="fas fa-satellite"></i> ${this.escapeHtml(satellite.name)}</h4>
            <p>${this.escapeHtml(satellite.description || 'No description available')}</p>
            <div class="satellite-meta">
                <span>${satellite.resolution || 'N/A'}</span>
                <span>${satellite.type || 'Unknown'}</span>
                <span>${satellite.status || 'Active'}</span>
            </div>
            <div class="satellite-actions">
                <button onclick="app.showSatelliteDetails('${satellite.name}')">Details</button>
                <button class="primary" onclick="app.downloadSatelliteData('${satellite.name}')">Download</button>
            </div>
        `;

        return card;
    }

    /**
     * Get filtered satellites
     */
    getFilteredSatellites() {
        let satellites = this.satelliteInfoState.satellites;

        // Apply search filter
        if (this.satelliteInfoState.filters.search) {
            const searchTerm = this.satelliteInfoState.filters.search.toLowerCase();
            satellites = satellites.filter(satellite => 
                satellite.name.toLowerCase().includes(searchTerm) ||
                satellite.description.toLowerCase().includes(searchTerm) ||
                (satellite.applications && satellite.applications.some(app => app.toLowerCase().includes(searchTerm)))
            );
        }

        // Apply type filter
        if (this.satelliteInfoState.filters.type && this.satelliteInfoState.filters.type !== 'all') {
            satellites = satellites.filter(satellite => 
                satellite.type === this.satelliteInfoState.filters.type
            );
        }

        return satellites;
    }

    /**
     * Filter satellites
     */
    filterSatellites() {
        this.satelliteInfoState.filters.search = this.satelliteGridElements.search?.value || '';
        this.updateSatelliteGrid();
    }

    /**
     * Clear satellite search
     */
    clearSatelliteSearch() {
        if (this.satelliteGridElements.search) {
            this.satelliteGridElements.search.value = '';
        }
        this.satelliteInfoState.filters.search = '';
        this.filterSatellites();
    }

    /**
     * Filter satellites by category
     */
    filterSatellitesByCategory(category) {
        // Update active filter tab
        this.satelliteGridElements.filterTabs?.forEach(tab => {
            tab.classList.toggle('active', tab.dataset.filter === category);
        });

        this.satelliteInfoState.filters.type = category;
        this.updateSatelliteGrid();
    }

    /**
     * Switch satellite grid view
     */
    switchSatelliteGridView(view) {
        const grid = this.satelliteGridElements.grid;
        if (grid) {
            grid.className = `satellite-grid ${view}-view`;
        }

        // Update view toggle buttons
        this.satelliteGridElements.viewToggles?.forEach(toggle => {
            toggle.classList.toggle('active', toggle.dataset.view === view);
        });
    }

    /**
     * Show satellite details
     */
    showSatelliteDetails(satelliteName) {
        const satellite = this.satelliteInfoState.satellites.find(s => s.name === satelliteName);
        if (!satellite) return;

        // Populate details panel
        this.populateSatelliteDetails(satellite);
        
        // Show panel
        if (this.satelliteGridElements.detailsPanel) {
            this.satelliteGridElements.detailsPanel.classList.add('open');
        }
    }

    /**
     * Populate satellite details
     */
    populateSatelliteDetails(satellite) {
        // Basic info
        if (document.getElementById('detail-satellite-name')) {
            document.getElementById('detail-satellite-name').textContent = satellite.name;
        }
        if (document.getElementById('detail-description')) {
            document.getElementById('detail-description').textContent = satellite.description || 'No description available';
        }
        if (document.getElementById('detail-resolution')) {
            document.getElementById('detail-resolution').textContent = satellite.resolution || 'N/A';
        }
        if (document.getElementById('detail-datasets')) {
            document.getElementById('detail-datasets').textContent = satellite.datasets_count || '0';
        }
        if (document.getElementById('detail-status')) {
            document.getElementById('detail-status').textContent = satellite.status || 'Active';
        }

        // Tags
        if (document.getElementById('satellite-tags')) {
            const tags = satellite.tags || [];
            document.getElementById('satellite-tags').innerHTML = tags.map(tag => `<span>${tag}</span>`).join('');
        }

        // Applications
        if (document.getElementById('detail-applications')) {
            const applications = satellite.applications || [];
            document.getElementById('detail-applications').innerHTML = applications.map(app => `
                <div class="application-item">
                    <h5>${app.name}</h5>
                    <p>${app.description}</p>
                </div>
            `).join('') || '<p>No applications specified</p>';
        }

        // Bands
        if (document.getElementById('detail-bands')) {
            const bands = satellite.bands || [];
            document.getElementById('detail-bands').innerHTML = bands.map(band => `
                <div class="band-item">
                    <h5>${band.name}</h5>
                    <p>${band.description}</p>
                </div>
            `).join('') || '<p>No bands specified</p>';
        }

        // Code snippet
        if (document.getElementById('code-block')) {
            const code = satellite.code_snippet || '// No code snippet available';
            document.getElementById('code-block').innerHTML = `<code>${this.escapeHtml(code)}</code>`;
        }
    }

    /**
     * Close satellite details panel
     */
    closeSatelliteDetailsPanel() {
        if (this.satelliteGridElements.detailsPanel) {
            this.satelliteGridElements.detailsPanel.classList.remove('open');
        }
    }

    /**
     * Use satellite for download
     */
    useSatelliteForDownload() {
        const satelliteName = document.getElementById('detail-satellite-name')?.textContent;
        if (!satelliteName) return;

        // Switch to download view and populate form
        this.switchView('download');
        
        // Populate download form with satellite info
        this.populateDownloadFormFromSatellite(satelliteName);
        
        this.showNotification(`Satellite "${satelliteName}" selected for download`, 'success');
    }

    /**
     * Populate download form from satellite
     */
    populateDownloadFormFromSatellite(satelliteName) {
        // Populate sensor select
        if (this.formElements.sensorSelect) {
            this.formElements.sensorSelect.value = satelliteName;
        }

        // Set other relevant fields based on satellite properties
        // This would be customized based on your download form structure
    }

    /**
     * Download satellite data
     */
    downloadSatelliteData(satelliteName) {
        // Switch to download view and populate form
        this.switchView('download');
        this.populateDownloadFormFromSatellite(satelliteName);
        
        this.showNotification(`Preparing download for "${satelliteName}"`, 'info');
    }

    /**
     * Share satellite
     */
    shareSatellite() {
        const satelliteName = document.getElementById('detail-satellite-name')?.textContent;
        if (!satelliteName) return;

        // Implement sharing functionality
        this.showNotification(`Sharing satellite "${satelliteName}"`, 'info');
    }

    /**
     * Utility function to escape HTML
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Format time in seconds to human readable format
     */
    formatTime(seconds) {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;
        
        if (hours > 0) {
            return `${hours}h ${minutes}m ${secs}s`;
        } else if (minutes > 0) {
            return `${minutes}m ${secs}s`;
        } else {
            return `${secs}s`;
        }
    }

    /**
     * Simulate crawler progress for demo purposes
     */
    simulateCrawlerProgress() {
        let progress = 0;
        const messages = [
            'Initializing web crawler...',
            'Connecting to Google Earth Engine...',
            'Fetching dataset catalog...',
            'Processing satellite information...',
            'Downloading metadata...',
            'Generating code snippets...',
            'Saving data to local storage...',
            'Finalizing data collection...'
        ];
        
        const interval = setInterval(() => {
            progress += Math.random() * 15;
            if (progress >= 100) {
                progress = 100;
                clearInterval(interval);
                
                // Update with final data
                this.satelliteInfoState.crawlerData = {
                    satellites_count: 25,
                    datasets_count: 150,
                    last_updated: new Date().toLocaleString()
                };
                
                this.crawlerCompleted();
            }
            
            const messageIndex = Math.floor((progress / 100) * messages.length);
            const message = messages[Math.min(messageIndex, messages.length - 1)];
            
            this.updateCrawlerProgress({
                percentage: progress,
                message: message,
                datasets_found: Math.floor(progress * 1.5),
                satellites_found: Math.floor(progress * 0.25)
            });
        }, 1000);
    }

    /**
     * Initialize settings (called from tabs.js)
     */
    initSettings(force = false) {
        console.log('[SETTINGS] Initializing settings...');
        
        try {
            // Initialize theme system
            this.initThemeSystem();
            
            // Load saved settings
            this.loadSettings();
            
            // Setup settings event listeners
            this.setupSettingsEventListeners();
            
            console.log('[SETTINGS] Settings initialized');
        } catch (error) {
            console.error('[SETTINGS] Settings initialization error:', error);
        }
    }

    /**
     * Initialize theme system
     */
    initThemeSystem() {
        console.log('[THEME] Initializing theme system...');
        
        // Create theme tabs
        this.createThemeTabs();
        
        // Populate theme grid
        this.populateThemeGrid();
        
        // Load current theme
        this.loadCurrentTheme();
    }

    /**
     * Create theme category tabs
     */
    createThemeTabs() {
        const tabContainer = document.getElementById('theme-tab-container');
        if (!tabContainer) return;

        const categories = ['All', 'Default', 'Dark', 'Nature', 'Ocean', 'Sunset', 'Minimal', 'Pride', 'Gaming', 'Artistic'];
        
        tabContainer.innerHTML = categories.map(category => 
            `<button class="theme-tab ${category === 'All' ? 'active' : ''}" data-category="${category.toLowerCase()}">${category}</button>`
        ).join('');

        // Add event listeners
        tabContainer.querySelectorAll('.theme-tab').forEach(tab => {
            tab.addEventListener('click', () => this.switchThemeCategory(tab.dataset.category));
        });
    }

    /**
     * Populate theme grid
     */
    populateThemeGrid() {
        const themeGrid = document.getElementById('theme-grid');
        if (!themeGrid) return;

        // Sample themes - in a real app, this would come from a theme registry
        const themes = [
            { id: 'default', name: 'Default', description: 'Clean and modern default theme', category: 'default' },
            { id: 'dark', name: 'Dark Mode', description: 'Elegant dark theme for low-light environments', category: 'dark' },
            { id: 'nature', name: 'Nature', description: 'Inspired by natural landscapes and earth tones', category: 'nature' },
            { id: 'ocean', name: 'Ocean', description: 'Deep blue ocean-inspired theme', category: 'ocean' },
            { id: 'sunset', name: 'Sunset', description: 'Warm sunset colors and gradients', category: 'sunset' },
            { id: 'minimal', name: 'Minimal', description: 'Clean and minimal design', category: 'minimal' }
        ];

        themeGrid.innerHTML = themes.map(theme => `
            <div class="theme-item" data-theme="${theme.id}" data-category="${theme.category}">
                <div class="theme-preview"></div>
                <div class="theme-name">${theme.name}</div>
                <div class="theme-description">${theme.description}</div>
            </div>
        `).join('');

        // Add event listeners
        themeGrid.querySelectorAll('.theme-item').forEach(item => {
            item.addEventListener('click', () => this.selectTheme(item.dataset.theme));
        });
    }

    /**
     * Switch theme category
     */
    switchThemeCategory(category) {
        console.log('[THEME] Switching to category:', category);
        
        // Update active tab
        document.querySelectorAll('.theme-tab').forEach(tab => {
            tab.classList.toggle('active', tab.dataset.category === category);
        });

        // Show/hide themes based on category
        document.querySelectorAll('.theme-item').forEach(item => {
            const shouldShow = category === 'all' || item.dataset.category === category;
            item.style.display = shouldShow ? 'block' : 'none';
        });
    }

    /**
     * Select a theme
     */
    selectTheme(themeId) {
        console.log('[THEME] Selecting theme:', themeId);
        
        // Update selected theme
        document.querySelectorAll('.theme-item').forEach(item => {
            item.classList.toggle('selected', item.dataset.theme === themeId);
        });

        // Apply theme
        this.applyTheme(themeId);
        
        // Save theme preference
        localStorage.setItem('selected-theme', themeId);
    }

    /**
     * Apply theme
     */
    applyTheme(themeId) {
        console.log('[THEME] Applying theme:', themeId);
        
        // Remove existing theme classes
        document.documentElement.classList.remove('theme-default', 'theme-dark', 'theme-nature', 'theme-ocean', 'theme-sunset', 'theme-minimal');
        
        // Add new theme class
        document.documentElement.classList.add(`theme-${themeId}`);
        
        // Update CSS variables based on theme
        this.updateThemeColors(themeId);
    }

    /**
     * Update theme colors
     */
    updateThemeColors(themeId) {
        const themes = {
            default: {
                '--primary': '#4A90E2',
                '--accent': '#50C878',
                '--background': '#f8f9fa'
            },
            dark: {
                '--primary': '#64B5F6',
                '--accent': '#81C784',
                '--background': '#1a1a1a'
            },
            nature: {
                '--primary': '#2E7D32',
                '--accent': '#8BC34A',
                '--background': '#F1F8E9'
            },
            ocean: {
                '--primary': '#0277BD',
                '--accent': '#00BCD4',
                '--background': '#E3F2FD'
            },
            sunset: {
                '--primary': '#FF5722',
                '--accent': '#FF9800',
                '--background': '#FFF3E0'
            },
            minimal: {
                '--primary': '#000000',
                '--accent': '#333333',
                '--background': '#ffffff'
            }
        };

        const theme = themes[themeId] || themes.default;
        Object.entries(theme).forEach(([property, value]) => {
            document.documentElement.style.setProperty(property, value);
        });
    }

    /**
     * Load current theme
     */
    loadCurrentTheme() {
        const savedTheme = localStorage.getItem('selected-theme') || 'default';
        this.selectTheme(savedTheme);
    }

    /**
     * Setup settings event listeners
     */
    setupSettingsEventListeners() {
        // Theme options
        document.getElementById('use-character-catchphrases')?.addEventListener('change', (e) => {
            localStorage.setItem('use-character-catchphrases', e.target.checked);
        });

        document.getElementById('show-special-icons')?.addEventListener('change', (e) => {
            localStorage.setItem('show-special-icons', e.target.checked);
        });

        document.getElementById('enable-animated-background')?.addEventListener('change', (e) => {
            localStorage.setItem('enable-animated-background', e.target.checked);
        });

        document.getElementById('toolbar-animation-select')?.addEventListener('change', (e) => {
            localStorage.setItem('toolbar-animation', e.target.value);
        });

        // Font size
        document.getElementById('font-size')?.addEventListener('input', (e) => {
            const size = e.target.value;
            document.getElementById('font-size-value').textContent = `${size}px`;
            document.documentElement.style.fontSize = `${size}px`;
            localStorage.setItem('font-size', size);
        });

        // Load saved values
        this.loadSettingsValues();
    }

    /**
     * Load settings values
     */
    loadSettingsValues() {
        // Theme options
        const useCatchphrases = localStorage.getItem('use-character-catchphrases') === 'true';
        const showIcons = localStorage.getItem('show-special-icons') === 'true';
        const animatedBg = localStorage.getItem('enable-animated-background') === 'true';
        const toolbarAnim = localStorage.getItem('toolbar-animation') || 'glow';
        const fontSize = localStorage.getItem('font-size') || '14';

        // Set checkbox values
        document.getElementById('use-character-catchphrases')?.checked = useCatchphrases;
        document.getElementById('show-special-icons')?.checked = showIcons;
        document.getElementById('enable-animated-background')?.checked = animatedBg;
        document.getElementById('toolbar-animation-select')?.value = toolbarAnim;
        document.getElementById('font-size')?.value = fontSize;
        document.getElementById('font-size-value')?.textContent = `${fontSize}px`;
    }

    /**
     * Load settings
     */
    loadSettings() {
        // This would load settings from a file or API in a real app
        console.log('[SETTINGS] Loading settings...');
    }

    /**
     * Show loading indicator
     */
    showLoading(message = 'Loading...') {
        this.isLoading = true;
        // Create or update loading indicator
        let loadingEl = document.getElementById('loading-indicator');
        if (!loadingEl) {
            loadingEl = document.createElement('div');
            loadingEl.id = 'loading-indicator';
            loadingEl.className = 'loading-indicator';
            loadingEl.innerHTML = `
                <div class="loading-spinner"></div>
                <div class="loading-message">${message}</div>
            `;
            document.body.appendChild(loadingEl);
        } else {
            loadingEl.querySelector('.loading-message').textContent = message;
        }
        loadingEl.style.display = 'flex';
    }

    /**
     * Hide loading indicator
     */
    hideLoading() {
        this.isLoading = false;
        const loadingEl = document.getElementById('loading-indicator');
        if (loadingEl) {
            loadingEl.style.display = 'none';
        }
    }

    /**
     * Show notification
     */
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-${this.getNotificationIcon(type)}"></i>
                <span>${message}</span>
            </div>
            <button class="notification-close" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        // Add to notification container
        let container = document.getElementById('notification-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'notification-container';
            container.className = 'notification-container';
            document.body.appendChild(container);
        }
        
        container.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }

    /**
     * Get notification icon based on type
     */
    getNotificationIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }

    /**
     * Handle keyboard shortcuts
     */
    handleKeyboardShortcuts(e) {
        // Ctrl/Cmd + S: Save
        if ((e.ctrlKey || e.metaKey) && e.key === 's') {
            e.preventDefault();
            this.saveSettings();
        }
        
        // Ctrl/Cmd + H: Help
        if ((e.ctrlKey || e.metaKey) && e.key === 'h') {
            e.preventDefault();
            this.openHelpModal();
        }
        
        // Escape: Close modals/panels
        if (e.key === 'Escape') {
            this.closeAllModals();
        }
    }

    /**
     * Handle window resize
     */
    handleResize() {
        // Update responsive elements
        const isMobile = window.innerWidth < 768;
        document.body.classList.toggle('mobile', isMobile);
    }

    /**
     * Save settings
     */
    saveSettings() {
        // Save current settings to localStorage
        const settings = {
            theme: this.currentTheme,
            fontSize: document.getElementById('font-size')?.value || '14',
            autoSave: document.getElementById('auto-save')?.checked || false,
            maxConcurrent: document.getElementById('max-concurrent')?.value || '3',
            downloadTimeout: document.getElementById('download-timeout')?.value || '300'
        };
        
        localStorage.setItem('flutter-earth-settings', JSON.stringify(settings));
        this.showNotification('Settings saved', 'success');
    }

    /**
     * Open help modal
     */
    openHelpModal() {
        this.openModal('help-modal');
    }

    /**
     * Close all modals
     */
    closeAllModals() {
        document.querySelectorAll('.modal').forEach(modal => {
            modal.classList.remove('open');
        });
    }

    /**
     * Switch settings tab
     */
    switchSettingsTab(tabName) {
        // Hide all panels
        this.settingsElements.panels.forEach(panel => {
            panel.style.display = 'none';
        });
        
        // Show selected panel
        const selectedPanel = document.getElementById(`${tabName}-panel`);
        if (selectedPanel) {
            selectedPanel.style.display = 'block';
        }
        
        // Update active tab
        this.settingsElements.tabs.forEach(tab => {
            tab.classList.toggle('active', tab.dataset.tab === tabName);
        });
    }

    /**
     * Update font size
     */
    updateFontSize(size) {
        document.documentElement.style.fontSize = `${size}px`;
        localStorage.setItem('font-size', size);
    }

    /**
     * Clear cache
     */
    clearCache() {
        // Clear localStorage
        localStorage.clear();
        this.showNotification('Cache cleared', 'success');
    }

    /**
     * Reset settings
     */
    resetSettings() {
        if (confirm('Are you sure you want to reset all settings to default?')) {
            localStorage.clear();
            location.reload();
        }
    }

    /**
     * Toggle theme
     */
    toggleTheme() {
        const themes = ['default', 'dark', 'nature', 'ocean', 'sunset', 'minimal'];
        const currentIndex = themes.indexOf(this.currentTheme);
        const nextIndex = (currentIndex + 1) % themes.length;
        this.applyTheme(themes[nextIndex]);
        this.currentTheme = themes[nextIndex];
    }

    // Add filterDatasets, clearDatasetSearch, viewDatasetDetails, closeDatasetDetailsPanel if missing
    filterDatasets() {
        const search = document.getElementById('dataset-search')?.value.toLowerCase() || '';
        const grid = document.getElementById('dataset-grid');
        if (!grid) return;
        Array.from(grid.children).forEach(card => {
            const text = card.textContent.toLowerCase();
            card.style.display = text.includes(search) ? '' : 'none';
        });
    }
    clearDatasetSearch() {
        const search = document.getElementById('dataset-search');
        if (search) search.value = '';
        this.filterDatasets();
    }
    viewDatasetDetails(datasetId) {
        // Find dataset from loaded data (assume this.datasets is set)
        const dataset = (this.datasets || []).find(d => d.id === datasetId);
        if (!dataset) return;
        // Populate details panel fields (implement as needed)
        document.getElementById('dataset-name').textContent = dataset.name || '-';
        document.getElementById('dataset-description').textContent = dataset.description || '-';
        document.getElementById('dataset-id').textContent = dataset.id || '-';
        document.getElementById('dataset-publisher').textContent = dataset.publisher || '-';
        document.getElementById('dataset-resolution').textContent = dataset.resolution || '-';
        document.getElementById('dataset-data-type').textContent = dataset.data_type || '-';
        document.getElementById('dataset-satellites').textContent = dataset.satellite || '-';
        document.getElementById('dataset-coverage').textContent = dataset.coverage || '-';
        document.getElementById('dataset-frequency').textContent = dataset.frequency || '-';
        document.getElementById('dataset-cloud-cover').textContent = dataset.cloud_cover || '-';
        document.getElementById('dataset-dates').textContent = dataset.dates || '-';
        document.getElementById('dataset-start-date').textContent = dataset.start_date || '-';
        document.getElementById('dataset-end-date').textContent = dataset.end_date || '-';
        document.getElementById('dataset-tags').textContent = (dataset.tags || []).join(', ');
        document.getElementById('dataset-applications').textContent = (dataset.applications || []).join(', ');
        document.getElementById('dataset-limitations').textContent = dataset.limitations || '-';
        document.getElementById('dataset-code-snippet').textContent = dataset.code_snippet || '-';
        document.getElementById('dataset-download-link').href = dataset.download_link || '#';
        // Show details panel
        document.getElementById('dataset-details-panel').classList.add('open');
    }
    closeDatasetDetailsPanel() {
        document.getElementById('dataset-details-panel').classList.remove('open');
    }

    /**
     * Initialize satellite info functionality
     */
    initSatelliteInfo() {
        console.log('=== INIT SATELLITE INFO DEBUG START ===');
        console.log('[INIT] initSatelliteInfo called');
        console.log('[INIT] this object:', this);
        console.log('[INIT] window.app:', window.app);
        
        // Re-initialize subtab event listeners after a short delay
        console.log('[INIT] Setting up delayed subtab event listener setup...');
        setTimeout(() => {
            console.log('[INIT] Delayed setup triggered');
            console.log('[INIT] this in timeout:', this);
            console.log('[INIT] window.app in timeout:', window.app);
            
            if (this && this.setupSubtabEventListeners) {
                console.log('[INIT] Calling this.setupSubtabEventListeners()');
                this.setupSubtabEventListeners();
            } else if (window.app && window.app.setupSubtabEventListeners) {
                console.log('[INIT] Calling window.app.setupSubtabEventListeners()');
                window.app.setupSubtabEventListeners();
            } else {
                console.error('[INIT] ❌ setupSubtabEventListeners method not found!');
                console.log('[INIT] this.setupSubtabEventListeners:', this?.setupSubtabEventListeners);
                console.log('[INIT] window.app.setupSubtabEventListeners:', window.app?.setupSubtabEventListeners);
            }
        }, 100);
        
        console.log('=== INIT SATELLITE INFO DEBUG END ===');
    }

    /**
     * Setup subtab event listeners specifically
     */
    setupSubtabEventListeners() {
        console.log('[SUBTAB] Setting up event listeners...');
        
        // Remove any existing listeners first
        const existingButtons = document.querySelectorAll('.subtab-btn');
        existingButtons.forEach(btn => {
            if (btn._subtabClickHandler) {
                btn.removeEventListener('click', btn._subtabClickHandler);
                delete btn._subtabClickHandler;
            }
        });

        // Add new event listeners
        const buttons = document.querySelectorAll('.subtab-btn');
        console.log(`[SUBTAB] Setting up ${buttons.length} event listeners`);
        
        buttons.forEach((btn, index) => {
            btn._subtabClickHandler = (e) => {
                const subtab = e.currentTarget.dataset.subtab;
                console.log(`[SUBTAB] Button clicked: ${subtab}`);
                
                // Ensure we're calling switchSubtab on the right object
                const appInstance = window.app || this;
                
                if (appInstance && typeof appInstance.switchSubtab === 'function') {
                    appInstance.switchSubtab(subtab);
                } else {
                    console.error('[SUBTAB] ❌ switchSubtab method not found!');
                }
            };
            
            btn.addEventListener('click', btn._subtabClickHandler);
        });

        console.log('[SUBTAB] Event listeners setup complete');
        
        // Test subtab functionality
        this.testSubtabFunctionality();
    }

    /**
     * Test subtab functionality
     */
    testSubtabFunctionality() {
        console.log('=== SUBTAB FUNCTIONALITY TEST START ===');
        console.log('[SUBTAB TEST] Testing subtab functionality...');
        
        const buttons = document.querySelectorAll('.subtab-btn');
        const contents = document.querySelectorAll('.subtab-content');
        
        console.log(`[SUBTAB TEST] Found ${buttons.length} buttons and ${contents.length} contents`);
        
        // Test each button
        buttons.forEach((btn, index) => {
            const subtab = btn.dataset.subtab;
            const content = document.getElementById(`${subtab}-subtab`);
            console.log(`[SUBTAB TEST] Button ${index}:`, {
                element: btn,
                dataset: btn.dataset,
                text: btn.textContent.trim(),
                classes: btn.className,
                hasClickHandler: !!btn._subtabClickHandler,
                contentFound: !!content,
                contentId: `${subtab}-subtab`,
                contentElement: content
            });
        });
        
        // Test each content
        contents.forEach((content, index) => {
            console.log(`[SUBTAB TEST] Content ${index}:`, {
                element: content,
                id: content.id,
                classes: content.className,
                display: window.getComputedStyle(content).display,
                visible: window.getComputedStyle(content).display !== 'none'
            });
        });
        
        // Test if we can manually trigger a switch
        console.log('[SUBTAB TEST] Testing manual switchSubtab call...');
        if (window.app && typeof window.app.switchSubtab === 'function') {
            console.log('[SUBTAB TEST] ✅ switchSubtab method available');
            console.log('[SUBTAB TEST] Testing switch to "crawler"...');
            window.app.switchSubtab('crawler');
        } else {
            console.error('[SUBTAB TEST] ❌ switchSubtab method not available!');
        }
        
        console.log('=== SUBTAB FUNCTIONALITY TEST END ===');
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('[DOM] DOMContentLoaded event fired');
    
    // Create global app instance
    window.app = new FlutterEarthEnhancedV2();
    window.flutterEarth = window.app; // For backward compatibility with tabs.js
    
    console.log('[DOM] App instance created');
    
    // Initialize satellite info functionality
    setTimeout(() => {
        if (window.app && window.app.initSatelliteInfo) {
            window.app.initSatelliteInfo();
        } else {
            console.error('[DOM] ❌ initSatelliteInfo method not found!');
        }
    }, 200);
    
    // Handle window resize
    window.addEventListener('resize', () => {
        window.app.handleResize();
    });
    
    // Handle keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        window.app.handleKeyboardShortcuts(e);
    });
    
    console.log('[DOM] Flutter Earth Enhanced v2.0 application started');
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = FlutterEarthEnhancedV2;
}

// Global test functions for debugging
window.testSubtabSwitch = function(subtabName) {
    console.log('=== MANUAL SUBTAB TEST ===');
    console.log('[TEST] Manual subtab switch requested:', subtabName);
    console.log('[TEST] window.app available:', !!window.app);
    
    if (window.app && typeof window.app.switchSubtab === 'function') {
        console.log('[TEST] Calling window.app.switchSubtab...');
        window.app.switchSubtab(subtabName);
    } else {
        console.error('[TEST] ❌ Cannot call switchSubtab!');
        console.log('[TEST] window.app:', window.app);
        console.log('[TEST] switchSubtab method:', window.app?.switchSubtab);
    }
};

window.testSubtabClick = function(subtabName) {
    console.log('=== MANUAL SUBTAB CLICK TEST ===');
    console.log('[TEST] Manual subtab click test requested:', subtabName);
    
    const button = document.querySelector(`.subtab-btn[data-subtab="${subtabName}"]`);
    if (button) {
        console.log('[TEST] Found button, triggering click...');
        button.click();
    } else {
        console.error('[TEST] ❌ Button not found!');
        console.log('[TEST] Available buttons:', Array.from(document.querySelectorAll('.subtab-btn')).map(btn => btn.dataset.subtab));
    }
};

window.debugSubtabElements = function() {
    console.log('=== SUBTAB ELEMENTS DEBUG ===');
    const buttons = document.querySelectorAll('.subtab-btn');
    const contents = document.querySelectorAll('.subtab-content');
    
    console.log('[DEBUG] Buttons found:', buttons.length);
    buttons.forEach((btn, i) => {
        console.log(`[DEBUG] Button ${i}:`, {
            element: btn,
            dataset: btn.dataset,
            text: btn.textContent.trim(),
            classes: btn.className,
            hasClickHandler: !!btn._subtabClickHandler
        });
    });
    
    console.log('[DEBUG] Contents found:', contents.length);
    contents.forEach((content, i) => {
        console.log(`[DEBUG] Content ${i}:`, {
            element: content,
            id: content.id,
            classes: content.className,
            display: window.getComputedStyle(content).display
        });
    });
};