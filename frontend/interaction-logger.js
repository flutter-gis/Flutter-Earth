// ===== COMPREHENSIVE INTERACTION LOGGING SYSTEM =====

class InteractionLogger {
    constructor() {
        this.logs = [];
        this.maxLogs = 1000; // Keep last 1000 interactions
        this.isEnabled = true;
        this.startTime = new Date();
        
        // Initialize logging
        this.initializeLogging();
        console.log('🔍 Interaction Logger initialized');
    }

    log(interaction) {
        if (!this.isEnabled) return;
        
        const logEntry = {
            timestamp: new Date().toISOString(),
            timeSinceStart: Date.now() - this.startTime.getTime(),
            ...interaction
        };
        
        this.logs.push(logEntry);
        
        // Keep only the last maxLogs entries
        if (this.logs.length > this.maxLogs) {
            this.logs = this.logs.slice(-this.maxLogs);
        }
        
        // Console output for debugging
        console.log(`📝 ${logEntry.type}: ${logEntry.element} - ${logEntry.details || ''}`);
    }

    logButtonClick(button, details = '') {
        this.log({
            type: 'button_click',
            element: button.id || button.className || button.tagName,
            text: button.textContent?.trim() || '',
            details: details,
            elementInfo: {
                id: button.id,
                className: button.className,
                tagName: button.tagName
            }
        });
    }

    logInputChange(input, details = '') {
        this.log({
            type: 'input_change',
            element: input.id || input.className || input.tagName,
            value: input.value,
            details: details,
            elementInfo: {
                id: input.id,
                className: input.className,
                tagName: input.tagName,
                type: input.type
            }
        });
    }

    logInputFocus(input) {
        this.log({
            type: 'input_focus',
            element: input.id || input.className || input.tagName,
            details: 'Input focused',
            elementInfo: {
                id: input.id,
                className: input.className,
                tagName: input.tagName,
                type: input.type
            }
        });
    }

    logTabSwitch(fromTab, toTab) {
        this.log({
            type: 'tab_switch',
            element: 'tab_system',
            details: `Switched from "${fromTab}" to "${toTab}"`,
            fromTab: fromTab,
            toTab: toTab
        });
    }

    logFormSubmit(form, details = '') {
        this.log({
            type: 'form_submit',
            element: form.id || form.className || form.tagName,
            details: details,
            elementInfo: {
                id: form.id,
                className: form.className,
                tagName: form.tagName
            }
        });
    }

    logError(error, context = '') {
        this.log({
            type: 'error',
            element: context,
            details: error.message || error,
            error: error
        });
    }

    getLogs(filter = {}) {
        let filteredLogs = [...this.logs];
        
        if (filter.type) {
            filteredLogs = filteredLogs.filter(log => log.type === filter.type);
        }
        
        if (filter.element) {
            filteredLogs = filteredLogs.filter(log => 
                log.element && log.element.includes(filter.element)
            );
        }
        
        if (filter.timeRange) {
            const now = Date.now();
            const startTime = now - filter.timeRange;
            filteredLogs = filteredLogs.filter(log => 
                log.timeSinceStart >= startTime
            );
        }
        
        return filteredLogs;
    }

    getLogsByType(type) {
        return this.getLogs({ type });
    }

    getLogsByElement(element) {
        return this.getLogs({ element });
    }

    getRecentLogs(minutes = 5) {
        return this.getLogs({ timeRange: minutes * 60 * 1000 });
    }

    exportLogs(format = 'json') {
        const data = {
            exportTime: new Date().toISOString(),
            totalLogs: this.logs.length,
            sessionStart: this.startTime.toISOString(),
            logs: this.logs
        };
        
        if (format === 'json') {
            return JSON.stringify(data, null, 2);
        } else if (format === 'csv') {
            return this.convertToCSV(data.logs);
        }
        
        return data;
    }

    convertToCSV(logs) {
        const headers = ['timestamp', 'type', 'element', 'details', 'text', 'value'];
        const csvRows = [headers.join(',')];
        
        logs.forEach(log => {
            const row = headers.map(header => {
                const value = log[header] || '';
                return `"${String(value).replace(/"/g, '""')}"`;
            });
            csvRows.push(row.join(','));
        });
        
        return csvRows.join('\n');
    }

    clearLogs() {
        this.logs = [];
        this.startTime = new Date();
        console.log('🧹 Logs cleared');
    }

