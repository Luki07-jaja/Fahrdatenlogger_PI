// Dashboard JavaScript - Erweiterte Version mit Höhe, Neigung und Karte
let charts = {};
let currentFile = null;
let recentFiles = [];
let map = null;
let routeLayer = null;

// Initialisierung beim Laden der Seite
document.addEventListener('DOMContentLoaded', function() {
    loadRecentFiles();
    loadDashboardData();
    
    // Auto-Refresh alle 10 Sekunden auf neue Fahrten prüfen
    setInterval(checkForNewFiles, 10000);
});

// Hauptfunktion zum Laden der Dashboard-Daten
async function loadDashboardData(file = null) {
    try {
        const url = file ? `/api/stats?file=${encodeURIComponent(file)}` : '/api/stats';
        const response = await fetch(url);
        const data = await response.json();
        
        if (data.error) {
            console.error('Error loading data:', data.error);
            return;
        }
        
        // Aktuelle Datei speichern
        currentFile = data.current_filepath;
        
        // Dateiname im Badge aktualisieren
        document.getElementById('current-file-name').textContent = data.current_file || 'Keine Datei';
        
        // KPI Cards aktualisieren
        updateKPIs(data);
        
        // Charts erstellen/aktualisieren
        updateCharts(data);
        
        // Karte zeichnen
        if (data.gps_data && data.gps_data.length > 0) {
            drawRoute(data.gps_data);
        } else {
            showEmptyMap();
        }
        
        // History markieren
        highlightCurrentFileInHistory();
        
    } catch (error) {
        console.error('Error fetching dashboard data:', error);
    }
}

// Letzte Dateien laden
async function loadRecentFiles() {
    try {
        const response = await fetch('/api/recent-files');
        const data = await response.json();
        
        recentFiles = data.files || [];
        displayRecentFiles(recentFiles);
        
    } catch (error) {
        console.error('Error loading recent files:', error);
        document.getElementById('history-list').innerHTML = 
            '<div class="empty-state">Fehler beim Laden der Dateien</div>';
    }
}

// Auf neue Dateien prüfen
async function checkForNewFiles() {
    try {
        const response = await fetch('/api/recent-files');
        const data = await response.json();
        
        const newFiles = data.files || [];
        
        // Prüfen ob neue Datei vorhanden
        if (newFiles.length > 0 && recentFiles.length > 0) {
            if (newFiles[0].filename !== recentFiles[0].filename) {
                // Neue Fahrt erkannt!
                showNotification('Neue Fahrt erkannt!');
                recentFiles = newFiles;
                displayRecentFiles(recentFiles);
            }
        }
    } catch (error) {
        console.error('Error checking for new files:', error);
    }
}

// History anzeigen
function displayRecentFiles(files) {
    const container = document.getElementById('history-list');
    
    if (!files || files.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                </svg>
                <p>Keine Fahrten gefunden</p>
                <small>Starte eine Fahrt mit dem Logger, um Daten zu sehen</small>
            </div>
        `;
        return;
    }
    
    let html = '';
    files.forEach((file, index) => {
        const isActive = currentFile === file.filepath;
        const num = index + 1;
        
        html += `
            <div class="history-item ${isActive ? 'active' : ''}" onclick="selectFile('${file.filepath}')">
                <div class="history-icon">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                        <polyline points="14 2 14 8 20 8"/>
                    </svg>
                </div>
                <div class="history-info">
                    <div class="history-title">Fahrt #${num} - ${file.date}</div>
                    <div class="history-meta">
                        <span>
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <circle cx="12" cy="12" r="10"/>
                                <polyline points="12 6 12 12 16 14"/>
                            </svg>
                            ${file.time}
                        </span>
                        <span>
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                                <polyline points="7 10 12 15 17 10"/>
                                <line x1="12" y1="15" x2="12" y2="3"/>
                            </svg>
                            ${file.size_kb} KB
                        </span>
                        <span>
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
                            </svg>
                            ${file.total_rows.toLocaleString('de-DE')} Punkte
                        </span>
                    </div>
                </div>
                <div class="history-actions" onclick="event.stopPropagation()">
                    <button class="icon-btn" onclick="viewFileCSV('${file.filepath}')" title="CSV ansehen">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                            <circle cx="12" cy="12" r="3"/>
                        </svg>
                    </button>
                    <button class="icon-btn" onclick="downloadFileCSV('${file.filepath}')" title="Herunterladen">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                            <polyline points="7 10 12 15 17 10"/>
                            <line x1="12" y1="15" x2="12" y2="3"/>
                        </svg>
                    </button>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

// ========== KARTEN-FUNKTIONEN ==========
function initMap() {
    if (map) {
        map.remove();
    }
    
    map = L.map('routeMap').setView([47.5, 10.0], 13);
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap',
        maxZoom: 19
    }).addTo(map);
}

