#!/usr/bin/env python3
"""
Fahrdatenlogger Dashboard - Verbesserte Version
Automatische CSV-Erkennung + Letzte 5 Fahrten Feature
"""

from flask import Flask, render_template, jsonify, send_file, request
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import glob
from pathlib import Path

app = Flask(__name__)

# Konfiguration - Passe diese Pfade an!
# Option 1: Raspberry Pi Logger Integration
LOGS_DIR = "/home/luki/Fahrdatenlogger/RaspberryPi_App/logs"
WATCH_FILE = os.path.join(LOGS_DIR, "latest_csv.txt")

# Option 2: Standalone Modus (falls kein Logger läuft)
# LOGS_DIR = "./logs"  # Lokaler logs Ordner

# Sicherstellen, dass logs Directory existiert
os.makedirs(LOGS_DIR, exist_ok=True)

def get_latest_csv():
    """Findet die neueste CSV-Datei (automatisch)"""
    try:
        # Methode 1: Aus Watch-File lesen (wenn Logger gerade geschlossen wurde)
        if os.path.exists(WATCH_FILE):
            with open(WATCH_FILE, 'r') as f:
                csv_path = f.read().strip()
                if os.path.exists(csv_path):
                    return csv_path
        
        # Methode 2: Neueste CSV im logs Ordner finden
        csv_files = glob.glob(os.path.join(LOGS_DIR, "*_fahrt.csv"))
        if csv_files:
            # Nach Änderungsdatum sortieren (neueste zuerst)
            latest = max(csv_files, key=os.path.getmtime)
            return latest
        
        return None
    except Exception as e:
        print(f"Fehler beim Finden der CSV: {e}")
        return None

def get_recent_csvs(limit=5):
    """Findet die letzten N CSV-Dateien mit Metadaten"""
    try:
        csv_files = glob.glob(os.path.join(LOGS_DIR, "*_fahrt.csv"))
        
        if not csv_files:
            return []
        
        # Nach Änderungsdatum sortieren (neueste zuerst)
        csv_files.sort(key=os.path.getmtime, reverse=True)
        
        recent = []
        for csv_file in csv_files[:limit]:
            try:
                # Dateiinfo sammeln
                stat = os.stat(csv_file)
                file_size = stat.st_size / 1024  # KB
                mod_time = datetime.fromtimestamp(stat.st_mtime)
                
                # Schnell-Info aus CSV lesen
                df = pd.read_csv(csv_file, sep=';', nrows=1)
                total_rows = sum(1 for _ in open(csv_file)) - 1  # Zeilen ohne Header
                
                # Dateiname parsen für Datum/Zeit
                basename = os.path.basename(csv_file)
                filename_parts = basename.replace('_fahrt.csv', '').split('_')
                
                recent.append({
                    'filename': basename,
                    'filepath': csv_file,
                    'date': filename_parts[0] if len(filename_parts) > 0 else 'Unbekannt',
                    'time': filename_parts[1].replace('-', ':') if len(filename_parts) > 1 else 'Unbekannt',
                    'modified': mod_time.strftime('%d.%m.%Y %H:%M:%S'),
                    'size_kb': round(file_size, 1),
                    'total_rows': total_rows
                })
            except Exception as e:
                print(f"Fehler beim Laden von {csv_file}: {e}")
                continue
        
        return recent
    except Exception as e:
        print(f"Fehler beim Sammeln der CSVs: {e}")
        return []

def parse_time(time_str):
    """Konvertiert HH:MM:SS:mmm Format zu Sekunden"""
    try:
        parts = time_str.split(':')
        hours = int(parts[0])
        minutes = int(parts[1])
        seconds = int(parts[2])
        milliseconds = int(parts[3]) if len(parts) > 3 else 0
        return hours * 3600 + minutes * 60 + seconds + milliseconds / 1000
    except:
        return 0