    initializeLogging() {
        // Set up global event listeners
        document.addEventListener('click', (e) => {
            if (e.target.tagName === 'BUTTON' || e.target.closest('button')) {
                const button = e.target.tagName === 'BUTTON' ? e.target : e.target.closest('button');
                this.logButtonClick(button);
            }
        });

        document.addEventListener('input', (e) => {
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.tagName === 'SELECT') {
                this.logInputChange(e.target);
            }
        });

        document.addEventListener('focusin', (e) => {
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.tagName === 'SELECT') {
                this.logInputFocus(e.target);
            }
        });

        document.addEventListener('submit', (e) => {
            this.logFormSubmit(e.target);
        });

        // Log page load
        this.log({
            type: 'page_load',
            element: 'document',
            details: 'Page loaded and logging initialized'
        });
    }
}

// Initialize the logger globally
const interactionLogger = new InteractionLogger();

// ===== LOG VIEWER FUNCTIONS =====

function showLogViewer() {
    const logs = interactionLogger.getLogs();
    const logViewerHTML = createLogViewerHTML(logs);
    
    // Create modal for log viewer
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.id = 'log-viewer-modal';
    modal.innerHTML = logViewerHTML;
    
    document.body.appendChild(modal);
    
    // Add event listeners for log viewer
    setupLogViewerEvents();
    
    console.log('📊 Log viewer opened');
}

function createLogViewerHTML(logs) {
    const logEntries = logs.map(log => `
        <div class="log-entry log-${log.type}">
            <div class="log-timestamp">${new Date(log.timestamp).toLocaleTimeString()}</div>
            <div class="log-type">${log.type}</div>
            <div class="log-element">${log.element}</div>
            <div class="log-details">${log.details || ''}</div>
            <div class="log-value">${log.value || log.text || ''}</div>
        </div>
    `).join('');
    
    return `
        <div class="modal-content log-viewer-content">
            <div class="log-viewer-header">
                <h3>📊 Interaction Logs (${logs.length} entries)</h3>
                <div class="log-viewer-controls">
                    <button id="export-logs-json" class="btn-secondary">Export JSON</button>
                    <button id="export-logs-csv" class="btn-secondary">Export CSV</button>
                    <button id="clear-logs" class="btn-secondary">Clear Logs</button>
                    <button id="close-log-viewer" class="btn-secondary">Close</button>
                </div>
            </div>
            
            <div class="log-filters">
                <select id="log-type-filter">
                    <option value="">All Types</option>
                    <option value="button_click">Button Clicks</option>
                    <option value="input_change">Input Changes</option>
                    <option value="input_focus">Input Focus</option>
                    <option value="tab_switch">Tab Switches</option>
                    <option value="form_submit">Form Submits</option>
                    <option value="error">Errors</option>
                </select>
                
                <input type="text" id="log-element-filter" placeholder="Filter by element...">
                
                <select id="log-time-filter">
                    <option value="">All Time</option>
                    <option value="5">Last 5 minutes</option>
                    <option value="15">Last 15 minutes</option>
                    <option value="60">Last hour</option>
                </select>
                
                <button id="apply-log-filters" class="btn-primary">Apply Filters</button>
            </div>
            
            <div class="log-stats">
                <div class="stat-item">
                    <span class="stat-number">${logs.filter(l => l.type === 'button_click').length}</span>
                    <span class="stat-label">Button Clicks</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number">${logs.filter(l => l.type === 'input_change').length}</span>
                    <span class="stat-label">Input Changes</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number">${logs.filter(l => l.type === 'tab_switch').length}</span>
                    <span class="stat-label">Tab Switches</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number">${logs.filter(l => l.type === 'error').length}</span>
                    <span class="stat-label">Errors</span>
                </div>
            </div>
            
            <div class="log-entries" id="log-entries">
                ${logEntries}
            </div>
        </div>
    `;
}

function setupLogViewerEvents() {
    // Close button
    document.getElementById('close-log-viewer').addEventListener('click', () => {
        document.getElementById('log-viewer-modal').remove();
    });
    
    // Export buttons
    document.getElementById('export-logs-json').addEventListener('click', () => {
        const jsonData = interactionLogger.exportLogs('json');
        downloadFile(jsonData, 'interaction-logs.json', 'application/json');
    });
    
    document.getElementById('export-logs-csv').addEventListener('click', () => {
        const csvData = interactionLogger.exportLogs('csv');
        downloadFile(csvData, 'interaction-logs.csv', 'text/csv');
    });
    
    // Clear logs
    document.getElementById('clear-logs').addEventListener('click', () => {
        if (confirm('Are you sure you want to clear all logs?')) {
            interactionLogger.clearLogs();
            document.getElementById('log-viewer-modal').remove();
            showNotification('Logs cleared successfully');
        }
    });
    
    // Filter functionality
    document.getElementById('apply-log-filters').addEventListener('click', () => {
        applyLogFilters();
    });
    
    // Auto-refresh every 5 seconds
    const refreshInterval = setInterval(() => {
        if (!document.getElementById('log-viewer-modal')) {
            clearInterval(refreshInterval);
            return;
        }
        refreshLogViewer();
    }, 5000);
}