function getSpeedColor(speed) {
    // Farbverlauf basierend auf Geschwindigkeit
    if (speed < 10) return '#10b981';      // Grün (sehr langsam)
    if (speed < 30) return '#84cc16';      // Hellgrün (langsam)
    if (speed < 50) return '#eab308';      // Gelb (mittel)
    if (speed < 70) return '#f97316';      // Orange (schnell)
    if (speed < 90) return '#ef4444';      // Rot (sehr schnell)
    return '#dc2626';                       // Dunkelrot (extrem schnell)
}

function drawRoute(gpsData) {
    if (!gpsData || gpsData.length === 0) {
        showEmptyMap();
        return;
    }
    
    // Container sichtbar machen
    document.getElementById('routeMap').style.display = 'block';
    document.getElementById('mapEmptyState').style.display = 'none';
    
    // Map initialisieren wenn nötig
    if (!map) {
        initMap();
    }
    
    // Alte Route löschen
    if (routeLayer) {
        map.removeLayer(routeLayer);
    }
    
    // Layer-Gruppe für alle Segmente
    routeLayer = L.layerGroup().addTo(map);
    
    // Route in Segmente aufteilen (farbcodiert nach Speed)
    for (let i = 0; i < gpsData.length - 1; i++) {
        const point1 = gpsData[i];
        const point2 = gpsData[i + 1];
        
        // Koordinaten
        const coords = [
            [point1.gps_lat, point1.gps_long],
            [point2.gps_lat, point2.gps_long]
        ];
        
        // Durchschnitts-Speed für dieses Segment
        const avgSpeed = (
            (point1.fusion_speed || 0) + (point2.fusion_speed || 0)
        ) / 2;
        
        // Segment mit Farbe zeichnen
        const segment = L.polyline(coords, {
            color: getSpeedColor(avgSpeed),
            weight: 5,
            opacity: 0.9,
            smoothFactor: 1
        }).addTo(routeLayer);
        
        // Popup mit Daten
        const popupContent = `
            <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto; min-width: 180px;">
                <strong style="font-size: 14px; color: #f8fafc;">Messpunkt ${i + 1}</strong>
                <hr style="margin: 8px 0; border: none; border-top: 1px solid #334155;">
                <table style="width: 100%; font-size: 13px; color: #e2e8f0;">
                    <tr>
                        <td style="padding: 4px 8px 4px 0; color: #94a3b8;">Geschwindigkeit:</td>
                        <td style="padding: 4px 0; font-weight: 600; color: ${getSpeedColor(avgSpeed)};">
                            ${avgSpeed.toFixed(1)} km/h
                        </td>
                    </tr>
                    ${point1.fusion_alt !== undefined ? `
                    <tr>
                        <td style="padding: 4px 8px 4px 0; color: #94a3b8;">Höhe:</td>
                        <td style="padding: 4px 0; font-weight: 600; color: #f8fafc;">${point1.fusion_alt.toFixed(1)} m</td>
                    </tr>
                    ` : ''}
                    ${point1.pitch_deg !== undefined ? `
                    <tr>
                        <td style="padding: 4px 8px 4px 0; color: #94a3b8;">Neigung:</td>
                        <td style="padding: 4px 0; font-weight: 600; color: #f8fafc;">${point1.pitch_deg.toFixed(1)}°</td>
                    </tr>
                    ` : ''}
                    ${point1.lean_deg !== undefined ? `
                    <tr>
                        <td style="padding: 4px 8px 4px 0; color: #94a3b8;">Schräglage:</td>
                        <td style="padding: 4px 0; font-weight: 600; color: #f8fafc;">${Math.abs(point1.lean_deg).toFixed(1)}°</td>
                    </tr>
                    ` : ''}
                    ${point1.pi_timestamp ? `
                    <tr>
                        <td style="padding: 4px 8px 4px 0; color: #94a3b8;">Zeit:</td>
                        <td style="padding: 4px 0; font-weight: 600; font-size: 11px; color: #f8fafc;">
                            ${point1.pi_timestamp.split('T')[1] || point1.pi_timestamp}
                        </td>
                    </tr>
                    ` : ''}
                </table>
            </div>
        `;
        
        segment.bindPopup(popupContent);
    }
    
    // Start Marker (grün)
    const start = gpsData[0];
    L.marker([start.gps_lat, start.gps_long], {
        icon: L.divIcon({
            html: '<div style="background: #10b981; width: 24px; height: 24px; border-radius: 50%; border: 3px solid white; box-shadow: 0 2px 8px rgba(0,0,0,0.4);"></div>',
            className: '',
            iconSize: [24, 24],
            iconAnchor: [12, 12]
        })
    }).bindPopup(`
        <div style="font-family: -apple-system; text-align: center;">
            <strong style="font-size: 15px; color: #10b981;">Start</strong><br>
            <span style="font-size: 12px; color: #94a3b8;">
                ${start.pi_timestamp ? start.pi_timestamp.split('T')[1] : '--'}
            </span>
        </div>
    `).addTo(routeLayer);
    
    // Ziel Marker (rot)
    const end = gpsData[gpsData.length - 1];
    L.marker([end.gps_lat, end.gps_long], {
        icon: L.divIcon({
            html: '<div style="background: #ef4444; width: 24px; height: 24px; border-radius: 50%; border: 3px solid white; box-shadow: 0 2px 8px rgba(0,0,0,0.4);"></div>',
            className: '',
            iconSize: [24, 24],
            iconAnchor: [12, 12]
        })
    }).bindPopup(`
        <div style="font-family: -apple-system; text-align: center;">
            <strong style="font-size: 15px; color: #ef4444;">Ziel</strong><br>
            <span style="font-size: 12px; color: #94a3b8;">
                ${end.pi_timestamp ? end.pi_timestamp.split('T')[1] : '--'}
            </span>
        </div>
    `).addTo(routeLayer);
    
    // Bounds berechnen und Karte zoomen
    const bounds = L.latLngBounds(
        gpsData.map(p => [p.gps_lat, p.gps_long])
    );
    map.fitBounds(bounds, { padding: [50, 50] });
    
    // Statistiken aktualisieren
    document.getElementById('mapPointCount').textContent = `${gpsData.length} Punkte`;
    
    // Distanz berechnen
    let totalDist = 0;
    for (let i = 1; i < gpsData.length; i++) {
        const p1 = L.latLng(gpsData[i-1].gps_lat, gpsData[i-1].gps_long);
        const p2 = L.latLng(gpsData[i].gps_lat, gpsData[i].gps_long);
        totalDist += p1.distanceTo(p2);
    }
    document.getElementById('mapDistance').textContent = `${(totalDist / 1000).toFixed(2)} km`;
}

