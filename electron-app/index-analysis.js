document.addEventListener('DOMContentLoaded', async () => {
    // --- DOM Elements ---
    const indexAnalysisForm = document.getElementById('indexAnalysisForm');
    const addRasterFilesButton = document.getElementById('addRasterFilesButton');
    const clearRasterFilesButton = document.getElementById('clearRasterFilesButton');
    const selectedFilesList = document.getElementById('selectedFilesList');
    const noFilesSelectedMsg = document.getElementById('noFilesSelected');

    const indicesSelectionArea = document.getElementById('indicesSelectionArea');
    const outputDirFieldIA = document.getElementById('outputDirFieldIA'); // IA suffix to avoid conflict if loaded with other views
    const browseOutputDirButtonIA = document.getElementById('browseOutputDirButtonIA');

    const startIndexAnalysisButton = document.getElementById('startIndexAnalysisButton');
    const analysisStatusText = document.getElementById('analysisStatusText');

    // --- State Variables ---
    let selectedFiles = [];
    let availableIndices = []; // Will be array of {id, name, description, ...} objects
    let selectedIndices = []; // Will be array of index IDs (e.g., "NDVI")

    // --- Helper Functions ---
    function updateSelectedFilesList() {
        selectedFilesList.innerHTML = '';
        if (selectedFiles.length === 0) {
            noFilesSelectedMsg.style.display = 'block';
            clearRasterFilesButton.disabled = true;
        } else {
            noFilesSelectedMsg.style.display = 'none';
            clearRasterFilesButton.disabled = false;
            selectedFiles.forEach((filePath, index) => {
                const li = document.createElement('li');

                const span = document.createElement('span');
                // Display only filename for brevity
                const fileName = filePath.includes('/') ? filePath.substring(filePath.lastIndexOf('/') + 1) : filePath.substring(filePath.lastIndexOf('\\') + 1);
                span.textContent = fileName;
                span.title = filePath; // Show full path on hover
                li.appendChild(span);

                const removeButton = document.createElement('button');
                removeButton.textContent = 'Remove';
                removeButton.type = 'button';
                removeButton.addEventListener('click', () => {
                    selectedFiles.splice(index, 1);
                    updateSelectedFilesList();
                    updateStartButtonState();
                });
                li.appendChild(removeButton);
                selectedFilesList.appendChild(li);
            });
        }
        updateStartButtonState();
    }

    function updateIndicesSelectionArea() {
        indicesSelectionArea.innerHTML = '';
        if (availableIndices && Array.isArray(availableIndices)) {
            availableIndices.forEach(indexInfo => {
                const label = document.createElement('label');
                const checkbox = document.createElement('input');
                checkbox.type = 'checkbox';
                checkbox.value = indexInfo.name; // Assuming 'name' is the ID like "NDVI"
                checkbox.checked = selectedIndices.includes(indexInfo.name);
                checkbox.addEventListener('change', (event) => {
                    if (event.target.checked) {
                        if (!selectedIndices.includes(event.target.value)) {
                            selectedIndices.push(event.target.value);
                        }
                    } else {
                        selectedIndices = selectedIndices.filter(id => id !== event.target.value);
                    }
                    updateStartButtonState();
                });
                label.appendChild(checkbox);
                label.appendChild(document.createTextNode(` ${indexInfo.name} - ${indexInfo.full_name || indexInfo.description}`)); // Use full_name or description
                indicesSelectionArea.appendChild(label);
            });
        }
    }

    function updateStartButtonState() {
        startIndexAnalysisButton.disabled = !(selectedFiles.length > 0 && selectedIndices.length > 0 && outputDirFieldIA.value.trim() !== "");
    }

    // --- Initialize Form ---
    async function initializeIndexAnalysisForm() {
        if (!window.electronAPI || !window.electronAPI.invokePython) {
            analysisStatusText.textContent = "Error: Backend connection failed.";
            return;
        }
        try {
            // Fetch available indices
            const indicesData = await window.electronAPI.invokePython('get-available-indices');
            if (indicesData && Array.isArray(indicesData)) {
                availableIndices = indicesData;
                updateIndicesSelectionArea();
            } else {
                console.error("Failed to load available indices or data is not an array:", indicesData);
                analysisStatusText.textContent = "Failed to load available indices.";
            }

            // Fetch default output directory
            const defaultOutputDir = await window.electronAPI.invokePython('get-setting', 'output_dir');
            if (defaultOutputDir) {
                outputDirFieldIA.value = defaultOutputDir;
            }
            updateStartButtonState();
        } catch (error) {
            console.error("Error initializing Index Analysis form:", error);
            analysisStatusText.textContent = `Error initializing: ${error.message || error}`;
        }
    }

    // --- Event Listeners ---
    if (addRasterFilesButton) {
        addRasterFilesButton.addEventListener('click', async () => {
            if (!window.electronAPI) return;
            try {
                // For selecting multiple files, we need a specific IPC in main.js
                const result = await window.electronAPI.invokePython('select-raster-files-dialog');
                if (result && !result.canceled && result.filePaths && result.filePaths.length > 0) {
                    result.filePaths.forEach(filePath => {
                        if (!selectedFiles.includes(filePath)) {
                            selectedFiles.push(filePath);
                        }
                    });
                    updateSelectedFilesList();
                }
            } catch (error) {
                console.error("Error selecting raster files:", error);
                analysisStatusText.textContent = `Error selecting files: ${error.message || error}`;
            }
        });
    }

    if (clearRasterFilesButton) {
        clearRasterFilesButton.addEventListener('click', () => {
            selectedFiles = [];
            updateSelectedFilesList();
        });
    }

    if (browseOutputDirButtonIA) {
        browseOutputDirButtonIA.addEventListener('click', async () => {
            if (!window.electronAPI) return;
            try {
                const result = await window.electronAPI.invokePython('select-directory-dialog');
                if (result && !result.canceled && result.filePaths.length > 0) {
                    outputDirFieldIA.value = result.filePaths[0];
                    updateStartButtonState();
                    // Optionally save this as the new default output_dir
                    // await window.electronAPI.invokePython('set-setting', 'output_dir', result.filePaths[0]);
                }
            } catch (error) {
                console.error("Error selecting output directory:", error);
                analysisStatusText.textContent = `Error selecting output dir: ${error.message || error}`;
            }
        });
    }
    if(outputDirFieldIA) {
        outputDirFieldIA.addEventListener('change', updateStartButtonState);
    }


    if (indexAnalysisForm) {
        indexAnalysisForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            if (startIndexAnalysisButton.disabled || !window.electronAPI) {
                return;
            }

            startIndexAnalysisButton.disabled = true;
            startIndexAnalysisButton.textContent = "Analysis Running...";
            analysisStatusText.textContent = "Starting analysis...";

            // Simplified band map (as in QML)
            // This should ideally be more sophisticated or user-configurable
            const bandMap = {
                'red': 3, 'nir': 4, 'blue': 1, 'green': 2, 'swir1': 5, 'swir2': 6
            };

            let overallSuccess = true;
            let errors = [];

            for (const indexType of selectedIndices) {
                analysisStatusText.textContent = `Processing ${indexType}...`;
                try {
                    const result = await window.electronAPI.invokePython('start-index-analysis', {
                        input_files: selectedFiles,
                        output_dir: outputDirFieldIA.value.trim(),
                        index_type: indexType,
                        band_map: bandMap // Sending the whole map
                    });

                    if (!result || !result.success) {
                        overallSuccess = false;
                        const errorMsg = result ? (result.error || `Failed to process ${indexType}`) : `Unknown error for ${indexType}`;
                        errors.push(errorMsg);
                        analysisStatusText.textContent = errorMsg;
                        console.error(`Error processing ${indexType}:`, result);
                        // break; // Optionally stop on first error
                    } else {
                         analysisStatusText.textContent = `${indexType} processed successfully.`;
                    }
                } catch (error) {
                    overallSuccess = false;
                    const errorMsg = `Critical error processing ${indexType}: ${error.message || error}`;
                    errors.push(errorMsg);
                    analysisStatusText.textContent = errorMsg;
                    console.error(errorMsg, error);
                    // break; // Optionally stop on first error
                }
            }

            if (overallSuccess) {
                analysisStatusText.textContent = "All selected index analyses completed successfully!";
                alert("Index analysis completed!");
            } else {
                analysisStatusText.textContent = `Analysis completed with errors: ${errors.join('; ')}`;
                alert(`Analysis completed with errors. Check status for details:\n- ${errors.join('\n- ')}`);
            }
            startIndexAnalysisButton.disabled = false;
            startIndexAnalysisButton.textContent = "Start Index Analysis";
            updateStartButtonState(); // Re-check conditions
        });
    }

    // Initial setup
    initializeIndexAnalysisForm();
});
console.log('Index Analysis script (index-analysis.js) loaded.');