function applyLogFilters() {
    const typeFilter = document.getElementById('log-type-filter').value;
    const elementFilter = document.getElementById('log-element-filter').value;
    const timeFilter = document.getElementById('log-time-filter').value;
    
    let filter = {};
    if (typeFilter) filter.type = typeFilter;
    if (elementFilter) filter.element = elementFilter;
    if (timeFilter) filter.timeRange = parseInt(timeFilter) * 60 * 1000;
    
    const filteredLogs = interactionLogger.getLogs(filter);
    updateLogViewerContent(filteredLogs);
}

function refreshLogViewer() {
    const logs = interactionLogger.getLogs();
    updateLogViewerContent(logs);
}

function updateLogViewerContent(logs) {
    const logEntries = document.getElementById('log-entries');
    if (!logEntries) return;
    
    const logEntriesHTML = logs.map(log => `
        <div class="log-entry log-${log.type}">
            <div class="log-timestamp">${new Date(log.timestamp).toLocaleTimeString()}</div>
            <div class="log-type">${log.type}</div>
            <div class="log-element">${log.element}</div>
            <div class="log-details">${log.details || ''}</div>
            <div class="log-value">${log.value || log.text || ''}</div>
        </div>
    `).join('');
    
    logEntries.innerHTML = logEntriesHTML;
    
    // Update stats
    updateLogStats(logs);
}

function updateLogStats(logs) {
    const stats = {
        button_click: logs.filter(l => l.type === 'button_click').length,
        input_change: logs.filter(l => l.type === 'input_change').length,
        tab_switch: logs.filter(l => l.type === 'tab_switch').length,
        error: logs.filter(l => l.type === 'error').length
    };
    
    const statElements = document.querySelectorAll('.log-stats .stat-number');
    if (statElements.length >= 4) {
        statElements[0].textContent = stats.button_click;
        statElements[1].textContent = stats.input_change;
        statElements[2].textContent = stats.tab_switch;
        statElements[3].textContent = stats.error;
    }
}

function downloadFile(content, filename, contentType) {
    const blob = new Blob([content], { type: contentType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    showNotification(`Logs exported as ${filename}`);
}

function showNotification(message) {
    const notification = document.getElementById('notification-popup');
    const notificationText = document.getElementById('notification-text');
    
    notificationText.textContent = message;
    notification.style.display = 'block';
    
    setTimeout(() => {
        notification.style.display = 'none';
    }, 3000);
}

// Add log viewer button to the UI
function addLogViewerButton() {
    // Add to status bar
    const statusBar = document.getElementById('status-bar');
    const statusContent = statusBar.querySelector('.status-content');
    
    const logButton = document.createElement('button');
    logButton.id = 'show-logs-btn';
    logButton.className = 'btn-secondary';
    logButton.innerHTML = '📊 View Logs';
    logButton.style.marginLeft = '10px';
    logButton.style.fontSize = '12px';
    logButton.style.padding = '4px 8px';
    
    logButton.addEventListener('click', showLogViewer);
    statusContent.appendChild(logButton);
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    addLogViewerButton();
    
    // Test logging to make sure it's working
    console.log('🔍 Interaction Logger: DOM loaded, testing logging...');
    
    // Log a test entry
    if (window.interactionLogger) {
        window.interactionLogger.log({
            type: 'system_init',
            element: 'interaction_logger',
            details: 'Logger initialized and ready'
        });
    }
    
    // Initialize themes immediately if available
    setTimeout(() => {
        if (window.availableThemes && window.availableThemes.length > 0) {
            console.log('🎨 Initializing theme system...');
            initializeThemeSystem();
        } else {
            console.warn('🎨 No themes available for initialization');
        }
    }, 500);
    
    // Also initialize when settings view becomes visible
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
                const settingsView = document.getElementById('settings-view');
                if (settingsView && settingsView.classList.contains('active')) {
                    // Settings view is now active, ensure theme system is initialized
                    setTimeout(() => {
                        if (window.availableThemes && window.availableThemes.length > 0) {
                            console.log('🎨 Re-initializing theme system for settings view...');
                            initializeThemeSystem();
                        }
                    }, 100);
                }
            }
        });
    });
    
    // Observe the settings view for class changes
    const settingsView = document.getElementById('settings-view');
    if (settingsView) {
        observer.observe(settingsView, { attributes: true });
    }
});

