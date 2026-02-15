# 🚀 QUICK START ANLEITUNG

## ⚡ Schnellstart in 3 Schritten

### 1️⃣ CSV-Pfad anpassen
Öffne `dashboard.py` und ändere in Zeile 16:
```python
CSV_FILE = '/mnt/user-data/uploads/2026-02-12_12-34-58_fahrt.csv'
```
zu deinem CSV-Pfad, z.B.:
```python
CSV_FILE = '/home/dein-user/fahrdaten/meine-fahrt.csv'
```

### 2️⃣ Dependencies installieren

**Linux/Mac:**
```bash
pip install -r requirements.txt
```

**oder direkt:**
```bash
pip install flask pandas numpy
```

### 3️⃣ Dashboard starten

**Linux/Mac:**
```bash
./start.sh
```

**Windows:**
```
start.bat
```

**oder manuell:**
```bash
python dashboard.py
```

### 4️⃣ Browser öffnen
```
http://localhost:5000
```

---

## 🎯 Das war's!

Dein Dashboard sollte jetzt laufen und zeigt:
- ✅ Durchschnittsgeschwindigkeit & Max-Speed
- ✅ Kurvenlage (Lean Angle)
- ✅ Batteriespannung & Temperatur
- ✅ Gesamtzeit & Strecke
- ✅ Interaktive Charts
- ✅ CSV Download & Viewer

---

## ⚠️ Probleme?

### Port bereits belegt?
Ändere in `dashboard.py` (letzte Zeile):
```python
app.run(debug=True, host='0.0.0.0', port=5000)
```
zu einem anderen Port, z.B.:
```python
app.run(debug=True, host='0.0.0.0', port=8080)
```

### CSV nicht gefunden?
- Überprüfe den Pfad in `dashboard.py`
- Stelle sicher, dass die Datei existiert
- Verwende absolute Pfade (z.B. `/home/user/file.csv`)

### Module nicht gefunden?
```bash
pip install flask pandas numpy
```

---

## 📱 Zugriff von anderen Geräten

Finde deine IP-Adresse:
```bash
# Linux/Mac
ifconfig | grep inet

# Windows
ipconfig
```

Dann öffne auf einem anderen Gerät:
```
http://DEINE-IP:5000
```

---

**Viel Erfolg! 🚗💨**
