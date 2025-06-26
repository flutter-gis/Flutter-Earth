document.addEventListener('DOMContentLoaded', async () => {
    // --- DOM Elements ---
    const themeCategoriesContainer = document.getElementById('theme-categories');
    const themeGridContainer = document.getElementById('theme-grid');
    const useCharacterCatchphrasesCheckbox = document.getElementById('useCharacterCatchphrases');
    const showSpecialIconsCheckbox = document.getElementById('showSpecialIcons');
    const enableAnimatedBackgroundCheckbox = document.getElementById('enableAnimatedBackground');
    const outputDirField = document.getElementById('outputDirField');
    const browseOutputDirButton = document.getElementById('browseOutputDir');
    const reloadSettingsButton = document.getElementById('reloadSettings');
    const clearCacheAndLogsButton = document.getElementById('clearCacheAndLogs');

    let allSettings = {};
    let availableThemes = [];
    let currentThemeName = '';
    let currentThemeData = {};

    // --- Helper Functions ---
    function getThemeByName(themeName) {
        return availableThemes.find(t => t.name === themeName);
    }

    function renderThemes(selectedCategoryName) {
        themeGridContainer.innerHTML = ''; // Clear previous themes
        const themesToRender = selectedCategoryName === 'All' || !selectedCategoryName
            ? availableThemes
            : availableThemes.filter(theme => (theme.category || 'Other') === selectedCategoryName);

        themesToRender.forEach(theme => {
            const item = document.createElement('div');
            item.classList.add('theme-item');
            if (theme.name === currentThemeName) {
                item.classList.add('selected');
            }
            item.dataset.themeName = theme.name;

            const preview = document.createElement('div');
            preview.classList.add('theme-preview');
            preview.style.backgroundColor = theme.background || '#ffffff'; // Use a default if not specified
            preview.style.borderColor = theme.primary || '#000000';

            const info = document.createElement('div');
            info.classList.add('theme-info');
            const name = document.createElement('h4');
            name.textContent = theme.display_name || theme.name;
            const category = document.createElement('p');
            category.textContent = theme.category || 'Other';

            info.appendChild(name);
            info.appendChild(category);
            item.appendChild(preview);
            item.appendChild(info);

            item.addEventListener('click', async () => {
                if (theme.name !== currentThemeName) {
                    await window.electronAPI.invokePython('set-theme', theme.name);
                    // The backend should ideally signal a theme change,
                    // which would trigger a reload of settings and UI update.
                    // For now, manually refresh.
                    loadSettings();
                }
            });
            themeGridContainer.appendChild(item);
        });
    }

    function renderThemeCategories() {
        themeCategoriesContainer.innerHTML = '';
        const categories = ['All', ...new Set(availableThemes.map(theme => theme.category || 'Other'))];
        let currentSelectedCategory = 'All';

        categories.forEach(categoryName => {
            const button = document.createElement('button');
            button.textContent = categoryName;
            button.dataset.categoryName = categoryName;
            if (categoryName === currentSelectedCategory) {
                button.classList.add('active');
            }
            button.addEventListener('click', () => {
                currentSelectedCategory = categoryName;
                document.querySelectorAll('#theme-categories button').forEach(btn => btn.classList.remove('active'));
                button.classList.add('active');
                renderThemes(categoryName);
            });
            themeCategoriesContainer.appendChild(button);
        });
        renderThemes(currentSelectedCategory); // Initial render for "All"
    }


    function updateUIWithOptions(options) {
        const opts = options || {}; // Handle null or undefined options
        useCharacterCatchphrasesCheckbox.checked = opts.use_character_catchphrases === true;
        showSpecialIconsCheckbox.checked = opts.show_special_icons === true;
        enableAnimatedBackgroundCheckbox.checked = opts.enable_animated_background === true;
    }

    // --- Load Initial Settings ---
    async function loadSettings() {
        try {
            allSettings = await window.electronAPI.invokePython('get-all-settings');
            availableThemes = await window.electronAPI.invokePython('get-available-themes');
            currentThemeData = await window.electronAPI.invokePython('get-current-theme-data');

            if (allSettings && allSettings.theme) {
                currentThemeName = allSettings.theme;
            } else if (currentThemeData && currentThemeData.metadata && currentThemeData.metadata.name) {
                 currentThemeName = currentThemeData.metadata.name;
            }


            console.log("Initial allSettings:", allSettings);
            console.log("Initial availableThemes:", availableThemes);
            console.log("Initial currentThemeData:", currentThemeData);
            console.log("Initial currentThemeName:", currentThemeName);


            if (allSettings) {
                outputDirField.value = allSettings.output_dir || '';
            }

            if (currentThemeData && currentThemeData.options) {
                updateUIWithOptions(currentThemeData.options);
            } else if (allSettings && allSettings.theme_suboptions) {
                // Fallback if currentThemeData.options is not available
                let suboptions = allSettings.theme_suboptions;
                if (typeof suboptions === 'string') {
                    try { suboptions = JSON.parse(suboptions); } catch (e) { suboptions = {};}
                }
                updateUIWithOptions(suboptions);
            }


            if (availableThemes) {
                renderThemeCategories();
            }

        } catch (error) {
            console.error("Error loading settings:", error);
            alert("Failed to load settings. Check console for details.");
        }
    }

    // --- Event Listeners ---
    useCharacterCatchphrasesCheckbox.addEventListener('change', async (event) => {
        await window.electronAPI.invokePython('set-setting', 'use_character_catchphrases', event.target.checked);
        // Consider a more robust way to update theme options, perhaps by sending the whole suboptions object
    });
    showSpecialIconsCheckbox.addEventListener('change', async (event) => {
        await window.electronAPI.invokePython('set-setting', 'show_special_icons', event.target.checked);
    });
    enableAnimatedBackgroundCheckbox.addEventListener('change', async (event) => {
        await window.electronAPI.invokePython('set-setting', 'enable_animated_background', event.target.checked);
    });

    outputDirField.addEventListener('change', async (event) => {
        await window.electronAPI.invokePython('set-setting', 'output_dir', event.target.value);
    });

    if (browseOutputDirButton) {
        browseOutputDirButton.addEventListener('click', async () => {
            const result = await window.electronAPI.invokePython('select-directory-dialog');
            if (result && !result.canceled && result.filePaths.length > 0) {
                const newPath = result.filePaths[0];
                outputDirField.value = newPath;
                await window.electronAPI.invokePython('set-setting', 'output_dir', newPath);
            }
        });
    }

    if (reloadSettingsButton) {
        reloadSettingsButton.addEventListener('click', async () => {
            await window.electronAPI.invokePython('reload-config');
            await loadSettings(); // Reload settings into UI
            alert('Settings reloaded!');
        });
    }

    if (clearCacheAndLogsButton) {
        clearCacheAndLogsButton.addEventListener('click', async () => {
            const confirmed = confirm("Are you sure you want to clear all cache and log files? This action cannot be undone.");
            if (confirmed) {
                try {
                    await window.electronAPI.invokePython('clear-cache-and-logs');
                    alert('Cache and logs cleared successfully!');
                } catch (error) {
                    console.error("Error clearing cache and logs:", error);
                    alert('Failed to clear cache and logs. See console for details.');
                }
            }
        });
    }

    // --- IPC Listeners for backend updates (if any) ---
    // Example: window.electronAPI.onConfigChanged((newConfig) => { loadSettings(); });
    // This would require setting up listeners in preload.js and handlers in main.js
    // to forward signals from Python.

    // Initial load
    await loadSettings();
});