// Theme-specific animation helpers
function getThemeAnimationDuration(themeName) {
    const durations = {
        'default_dark': 0.4,
        'light': 0.5,
        'unity_pride': 0.6,
        'cyberpunk': 0.8,
        'ocean_depths': 0.5,
        'sunset_vibes': 0.6,
        'forest_mist': 0.5,
        'neon_dreams': 0.7,
        'aurora_borealis': 0.6,
        // Pride themes
        'wlw_pride': 0.5,
        'mlm_pride': 0.6,
        'genderqueer_pride': 0.7,
        'nonbinary_pride': 0.6,
        'trans_pride': 0.7,
        'pan_pride': 0.7,
        'ace_pride': 0.5,
        'aro_pride': 0.7,
        'enby_pride': 0.6,
        'bi_pride': 0.7,
        // Minecraft themes
        'creeper': 0.8,
        'skeleton': 0.7,
        'enderman': 0.6,
        // MLP themes
        'princess_luna': 0.7,
        'princess_celestia': 0.6
    };
    return durations[themeName] || 0.4;
}

function getThemeApplyingText(themeName) {
    const texts = {
        'default_dark': '🌑 Applying...',
        'light': '🌞 Applying...',
        'unity_pride': '🌈 Applying...',
        'cyberpunk': '⚡ Applying...',
        'ocean_depths': '🌊 Applying...',
        'sunset_vibes': '🌅 Applying...',
        'forest_mist': '🌲 Applying...',
        'neon_dreams': '💫 Applying...',
        'aurora_borealis': '✨ Applying...',
        // Pride themes
        'wlw_pride': '💖 Applying...',
        'mlm_pride': '💙 Applying...',
        'genderqueer_pride': '💜 Applying...',
        'nonbinary_pride': '💛 Applying...',
        'trans_pride': '💗 Applying...',
        'pan_pride': '💖 Applying...',
        'ace_pride': '🖤 Applying...',
        'aro_pride': '💚 Applying...',
        'enby_pride': '💛 Applying...',
        'bi_pride': '💖 Applying...',
        // Minecraft themes
        'creeper': '💣 Applying...',
        'skeleton': '💀 Applying...',
        'enderman': '👾 Applying...',
        // MLP themes
        'princess_luna': '🌙 Applying...',
        'princess_celestia': '🌞 Applying...'
    };
    return texts[themeName] || 'Applying...';
}

// Simple theme system initialization
function initializeThemeSystem() {
    const themeGrid = document.getElementById('theme-grid');
    const themeTabContainer = document.getElementById('theme-tab-container');
    
    if (!themeGrid || !window.availableThemes) {
        console.warn('🎨 Theme grid or themes not available');
        return;
    }
    
    console.log(`🎨 Initializing ${window.availableThemes.length} themes`);
    
    // Initialize theme tabs
    if (themeTabContainer) {
        const categories = ['all', 'professional', 'pride', 'gaming', 'nature', 'tech', 'artistic'];
        themeTabContainer.innerHTML = '';
        
        categories.forEach(category => {
            const tab = document.createElement('button');
            tab.className = 'theme-tab';
            tab.dataset.category = category;
            tab.textContent = category === 'all' ? 'All Themes' : category.charAt(0).toUpperCase() + category.slice(1);
            tab.addEventListener('click', () => {
                // Remove active class from all tabs
                document.querySelectorAll('.theme-tab').forEach(t => t.classList.remove('active'));
                // Add active class to clicked tab
                tab.classList.add('active');
                // Update theme grid
                updateThemeGrid(category);
            });
            themeTabContainer.appendChild(tab);
        });
        
        // Set first tab as active
        const firstTab = themeTabContainer.querySelector('.theme-tab');
        if (firstTab) firstTab.classList.add('active');
    }
    
    // Initialize theme grid with all themes
    updateThemeGrid('all');
}