def analyze_data(csv_file=None):
    """Analysiert die CSV-Daten und berechnet Statistiken"""
    try:
        # CSV-Datei auswählen
        if csv_file is None:
            csv_file = get_latest_csv()
        
        if csv_file is None or not os.path.exists(csv_file):
            raise FileNotFoundError("Keine CSV-Datei gefunden")
        
        # CSV laden mit Semikolon als Trennzeichen
        df = pd.read_csv(csv_file, sep=';')
        
        # Datenbereinigung - nur numerische Werte
        numeric_cols = ['gps_speed', 'lean_deg', 'batt_voltage', 'max_batt_temp', 'drive_distance']
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # GPS Speed von km/h filtern (nur gültige Werte > 0)
        valid_speeds = df[df['gps_speed'] > 0]['gps_speed']
        
        # Fahrzeit berechnen
        drive_times = df['drive_time'].apply(parse_time)
        total_time_seconds = drive_times.max() if len(drive_times) > 0 else 0
        total_time = str(timedelta(seconds=int(total_time_seconds)))
        
        # Gesamtstrecke (letzter Wert in km)
        total_distance = df['drive_distance'].max() / 1000  # Umrechnung in km
        
        # Statistiken berechnen
        stats = {
            # Dateiinfo
            'current_file': os.path.basename(csv_file),
            'current_filepath': csv_file,
            
            # Geschwindigkeit
            'avg_speed': round(valid_speeds.mean(), 2) if len(valid_speeds) > 0 else 0,
            'max_speed': round(valid_speeds.max(), 2) if len(valid_speeds) > 0 else 0,
            'min_speed': round(valid_speeds.min(), 2) if len(valid_speeds) > 0 else 0,
            
            # Kurvenlage (Lean Angle)
            'avg_lean': round(df['lean_deg'].abs().mean(), 2),
            'max_lean': round(df['lean_deg'].abs().max(), 2),
            'max_lean_left': round(df['lean_deg'].min(), 2),
            'max_lean_right': round(df['lean_deg'].max(), 2),
            
            # Batterie Spannung
            'avg_voltage': round(df['batt_voltage'].mean(), 2),
            'max_voltage': round(df['batt_voltage'].max(), 2),
            'min_voltage': round(df['batt_voltage'].min(), 2),
            
            # Batterie Temperatur
            'avg_temp': round(df['max_batt_temp'].mean(), 2),
            'max_temp': round(df['max_batt_temp'].max(), 2),
            'min_temp': round(df['max_batt_temp'].min(), 2),
            
            # Fahrt Info
            'total_time': total_time,
            'total_distance': round(total_distance, 2),
            'total_records': len(df),
            
            # Zeitreihen für Diagramme (alle 50. Datenpunkt)
            'speed_data': valid_speeds[::50].tolist() if len(valid_speeds) > 0 else [],
            'lean_data': df['lean_deg'][::50].tolist(),
            'voltage_data': df['batt_voltage'][::50].tolist(),
            'temp_data': df['max_batt_temp'][::50].tolist(),
        }
        
        return stats
    
    except Exception as e:
        print(f"Error analyzing data: {e}")
        return {
            'error': str(e),
            'current_file': 'Keine Datei',
            'current_filepath': None,
            'avg_speed': 0, 'max_speed': 0, 'min_speed': 0,
            'avg_lean': 0, 'max_lean': 0, 'max_lean_left': 0, 'max_lean_right': 0,
            'avg_voltage': 0, 'max_voltage': 0, 'min_voltage': 0,
            'avg_temp': 0, 'max_temp': 0, 'min_temp': 0,
            'total_time': '00:00:00', 'total_distance': 0, 'total_records': 0,
            'speed_data': [], 'lean_data': [], 'voltage_data': [], 'temp_data': []
        }

@app.route('/')
def index():
    """Hauptseite mit Dashboard"""
    return render_template('dashboard.html')

@app.route('/api/stats')
def get_stats():
    """API Endpoint für Statistiken"""
    # Optional: Spezifische Datei laden
    csv_file = request.args.get('file', None)
    stats = analyze_data(csv_file)
    return jsonify(stats)

@app.route('/api/recent-files')
def get_recent_files():
    """API Endpoint für letzte 5 Dateien"""
    recent = get_recent_csvs(limit=5)
    return jsonify({
        'files': recent,
        'count': len(recent)
    })

@app.route('/download/csv')
def download_csv():
    """Download der aktuellen CSV-Datei"""
    try:
        csv_file = request.args.get('file', None)
        
        if csv_file is None:
            csv_file = get_latest_csv()
        
        if csv_file is None or not os.path.exists(csv_file):
            return jsonify({'error': 'Datei nicht gefunden'}), 404
        
        return send_file(
            csv_file,
            mimetype='text/csv',
            as_attachment=True,
            download_name=os.path.basename(csv_file)
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@app.route('/view/csv')
def view_csv():
    """CSV-Daten als JSON anzeigen"""
    try:
        csv_file = request.args.get('file', None)
        
        if csv_file is None:
            csv_file = get_latest_csv()
        
        if csv_file is None or not os.path.exists(csv_file):
            return jsonify({'error': 'Datei nicht gefunden'}), 404
        
        df = pd.read_csv(csv_file, sep=';')
        # Erste 1000 Zeilen für Anzeige
        data = df.head(1000).to_dict(orient='records')
        return jsonify({
            'filename': os.path.basename(csv_file),
            'total_rows': len(df),
            'displayed_rows': min(1000, len(df)),
            'columns': df.columns.tolist(),
            'data': data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@app.route('/health')
def health_check():
    """Health Check Endpoint"""
    latest = get_latest_csv()
    recent_count = len(get_recent_csvs())
    
    return jsonify({
        'status': 'ok',
        'logs_dir': LOGS_DIR,
        'watch_file_exists': os.path.exists(WATCH_FILE),
        'latest_csv': os.path.basename(latest) if latest else None,
        'recent_files_count': recent_count
    })

if __name__ == '__main__':
    
    latest = get_latest_csv()
    if latest:
        print(f" Aktuelle CSV: {os.path.basename(latest)}")
    else:
        print(" Keine CSV-Dateien gefunden")
    
    recent = get_recent_csvs()
    print(f" Letzte Fahrten: {len(recent)}")
    
    app.run(debug=True, host='0.0.0.0', port=8080)
