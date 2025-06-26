document.addEventListener('DOMContentLoaded', () => {
    // --- DOM Elements ---
    const loadRasterButton = document.getElementById('loadRasterButton');
    const loadVectorButton = document.getElementById('loadVectorButton');
    const clearAllDataButton = document.getElementById('clearAllDataButton');

    const rasterDataSection = document.getElementById('rasterDataSection');
    const rasterFilePathElement = document.getElementById('rasterFilePath');
    const rasterDimensionsElement = document.getElementById('rasterDimensions');
    const rasterBandsElement = document.getElementById('rasterBands');
    const rasterCRSElement = document.getElementById('rasterCRS');
    const rasterDataTypeElement = document.getElementById('rasterDataType');
    const rasterNoDataElement = document.getElementById('rasterNoData');
    const rasterBoundsElement = document.getElementById('rasterBounds');

    const vectorDataSection = document.getElementById('vectorDataSection');
    const vectorFilePathElement = document.getElementById('vectorFilePath');
    const vectorFeatureCountElement = document.getElementById('vectorFeatureCount');
    const vectorGeomTypesElement = document.getElementById('vectorGeomTypes');
    const vectorCRSElement = document.getElementById('vectorCRS');
    const vectorBoundsElement = document.getElementById('vectorBounds');
    const vectorAttributesElement = document.getElementById('vectorAttributes');

    const noDataLoadedMessage = document.getElementById('noDataLoadedMessage');

    // --- State ---
    let currentRasterFile = "";
    let currentVectorFile = "";

    // --- Helper Functions ---
    function showRasterData(filePath, data) {
        currentRasterFile = filePath;
        rasterFilePathElement.textContent = filePath;
        if (data && data.success) {
            rasterDimensionsElement.textContent = (data.width && data.height) ? `${data.width} x ${data.height}` : 'N/A';
            rasterBandsElement.textContent = Array.isArray(data.bands) ? data.bands.map(b => b.name || b).join(', ') : (data.bands || 'N/A');
            rasterCRSElement.textContent = data.crs || 'N/A';
            rasterDataTypeElement.textContent = data.dtype || 'N/A';
            rasterNoDataElement.textContent = data.nodata !== undefined ? String(data.nodata) : 'N/A';
            rasterBoundsElement.textContent = data.bounds ?
                `(${data.bounds.left.toFixed(4)}, ${data.bounds.bottom.toFixed(4)}) to (${data.bounds.right.toFixed(4)}, ${data.bounds.top.toFixed(4)})`
                : 'N/A';
            rasterDataSection.style.display = 'block';
        } else {
            rasterDimensionsElement.textContent = 'Error loading data';
            rasterBandsElement.textContent = data ? data.error : 'N/A';
            rasterCRSElement.textContent = '';
            rasterDataTypeElement.textContent = '';
            rasterNoDataElement.textContent = '';
            rasterBoundsElement.textContent = '';
            rasterDataSection.style.display = 'block'; // Show section to display error
        }
        updateUIVisibility();
    }

    function showVectorData(filePath, data) {
        currentVectorFile = filePath;
        vectorFilePathElement.textContent = filePath;
        if (data && data.success) {
            vectorFeatureCountElement.textContent = data.feature_count !== undefined ? data.feature_count : 'N/A';
            vectorGeomTypesElement.textContent = Array.isArray(data.geometry_types) ? data.geometry_types.join(', ') : (data.geometry_types || 'N/A');
            vectorCRSElement.textContent = data.crs || 'N/A';
            vectorBoundsElement.textContent = Array.isArray(data.bounds) && data.bounds.length === 4 ?
                `(${data.bounds[0].toFixed(4)}, ${data.bounds[1].toFixed(4)}) to (${data.bounds[2].toFixed(4)}, ${data.bounds[3].toFixed(4)})`
                : 'N/A';
            vectorAttributesElement.textContent = Array.isArray(data.columns) ? data.columns.join(', ') : (data.columns || 'N/A');
            vectorDataSection.style.display = 'block';
        } else {
            vectorFeatureCountElement.textContent = 'Error loading data';
            vectorGeomTypesElement.textContent = data ? data.error : 'N/A';
            vectorCRSElement.textContent = '';
            vectorBoundsElement.textContent = '';
            vectorAttributesElement.textContent = '';
            vectorDataSection.style.display = 'block'; // Show section to display error
        }
        updateUIVisibility();
    }

    function clearRasterDisplay() {
        currentRasterFile = "";
        rasterDataSection.style.display = 'none';
        rasterFilePathElement.textContent = '';
        // Clear other raster fields if desired
    }

    function clearVectorDisplay() {
        currentVectorFile = "";
        vectorDataSection.style.display = 'none';
        vectorFilePathElement.textContent = '';
        // Clear other vector fields
    }

    function updateUIVisibility() {
        const hasRaster = currentRasterFile !== "";
        const hasVector = currentVectorFile !== "";

        rasterDataSection.style.display = hasRaster ? 'block' : 'none';
        vectorDataSection.style.display = hasVector ? 'block' : 'none';

        if (!hasRaster && !hasVector) {
            noDataLoadedMessage.style.display = 'block';
            clearAllDataButton.disabled = true;
        } else {
            noDataLoadedMessage.style.display = 'none';
            clearAllDataButton.disabled = false;
        }
    }

    // --- Event Listeners ---
    if (loadRasterButton) {
        loadRasterButton.addEventListener('click', async () => {
            if (!window.electronAPI) return;
            try {
                const result = await window.electronAPI.invokePython('select-file-dialog', {
                    title: "Select Raster File",
                    filters: [
                        { name: 'GeoTIFF Files', extensions: ['tif', 'tiff'] },
                        { name: 'All Files', extensions: ['*'] }
                    ]
                });
                if (result && !result.canceled && result.filePaths.length > 0) {
                    const filePath = result.filePaths[0];
                    const rasterInfo = await window.electronAPI.invokePython('load-raster-data', filePath);
                    showRasterData(filePath, rasterInfo);
                }
            } catch (error) {
                console.error("Error loading raster data:", error);
                showRasterData("", { success: false, error: error.message || "Failed to load raster." });
            }
        });
    }

    if (loadVectorButton) {
        loadVectorButton.addEventListener('click', async () => {
            if (!window.electronAPI) return;
            try {
                const result = await window.electronAPI.invokePython('select-file-dialog', {
                    title: "Select Vector File",
                    filters: [
                        { name: 'Vector Files', extensions: ['geojson', 'json', 'shp', 'kml', 'kmz'] },
                        { name: 'All Files', extensions: ['*'] }
                    ]
                });
                if (result && !result.canceled && result.filePaths.length > 0) {
                    const filePath = result.filePaths[0];
                    const vectorInfo = await window.electronAPI.invokePython('load-vector-data', filePath);
                    showVectorData(filePath, vectorInfo);
                }
            } catch (error) {
                console.error("Error loading vector data:", error);
                showVectorData("", { success: false, error: error.message || "Failed to load vector." });
            }
        });
    }

    if (clearAllDataButton) {
        clearAllDataButton.addEventListener('click', () => {
            clearRasterDisplay();
            clearVectorDisplay();
            updateUIVisibility();
        });
    }

    // Initial UI state
    updateUIVisibility();
});
console.log('Data Viewer script (data-viewer.js) loaded.');