function updateThemeGrid(category = 'all') {
    const themeGrid = document.getElementById('theme-grid');
    if (!themeGrid || !window.availableThemes) return;
    
    let themesToShow = window.availableThemes;
    if (category && category !== 'all') {
        themesToShow = window.availableThemes.filter(t => t.category === category);
    }
    
    console.log(`🎨 Showing ${themesToShow.length} themes for category: ${category}`);
    
    themeGrid.innerHTML = '';
    
    if (themesToShow.length === 0) {
        themeGrid.innerHTML = '<div class="theme-error">No themes found for this category.</div>';
        return;
    }
    
    themesToShow.forEach(theme => {
        const themeCard = document.createElement('div');
        themeCard.className = 'theme-item';
        themeCard.dataset.theme = theme.name;
        themeCard.tabIndex = 0; // Make focusable
        themeCard.setAttribute('role', 'button');
        themeCard.setAttribute('aria-label', `Apply ${theme.display_name} theme`);
        themeCard.innerHTML = `
            <div class="theme-preview" data-theme="${theme.name}" style="
                background: ${theme.colors?.background || '#1e1e1e'};
                border: 2px solid ${theme.colors?.primary || '#007acc'};
                position: relative;
                overflow: hidden;
            "></div>
            <div class="theme-name">${theme.display_name}</div>
            <div class="theme-description">${theme.category}</div>
        `;
        
        const handleThemeSelection = () => {
            // Get theme-specific animation
            const animationName = `themeClick-${theme.name}`;
            const animationDuration = getThemeAnimationDuration(theme.name);
            
            // Add theme-specific click animation
            themeCard.style.animation = `${animationName} ${animationDuration} ease-out`;
            
            // Remove selected class from all themes
            document.querySelectorAll('.theme-item').forEach(item => item.classList.remove('selected'));
            
            // Add selected class to clicked theme
            themeCard.classList.add('selected');
            
            // Show applying indicator with theme-specific text
            const originalText = themeCard.querySelector('.theme-name').textContent;
            const applyingText = getThemeApplyingText(theme.name);
            themeCard.querySelector('.theme-name').textContent = applyingText;
            themeCard.style.pointerEvents = 'none';
            
            // Apply the theme
            applyTheme(theme.name);
            
            // Reset after animation completes
            setTimeout(() => {
                themeCard.querySelector('.theme-name').textContent = originalText;
                themeCard.style.pointerEvents = 'auto';
                themeCard.style.animation = '';
            }, animationDuration * 1000 + 200);
        };
        
        themeCard.addEventListener('click', handleThemeSelection);
        themeCard.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                handleThemeSelection();
            }
        });
        
        themeGrid.appendChild(themeCard);
        
        // Enhance with artistic effects and theme colors
        const preview = themeCard.querySelector('.theme-preview');
        enhanceThemePreview(theme, preview);
        
        // Add artistic effects if available
        if (window.artisticEffects) {
            window.artisticEffects.enhanceThemePreview(theme.name, preview);
        }
    });
}

