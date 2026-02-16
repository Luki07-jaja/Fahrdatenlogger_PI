# 🏍️ Fahrdatenlogger - Logger & Dashboard Integration

## 📋 Übersicht

Dieses Paket enthält alle Änderungen, um deinen RaspberryPi Logger automatisch mit dem Web Dashboard zu verbinden und das Dashboard um ein History-Feature zu erweitern.

## ✨ Neue Features

### Logger (RaspberryPi_App):
- ✅ Automatisches Schreiben des CSV-Pfads nach Fahrtende
- ✅ Trigger-File für Dashboard-Integration
- ✅ Minimal invasive Änderungen (nur 1 Funktion erweitert)

### Dashboard (Web UI):
- ✅ **Automatische CSV-Erkennung** - Findet neueste Fahrt automatisch
- ✅ **Letzte 5 Fahrten anzeigen** - Mit Metadaten (Datum, Zeit, Größe, Datenpunkte)
- ✅ **Download beliebiger Fahrten** - Direkt aus der History
- ✅ **CSV-Ansicht für jede Fahrt** - Schnellansicht der Rohdaten
- ✅ **Live-Aktualisierung** - Prüft alle 10 Sekunden auf neue Fahrten
- ✅ **Visuelles Highlight** - Aktuelle Fahrt wird in der History markiert
- ✅ **Original Design beibehalten** - Alle Farben und Styles bleiben gleich

## 📁 Dateien in diesem Paket

### Logger-Änderungen:
- `LOGGER_CHANGES.md` - Detaillierte Anweisungen für Logger-Änderungen

### Dashboard-Dateien (komplett):
- `dashboard.py` - Verbesserter Flask-Server mit Auto-Detection
- `templates/dashboard.html` - Erweiterte HTML-Vorlage mit History
- `static/js/dashboard.js` - Verbessertes JavaScript mit neuen Features
- `static/css/style.css` - Original CSS (unverändert, für Vollständigkeit)

### Dokumentation:
- `README.md` - Diese Datei
- `INSTALLATION.md` - Schritt-für-Schritt Installationsanleitung
- `TESTING.md` - So testest du die Integration

## 🚀 Schnellstart

### 1. Dashboard Setup

#### Option A: Bestehende Installation erweitern

1. **Sichere dein altes Dashboard:**
   ```bash
   cd /pfad/zu/fahrdatenlogger-dashboard
   cp dashboard.py dashboard.py.backup
   ```

2. **Ersetze die Dateien:**
   ```bash
   # dashboard.py ersetzen
   cp dashboard.py /pfad/zu/fahrdatenlogger-dashboard/
   
   # templates/dashboard.html ersetzen
   cp templates/dashboard.html /pfad/zu/fahrdatenlogger-dashboard/templates/
   
   # static/js/dashboard.js ersetzen
   cp static/js/dashboard.js /pfad/zu/fahrdatenlogger-dashboard/static/js/
   ```

3. **Pfade in dashboard.py anpassen (Zeile 16-18):**
   ```python
   # Passe diese Pfade an!
   LOGS_DIR = "/home/luki/Fahrdatenlogger/RaspberryPi_App/logs"
   WATCH_FILE = os.path.join(LOGS_DIR, "latest_csv.txt")
   ```

4. **Dashboard starten:**
   ```bash
   python3 dashboard.py
   ```

#### Option B: Neue Installation

```bash
# Verzeichnis erstellen
mkdir fahrdatenlogger-dashboard-v2
cd fahrdatenlogger-dashboard-v2

# Dateien kopieren (aus diesem Paket)
# Struktur:
# fahrdatenlogger-dashboard-v2/
# ├── dashboard.py
# ├── templates/
# │   └── dashboard.html
# └── static/
#     ├── css/
#     │   └── style.css
#     └── js/
#         └── dashboard.js

# Abhängigkeiten installieren
pip install flask pandas numpy --break-system-packages

# Pfade in dashboard.py anpassen
nano dashboard.py  # Zeile 16-18 ändern

# Starten
python3 dashboard.py
```

## 🔧 Konfiguration

### Dashboard-Pfade anpassen

In `dashboard.py` (Zeile 16-18):

```python
# WICHTIG: Diese Pfade müssen zum Logger passen!
LOGS_DIR = "/home/luki/Fahrdatenlogger/RaspberryPi_App/logs"
WATCH_FILE = os.path.join(LOGS_DIR, "latest_csv.txt")
```

### Standalone-Modus (ohne Logger)

Wenn du das Dashboard ohne laufenden Logger testen willst:

```python
# In dashboard.py Zeile 18 auskommentieren:
# WATCH_FILE = os.path.join(LOGS_DIR, "latest_csv.txt")

# Und einen lokalen logs-Ordner verwenden:
LOGS_DIR = "./logs"
```

## 📊 Wie es funktioniert

### Logger → Dashboard Flow:

1. **Fahrt startet** → Logger erstellt neue SQLite DB
2. **Fahrt läuft** → Daten werden geloggt
3. **Fahrt endet** → `logger.close()` wird aufgerufen
4. **CSV Export** → SQLite → CSV Datei erstellt
5. **Trigger** → Pfad wird in `latest_csv.txt` geschrieben ✨ NEU!
6. **Dashboard** → Prüft alle 10 Sek. auf neue Dateien
7. **Auto-Update** → Zeigt neue Fahrt in History an

### Dashboard Features:

