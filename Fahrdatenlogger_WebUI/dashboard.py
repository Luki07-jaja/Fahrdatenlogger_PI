#!/usr/bin/env python3
"""
Fahrdatenlogger Dashboard - Erweiterte Version
Mit Höhe (Altitude) und Neigung (Pitch) Support + Karte
"""

from flask import Flask, render_template, jsonify, send_file, request
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import glob
from pathlib import Path

app = Flask(__name__)

# Konfiguration
LOGS_DIR = "/home/luki/Fahrdatenlogger/RaspberryPi_App/logs"
WATCH_FILE = os.path.join(LOGS_DIR, "latest_csv.txt")

os.makedirs(LOGS_DIR, exist_ok=True)

def get_latest_csv():
    """Findet die neueste CSV-Datei (automatisch)"""
    try:
        if os.path.exists(WATCH_FILE):
            with open(WATCH_FILE, 'r') as f:
                csv_path = f.read().strip()
                if os.path.exists(csv_path):
                    return csv_path
        
        csv_files = glob.glob(os.path.join(LOGS_DIR, "*_fahrt.csv"))
        if csv_files:
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
        
        csv_files.sort(key=os.path.getmtime, reverse=True)
        
        recent = []
        for csv_file in csv_files[:limit]:
            try:
                stat = os.stat(csv_file)
                file_size = stat.st_size / 1024
                mod_time = datetime.fromtimestamp(stat.st_mtime)
                
                # Zeilen zählen (schneller als pandas)
                with open(csv_file, 'r') as f:
                    total_rows = sum(1 for _ in f) - 1  # -1 für Header
                
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
        if csv_file is None:
            csv_file = get_latest_csv()
        
        if csv_file is None or not os.path.exists(csv_file):
            raise FileNotFoundError("Keine CSV-Datei gefunden")
        
        # CSV laden
        df = pd.read_csv(csv_file, sep=';')
        
        # Datenbereinigung
        numeric_cols = ['fusion_speed', 'lean_deg', 'batt_voltage', 'max_batt_temp', 
                       'drive_distance', 'fusion_alt', 'pitch_deg', 'gps_lat', 'gps_long']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # GPS Speed filtern
        valid_speeds = df[df['fusion_speed'] > 0]['fusion_speed']
        
        # Fahrzeit
        drive_times = df['drive_time'].apply(parse_time)
        total_time_seconds = drive_times.max() if len(drive_times) > 0 else 0
        total_time = str(timedelta(seconds=int(total_time_seconds)))
        
        # Gesamtstrecke
        total_distance = df['drive_distance'].max() / 1000
        
        # ========== Höhe (Altitude) Statistiken ==========
        altitude_stats = {}
        if 'fusion_alt' in df.columns:
            valid_altitude = df['fusion_alt'].dropna()
            if len(valid_altitude) > 0:
                altitude_stats = {
                    'avg_altitude': round(valid_altitude.mean(), 2),
                    'max_altitude': round(valid_altitude.max(), 2),
                    'min_altitude': round(valid_altitude.min(), 2),
                    'altitude_gain': round(valid_altitude.max() - valid_altitude.min(), 2),
                    'altitude_data': valid_altitude[::50].tolist()
                }
            else:
                altitude_stats = {
                    'avg_altitude': 0,
                    'max_altitude': 0,
                    'min_altitude': 0,
                    'altitude_gain': 0,
                    'altitude_data': []
                }
        else:
            altitude_stats = {
                'avg_altitude': 0,
                'max_altitude': 0,
                'min_altitude': 0,
                'altitude_gain': 0,
                'altitude_data': []
            }
        
        # ========== Neigung (Pitch) Statistiken ==========
        pitch_stats = {}
        if 'pitch_deg' in df.columns:
            valid_pitch = df['pitch_deg'].dropna()
            if len(valid_pitch) > 0:
                pitch_stats = {
                    'avg_pitch': round(valid_pitch.abs().mean(), 2),
                    'max_pitch_up': round(valid_pitch.max(), 2),
                    'max_pitch_down': round(valid_pitch.min(), 2),
                    'pitch_data': valid_pitch[::50].tolist()
                }
            else:
                pitch_stats = {
                    'avg_pitch': 0,
                    'max_pitch_up': 0,
                    'max_pitch_down': 0,
                    'pitch_data': []
                }
        else:
            pitch_stats = {
                'avg_pitch': 0,
                'max_pitch_up': 0,
                'max_pitch_down': 0,
                'pitch_data': []
            }
        
        # ========== GPS Daten für Karte (mit Speed, Altitude, Pitch) ==========
        gps_data = []
        if 'gps_lat' in df.columns and 'gps_long' in df.columns:
            # Spalten die wir brauchen
            gps_cols = ['gps_lat', 'gps_long', 'pi_timestamp']
            if 'fusion_speed' in df.columns:
                gps_cols.append('fusion_speed')
            if 'fusion_alt' in df.columns:
                gps_cols.append('fusion_alt')
            if 'pitch_deg' in df.columns:
                gps_cols.append('pitch_deg')
            if 'lean_deg' in df.columns:
                gps_cols.append('lean_deg')
            
            # Nur gültige GPS-Punkte (nicht 0/0)
            valid_gps = df[
                (df['gps_lat'].notna()) & 
                (df['gps_long'].notna()) &
                (df['gps_lat'] != 0) & 
                (df['gps_long'] != 0)
            ][gps_cols]
            
            # Jeden 5. Punkt nehmen (mehr Punkte für besseren Farbverlauf)
            gps_data = valid_gps[::5].to_dict(orient='records')
        
        # Statistiken zusammenführen
        stats = {
            # Dateiinfo
            'current_file': os.path.basename(csv_file),
            'current_filepath': csv_file,
            
            # Geschwindigkeit
            'avg_speed': round(valid_speeds.mean(), 2) if len(valid_speeds) > 0 else 0,
            'max_speed': round(valid_speeds.max(), 2) if len(valid_speeds) > 0 else 0,
            'min_speed': round(valid_speeds.min(), 2) if len(valid_speeds) > 0 else 0,
            
            # Kurvenlage
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
            
            # Zeitreihen für Diagramme
            'speed_data': valid_speeds[::50].tolist() if len(valid_speeds) > 0 else [],
            'lean_data': df['lean_deg'][::50].tolist(),
            'voltage_data': df['batt_voltage'][::50].tolist(),
            'temp_data': df['max_batt_temp'][::50].tolist(),
            
            # GPS Daten für Karte
            'gps_data': gps_data
        }
        
        # Höhe und Neigung hinzufügen
        stats.update(altitude_stats)
        stats.update(pitch_stats)
        
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
            'speed_data': [], 'lean_data': [], 'voltage_data': [], 'temp_data': [],
            'avg_altitude': 0, 'max_altitude': 0, 'min_altitude': 0, 'altitude_gain': 0, 'altitude_data': [],
            'avg_pitch': 0, 'max_pitch_up': 0, 'max_pitch_down': 0, 'pitch_data': [],
            'gps_data': []
        }

@app.route('/')
def index():
    """Hauptseite mit Dashboard"""
    return render_template('dashboard.html')

@app.route('/api/stats')
def get_stats():
    """API Endpoint für Statistiken (inkl. GPS-Daten)"""
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
        print(f"✓ Aktuelle CSV: {os.path.basename(latest)}")
    else:
        print("✗ Keine CSV-Dateien gefunden")
    
    recent = get_recent_csvs()
    print(f"✓ Letzte Fahrten: {len(recent)}")
    
    app.run(debug=True, host='0.0.0.0', port=8080)