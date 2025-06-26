$(function() {
    // Modal logic
    function openModal(id, content) {
        $(id).html(content).show();
    }
    function closeModal(id) {
        $(id).hide().empty();
    }
    // Calendar modal
    $(document).on('click', '.calendar-btn', function() {
        const target = $(this).data('target');
        openModal('#calendar-modal', `
            <div class="calendar-popup">
                <input type="date" id="calendar-date">
                <button id="calendar-ok">OK</button>
                <button id="calendar-cancel">Cancel</button>
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
    // Map modal
    $('#map-btn').on('click', function() {
        openModal('#map-modal', '<iframe src="map_selector.html" width="600" height="400" style="border:none;"></iframe><button id="map-close">Close</button>');
        $('#map-close').off('click').on('click', function() {
            closeModal('#map-modal');
        });
    });
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
    // Offline detection
    function checkBackend() {
        // Stub: try to ping backend
        // $.get('/api/ping').done(...).fail(...)
        if (!navigator.onLine) {
            $('#download-status').text('Backend not connected (offline mode)').css('color', '#d32f2f');
        } else {
            $('#download-status').text('Ready').css('color', '#388e3c');
        }
    }
    window.addEventListener('online', checkBackend);
    window.addEventListener('offline', checkBackend);
    checkBackend();
    // Download controls
    $('#start-download').on('click', function() {
        if (!navigator.onLine) {
            $('#download-status').text('Cannot start download: backend not connected').css('color', '#d32f2f');
            return;
        }
        // TODO: Gather all form data and send to backend
        $('#download-status').text('Download started...').css('color', '#388e3c');
    });
    $('#cancel-download').on('click', function() {
        $('#download-status').text('Download cancelled').css('color', '#d32f2f');
    });
    // Sensor select stub
    $('#sensor-select').html('<option>Sentinel-2</option><option>Landsat-8</option>');
}); 