function applyTheme(themeName) {
    console.log(`🎨 Applying theme: ${themeName}`);
    
    // Set theme attribute on both document element and body
    document.documentElement.setAttribute('data-theme', themeName);
    document.body.setAttribute('data-theme', themeName);
    
    // Find the theme data
    const theme = window.availableThemes.find(t => t.name === themeName);
    if (!theme) {
        console.warn(`🎨 Theme not found: ${themeName}`);
        return;
    }
    
    // Apply CSS variables with proper mapping
    const root = document.documentElement;
    if (theme.colors) {
        // Map theme colors to CSS custom properties
        const colorMapping = {
            'background': '--bg',
            'foreground': '--surface',
            'primary': '--primary',
            'secondary': '--secondary',
            'accent': '--accent',
            'error': '--error',
            'success': '--success',
            'text': '--text',
            'text_subtle': '--text-subtle',
            'disabled': '--disabled',
            'widget_bg': '--surface-light',
            'widget_border': '--border',
            'text_on_primary': '--text-on-primary',
            'button_bg': '--button-bg',
            'button_fg': '--button-fg',
            'button_hover_bg': '--button-hover-bg',
            'entry_bg': '--entry-bg',
            'entry_fg': '--entry-fg',
            'entry_border': '--entry-border',
            'list_bg': '--list-bg',
            'list_fg': '--list-fg',
            'list_selected_bg': '--list-selected-bg',
            'list_selected_fg': '--list-selected-fg',
            'tooltip_bg': '--tooltip-bg',
            'tooltip_fg': '--tooltip-fg',
            'progressbar_bg': '--progressbar-bg',
            'progressbar_fg': '--progressbar-fg'
        };
        
        Object.entries(theme.colors).forEach(([key, value]) => {
            const cssVar = colorMapping[key] || `--${key.replace(/_/g, '-')}`;
            root.style.setProperty(cssVar, value);
        });
        
        // Set additional CSS variables for compatibility
        root.style.setProperty('--surface', theme.colors.widget_bg || theme.colors.background);
        root.style.setProperty('--border', theme.colors.widget_border || theme.colors.primary);
        root.style.setProperty('--surface-light', theme.colors.entry_bg || theme.colors.widget_bg);
    }
    
    // Apply artistic effects to all theme previews and refresh them
    document.querySelectorAll('.theme-preview').forEach(preview => {
        const themeKey = preview.dataset.theme;
        if (themeKey) {
            const theme = window.availableThemes.find(t => t.name === themeKey);
            if (theme) {
                enhanceThemePreview(theme, preview);
            }
            if (window.artisticEffects) {
                window.artisticEffects.enhanceThemePreview(themeKey, preview);
            }
        }
    });
    
    // Update status bar if it exists
    const statusBar = document.getElementById('status-bar');
    if (statusBar) {
        const statusContent = statusBar.querySelector('.status-content');
        if (statusContent) {
            // Find or create theme indicator
            let themeIndicator = statusContent.querySelector('.current-theme-indicator');
            if (!themeIndicator) {
                themeIndicator = document.createElement('span');
                themeIndicator.className = 'current-theme-indicator';
                themeIndicator.style.cssText = `
                    color: var(--primary, #007acc);
                    font-weight: 500;
                    margin-left: 10px;
                    font-size: 12px;
                `;
                statusContent.appendChild(themeIndicator);
            }
            themeIndicator.textContent = `Theme: ${theme.display_name}`;
        }
    }
    
    // Log the theme change
    if (window.interactionLogger) {
        window.interactionLogger.log({
            type: 'theme_change',
            element: 'theme_system',
            details: `Changed to theme: ${theme.display_name}`,
            value: themeName
        });
    }
    
    console.log(`🎨 Theme applied: ${theme.display_name}`);
    console.log(`🎨 Applied colors:`, theme.colors);
}

// Function to enhance theme previews with actual theme colors and effects
function enhanceThemePreview(theme, previewElement) {
    if (!previewElement || !theme.colors) return;
    
    // Apply theme colors to preview
    previewElement.style.background = theme.colors.background || '#1e1e1e';
    previewElement.style.borderColor = theme.colors.primary || '#007acc';
    
    // Create gradient overlay based on theme colors
    const primaryColor = theme.colors.primary || '#007acc';
    const secondaryColor = theme.colors.secondary || '#666666';
    const accentColor = theme.colors.accent || '#ff6b35';
    
    // Add theme-specific gradient overlay
    const gradientOverlay = document.createElement('div');
    gradientOverlay.style.cssText = `
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(135deg, 
            ${primaryColor}20 0%, 
            ${secondaryColor}30 50%, 
            ${accentColor}20 100%);
        pointer-events: none;
        border-radius: inherit;
    `;
    
    // Remove existing overlay if any
    const existingOverlay = previewElement.querySelector('.theme-gradient-overlay');
    if (existingOverlay) {
        existingOverlay.remove();
    }
    
    gradientOverlay.className = 'theme-gradient-overlay';
    previewElement.appendChild(gradientOverlay);
    
    // Add theme-specific decorative elements
    const decoration = document.createElement('div');
    decoration.style.cssText = `
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 20px;
        height: 20px;
        background: ${primaryColor};
        border-radius: 50%;
        opacity: 0.6;
        pointer-events: none;
    `;
    
    // Remove existing decoration if any
    const existingDecoration = previewElement.querySelector('.theme-decoration');
    if (existingDecoration) {
        existingDecoration.remove();
    }
    
    decoration.className = 'theme-decoration';
    previewElement.appendChild(decoration);
    
    // Add theme emoji if available
    if (theme.emoji) {
        const emojiElement = document.createElement('div');
        emojiElement.style.cssText = `
            position: absolute;
            top: 5px;
            right: 5px;
            font-size: 16px;
            opacity: 0.8;
            pointer-events: none;
        `;
        emojiElement.textContent = theme.emoji;
        
        // Remove existing emoji if any
        const existingEmoji = previewElement.querySelector('.theme-emoji');
        if (existingEmoji) {
            existingEmoji.remove();
        }
        
        emojiElement.className = 'theme-emoji';
        previewElement.appendChild(emojiElement);
    }
} 