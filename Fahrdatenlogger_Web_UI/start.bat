@echo off
echo ================================================
echo 🚗 Fahrdatenlogger Dashboard
echo ================================================
echo.

REM Überprüfe ob Python installiert ist
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python ist nicht installiert!
    echo Bitte installiere Python 3.8 oder hoeher von python.org
    pause
    exit /b 1
)

echo ✅ Python gefunden
echo.

echo 📦 Ueberpruefe Abhaengigkeiten...
echo.

REM Installiere Requirements
if exist requirements.txt (
    pip install -q -r requirements.txt
    if errorlevel 1 (
        echo ❌ Fehler beim Installieren der Abhaengigkeiten
        pause
        exit /b 1
    )
    echo ✅ Alle Abhaengigkeiten installiert
) else (
    echo ⚠️  requirements.txt nicht gefunden
    echo Installiere manuell: pip install flask pandas numpy
)

echo.
echo 🚀 Starte Dashboard...
echo.
echo ================================================
echo Dashboard laeuft auf: http://localhost:5000
echo ================================================
echo.
echo Druecke CTRL+C zum Beenden
echo.

REM Starte Flask App
python dashboard.py

pause
