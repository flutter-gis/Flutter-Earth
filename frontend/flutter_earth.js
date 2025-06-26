// Flutter Earth JavaScript - Converted from QML

class FlutterEarth {
    constructor() {
        this.currentView = 'welcome';
        this.connectionStatus = 'offline';
        this.statusBarText = 'Initializing...';
        this.currentDate = new Date();
        this.selectedDate = null;
        this.calendarTarget = null;
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.hideSplashScreen();
        this.updateConnectionStatus('online');
        this.loadSensors();
        this.setupCalendar();
    }

    setupEventListeners() {
        // Sidebar navigation
        document.querySelectorAll('.sidebar-item').forEach(item => {
            item.addEventListener('click', (e) => {
                const view = item.dataset.view;
                const panel = item.dataset.panel;
                
                if (view) {
                    this.switchView(view);
                } else if (panel) {
                    this.showPanel(panel);
                }
                
                // Update active state
                document.querySelectorAll('.sidebar-item').forEach(i => i.classList.remove('active'));
                item.classList.add('active');
            });
        });

        // Help button
        document.getElementById('help-button').addEventListener('click', () => {
            this.showHelpPopup();
        });

        // Auth dialog
        document.getElementById('auth-submit').addEventListener('click', () => {
            this.submitAuth();
        });

        document.getElementById('auth-help').addEventListener('click', () => {
            this.showHelpPopup();
        });

        // Help popup close
        document.getElementById('help-close').addEventListener('click', () => {
            this.hideHelpPopup();
        });

        // Calendar buttons
        document.getElementById('calendar-prev').addEventListener('click', () => {
            this.previousMonth();
        });

        document.getElementById('calendar-next').addEventListener('click', () => {
            this.nextMonth();
        });

        // Map selector
        document.getElementById('map-selector-btn').addEventListener('click', () => {
            this.showMapSelector();
        });

        document.getElementById('map-confirm').addEventListener('click', () => {
            this.confirmMapSelection();
        });

        document.getElementById('map-cancel').addEventListener('click', () => {
            this.hideMapSelector();
        });

        // Calendar buttons
        document.querySelectorAll('.calendar-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.calendarTarget = e.target.dataset.target;
                this.showCalendar();
            });
        });

        // Download controls
        document.getElementById('start-download').addEventListener('click', () => {
            this.startDownload();
        });

        document.getElementById('cancel-download').addEventListener('click', () => {
            this.cancelDownload();
        });

        // Browse button
        document.getElementById('browse-btn').addEventListener('click', () => {
            this.browseOutputDirectory();
        });

        // Theme selector
        document.getElementById('theme-select').addEventListener('change', (e) => {
            this.changeTheme(e.target.value);
        });

        // Modal backdrop clicks
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    modal.style.display = 'none';
                }
            });
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            this.handleKeyboardShortcuts(e);
        });
    }

    hideSplashScreen() {
        setTimeout(() => {
            const splash = document.getElementById('splash-screen');
            splash.classList.add('hidden');
            setTimeout(() => {
                splash.style.display = 'none';
            }, 300);
        }, 2000);
    }

    switchView(viewName) {
        // Hide all views
        document.querySelectorAll('.view-content').forEach(view => {
            view.classList.remove('active');
        });

        // Show selected view
        const targetView = document.getElementById(`${viewName}-view`);
        if (targetView) {
            targetView.classList.add('active');
            this.currentView = viewName;
        }

        // Update page title
        document.title = `Flutter Earth - ${this.getViewTitle(viewName)}`;
    }

    getViewTitle(viewName) {
        const titles = {
            'welcome': 'Home',
            'map': 'Map',
            'download': 'Download',
            'satelliteInfo': 'Satellite Info',
            'indexAnalysis': 'Index Analysis',
            'vectorDownload': 'Vector Download',
            'dataViewer': 'Data Viewer',
            'progress': 'Progress',
            'settings': 'Settings',
            'about': 'About'
        };
        return titles[viewName] || 'Flutter Earth';
    }

    showPanel(panelType) {
        // This would show dockable panels like toolbox, bookmarks, etc.
        console.log(`Showing panel: ${panelType}`);
        this.showNotification(`Panel ${panelType} opened`);
    }

    updateConnectionStatus(status) {
        this.connectionStatus = status;
        const statusElement = document.getElementById('connection-status');
        const statusBar = document.getElementById('status-bar');
        
        if (status === 'online') {
            statusElement.textContent = 'Status: Online';
            statusElement.className = 'status-text online';
            statusBar.style.backgroundColor = 'var(--success)';
            this.statusBarText = 'Online';
        } else {
            statusElement.textContent = 'Status: Offline';
            statusElement.className = 'status-text offline';
            statusBar.style.backgroundColor = 'var(--error)';
            this.statusBarText = 'Offline';
        }
    }

    showAuthDialog() {
        document.getElementById('auth-dialog').style.display = 'flex';
    }

    hideAuthDialog() {
        document.getElementById('auth-dialog').style.display = 'none';
    }

    submitAuth() {
        const keyFile = document.getElementById('key-file').files[0];
        const projectId = document.getElementById('project-id').value;

        if (!keyFile || !projectId) {
            this.showNotification('Please provide both key file and project ID', 'error');
            return;
        }

        // Simulate auth process
        this.showNotification('Authentication successful!');
        this.hideAuthDialog();
        this.updateConnectionStatus('online');
    }

    showHelpPopup() {
        document.getElementById('help-popup').style.display = 'flex';
    }

    hideHelpPopup() {
        document.getElementById('help-popup').style.display = 'none';
    }

    showCalendar() {
        this.renderCalendar();
        document.getElementById('calendar-modal').style.display = 'flex';
    }

    hideCalendar() {
        document.getElementById('calendar-modal').style.display = 'none';
    }

    renderCalendar() {
        const year = this.currentDate.getFullYear();
        const month = this.currentDate.getMonth();
        
        const firstDay = new Date(year, month, 1);
        const lastDay = new Date(year, month + 1, 0);
        const startDate = new Date(firstDay);
        startDate.setDate(startDate.getDate() - firstDay.getDay());
        
        const calendarGrid = document.getElementById('calendar-grid');
        const calendarTitle = document.getElementById('calendar-title');
        
        calendarTitle.textContent = `${this.getMonthName(month)} ${year}`;
        calendarGrid.innerHTML = '';

        // Add day headers
        const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
        days.forEach(day => {
            const dayHeader = document.createElement('div');
            dayHeader.className = 'calendar-day-header';
            dayHeader.textContent = day;
            calendarGrid.appendChild(dayHeader);
        });

        // Add calendar days
        for (let i = 0; i < 42; i++) {
            const date = new Date(startDate);
            date.setDate(startDate.getDate() + i);
            
            const dayElement = document.createElement('div');
            dayElement.className = 'calendar-day';
            dayElement.textContent = date.getDate();
            
            if (date.getMonth() !== month) {
                dayElement.classList.add('other-month');
            }
            
            if (this.isSameDate(date, this.selectedDate)) {
                dayElement.classList.add('selected');
            }
            
            dayElement.addEventListener('click', () => {
                this.selectDate(date);
            });
            
            calendarGrid.appendChild(dayElement);
        }
    }

    selectDate(date) {
        this.selectedDate = date;
        if (this.calendarTarget) {
            const input = document.querySelector(this.calendarTarget);
            if (input) {
                input.value = this.formatDate(date);
            }
        }
        this.hideCalendar();
    }

    formatDate(date) {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    }

    isSameDate(date1, date2) {
        if (!date1 || !date2) return false;
        return date1.getFullYear() === date2.getFullYear() &&
               date1.getMonth() === date2.getMonth() &&
               date1.getDate() === date2.getDate();
    }

    getMonthName(month) {
        const months = [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ];
        return months[month];
    }

    previousMonth() {
        this.currentDate.setMonth(this.currentDate.getMonth() - 1);
        this.renderCalendar();
    }

    nextMonth() {
        this.currentDate.setMonth(this.currentDate.getMonth() + 1);
        this.renderCalendar();
    }

    showMapSelector() {
        document.getElementById('map-modal').style.display = 'flex';
    }

    hideMapSelector() {
        document.getElementById('map-modal').style.display = 'none';
    }

    confirmMapSelection() {
        // This would get the selected coordinates from the map iframe
        this.showNotification('Map selection confirmed');
        this.hideMapSelector();
    }

    loadSensors() {
        const sensorSelect = document.getElementById('sensor-select');
        const sensors = [
            { value: 'landsat8', label: 'Landsat 8' },
            { value: 'sentinel2', label: 'Sentinel-2' },
            { value: 'modis', label: 'MODIS' },
            { value: 'aster', label: 'ASTER' }
        ];

        sensors.forEach(sensor => {
            const option = document.createElement('option');
            option.value = sensor.value;
            option.textContent = sensor.label;
            sensorSelect.appendChild(option);
        });
    }

    startDownload() {
        const aoiInput = document.getElementById('aoi-input').value;
        const startDate = document.getElementById('start-date').value;
        const endDate = document.getElementById('end-date').value;
        const sensor = document.getElementById('sensor-select').value;
        const outputDir = document.getElementById('output-dir').value;

        if (!aoiInput || !startDate || !endDate || !sensor || !outputDir) {
            this.showNotification('Please fill in all required fields', 'error');
            return;
        }

        this.showNotification('Download started successfully!');
        this.switchView('progress');
        
        // Simulate download progress
        this.simulateDownloadProgress();
    }

    simulateDownloadProgress() {
        const progressItem = document.querySelector('.progress-item');
        const progressFill = progressItem.querySelector('.progress-fill');
        const progressDetails = progressItem.querySelector('.progress-details');
        
        let progress = 0;
        const interval = setInterval(() => {
            progress += Math.random() * 10;
            if (progress >= 100) {
                progress = 100;
                clearInterval(interval);
                this.showNotification('Download completed!');
            }
            
            progressFill.style.width = `${progress}%`;
            progressDetails.innerHTML = `
                <span>${Math.round(progress)}% Complete</span>
                <span>${(progress * 0.051).toFixed(1)} GB / 5.1 GB</span>
            `;
        }, 1000);
    }

    cancelDownload() {
        this.showNotification('Download cancelled');
    }

    browseOutputDirectory() {
        // In a real implementation, this would open a file dialog
        // For now, we'll simulate it
        const outputDir = document.getElementById('output-dir');
        outputDir.value = '/path/to/output/directory';
        this.showNotification('Output directory selected');
    }

    changeTheme(themeName) {
        document.documentElement.setAttribute('data-theme', themeName);
        this.showNotification(`Theme changed to ${themeName}`);
    }

    showNotification(message, type = 'success') {
        const notification = document.getElementById('notification-popup');
        const notificationText = document.getElementById('notification-text');
        const notificationContent = notification.querySelector('.notification-content');
        
        notificationText.textContent = message;
        
        // Update notification style based on type
        notificationContent.className = 'notification-content';
        if (type === 'error') {
            notificationContent.style.background = 'var(--error)';
        } else if (type === 'warning') {
            notificationContent.style.background = 'var(--warning)';
        } else {
            notificationContent.style.background = 'var(--success)';
        }
        
        notification.style.display = 'block';
        
        // Auto-hide after 3 seconds
        setTimeout(() => {
            notification.style.display = 'none';
        }, 3000);
    }

    handleKeyboardShortcuts(e) {
        // Ctrl/Cmd + key shortcuts
        if (e.ctrlKey || e.metaKey) {
            switch (e.key) {
                case '1':
                    e.preventDefault();
                    this.switchView('welcome');
                    break;
                case '2':
                    e.preventDefault();
                    this.switchView('download');
                    break;
                case '3':
                    e.preventDefault();
                    this.switchView('map');
                    break;
                case '4':
                    e.preventDefault();
                    this.switchView('settings');
                    break;
                case 'h':
                    e.preventDefault();
                    this.showHelpPopup();
                    break;
                case 'q':
                    e.preventDefault();
                    this.showAuthDialog();
                    break;
            }
        }

        // Escape key to close modals
        if (e.key === 'Escape') {
            document.querySelectorAll('.modal').forEach(modal => {
                if (modal.style.display === 'flex') {
                    modal.style.display = 'none';
                }
            });
        }
    }

    // Utility methods
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.flutterEarth = new FlutterEarth();
    
    // Set default active sidebar item
    document.querySelector('.sidebar-item[data-view="welcome"]').classList.add('active');
    
    // Add some CSS for calendar day headers
    const style = document.createElement('style');
    style.textContent = `
        .calendar-day-header {
            aspect-ratio: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
            color: var(--text-subtle);
            font-size: var(--font-size-small);
        }
    `;
    document.head.appendChild(style);
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = FlutterEarth;
} 