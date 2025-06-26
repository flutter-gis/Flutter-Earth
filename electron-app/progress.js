document.addEventListener('DOMContentLoaded', () => {
    // --- DOM Elements ---
    const currentTaskStatusElement = document.getElementById('currentTaskStatus');
    const currentTaskMessageElement = document.getElementById('currentTaskMessage');
    const currentTaskProgressBar = document.getElementById('currentTaskProgressBar');

    const refreshHistoryButton = document.getElementById('refreshHistoryButton');
    const clearHistoryButton = document.getElementById('clearHistoryButton');
    const taskHistoryBody = document.getElementById('taskHistoryBody');
    const noHistoryMessage = document.getElementById('noHistoryMessage');

    // --- Helper Functions ---
    function updateCurrentTaskDisplay(dlStatus) {
        if (!dlStatus) {
            currentTaskStatusElement.textContent = "Unknown";
            currentTaskMessageElement.textContent = "-";
            currentTaskProgressBar.value = 0;
            return;
        }

        currentTaskStatusElement.textContent = dlStatus.status ? dlStatus.status.charAt(0).toUpperCase() + dlStatus.status.slice(1) : "Unknown";
        currentTaskMessageElement.textContent = dlStatus.message || "-";

        if (dlStatus.status === "downloading" || dlStatus.status === "processing") {
            currentTaskProgressBar.value = dlStatus.progress || 0;
            currentTaskProgressBar.style.display = 'block';
        } else if (dlStatus.status === "complete") {
            currentTaskProgressBar.value = 100;
            currentTaskProgressBar.style.display = 'block';
        } else {
            currentTaskProgressBar.value = 0;
            // currentTaskProgressBar.style.display = 'none'; // Or keep it visible but empty
        }
    }

    async function loadTaskHistory() {
        if (!window.electronAPI || !window.electronAPI.invokePython) {
            console.error("electronAPI not available for loading history.");
            noHistoryMessage.textContent = "Error: Backend connection failed.";
            noHistoryMessage.style.display = 'block';
            taskHistoryBody.innerHTML = '';
            return;
        }

        try {
            const history = await window.electronAPI.invokePython('get-download-history');
            taskHistoryBody.innerHTML = ''; // Clear existing rows

            if (history && Array.isArray(history) && history.length > 0) {
                noHistoryMessage.style.display = 'none';
                history.forEach(task => {
                    const row = taskHistoryBody.insertRow();
                    row.insertCell().textContent = task.task_id || 'N/A';
                    row.insertCell().textContent = task.start_time ? new Date(task.start_time).toLocaleString() : 'N/A';
                    row.insertCell().textContent = task.end_time ? new Date(task.end_time).toLocaleString() : '-';
                    row.insertCell().textContent = task.status || 'Unknown';

                    let details = '';
                    if (task.params) { // Assuming params might be stored with history
                        details = `Sensor: ${task.params.sensor_name || 'N/A'}`;
                        // Add more relevant params if available and desired
                    } else if (task.message) {
                        details = task.message;
                    }
                    row.insertCell().textContent = details || '-';
                });
            } else {
                noHistoryMessage.textContent = "No task history available.";
                noHistoryMessage.style.display = 'block';
            }
        } catch (error) {
            console.error("Error loading task history:", error);
            noHistoryMessage.textContent = `Error loading history: ${error.message || error}`;
            noHistoryMessage.style.display = 'block';
        }
    }

    // --- Event Listeners ---
    if (refreshHistoryButton) {
        refreshHistoryButton.addEventListener('click', loadTaskHistory);
    }

    if (clearHistoryButton) {
        clearHistoryButton.addEventListener('click', async () => {
            if (!window.electronAPI || !window.electronAPI.invokePython) {
                console.error("electronAPI not available for clearing history.");
                alert("Error: Backend connection failed.");
                return;
            }
            const confirmed = confirm("Are you sure you want to clear all task history? This action cannot be undone.");
            if (confirmed) {
                try {
                    const result = await window.electronAPI.invokePython('clear-download-history');
                    if (result && result.success) {
                        alert("Task history cleared successfully.");
                        loadTaskHistory(); // Refresh the view
                    } else {
                        alert(`Failed to clear history: ${result ? result.error : 'Unknown error'}`);
                    }
                } catch (error) {
                    console.error("Error clearing task history:", error);
                    alert(`Error clearing history: ${error.message || error}`);
                }
            }
        });
    }

    // Listen for global download status updates to update the "Current Task" section
    if (window.electronAPI && window.electronAPI.onDownloadStatusUpdate) {
        window.electronAPI.onDownloadStatusUpdate(updateCurrentTaskDisplay);
    }

    // Fetch initial current task status (could also be part of an initial app state load)
    async function fetchInitialCurrentTaskStatus() {
        if (window.electronAPI && window.electronAPI.invokePython) {
            try {
                const initialDlStatus = await window.electronAPI.invokePython('get-download-status');
                updateCurrentTaskDisplay(initialDlStatus);
            } catch (error) {
                console.warn("Could not fetch initial download status for ProgressView:", error);
                updateCurrentTaskDisplay(null); // Show as unknown/idle
            }
        }
    }

    // Initial Load
    loadTaskHistory();
    fetchInitialCurrentTaskStatus();
});
console.log('Progress script (progress.js) loaded.');
