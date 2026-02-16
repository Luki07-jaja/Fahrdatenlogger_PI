#!/bin/bash

echo "=================================="
echo "Fahrdatenlogger Dashboard Setup"
echo "=================================="
echo ""

# Prüfe Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 nicht gefunden!"
    exit 1
fi

echo "✓ Python3 gefunden: $(python3 --version)"

# Installiere Abhängigkeiten
echo ""
echo "📦 Installiere Abhängigkeiten..."
pip3 install flask pandas numpy --break-system-packages

# Prüfe ob erfolgreich
if [ $? -eq 0 ]; then
    echo "✓ Abhängigkeiten installiert"
else
    echo "❌ Installation fehlgeschlagen"
    exit 1
fi

# Konfiguration
echo ""
echo "⚙️  Konfiguration:"
echo ""
echo "Bitte passe die Pfade in dashboard.py an:"
echo "  - Zeile 16: LOGS_DIR = \"/dein/pfad/zu/RaspberryPi_App/logs\""
echo ""
echo "Dann starte das Dashboard mit:"
echo "  python3 dashboard.py"
echo ""
echo "Dashboard wird verfügbar sein unter: http://localhost:5000"
echo ""
echo "=================================="
echo "✅ Setup abgeschlossen!"
echo "=================================="