function showEmptyMap() {
    document.getElementById('routeMap').style.display = 'none';
    document.getElementById('mapEmptyState').style.display = 'flex';
    document.getElementById('mapPointCount').textContent = '-- Punkte';
    document.getElementById('mapDistance').textContent = '-- km';
}

// Datei auswählen und Dashboard aktualisieren
function selectFile(filepath) {
    loadDashboardData(filepath);
}

// Aktuelle Datei in History markieren
function highlightCurrentFileInHistory() {
    document.querySelectorAll('.history-item').forEach(item => {
        item.classList.remove('active');
    });
    
    if (currentFile) {
        const items = document.querySelectorAll('.history-item');
        items.forEach(item => {
            if (item.onclick.toString().includes(currentFile)) {
                item.classList.add('active');
            }
        });
    }
}

// History manuell aktualisieren
async function refreshHistory() {
    const btn = document.getElementById('refresh-btn');
    btn.classList.add('spinning');
    
    await loadRecentFiles();
    
    setTimeout(() => {
        btn.classList.remove('spinning');
    }, 500);
}

// Benachrichtigung anzeigen
function showNotification(message) {
    if (Notification.permission === "granted") {
        new Notification("Fahrdatenlogger", {
            body: message,
            icon: "/static/favicon.ico"
        });
    }
    console.log('Notification:', message);
}

