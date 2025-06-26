document.addEventListener('DOMContentLoaded', async () => {
    // --- DOM Elements ---
    const downloadForm = document.getElementById('downloadForm');
    const aoiField = document.getElementById('aoiField');
    const startDateField = document.getElementById('startDateField');
    const endDateField = document.getElementById('endDateField');
    const sensorCombo = document.getElementById('sensorCombo');
    const outputDirField = document.getElementById('outputDirField');
    const browseOutputDirButton = document.getElementById('browseOutputDirButton');
    const cloudMaskBox = document.getElementById('cloudMaskBox');
    const maxCloudSpin = document.getElementById('maxCloudSpin');

    const useBestResolutionBox = document.getElementById('useBestResolutionBox');
    const targetResolutionSpin = document.getElementById('targetResolutionSpin');
    const tilingMethodCombo = document.getElementById('tilingMethodCombo');
    const numSubsectionsSpin = document.getElementById('numSubsectionsSpin');
    const overwriteBox = document.getElementById('overwriteBox');
    const cleanupTilesBox = document.getElementById('cleanupTilesBox');

    const startDownloadButton = document.getElementById('startDownloadButton');
    const cancelDownloadButton = document.getElementById('cancelDownloadButton');
    const downloadProgressBar = document.getElementById('downloadProgressBar');
    const downloadStatusText = document.getElementById('downloadStatusText');
    const downloadLogArea = document.getElementById('downloadLogArea');

    // --- Helper Functions ---
    function appendToLog(message) {
        const timestamp = new Date().toLocaleTimeString();
        downloadLogArea.value += `[${timestamp}] ${message}\n`;
        downloadLogArea.scrollTop = downloadLogArea.scrollHeight; // Auto-scroll
    }

    function updateDownloadProgress(current, total) {
        if (total > 0) {
            const percentage = (current / total) * 100;
            downloadProgressBar.value = percentage;
            downloadStatusText.textContent = `Downloading: ${current} / ${total} (${percentage.toFixed(0)}%)`;
        } else {
            downloadProgressBar.value = 0;
        }
    }

    function setDownloadStatusMessage(message) {
        downloadStatusText.textContent = message;
    }


    // --- Initialize Form with Settings & Populate Combos ---
    async function initializeForm() {
        if (!window.electronAPI || !window.electronAPI.invokePython) {
            console.error("electronAPI not available.");
            appendToLog("Error: Cannot connect to backend services.");
            return;
        }

        try {
            const settings = await window.electronAPI.invokePython('get-all-settings');
            if (settings) {
                // AOI might not be in settings, typically user-entered per session
                startDateField.value = settings.start_date || new Date().toISOString().split('T')[0];
                endDateField.value = settings.end_date || new Date().toISOString().split('T')[0];
                outputDirField.value = settings.output_dir || '';
                cloudMaskBox.checked = settings.cloud_mask === true; // Ensure boolean
                maxCloudSpin.value = settings.max_cloud_cover !== undefined ? settings.max_cloud_cover : 20;

                useBestResolutionBox.checked = settings.use_best_resolution !== undefined ? settings.use_best_resolution : true;
                targetResolutionSpin.value = settings.target_resolution || 30;
                targetResolutionSpin.disabled = useBestResolutionBox.checked;

                tilingMethodCombo.value = settings.tiling_method || "degree";
                numSubsectionsSpin.value = settings.num_subsections || 100;
                numSubsectionsSpin.disabled = tilingMethodCombo.value !== "pixel";

                overwriteBox.checked = settings.overwrite_existing === true;
                cleanupTilesBox.checked = settings.cleanup_tiles !== undefined ? settings.cleanup_tiles : true;

                // Populate sensor combo
                const sensors = await window.electronAPI.invokePython('get-all-sensors');
                sensorCombo.innerHTML = ''; // Clear existing
                if (sensors && Array.isArray(sensors)) {
                    sensors.forEach(sensorName => {
                        const option = document.createElement('option');
                        option.value = sensorName;
                        option.textContent = sensorName;
                        sensorCombo.appendChild(option);
                    });
                    if (settings.sensor_priority && settings.sensor_priority.length > 0) {
                        sensorCombo.value = settings.sensor_priority[0];
                    } else if (sensors.length > 0) {
                        sensorCombo.value = sensors[0]; // Default to first if no priority
                    }
                }
                 appendToLog("Download form initialized with current settings.");
            } else {
                 appendToLog("Could not load initial settings for the download form.");
            }
        } catch (error) {
            console.error("Error initializing download form:", error);
            appendToLog(`Error initializing form: ${error.message || error}`);
        }
    }

    // --- Event Listeners for Form Inputs (to save settings immediately) ---
    async function saveSetting(key, value) {
         if (!window.electronAPI) return;
        try {
            await window.electronAPI.invokePython('set-setting', key, value);
            // console.log(`Setting ${key} saved: ${value}`);
        } catch (error) {
            console.error(`Error saving setting ${key}:`, error);
            appendToLog(`Error saving setting ${key}: ${error.message || error}`);
        }
    }

    // Example listeners (add for all relevant fields if they should persist immediately)
    if (outputDirField) outputDirField.addEventListener('change', (e) => saveSetting('output_dir', e.target.value));
    if (cloudMaskBox) cloudMaskBox.addEventListener('change', (e) => saveSetting('cloud_mask', e.target.checked));
    if (maxCloudSpin) maxCloudSpin.addEventListener('change', (e) => saveSetting('max_cloud_cover', parseFloat(e.target.value)));

    if (useBestResolutionBox) useBestResolutionBox.addEventListener('change', (e) => {
        targetResolutionSpin.disabled = e.target.checked;
        saveSetting('use_best_resolution', e.target.checked);
    });
    if (targetResolutionSpin) targetResolutionSpin.addEventListener('change', (e) => saveSetting('target_resolution', parseInt(e.target.value, 10)));

    if (tilingMethodCombo) tilingMethodCombo.addEventListener('change', (e) => {
        numSubsectionsSpin.disabled = e.target.value !== "pixel";
        saveSetting('tiling_method', e.target.value);
    });
    if (numSubsectionsSpin) numSubsectionsSpin.addEventListener('change', (e) => saveSetting('num_subsections', parseInt(e.target.value, 10)));

    if (overwriteBox) overwriteBox.addEventListener('change', (e) => saveSetting('overwrite_existing', e.target.checked));
    if (cleanupTilesBox) cleanupTilesBox.addEventListener('change', (e) => saveSetting('cleanup_tiles', e.target.checked));
    // Note: AOI, start/end date, sensor are typically per-download, not saved as global settings this way.

    // --- Browse for Output Directory ---
    if (browseOutputDirButton) {
        browseOutputDirButton.addEventListener('click', async () => {
            if (!window.electronAPI) return;
            try {
                const result = await window.electronAPI.invokePython('select-directory-dialog');
                if (result && !result.canceled && result.filePaths.length > 0) {
                    const newPath = result.filePaths[0];
                    outputDirField.value = newPath;
                    await saveSetting('output_dir', newPath); // Save this new default
                }
            } catch (error) {
                console.error("Error selecting output directory:", error);
                appendToLog(`Error selecting directory: ${error.message || error}`);
            }
        });
    }

    // --- Form Submission (Start Download) ---
    if (downloadForm) {
        downloadForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            if (!window.electronAPI) {
                appendToLog("Cannot start download: backend connection not available.");
                return;
            }

            const aoi = aoiField.value.trim();
            const outputDir = outputDirField.value.trim();

            if (!aoi) {
                alert("Area of Interest (AOI) cannot be empty.");
                appendToLog("Validation Error: AOI is empty.");
                return;
            }
            if (!outputDir) {
                alert("Output Directory cannot be empty.");
                appendToLog("Validation Error: Output Directory is empty.");
                return;
            }

            const params = {
                area_of_interest: aoi,
                start_date: startDateField.value,
                end_date: endDateField.value,
                sensor_name: sensorCombo.value,
                output_dir: outputDir,
                cloud_mask: cloudMaskBox.checked,
                max_cloud_cover: parseFloat(maxCloudSpin.value),
                use_best_resolution: useBestResolutionBox.checked,
                target_resolution: parseInt(targetResolutionSpin.value, 10),
                tiling_method: tilingMethodCombo.value,
                num_subsections: parseInt(numSubsectionsSpin.value, 10),
                overwrite_existing: overwriteBox.checked,
                cleanup_tiles: cleanupTilesBox.checked
            };

            appendToLog(`Starting download with params: ${JSON.stringify(params, null, 2)}`);
            setDownloadStatusMessage("Download initiated...");
            downloadProgressBar.value = 0;

            try {
                const result = await window.electronAPI.invokePython('start-download-with-params', params);
                if (result && result.success) {
                    appendToLog(`Download started successfully. Message: ${result.message || ''}`);
                    // Progress will be handled by onDownloadProgressUpdated from main process via polling get_download_status
                } else {
                    const errorMsg = result ? result.error || result.message : "Unknown error";
                    appendToLog(`Failed to start download: ${errorMsg}`);
                    setDownloadStatusMessage(`Error: ${errorMsg}`);
                    alert(`Failed to start download: ${errorMsg}`);
                }
            } catch (error) {
                console.error("Error starting download:", error);
                appendToLog(`Critical error starting download: ${error.message || error}`);
                setDownloadStatusMessage(`Error: ${error.message || error}`);
                alert(`Critical error starting download: ${error.message || error}`);
            }
        });
    }

    // --- Cancel Download ---
    if (cancelDownloadButton) {
        cancelDownloadButton.addEventListener('click', async () => {
             if (!window.electronAPI) {
                appendToLog("Cannot cancel download: backend connection not available.");
                return;
            }
            appendToLog("Requesting download cancellation...");
            try {
                const result = await window.electronAPI.invokePython('cancel-download');
                 if (result && result.success) {
                    appendToLog("Download cancellation requested successfully.");
                    setDownloadStatusMessage("Download cancellation requested.");
                } else {
                    const errorMsg = result ? result.error || result.message : "Unknown error";
                    appendToLog(`Failed to request cancellation: ${errorMsg}`);
                    alert(`Failed to request cancellation: ${errorMsg}`);
                }
            } catch (error) {
                console.error("Error cancelling download:", error);
                appendToLog(`Critical error cancelling download: ${error.message || error}`);
                alert(`Critical error cancelling download: ${error.message || error}`);
            }
        });
    }

    // --- Listen for Global Download Status Updates (from polling in main renderer.js) ---
    // This view-specific script doesn't need to listen to onDownloadStatusUpdate
    // if the main renderer.js already updates the global status bar.
    // However, if this view needs more detailed progress or its own progress bar,
    // it could also listen. For now, we assume the global status bar is sufficient.
    // If this view had its own progress bar (like downloadProgressBar here), we would update it.
    // The QML had `onDownloadProgressUpdated` and `onDownloadErrorOccurred` signals.
    // The current polling mechanism in main.js sends 'download-status-update'.

    // Let's make this view's progress bar also listen to the global 'download-status-update'
    if (window.electronAPI && window.electronAPI.onDownloadStatusUpdate) {
        window.electronAPI.onDownloadStatusUpdate((dlStatus) => {
            // console.log("DownloadView received dlStatus:", dlStatus);
            if (dlStatus) {
                if (dlStatus.status === "downloading" || dlStatus.status === "processing") {
                    updateDownloadProgress(dlStatus.progress, 100); // Assuming progress is 0-100
                    setDownloadStatusMessage(dlStatus.message + ` (${dlStatus.progress}%)`);
                } else if (dlStatus.status === "complete") {
                    updateDownloadProgress(100, 100);
                    setDownloadStatusMessage(dlStatus.message || "Download complete.");
                    appendToLog(dlStatus.message || "Download complete.");
                } else if (dlStatus.status === "error") {
                    downloadProgressBar.value = 0; // Or indicate error state
                    setDownloadStatusMessage(`Error: ${dlStatus.message}`);
                    appendToLog(`Error: ${dlStatus.message}`);
                } else if (dlStatus.status === "idle") {
                    downloadProgressBar.value = 0;
                    setDownloadStatusMessage(dlStatus.message || "Idle.");
                } else {
                    setDownloadStatusMessage(dlStatus.message || "Status unknown.");
                }
                // Potentially update downloadLogArea with more detailed messages if provided in dlStatus
            }
        });
    }

    // --- Config Change Listener (from QML) ---
    // If settings change elsewhere (e.g. direct config file edit then reload in settings),
    // this view should update its defaults.
    // This requires a 'config-changed' event from main process.
    // For now, initializeForm loads current settings on view load.
    // If electronAPI.onConfigChanged were available:
    // window.electronAPI.onConfigChanged((newConfig) => { initializeForm(); });


    // Initial setup
    initializeForm();
    appendToLog("Download View Loaded.");
});
console.log('Download script (download.js) loaded.');
