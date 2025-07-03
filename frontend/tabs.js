// ===== CLEAN TAB SYSTEM JAVASCRIPT =====

class CleanTabSystem {
    constructor() {
        this.currentTab = 'welcome';
        this.tabButtons = null;
        this.tabContents = null;
        this.debugLogs = null;
        
        this.init();
    }
    
    init() {
        console.log('[TABS] Initializing Clean Tab System...');
        
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setupTabs());
        } else {
            this.setupTabs();
        }
    }
    
    setupTabs() {
        console.log('[TABS] Setting up tabs...');
        
        // Get all tab elements
        this.tabButtons = document.querySelectorAll('.toolbar-item[data-view]');
        this.tabContents = document.querySelectorAll('.view-content');
        
        console.log(`[TABS] Found ${this.tabButtons.length} tab buttons`);
        console.log(`[TABS] Found ${this.tabContents.length} tab contents`);
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Initialize with welcome tab
        this.switchToTab('welcome');
        
        console.log('[TABS] Tab system setup complete');
    }
    
    setupEventListeners() {
        console.log('[TABS] Setting up event listeners...');
        
        this.tabButtons.forEach(button => {
            const viewName = button.dataset.view;
            console.log(`[TABS] Setting up listener for: ${viewName}`);
            
            // Remove any existing listeners
            button.removeEventListener('click', button._tabClickHandler);
            
            // Create new click handler
            button._tabClickHandler = (event) => {
                event.preventDefault();
                event.stopPropagation();
                
                console.log(`[TABS] Tab clicked: ${viewName}`);
                this.switchToTab(viewName);
            };
            
            // Add event listener
            button.addEventListener('click', button._tabClickHandler);
        });
        
        console.log('[TABS] Event listeners setup complete');
    }
    
    switchToTab(tabName) {
        console.log(`[TABS] Switching to tab: ${tabName}`);
        
        // Get current tab for logging
        const previousTab = this.currentTab;
        
        // Validate input
        if (!tabName) {
            console.error('[TABS] No tab name provided');
            return;
        }
        
        // Check if tab exists
        const targetContent = document.getElementById(`${tabName}-view`);
        if (!targetContent) {
            console.error(`[TABS] Tab content not found: ${tabName}-view`);
            return;
        }
        
        // Hide all tab contents
        this.tabContents.forEach(content => {
            content.classList.remove('active');
            content.style.display = 'none';
            console.log(`[TABS] Hidden: ${content.id}`);
        });
        
        // Remove active class from all buttons
        this.tabButtons.forEach(button => {
            button.classList.remove('active');
        });
        
        // Show target tab content
        targetContent.classList.add('active');
        targetContent.style.display = 'block';
        console.log(`[TABS] Activated: ${targetContent.id}`);
        
        // Add active class to target button
        const targetButton = document.querySelector(`.toolbar-item[data-view="${tabName}"]`);
        if (targetButton) {
            targetButton.classList.add('active');
            console.log(`[TABS] Button activated: ${tabName}`);
        } else {
            console.warn(`[TABS] Button not found for: ${tabName}`);
        }
        
        // Update current tab
        this.currentTab = tabName;
        
        // Log the tab switch
        if (window.interactionLogger) {
            window.interactionLogger.logTabSwitch(previousTab, tabName);
        }
        
        // Handle view-specific logic
        this.handleViewSpecificLogic(tabName);
        
        console.log(`[TABS] Successfully switched to: ${tabName}`);
    }
    
    handleViewSpecificLogic(tabName) {
        console.log(`[TABS] Handling specific logic for: ${tabName}`);
        
        switch (tabName) {
            case 'welcome':
                console.log('[TABS] Welcome view activated');
                break;
                
            case 'map':
                console.log('[TABS] Map view activated');
                break;
                
            case 'download':
                console.log('[TABS] Download view activated');
                break;
                
            case 'satelliteInfo':
                console.log('[TABS] Satellite Info view activated');
                break;
                
            case 'settings':
                console.log('[TABS] Settings view activated');
                // Initialize theme system when settings view is loaded
                setTimeout(() => {
                    if (window.flutterEarth && window.flutterEarth.initSettings) {
                        window.flutterEarth.initSettings(true);
                    }
                }, 100);
                break;
                
            case 'about':
                console.log('[TABS] About view activated');
                break;
                
            default:
                console.log(`[TABS] Unknown view: ${tabName}`);
                break;
        }
    }
    
    // Public methods for external use
    getCurrentTab() {
        return this.currentTab;
    }
    
    switchTab(tabName) {
        this.switchToTab(tabName);
    }
}

// Initialize when script loads
let tabSystem = null;

function initializeTabSystem() {
    if (!tabSystem) {
        tabSystem = new CleanTabSystem();
        window.tabSystem = tabSystem;
        console.log('[TABS] Tab system initialized globally');
    }
    return tabSystem;
}

// Auto-initialize
initializeTabSystem();

// Export for use in other scripts
window.CleanTabSystem = CleanTabSystem;
window.initializeTabSystem = initializeTabSystem; 