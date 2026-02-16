// Dashboard JavaScript - Erweiterte Version mit History Feature
let charts = {};
let currentFile = null;
let recentFiles = [];

// Initialisierung beim Laden der Seite
document.addEventListener('DOMContentLoaded', function() {
    loadRecentFiles();
    loadDashboardData();
    
    // Auto-Refresh alle 10 Sekunden auf neue Fahrten prüfen
    setInterval(checkForNewFiles, 10000);
});

// Haupt funktion zum Laden der Dashboard-Daten
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
                
                // Optional: Automatisch neue Fahrt laden
                // loadDashboardData(newFiles[0].filepath);
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
    // Einfache Browser-Benachrichtigung
    if (Notification.permission === "granted") {
        new Notification("Fahrdatenlogger", {
            body: message,
            icon: "/static/favicon.ico"
        });
    }
    
    // Alternativ: Inline-Benachrichtigung im UI
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
    
    // Datensatz-Anzahl
    document.getElementById('record-count').textContent = 
        data.total_records.toLocaleString('de-DE');
}

// Charts erstellen/aktualisieren
function updateCharts(data) {
    // Geschwindigkeits-Chart
    createOrUpdateChart('speedChart', {
        label: 'Geschwindigkeit (km/h)',
        data: data.speed_data,
        borderColor: '#00d4ff',
        backgroundColor: 'rgba(0, 212, 255, 0.1)',
        fill: true
    });
    
    // Kurvenlage-Chart
    createOrUpdateChart('leanChart', {
        label: 'Kurvenlage (°)',
        data: data.lean_data,
        borderColor: '#fa709a',
        backgroundColor: 'rgba(250, 112, 154, 0.1)',
        fill: true
    });
    
    // Batteriespannungs-Chart
    createOrUpdateChart('voltageChart', {
        label: 'Spannung (V)',
        data: data.voltage_data,
        borderColor: '#43e97b',
        backgroundColor: 'rgba(67, 233, 123, 0.1)',
        fill: true
    });
    
    // Batterietemperatur-Chart
    createOrUpdateChart('tempChart', {
        label: 'Temperatur (°C)',
        data: data.temp_data,
        borderColor: '#ff6b6b',
        backgroundColor: 'rgba(255, 107, 107, 0.1)',
        fill: true
    });
}

// Hilfsfunktion zum Erstellen/Aktualisieren von Charts
function createOrUpdateChart(canvasId, config) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    
    // Wenn Chart existiert, zerstöre ihn
    if (charts[canvasId]) {
        charts[canvasId].destroy();
    }
    
    // Labels erstellen (Messpunkt-Nummern)
    const labels = config.data.map((_, index) => index + 1);
    
    // Neuen Chart erstellen
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

// CSV Download (aktuelle Datei)
function downloadCSV() {
    const url = currentFile ? 
        `/download/csv?file=${encodeURIComponent(currentFile)}` : 
        '/download/csv';
    window.location.href = url;
}

// CSV Download (spezifische Datei)
function downloadFileCSV(filepath) {
    window.location.href = `/download/csv?file=${encodeURIComponent(filepath)}`;
}

// CSV Anzeigen (aktuelle Datei)
async function viewCSV() {
    const url = currentFile ? 
        `/view/csv?file=${encodeURIComponent(currentFile)}` : 
        '/view/csv';
    await viewCSVWithUrl(url);
}

// CSV Anzeigen (spezifische Datei)
async function viewFileCSV(filepath) {
    const url = `/view/csv?file=${encodeURIComponent(filepath)}`;
    await viewCSVWithUrl(url);
}

// CSV Modal anzeigen
async function viewCSVWithUrl(url) {
    const modal = document.getElementById('csvModal');
    const content = document.getElementById('csvContent');
    
    // Modal öffnen
    modal.style.display = 'block';
    content.innerHTML = '<div class="loading">Lade CSV-Daten</div>';
    
    try {
        const response = await fetch(url);
        const data = await response.json();
        
        if (data.error) {
            content.innerHTML = `<div class="error">Fehler: ${data.error}</div>`;
            return;
        }
        
        // Tabelle erstellen
        let html = `
            <div style="margin-bottom: 1rem; color: #9aa0a6;">
                <strong>${data.filename}</strong><br>
                Zeige ${data.displayed_rows} von ${data.total_rows} Zeilen
            </div>
            <table class="csv-table">
                <thead>
                    <tr>
        `;
        
        // Spaltenköpfe
        data.columns.forEach(col => {
            html += `<th>${col}</th>`;
        });
        html += '</tr></thead><tbody>';
        
        // Datenzeilen
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

// Modal schließen
function closeModal() {
    document.getElementById('csvModal').style.display = 'none';
}

// Modal schließen bei Klick außerhalb
window.onclick = function(event) {
    const modal = document.getElementById('csvModal');
    if (event.target == modal) {
        modal.style.display = 'none';
    }
}

// ESC-Taste zum Schließen
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        closeModal();
    }
});

// Benachrichtigungs-Berechtigung anfordern (optional)
if ('Notification' in window && Notification.permission === 'default') {
    Notification.requestPermission();
}
