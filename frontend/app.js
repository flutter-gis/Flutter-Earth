$(function() {
    // Navigation and View Management
    let currentView = 'home';
    
    function switchView(viewName) {
        $('.view').removeClass('active');
        $('.nav-item').removeClass('active');
        $(`#${viewName}-view`).addClass('active');
        $(`.nav-item[data-view="${viewName}"]`).addClass('active');
        currentView = viewName;
        
        // Update URL hash
        window.location.hash = viewName;
        
        // Initialize view-specific functionality
        initializeView(viewName);
    }
    
    function initializeView(viewName) {
        switch(viewName) {
            case 'home':
                updateDashboard();
                break;
            case 'map':
                initializeMap();
                break;
            case 'satellite':
                loadSatelliteInfo();
                break;
            case 'data-viewer':
                loadDataViewer();
                break;
            case 'download':
                initializeDownload();
                break;
            case 'progress':
                updateProgress();
                break;
            case 'settings':
                loadSettings();
                break;
        }
    }
    
    // Navigation event handlers
    $('.nav-item').on('click', function(e) {
        e.preventDefault();
        const viewName = $(this).data('view');
        switchView(viewName);
    });
    
    // Handle URL hash changes
    $(window).on('hashchange', function() {
        const hash = window.location.hash.slice(1) || 'home';
        switchView(hash);
    });
    
    // Initialize with current hash or default to home
    const initialView = window.location.hash.slice(1) || 'home';
    switchView(initialView);
    
    // Modal Management
    function openModal(id, content) {
        $(id).html(content).show();
    }
    
    function closeModal(id) {
        $(id).hide().empty();
    }
    
    // Close modals when clicking outside
    $('.modal').on('click', function(e) {
        if (e.target === this) {
            closeModal('#' + $(this).attr('id'));
        }
    });
    
    // Calendar Modal
    $(document).on('click', '.calendar-btn', function() {
        const target = $(this).data('target');
        openModal('#calendar-modal', `
            <div class="calendar-popup">
                <h3>Select Date</h3>
                <input type="date" id="calendar-date">
                <div class="calendar-buttons">
                    <button id="calendar-ok">OK</button>
                    <button id="calendar-cancel">Cancel</button>
                </div>
            </div>
        `);
        
        $('#calendar-ok').off('click').on('click', function() {
            const val = $('#calendar-date').val();
            $(target).val(val);
            closeModal('#calendar-modal');
        });
        
        $('#calendar-cancel').off('click').on('click', function() {
            closeModal('#calendar-modal');
        });
    });
    
    // Map Modal
    $('#map-btn').on('click', function() {
        openModal('#map-modal', `
            <div class="map-popup">
                <h3>Select Area of Interest</h3>
                <iframe src="map_selector.html" width="800" height="600" style="border:none; border-radius: var(--radius);"></iframe>
                <button id="map-close">Close</button>
            </div>
        `);
        
        $('#map-close').off('click').on('click', function() {
            closeModal('#map-modal');
        });
    });
    
    // Handle AOI from map selector
    window.addEventListener('message', function(event) {
        if (event.data.type === 'aoi') {
            $('#aoi-input').val(JSON.stringify(event.data.geojson));
            $('#aoi-summary').text('AOI set from map selector');
            closeModal('#map-modal');
        }
    });
    
    // Home Dashboard
    function updateDashboard() {
        // Update system status
        checkBackend();
        updateStorageStatus();
        updateActiveDownloads();
        
        // Load recent downloads
        loadRecentDownloads();
    }
    
    function updateStorageStatus() {
        // Simulate storage check
        $('#storage-status').text('2.3 GB free');
    }
    
    function updateActiveDownloads() {
        // Simulate active downloads count
        $('#active-downloads').text('0');
    }
    
    function loadRecentDownloads() {
        // Simulate recent downloads
        const recentDownloads = [
            { name: 'Sentinel-2 Scene', date: '2024-01-15' },
            { name: 'Landsat-8 Collection', date: '2024-01-10' }
        ];
        
        let html = recentDownloads.map(item => `
            <div class="recent-item">
                <span class="item-name">${item.name}</span>
                <span class="item-date">${item.date}</span>
            </div>
        `).join('');
        
        $('#recent-downloads').html(html);
    }
    
    // Quick Actions
    $('.action-btn').on('click', function() {
        const action = $(this).data('action');
        switch(action) {
            case 'new-download':
                switchView('download');
                break;
            case 'view-map':
                switchView('map');
                break;
            case 'browse-data':
                switchView('data-viewer');
                break;
        }
    });
    
    // Map View
    function initializeMap() {
        // Initialize satellite map if not already done
        if (!$('#satellite-map').hasClass('initialized')) {
            // This would initialize Leaflet map
            $('#satellite-map').addClass('initialized');
        }
        
        // Update map controls
        updateMapControls();
    }
    
    function updateMapControls() {
        // Handle satellite selection
        $('#map-satellite-select').on('change', function() {
            // Update map with selected satellite
            console.log('Satellite changed to:', $(this).val());
        });
        
        // Handle date selection
        $('#map-date-select').on('change', function() {
            // Update map with selected date
            console.log('Date changed to:', $(this).val());
        });
        
        // Handle refresh
        $('#map-refresh-btn').on('click', function() {
            // Refresh map data
            console.log('Refreshing map...');
        });
    }
    
    // Satellite Info View
    function loadSatelliteInfo() {
        // Load satellite information
        console.log('Loading satellite information...');
    }
    
    // Data Viewer
    function loadDataViewer() {
        // Handle data type selection
        $('#data-type-select').on('change', function() {
            const dataType = $(this).val();
            $('.data-panel').removeClass('active');
            $(`#${dataType}-table`).addClass('active');
        });
        
        // Handle export
        $('#export-data-btn').on('click', function() {
            console.log('Exporting data...');
        });
        
        // Load sample data
        loadSampleData();
    }
    
    function loadSampleData() {
        const sampleData = [
            { id: 1, date: '2024-01-15', cloudCover: '5%', quality: 'Excellent' },
            { id: 2, date: '2024-01-10', cloudCover: '12%', quality: 'Good' },
            { id: 3, date: '2024-01-05', cloudCover: '25%', quality: 'Fair' }
        ];
        
        let html = sampleData.map(item => `
            <tr>
                <td>${item.id}</td>
                <td>${item.date}</td>
                <td>${item.cloudCover}</td>
                <td>${item.quality}</td>
                <td><button class="action-btn small">View</button></td>
            </tr>
        `).join('');
        
        $('#table-body').html(html);
    }
    
    // Download View
    function initializeDownload() {
        // AOI input summary
        $('#aoi-input').on('input', function() {
            $('#aoi-summary').text($(this).val().length ? 'AOI set.' : '');
        });
        
        // Multi-satellite order logic
        let satellites = [];
        
        function renderSatList() {
            let html = satellites.map((sat, i) => `
                <div class="sat-row">
                    <input type="text" class="sat-name" value="${sat.name}" placeholder="Satellite Name">
                    <input type="text" class="sat-date" value="${sat.date}" placeholder="YYYY-MM-DD">
                    <input type="number" class="sat-res" value="${sat.res}" placeholder="Res (m)">
                    <button class="remove-sat" data-idx="${i}">Remove</button>
                </div>
            `).join('');
            $('#multi-sat-list').html(html);
        }
        
        $('#add-sat').on('click', function() {
            satellites.push({name:'', date:'', res:30});
            renderSatList();
        });
        
        $('#multi-sat-list').on('click', '.remove-sat', function() {
            satellites.splice($(this).data('idx'), 1);
            renderSatList();
        });
        
        $('#multi-sat-list').on('input', '.sat-name, .sat-date, .sat-res', function() {
            const idx = $(this).closest('.sat-row').index();
            satellites[idx].name = $(this).closest('.sat-row').find('.sat-name').val();
            satellites[idx].date = $(this).closest('.sat-row').find('.sat-date').val();
            satellites[idx].res = $(this).closest('.sat-row').find('.sat-res').val();
        });
        
        // Sensor select
        $('#sensor-select').html('<option>Sentinel-2</option><option>Landsat-8</option>');
        
        // Download controls
        $('#start-download').on('click', function() {
            if (!navigator.onLine) {
                $('#download-status').text('Cannot start download: backend not connected').css('color', '#d32f2f');
                return;
            }
            $('#download-status').text('Download started...').css('color', '#388e3c');
        });
        
        $('#cancel-download').on('click', function() {
            $('#download-status').text('Download cancelled').css('color', '#d32f2f');
        });
    }
    
    // Progress View
    function updateProgress() {
        // Handle clear completed
        $('#clear-completed').on('click', function() {
            $('.progress-item.completed').fadeOut();
        });
        
        // Simulate progress updates
        simulateProgress();
    }
    
    function simulateProgress() {
        // Simulate progress bar animation
        $('.progress-item:not(.completed) .progress-fill').each(function() {
            const currentWidth = parseInt($(this).css('width'));
            const targetWidth = Math.min(currentWidth + Math.random() * 10, 100);
            $(this).css('width', targetWidth + '%');
        });
    }
    
    // Settings View
    function loadSettings() {
        // Load current settings
        loadCurrentSettings();
        
        // Handle settings changes
        $('.settings-card input, .settings-card select').on('change', function() {
            saveSetting($(this).attr('id'), $(this).val());
        });
    }
    
    function loadCurrentSettings() {
        // Load settings from localStorage or backend
        const settings = {
            'default-output': 'C:\\Downloads\\SatelliteData',
            'max-concurrent': '3',
            'auto-cleanup': true,
            'theme-select': 'light',
            'font-size': 'medium',
            'debug-mode': false
        };
        
        Object.keys(settings).forEach(key => {
            const element = $(`#${key}`);
            if (element.length) {
                if (element.attr('type') === 'checkbox') {
                    element.prop('checked', settings[key]);
                } else {
                    element.val(settings[key]);
                }
            }
        });
    }
    
    function saveSetting(key, value) {
        // Save setting to localStorage or backend
        console.log(`Saving setting: ${key} = ${value}`);
        localStorage.setItem(key, value);
    }
    
    // Global Search
    $('#search-btn').on('click', function() {
        const query = $('#global-search').val();
        if (query.trim()) {
            performGlobalSearch(query);
        }
    });
    
    $('#global-search').on('keypress', function(e) {
        if (e.which === 13) {
            $('#search-btn').click();
        }
    });
    
    function performGlobalSearch(query) {
        console.log('Performing global search for:', query);
        // Implement search functionality
        // Could search across satellites, data, downloads, etc.
    }
    
    // Backend Connection Management
    function checkBackend() {
        if (!navigator.onLine) {
            $('#connection-status').text('🔴 Offline').css('color', '#d32f2f');
            $('#backend-status').text('Disconnected').css('color', '#d32f2f');
        } else {
            // Try to ping backend
            $.ajax({
                url: '/api/ping',
                method: 'GET',
                timeout: 5000
            }).done(function() {
                $('#connection-status').text('🟢 Online').css('color', '#4caf50');
                $('#backend-status').text('Connected').css('color', '#4caf50');
            }).fail(function() {
                $('#connection-status').text('🟡 Limited').css('color', '#ff9800');
                $('#backend-status').text('Limited').css('color', '#ff9800');
            });
        }
    }
    
    // Online/Offline event handlers
    window.addEventListener('online', function() {
        checkBackend();
    });
    
    window.addEventListener('offline', function() {
        checkBackend();
    });
    
    // Initialize connection status
    checkBackend();
    
    // Periodic updates
    setInterval(function() {
        if (currentView === 'home') {
            updateDashboard();
        } else if (currentView === 'progress') {
            updateProgress();
        }
    }, 5000);
    
    // Handle window resize for responsive design
    $(window).on('resize', function() {
        // Handle responsive layout changes
        if ($(window).width() <= 768) {
            // Mobile layout adjustments
        }
    });
    
    // Initialize tooltips and other UI enhancements
    $('[title]').tooltip();
    
    // Handle form submissions
    $('form').on('submit', function(e) {
        e.preventDefault();
        // Handle form submission
    });
    
    // Initialize all views
    initializeView(currentView);
}); 