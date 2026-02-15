#!/bin/bash

echo "================================================"
echo "🚗 Fahrdatenlogger Dashboard"
echo "================================================"
echo ""

# Überprüfe ob Python installiert ist
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 ist nicht installiert!"
    echo "Bitte installiere Python 3.8 oder höher."
    exit 1
fi

echo "✅ Python gefunden: $(python3 --version)"
echo ""

# Überprüfe ob pip installiert ist
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip ist nicht installiert!"
    echo "Bitte installiere pip."
    exit 1
fi

echo "📦 Überprüfe Abhängigkeiten..."
echo ""

# Installiere Requirements falls nötig
if [ -f "requirements.txt" ]; then
    pip3 install -q -r requirements.txt
    if [ $? -eq 0 ]; then
        echo "✅ Alle Abhängigkeiten installiert"
    else
        echo "❌ Fehler beim Installieren der Abhängigkeiten"
        exit 1
    fi
else
    echo "⚠️  requirements.txt nicht gefunden"
    echo "Installiere manuell: pip3 install flask pandas numpy"
fi

echo ""
echo "🚀 Starte Dashboard..."
echo ""
echo "================================================"
echo "Dashboard läuft auf: http://localhost:5000"
echo "================================================"
echo ""
echo "Drücke CTRL+C zum Beenden"
echo ""

# Starte Flask App
python3 dashboard.py
