# 🚗 Fahrdatenlogger Dashboard

Ein modernes, Dark-Mode Dashboard zur Visualisierung von Fahrdaten aus deinem Tacho-Logger.

## 📊 Features

### Anzeige von Mittelwerten
- ✅ Durchschnittsgeschwindigkeit (inkl. Max/Min)
- ✅ Kurvenlage in Grad (Lean Angle)
- ✅ Batteriespannung (Durchschnitt, Min, Max)
- ✅ Batterietemperatur (Durchschnitt, Max)

### Fahrtinformationen
- ✅ Gesamte Fahrzeit (HH:MM:SS)
- ✅ Gesamtstrecke in km
- ✅ Anzahl der Datensätze

### Datenvisualisierung
- 📈 Interaktive Charts für:
  - Geschwindigkeitsverlauf
  - Kurvenlage über Zeit
  - Batteriespannungsverlauf
  - Temperaturverlauf

### Datenverwaltung
- 📥 Download der kompletten CSV-Datei
- 👁️ CSV-Viewer im Browser (erste 1000 Zeilen)

## 🎨 Design

- 🌑 Moderner Dark Mode
- 📱 Responsive Design
- 💎 Glassmorphismus-Effekte
- ⚡ Smooth Animationen
- 📊 Professionelle Datenvisualisierung

## 🛠️ Installation

### Voraussetzungen
- Python 3.8 oder höher
- pip (Python Package Manager)

### Schritt 1: Abhängigkeiten installieren

```bash
pip install flask pandas numpy
```

### Schritt 2: CSV-Datei Pfad anpassen

Öffne `dashboard.py` und passe den CSV-Pfad in Zeile 16 an:

```python
CSV_FILE = '/pfad/zu/deiner/fahrt.csv'
```

### Schritt 3: Server starten

```bash
python dashboard.py
```

oder mit dem Start-Script:

```bash
chmod +x start.sh
./start.sh
```

### Schritt 4: Dashboard öffnen

Öffne deinen Browser und gehe zu:
```
http://localhost:5000
```

## 📁 Projektstruktur

```
fahrdatenlogger-dashboard/
├── dashboard.py           # Python Backend (Flask + Datenanalyse)
├── start.sh              # Start-Script
├── requirements.txt      # Python Dependencies
├── templates/
│   └── dashboard.html    # HTML Template
└── static/
    ├── css/
    │   └── style.css     # Styling (Dark Mode)
    └── js/
        └── dashboard.js  # JavaScript für Interaktivität
```

## 🔧 Technologien

### Backend
- **Flask** - Python Web Framework
- **Pandas** - Datenverarbeitung und Analyse
- **NumPy** - Numerische Berechnungen

### Frontend
- **HTML5** - Struktur
- **CSS3** - Styling mit modernem Dark Mode
- **JavaScript** - Interaktivität
- **Chart.js** - Datenvisualisierung

## 📝 CSV Format

Das Dashboard erwartet eine CSV-Datei mit Semikolon-Trennung (`;`) und folgenden Spalten:

- `drive_time` - Fahrzeit im Format HH:MM:SS:mmm
- `drive_distance` - Gefahrene Strecke in Metern
- `gps_speed` - Geschwindigkeit in km/h
- `lean_deg` - Kurvenlage in Grad
- `batt_voltage` - Batteriespannung in Volt
- `max_batt_temp` - Maximale Batterietemperatur in °C

Weitere Spalten werden ignoriert, können aber in der CSV-Ansicht eingesehen werden.

## 🚀 Features im Detail

### Mittelwert-Berechnung
- Filtert ungültige Werte (z.B. GPS-Speed = 0)
- Berechnet statistische Kennzahlen (Durchschnitt, Min, Max)
- Berücksichtigt absolute Werte bei Kurvenlage

### Charts
- Zeigt jeden 50. Datenpunkt für bessere Performance
- Interaktive Hover-Tooltips
- Responsive und smooth

### CSV-Viewer
- Zeigt die ersten 1000 Zeilen an
- Scrollbare Tabelle
- Alle Spalten sichtbar

## ⚙️ Anpassungen

### CSV-Pfad ändern
```python
# In dashboard.py, Zeile 16
CSV_FILE = '/dein/pfad/zur/datei.csv'
```

### Port ändern
```python
# In dashboard.py, letzte Zeile
app.run(debug=True, host='0.0.0.0', port=5000)  # Ändere 5000 zu deinem Port
```

### Sampling-Rate der Charts
```python
# In dashboard.py, bei den Zeitreihen
'speed_data': valid_speeds[::50].tolist()  # Ändere 50 zu deinem Wert
```

## 🐛 Troubleshooting

### "No module named 'flask'" Fehler
```bash
pip install flask pandas numpy
```

### CSV-Datei nicht gefunden
Überprüfe den Pfad in `dashboard.py` (Zeile 16) und stelle sicher, dass die Datei existiert.

### Port bereits in Verwendung
Ändere den Port in `dashboard.py` (letzte Zeile) oder stoppe den anderen Prozess:
```bash
# Linux/Mac
lsof -ti:5000 | xargs kill -9

# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

## 📱 Mobile Ansicht

Das Dashboard ist vollständig responsive und funktioniert auf:
- 📱 Smartphones
- 📱 Tablets
- 💻 Laptops
- 🖥️ Desktop-Monitoren

## 🔐 Sicherheit

**Hinweis:** Dieses Dashboard ist für den lokalen Gebrauch konzipiert. 
Für den produktiven Einsatz solltest du:
- HTTPS aktivieren
- Authentifizierung hinzufügen
- CORS-Richtlinien konfigurieren
- Rate-Limiting implementieren

## 📄 Lizenz

Dieses Projekt ist für den persönlichen Gebrauch frei verfügbar.

## 🤝 Support

Bei Fragen oder Problemen kannst du:
1. Die CSV-Datei überprüfen
2. Die Python-Konsole auf Fehler überprüfen
3. Den Browser-Entwickler-Console überprüfen (F12)

## 🎯 Zukünftige Features (Optional)

- [ ] GPS-Kartenansicht der Route
- [ ] Export als PDF-Report
- [ ] Vergleich mehrerer Fahrten
- [ ] Echtzeit-Monitoring während der Fahrt
- [ ] Datenbank-Integration
- [ ] Benutzer-Authentifizierung
- [ ] Fahrtstatistik-Historie

---

**Viel Spaß mit deinem Fahrdatenlogger Dashboard! 🚗💨**