#### Automatische Erkennung:
```
Methode 1: Watch-File lesen (latest_csv.txt)
    ↓
Methode 2: Neueste CSV im logs/ Ordner finden
    ↓
Zeigt aktuellste Fahrt im Dashboard
```

#### History-Feature:
```
Findet alle *_fahrt.csv Dateien
    ↓
Sortiert nach Änderungsdatum
    ↓
Zeigt letzte 5 mit Metadaten
    ↓
Jede Fahrt: Anzeigen, Downloaden, Analysieren
```

## 🎨 UI-Features

### History-Liste:
- 📁 **Fahrt #1-5** mit Datum/Zeit
- 📏 **Dateigröße** in KB
- 📊 **Anzahl Datenpunkte**
- 👁️ **CSV ansehen** Button
- 📥 **Download** Button
- 💜 **Active-State** für aktuell angezeigte Fahrt

### Header-Buttons:
- **CSV Ansehen** → Zeigt Rohdaten der aktuellen Fahrt
- **Download CSV** → Lädt aktuelle Fahrt herunter

### Auto-Refresh:
- ⏰ Prüft alle 10 Sekunden auf neue Dateien
- 🔔 Optional: Browser-Benachrichtigung bei neuer Fahrt
- 🔄 Manueller Refresh-Button in History

## 🧪 Testing

### 1. Logger-Test (ohne Dashboard)

```bash
cd /home/luki/Fahrdatenlogger/RaspberryPi_App
python3 main.py
# Warte einige Sekunden
# CTRL+C zum Beenden

# Prüfe ob latest_csv.txt erstellt wurde:
cat logs/latest_csv.txt
# Sollte Pfad zur CSV anzeigen
```

### 2. Dashboard-Test (ohne Logger)

```bash
# Test-CSV erstellen
mkdir -p logs
echo "id,timestamp,speed
1,2026-02-16 10:00:00,50
2,2026-02-16 10:00:01,55" > logs/test_fahrt.csv

# Dashboard starten
python3 dashboard.py
# Browser öffnen: http://localhost:5000
```

### 3. Integrationstest

```bash
# Terminal 1: Dashboard starten
python3 dashboard.py

# Terminal 2: Logger starten
cd RaspberryPi_App
python3 main.py
# Warte 10-30 Sekunden
# CTRL+C

# Browser: Dashboard sollte automatisch aktualisieren
```

## 🐛 Fehlersuche

### Problem: Dashboard findet keine CSV

**Lösung:**
```python
# In dashboard.py den LOGS_DIR prüfen:
print(f"Suche CSVs in: {LOGS_DIR}")
print(f"Gefunden: {glob.glob(os.path.join(LOGS_DIR, '*_fahrt.csv'))}")
```

### Problem: History leer

**Checks:**
1. Existiert der logs/ Ordner?
2. Sind CSV-Dateien mit `*_fahrt.csv` Pattern vorhanden?
3. Sind die Dateien lesbar?

```bash
ls -la /home/luki/Fahrdatenlogger/RaspberryPi_App/logs/
```

### Problem: Auto-Refresh funktioniert nicht

**Lösung:** Browser-Konsole öffnen (F12) und nach Fehlern suchen

```javascript
// In Browser-Konsole testen:
fetch('/api/recent-files')
  .then(r => r.json())
  .then(d => console.log(d))
```

## 📝 API Endpoints

Das Dashboard bietet folgende API-Endpoints:

### `GET /api/stats`
Statistiken der aktuellen/spezifischen Fahrt
- Optional: `?file=/pfad/zur/fahrt.csv`

### `GET /api/recent-files`
Letzte 5 Fahrten mit Metadaten

### `GET /download/csv`
CSV-Datei herunterladen
- Optional: `?file=/pfad/zur/fahrt.csv`

### `GET /view/csv`
CSV-Daten als JSON
- Optional: `?file=/pfad/zur/fahrt.csv`

### `GET /health`
Health Check - zeigt System-Status

## 🔐 Sicherheitshinweise

### Produktion (öffentlicher Zugriff):

```python
# In dashboard.py ändern:
# NICHT für Produktion:
app.run(debug=True, host='0.0.0.0', port=5000)

# FÜR Produktion:
app.run(debug=False, host='127.0.0.1', port=5000)
# + nginx als Reverse Proxy
# + Authentifizierung hinzufügen
```

## 🎯 Nächste Schritte

1. ✅ Logger-Änderungen implementieren
2. ✅ Dashboard-Dateien ersetzen
3. ✅ Pfade anpassen
4. ✅ Testen
5. 🚀 **Fertig!**

## 💡 Weitere Verbesserungsideen

Möglich für die Zukunft:
- 🗺️ GPS-Karte in History-Preview
- 📈 Mini-Charts in History-Items
- 🔍 Such-/Filterfunktion für Fahrten
- 📊 Vergleich zwischen zwei Fahrten
- 📤 Export als PDF-Report
- 🌐 Live-View während der Fahrt

## 📞 Support

Bei Problemen:
1. Prüfe die Logs: `tail -f logs/run_*_debug.log`
2. Browser-Konsole checken (F12)
3. Health-Check: `curl http://localhost:5000/health`

## 🎉 Viel Erfolg!

Die Integration ist so designed, dass:
- ✅ Logger minimal geändert wird (nur 1 Funktion)
- ✅ Dashboard vollständig kompatibel ist
- ✅ Alles rückwärtskompatibel bleibt
- ✅ Kein Breaking Change entsteht

**Happy Coding & Safe Riding!** 🏍️💨
