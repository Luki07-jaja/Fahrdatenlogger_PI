// Dashboard JavaScript
let charts = {};

// Initialisierung beim Laden der Seite
document.addEventListener('DOMContentLoaded', function() {
    loadDashboardData();
    // Aktualisierung alle 30 Sekunden (optional)
    // setInterval(loadDashboardData, 30000);
});

// Hauptfunktion zum Laden der Dashboard-Daten
async function loadDashboardData() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();
        
        if (data.error) {
            console.error('Error loading data:', data.error);
            return;
        }
        
        // KPI Cards aktualisieren
        updateKPIs(data);
        
        // Charts erstellen/aktualisieren
        updateCharts(data);
        
    } catch (error) {
        console.error('Error fetching dashboard data:', error);
    }
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

// CSV Download
function downloadCSV() {
    window.location.href = '/download/csv';
}

// CSV Anzeigen
async function viewCSV() {
    const modal = document.getElementById('csvModal');
    const content = document.getElementById('csvContent');
    
    // Modal öffnen
    modal.style.display = 'block';
    content.innerHTML = '<div class="loading">Lade CSV-Daten</div>';
    
    try {
        const response = await fetch('/view/csv');
        const data = await response.json();
        
        if (data.error) {
            content.innerHTML = `<div class="error">Fehler: ${data.error}</div>`;
            return;
        }
        
        // Tabelle erstellen
        let html = `
            <div style="margin-bottom: 1rem; color: #9aa0a6;">
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