// KPI Cards aktualisieren
function updateKPIs(data) {
    // Fahrzeit
    document.getElementById('total-time').textContent = data.total_time || '00:00:00';
    
    // Gesamtstrecke
    document.getElementById('total-distance').innerHTML = 
        `${data.total_distance.toFixed(2)} <span class="unit">km</span>`;
    
    // Geschwindigkeit
    document.getElementById('avg-speed').innerHTML = 
        `${data.avg_speed.toFixed(2)} <span class="unit">km/h</span>`;
    document.getElementById('max-speed').textContent = data.max_speed.toFixed(2);
    
    // Kurvenlage
    document.getElementById('avg-lean').innerHTML = 
        `${data.avg_lean.toFixed(2)} <span class="unit">°</span>`;
    document.getElementById('max-lean').textContent = data.max_lean.toFixed(2);
    
    // Batteriespannung
    document.getElementById('avg-voltage').innerHTML = 
        `${data.avg_voltage.toFixed(2)} <span class="unit">V</span>`;
    document.getElementById('min-voltage').textContent = data.min_voltage.toFixed(2);
    document.getElementById('max-voltage').textContent = data.max_voltage.toFixed(2);
    
    // Batterietemperatur
    document.getElementById('avg-temp').innerHTML = 
        `${data.avg_temp.toFixed(2)} <span class="unit">°C</span>`;
    document.getElementById('max-temp').textContent = data.max_temp.toFixed(2);
    
    // Höhe (Altitude)
    if (document.getElementById('avg-altitude')) {
        document.getElementById('avg-altitude').innerHTML = 
            `${data.avg_altitude.toFixed(2)} <span class="unit">m</span>`;
        document.getElementById('max-altitude').textContent = data.max_altitude.toFixed(2);
        document.getElementById('min-altitude').textContent = data.min_altitude.toFixed(2);
        document.getElementById('altitude-gain').textContent = data.altitude_gain.toFixed(2);
    }
    
    // Neigung (Pitch)
    if (document.getElementById('avg-pitch')) {
        document.getElementById('avg-pitch').innerHTML = 
            `${data.avg_pitch.toFixed(2)} <span class="unit">°</span>`;
        document.getElementById('max-pitch-up').textContent = data.max_pitch_up.toFixed(2);
        document.getElementById('max-pitch-down').textContent = Math.abs(data.max_pitch_down).toFixed(2);
    }
    
    // Datensatz-Anzahl
    document.getElementById('record-count').textContent = 
        data.total_records.toLocaleString('de-DE');
}

// Charts erstellen/aktualisieren
function updateCharts(data) {
    createOrUpdateChart('speedChart', {
        label: 'Geschwindigkeit (km/h)',
        data: data.speed_data,
        borderColor: '#00d4ff',
        backgroundColor: 'rgba(0, 212, 255, 0.1)',
        fill: true
    });
    
    createOrUpdateChart('leanChart', {
        label: 'Kurvenlage (°)',
        data: data.lean_data,
        borderColor: '#fa709a',
        backgroundColor: 'rgba(250, 112, 154, 0.1)',
        fill: true
    });
    
    createOrUpdateChart('voltageChart', {
        label: 'Spannung (V)',
        data: data.voltage_data,
        borderColor: '#43e97b',
        backgroundColor: 'rgba(67, 233, 123, 0.1)',
        fill: true
    });
    
    createOrUpdateChart('tempChart', {
        label: 'Temperatur (°C)',
        data: data.temp_data,
        borderColor: '#ff6b6b',
        backgroundColor: 'rgba(255, 107, 107, 0.1)',
        fill: true
    });
    
    createOrUpdateChart('altitudeChart', {
        label: 'Höhe (m)',
        data: data.altitude_data,
        borderColor: '#a78bfa',
        backgroundColor: 'rgba(167, 139, 250, 0.1)',
        fill: true
    });
    
    createOrUpdateChart('pitchChart', {
        label: 'Neigung (°)',
        data: data.pitch_data,
        borderColor: '#fbbf24',
        backgroundColor: 'rgba(251, 191, 36, 0.1)',
        fill: true
    });
}

