// Main renderer process logic for index.html
document.addEventListener('DOMContentLoaded', () => {
    const contentDiv = document.getElementById('content');
    const mainHeading = document.getElementById('main-heading');
    const welcomeMessage = document.getElementById('main-welcome-message');

    const homeButton = document.getElementById('home-button');
    const settingsButton = document.getElementById('settings-button');
    const aboutButton = document.getElementById('about-button');
    const downloadButton = document.getElementById('download-button');
    const progressButton = document.getElementById('progress-button');
    const indexAnalysisButton = document.getElementById('index-analysis-button');
    const vectorDownloadButton = document.getElementById('vector-download-button');
    const dataViewerButton = document.getElementById('data-viewer-button'); // Added Data Viewer Button

    // Status Bar Elements
    const statusBarTextElement = document.getElementById('status-text');
    const connectionStatusElement = document.getElementById('connection-status');
    const downloadStatusTextElement = document.getElementById('download-status-text');

    // Store original welcome message and heading
    const originalHeading = mainHeading.textContent;
    const originalWelcomeMessageDisplay = welcomeMessage.style.display;


    async function loadView(viewName, scriptSrc = null, pageTitle = "Flutter Earth") {
        try {
            const response = await fetch(`${viewName}.html`);
            if (!response.ok) {
                throw new Error(`Failed to load ${viewName}.html: ${response.statusText}`);
            }
            const html = await response.text();
            contentDiv.innerHTML = html;
            mainHeading.textContent = pageTitle;
            welcomeMessage.style.display = 'none'; // Hide welcome message when a view is loaded

            // Remove any old view-specific script
            const oldScript = document.querySelector('script[data-view-script]');
            if (oldScript) oldScript.remove();

            if (scriptSrc) {
                let newScriptElement;
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');
                const inlineScriptTag = doc.querySelector(`script[src="${scriptSrc}"]`);

                if (inlineScriptTag) {
                    newScriptElement = document.createElement('script');
                    newScriptElement.src = inlineScriptTag.src;
                    if (inlineScriptTag.defer) newScriptElement.defer = true;
                    if (inlineScriptTag.async) newScriptElement.async = true;
                } else { // Fallback if scriptSrc is provided but not found in fetched HTML (e.g. script is not in the HTML)
                    newScriptElement = document.createElement('script');
                    newScriptElement.src = scriptSrc;
                    newScriptElement.defer = true;
                }

                if (newScriptElement) {
                    newScriptElement.dataset.viewScript = 'true';
                    document.body.appendChild(newScriptElement);
                }
            }
        } catch (error) {
            contentDiv.innerHTML = `<p>Error loading ${viewName}: ${error.message}</p>`;
            console.error(`Error loading ${viewName}.html:`, error);
            welcomeMessage.style.display = originalWelcomeMessageDisplay;
            mainHeading.textContent = originalHeading;
        }
    }

    if (homeButton) {
        homeButton.addEventListener('click', () => {
            contentDiv.innerHTML = '';
            mainHeading.textContent = originalHeading;
            welcomeMessage.style.display = originalWelcomeMessageDisplay;
            const oldScript = document.querySelector('script[data-view-script]');
            if (oldScript) oldScript.remove();
            updateStatusText("Welcome to Flutter Earth!"); // Update status bar for home
        });
    }

    if (settingsButton) {
        settingsButton.addEventListener('click', () => {
            loadView('settings', 'settings.js', 'Settings - Flutter Earth');
            updateStatusText("Viewing Application Settings.");
        });
    }

    if (aboutButton) {
        aboutButton.addEventListener('click', () => {
            loadView('about', 'about.js', 'About - Flutter Earth');
            updateStatusText("Viewing About Information.");
        });
    }

    if (downloadButton) {
        downloadButton.addEventListener('click', () => {
            loadView('download', 'download.js', 'Download Satellite Data');
            updateStatusText("Open Download View.");
        });
    }

    if (progressButton) {
        progressButton.addEventListener('click', () => {
            loadView('progress', 'progress.js', 'Task Progress & History');
            updateStatusText("Viewing Task Progress and History.");
        });
    }

    if (indexAnalysisButton) {
        indexAnalysisButton.addEventListener('click', () => {
            loadView('index-analysis', 'index-analysis.js', 'Index Analysis');
            updateStatusText("Open Index Analysis View.");
        });
    }

    if (vectorDownloadButton) {
        vectorDownloadButton.addEventListener('click', () => {
            loadView('vector-download', 'vector-download.js', 'Vector Data Download');
            updateStatusText("Open Vector Data Download View.");
        });
    }

    if (dataViewerButton) {
        dataViewerButton.addEventListener('click', () => {
            loadView('data-viewer', 'data-viewer.js', 'Data Viewer');
            updateStatusText("Open Data Viewer.");
        });
    }

    // --- Status Bar Logic ---
    function updateStatusText(message) {
        if (statusBarTextElement) {
            statusBarTextElement.textContent = message;
        }
    }

    function updateConnectionStatus(status) { // status is 'online' or 'offline'
        if (connectionStatusElement) {
            connectionStatusElement.textContent = status.charAt(0).toUpperCase() + status.slice(1); // Capitalize
            connectionStatusElement.className = status; // 'online' or 'offline' for CSS styling
        }
        // Potentially update a global theme variable for status bar color if needed here,
        // similar to QML's statusBarColor property based on ThemeProvider.
    }

    // --- Initialize API and Listeners ---
    if (window.electronAPI) {
        console.log("electronAPI is available in index.html's renderer.");

        // Listen for connection status changes from main process
        window.electronAPI.onConnectionStatusChanged((status) => {
            console.log('Connection status changed:', status);
            updateConnectionStatus(status);
        });

        // Listen for general status messages
        window.electronAPI.onStatusMessageUpdate((message) => {
            console.log('Status message update:', message);
            updateStatusText(message);
        });

        // Listen for theme changes to update main shell if necessary
        window.electronAPI.onThemeChanged((themeName, themeData) => {
            console.log('Theme changed in main renderer:', themeName, themeData);
            // Example: apply theme to body or specific main elements
            // document.body.className = `theme-${themeName}`; // Simple example
            // Or more complex: iterate themeData.colors and apply CSS variables
            if (themeData && themeData.colors) {
                document.documentElement.style.setProperty('--theme-background', themeData.colors.background || '#f0f2f5');
                document.documentElement.style.setProperty('--theme-text', themeData.colors.text || '#333');
                document.documentElement.style.setProperty('--theme-primary', themeData.colors.primary || '#007bff');
                // Update status bar based on new theme (if it's part of themeData)
                // For now, connection status styling is independent of theme.
            }
             updateStatusText(`Theme changed to ${themeData.metadata ? themeData.metadata.display_name : themeName}`);
        });


        // Request initial status from backend (if backend emits it on request or startup)
        // This requires an IPC call that Python bridge handles and potentially emits back.
        // For now, we'll assume backend pushes status changes.
        // Or, we can have a "get-initial-status" invokePython call.
        async function fetchInitialConnectionStatus() {
            try {
                const initialStatus = await window.electronAPI.invokePython('get-connection-status');
                if (initialStatus && initialStatus.status) { // Check initialStatus before accessing its properties
                     updateConnectionStatus(initialStatus.status);
                     updateStatusText(initialStatus.message || "System Ready.");
                } else {
                    // Handle case where initialStatus might be null or not have .status
                    updateConnectionStatus('offline');
                    updateStatusText("Could not determine initial connection status.");
                }
            } catch (error) {
                console.warn("Could not fetch initial connection status:", error);
                updateConnectionStatus('offline');
                updateStatusText("Failed to get initial status.");
            }
        }
        fetchInitialConnectionStatus(); // Fetch initial connection status

        // Listener for download status updates
        window.electronAPI.onDownloadStatusUpdate((dlStatus) => {
            if (downloadStatusTextElement) {
                if (dlStatus && dlStatus.message) {
                    let displayText = dlStatus.message;
                    if (dlStatus.status === "downloading" || dlStatus.status === "processing") {
                        displayText += ` (${dlStatus.progress}%)`;
                    }
                    downloadStatusTextElement.textContent = displayText;
                } else {
                    downloadStatusTextElement.textContent = ""; // Clear if no message
                }
            }
        });

    } else {
        console.error('electronAPI not found in index.html. Check preload script.');
        updateStatusText("Error: UI bridge not available.");
        updateConnectionStatus("offline");
    }

    // Trigger home view on initial load
    if(homeButton) homeButton.click();
    else { // Fallback if no home button (e.g. simplified HTML)
        updateStatusText("Welcome to Flutter Earth!");
    }
});

console.log('Main renderer script (renderer.js) loaded.');