// Helper to save all theme sub-options at once (matching QML logic)
// This would be called by the individual checkbox listeners if preferred
async function saveThemeSubOptions() {
    const subOptions = {
        use_character_catchphrases: document.getElementById('useCharacterCatchphrases').checked,
        show_special_icons: document.getElementById('showSpecialIcons').checked,
        enable_animated_background: document.getElementById('enableAnimatedBackground').checked
    };
    // The QML version stringifies this. If your Python backend expects an object, don't stringify.
    // If it expects a JSON string (like in the QML), then stringify.
    // Assuming Python backend's setSetting for "theme_suboptions" handles a JS object directly or a JSON string.
    // Let's assume it handles a JS object for simplicity with Electron IPC.
    await window.electronAPI.invokePython('set-setting', 'theme_suboptions', subOptions);
    // Refresh relevant part of UI or reload all settings
    const updatedThemeData = await window.electronAPI.invokePython('get-current-theme-data');
    if (updatedThemeData && updatedThemeData.options) {
         updateUIWithOptions(updatedThemeData.options);
    }
}

// Modify checkbox listeners to call saveThemeSubOptions
document.getElementById('useCharacterCatchphrases').addEventListener('change', saveThemeSubOptions);
document.getElementById('showSpecialIcons').addEventListener('change', saveThemeSubOptions);
document.getElementById('enableAnimatedBackground').addEventListener('change', saveThemeSubOptions);
console.log('Settings script loaded.');