// Hilfsfunktion zum Erstellen/Aktualisieren von Charts
function createOrUpdateChart(canvasId, config) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    
    if (charts[canvasId]) {
        charts[canvasId].destroy();
    }
    
    const labels = config.data.map((_, index) => index + 1);
    
    charts[canvasId] = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: config.label,
                data: config.data,
                borderColor: config.borderColor,
                backgroundColor: config.backgroundColor,
                borderWidth: 2,
                pointRadius: 0,
                pointHoverRadius: 5,
                fill: config.fill || false,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        color: '#e8eaed',
                        font: {
                            size: 12,
                            family: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto'
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(26, 31, 41, 0.95)',
                    titleColor: '#e8eaed',
                    bodyColor: '#9aa0a6',
                    borderColor: config.borderColor,
                    borderWidth: 1,
                    padding: 12,
                    displayColors: true,
                    callbacks: {
                        label: function(context) {
                            return config.label + ': ' + context.parsed.y.toFixed(2);
                        }
                    }
                }
            },
            scales: {
                x: {
                    display: true,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.05)',
                        drawBorder: false
                    },
                    ticks: {
                        color: '#9aa0a6',
                        maxTicksLimit: 10,
                        font: {
                            size: 11
                        }
                    },
                    title: {
                        display: true,
                        text: 'Messpunkt',
                        color: '#9aa0a6'
                    }
                },
                y: {
                    display: true,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.05)',
                        drawBorder: false
                    },
                    ticks: {
                        color: '#9aa0a6',
                        font: {
                            size: 11
                        }
                    }
                }
            }
        }
    });
}

// CSV Download/View Funktionen
function downloadCSV() {
    const url = currentFile ? 
        `/download/csv?file=${encodeURIComponent(currentFile)}` : 
        '/download/csv';
    window.location.href = url;
}

function downloadFileCSV(filepath) {
    window.location.href = `/download/csv?file=${encodeURIComponent(filepath)}`;
}

async function viewCSV() {
    const url = currentFile ? 
        `/view/csv?file=${encodeURIComponent(currentFile)}` : 
        '/view/csv';
    await viewCSVWithUrl(url);
}

async function viewFileCSV(filepath) {
    const url = `/view/csv?file=${encodeURIComponent(filepath)}`;
    await viewCSVWithUrl(url);
}

async function viewCSVWithUrl(url) {
    const modal = document.getElementById('csvModal');
    const content = document.getElementById('csvContent');
    
    modal.style.display = 'block';
    content.innerHTML = '<div class="loading">Lade CSV-Daten</div>';
    
    try {
        const response = await fetch(url);
        const data = await response.json();
        
        if (data.error) {
            content.innerHTML = `<div class="error">Fehler: ${data.error}</div>`;
            return;
        }
        
        let html = `
            <div style="margin-bottom: 1rem; color: #9aa0a6;">
                <strong>${data.filename}</strong><br>
                Zeige ${data.displayed_rows} von ${data.total_rows} Zeilen
            </div>
            <table class="csv-table">
                <thead>
                    <tr>
        `;
        
        data.columns.forEach(col => {
            html += `<th>${col}</th>`;
        });
        html += '</tr></thead><tbody>';
        
        data.data.forEach(row => {
            html += '<tr>';
            data.columns.forEach(col => {
                html += `<td>${row[col] !== null && row[col] !== undefined ? row[col] : ''}</td>`;
            });
            html += '</tr>';
        });
        
        html += '</tbody></table>';
        content.innerHTML = html;
        
    } catch (error) {
        console.error('Error loading CSV:', error);
        content.innerHTML = `<div class="error">Fehler beim Laden der CSV-Daten</div>`;
    }
}

function closeModal() {
    document.getElementById('csvModal').style.display = 'none';
}

window.onclick = function(event) {
    const modal = document.getElementById('csvModal');
    if (event.target == modal) {
        modal.style.display = 'none';
    }
}

document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        closeModal();
    }
});

if ('Notification' in window && Notification.permission === 'default') {
    Notification.requestPermission();
}