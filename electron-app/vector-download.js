document.addEventListener('DOMContentLoaded', async () => {
    // --- DOM Elements ---
    const vectorDownloadForm = document.getElementById('vectorDownloadForm');
    const dataSourceCombo = document.getElementById('dataSourceCombo');
    const dataSourceDescription = document.getElementById('dataSourceDescription');
    const queryArea = document.getElementById('queryArea');
    const loadExampleQueryButton = document.getElementById('loadExampleQueryButton');
    const clearQueryButton = document.getElementById('clearQueryButton');
    const aoiFieldVD = document.getElementById('aoiFieldVD');
    const selectOnMapButtonVD = document.getElementById('selectOnMapButtonVD');
    const outputDirFieldVD = document.getElementById('outputDirFieldVD');
    const browseOutputDirButtonVD = document.getElementById('browseOutputDirButtonVD');
    const outputFormatCombo = document.getElementById('outputFormatCombo');
    const startVectorDownloadButton = document.getElementById('startVectorDownloadButton');
    const vectorDownloadStatusText = document.getElementById('vectorDownloadStatusText');

    // --- State Variables ---
    let dataSources = [];
    let outputFormats = [];
    let currentAoiFromMap = []; // To store AOI fetched from backend

    // --- Helper Functions ---
    function updateDataSourceDescription() {
        const selectedSource = dataSources.find(ds => ds.name === dataSourceCombo.value);
        if (selectedSource) {
            dataSourceDescription.textContent = selectedSource.description || '';
        } else {
            dataSourceDescription.textContent = '';
        }
        updateQueryPlaceholder();
        updateStartButtonState();
    }

    function updateQueryPlaceholder() {
        const selectedSourceValue = dataSourceCombo.value;
        if (selectedSourceValue === "Overpass API (OSM)") {
            queryArea.placeholder = "Enter Overpass QL query (e.g., [out:json]; node[\"amenity\"=\"school\"]({{bbox}}); out;)";
        } else if (selectedSourceValue === "WFS") {
            queryArea.placeholder = "Enter WFS service URL (e.g., https://example.com/geoserver/wfs?service=WFS&version=1.0.0&request=GetFeature&typeName=ns:layer&outputFormat=application/json)";
        } else if (selectedSourceValue === "GeoJSON URL") {
            queryArea.placeholder = "Enter direct GeoJSON file URL (e.g., https://example.com/data.geojson)";
        } else {
            queryArea.placeholder = "Enter query or URL...";
        }
    }

    function loadExampleQuery() {
        const selectedSourceValue = dataSourceCombo.value;
        if (selectedSourceValue === "Overpass API (OSM)") {
            queryArea.value = '[out:json];\n// Example: find schools in bounding box\nnode["amenity"="school"]({{bbox}});\nout;';
        } else if (selectedSourceValue === "WFS") {
            queryArea.value = 'https://example.com/geoserver/wfs?service=WFS&version=1.0.0&request=GetFeature&typeName=namespace:layer&outputFormat=application/json&bbox={bbox}';
        } else if (selectedSourceValue === "GeoJSON URL") {
            queryArea.value = 'https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson'; // Example public GeoJSON
        }
        updateStartButtonState();
    }

    function updateStartButtonState() {
        startVectorDownloadButton.disabled = !(queryArea.value.trim() !== "" && outputDirFieldVD.value.trim() !== "");
    }

    // --- Initialize Form ---
    async function initializeVectorDownloadForm() {
        if (!window.electronAPI || !window.electronAPI.invokePython) {
            vectorDownloadStatusText.textContent = "Error: Backend connection failed.";
            return;
        }
        try {
            dataSources = await window.electronAPI.invokePython('get-vector-data-sources');
            outputFormats = await window.electronAPI.invokePython('get-vector-output-formats');
            const defaultOutputDir = await window.electronAPI.invokePython('get-setting', 'output_dir');
            currentAoiFromMap = await window.electronAPI.invokePython('get-current-aoi') || [];


            if (dataSources && Array.isArray(dataSources)) {
                dataSourceCombo.innerHTML = '';
                dataSources.forEach(ds => {
                    const option = document.createElement('option');
                    option.value = ds.name; // Assuming 'name' is the value/ID
                    option.textContent = ds.name; // And also the display text
                    dataSourceCombo.appendChild(option);
                });
                if (dataSources.length > 0) dataSourceCombo.value = dataSources[0].name;
                updateDataSourceDescription();
            }

            if (outputFormats && Array.isArray(outputFormats)) {
                outputFormatCombo.innerHTML = '';
                outputFormats.forEach(format => {
                    const option = document.createElement('option');
                    option.value = format; // Assuming format is a string
                    option.textContent = format;
                    outputFormatCombo.appendChild(option);
                });
                if (outputFormats.length > 0) outputFormatCombo.value = outputFormats[0];
            }

            if (defaultOutputDir) {
                outputDirFieldVD.value = defaultOutputDir;
            }

            // aoiFieldVD.value = currentAoiFromMap.length > 0 ? JSON.stringify(currentAoiFromMap) : "";


            updateStartButtonState();
            vectorDownloadStatusText.textContent = "Ready.";

        } catch (error) {
            console.error("Error initializing Vector Download form:", error);
            vectorDownloadStatusText.textContent = `Error initializing: ${error.message || error}`;
        }
    }

    // --- Event Listeners ---
    if (dataSourceCombo) {
        dataSourceCombo.addEventListener('change', updateDataSourceDescription);
    }
    if (queryArea) {
        queryArea.addEventListener('input', updateStartButtonState);
    }
    if (loadExampleQueryButton) {
        loadExampleQueryButton.addEventListener('click', loadExampleQuery);
    }
    if (clearQueryButton) {
        clearQueryButton.addEventListener('click', () => {
            queryArea.value = '';
            updateStartButtonState();
        });
    }

    if (selectOnMapButtonVD) {
        selectOnMapButtonVD.addEventListener('click', async () => {
            if (!window.electronAPI) return;
            try {
                currentAoiFromMap = await window.electronAPI.invokePython('get-current-aoi') || [];
                if (currentAoiFromMap.length > 0) {
                    // Try to format as a simple bbox string if it looks like one, else stringify
                    if (currentAoiFromMap.length === 4 && currentAoiFromMap.every(n => typeof n === 'number')) {
                        aoiFieldVD.value = currentAoiFromMap.join(',');
                    } else {
                         aoiFieldVD.value = JSON.stringify(currentAoiFromMap);
                    }
                } else {
                    aoiFieldVD.value = ""; // Clear if no AOI from map
                    alert("No current AOI set from map. Please define one in the map view if available.");
                }
            } catch (error) {
                console.error("Error fetching AOI from map:", error);
                alert("Could not fetch AOI from map.");
            }
        });
    }

    if (outputDirFieldVD) {
        outputDirFieldVD.addEventListener('change', updateStartButtonState); // Though it's readonly, path might change via browse
    }

    if (browseOutputDirButtonVD) {
        browseOutputDirButtonVD.addEventListener('click', async () => {
            if (!window.electronAPI) return;
            try {
                const result = await window.electronAPI.invokePython('select-directory-dialog');
                if (result && !result.canceled && result.filePaths.length > 0) {
                    outputDirFieldVD.value = result.filePaths[0];
                    updateStartButtonState();
                    // Optionally save as new default output_dir
                    // await window.electronAPI.invokePython('set-setting', 'output_dir', result.filePaths[0]);
                }
            } catch (error) {
                console.error("Error selecting output directory:", error);
                vectorDownloadStatusText.textContent = `Error selecting output dir: ${error.message || error}`;
            }
        });
    }

    if (vectorDownloadForm) {
        vectorDownloadForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            if (startVectorDownloadButton.disabled || !window.electronAPI) return;

            startVectorDownloadButton.disabled = true;
            startVectorDownloadButton.textContent = "Downloading...";
            vectorDownloadStatusText.textContent = "Starting vector download...";

            let aoiList = [];
            const aoiString = aoiFieldVD.value.trim();
            if (aoiString) {
                try {
                    if (aoiString.startsWith("[")) { // Assume JSON array
                        aoiList = JSON.parse(aoiString);
                    } else { // Assume comma-separated numbers for bbox
                        aoiList = aoiString.split(",").map(x => parseFloat(x.trim()));
                        if (aoiList.some(isNaN) || (aoiList.length !== 0 && aoiList.length !== 4)) {
                            throw new Error("Bounding box must be 4 numbers (minLon,minLat,maxLon,maxLat) or empty.");
                        }
                    }
                } catch (e) {
                    vectorDownloadStatusText.textContent = `Invalid AOI format: ${e.message}`;
                    alert(`Invalid AOI format: ${e.message}`);
                    startVectorDownloadButton.disabled = false;
                    startVectorDownloadButton.textContent = "Start Vector Download";
                    return;
                }
            }

            // Generate output filename (Python side might do this better based on query/source)
            const timestamp = new Date().toISOString().replace(/[:.]/g, "-");
            const formatExtension = (outputFormatCombo.value || "geojson").toLowerCase();
            const outputFilename = `vector_data_${dataSourceCombo.value.replace(/\s/g, '_')}_${timestamp}.${formatExtension}`;
            const outputPath = `${outputDirFieldVD.value.trim()}/${outputFilename}`;


            const params = {
                aoi: aoiList, // Send parsed list
                query: queryArea.value.trim(),
                output_path: outputPath, // Let Python create the full path with filename
                output_format: outputFormatCombo.value
            };

            try {
                const result = await window.electronAPI.invokePython('start-vector-download', params);
                if (result && result.success) {
                    vectorDownloadStatusText.textContent = `Download successful: ${result.message || outputPath}`;
                    alert(`Download successful: ${result.message || outputPath}`);
                } else {
                    const errorMsg = result ? (result.error || "Download failed.") : "Unknown download error.";
                    vectorDownloadStatusText.textContent = `Error: ${errorMsg}`;
                    alert(`Download failed: ${errorMsg}`);
                }
            } catch (error) {
                console.error("Error starting vector download:", error);
                vectorDownloadStatusText.textContent = `Critical error: ${error.message || error}`;
                alert(`Critical error during download: ${error.message || error}`);
            }

            startVectorDownloadButton.disabled = false;
            startVectorDownloadButton.textContent = "Start Vector Download";
            updateStartButtonState();
        });
    }

    // Initial setup
    initializeVectorDownloadForm();
});
console.log('Vector Download script (vector-download.js) loaded.');
