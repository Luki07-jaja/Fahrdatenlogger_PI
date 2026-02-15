#!/usr/bin/env python3
"""
Fahrdatenlogger Dashboard
Analysiert CSV-Daten und stellt sie in einem modernen Dark-Mode Dashboard dar
"""

from flask import Flask, render_template, jsonify, send_file
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

app = Flask(__name__)

# CSV-Datei Pfad (anpassbar)
CSV_FILE = "C:\\Users\\lukas\\Downloads\\2026-02-12_12-34-58_fahrt.csv"

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

def analyze_data():
    """Analysiert die CSV-Daten und berechnet Statistiken"""
    try:
        # CSV laden mit Semikolon als Trennzeichen
        df = pd.read_csv(CSV_FILE, sep=';')
        
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
    stats = analyze_data()
    return jsonify(stats)

@app.route('/download/csv')
def download_csv():
    """Download der CSV-Datei"""
    try:
        return send_file(
            CSV_FILE,
            mimetype='text/csv',
            as_attachment=True,
            download_name='fahrt_data.csv'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@app.route('/view/csv')
def view_csv():
    """CSV-Daten als JSON anzeigen"""
    try:
        df = pd.read_csv(CSV_FILE, sep=';')
        # Erste 1000 Zeilen für Anzeige
        data = df.head(1000).to_dict(orient='records')
        return jsonify({
            'total_rows': len(df),
            'displayed_rows': min(1000, len(df)),
            'columns': df.columns.tolist(),
            'data': data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 404

if __name__ == '__main__':
    print("=" * 60)
    print("🚗 Fahrdatenlogger Dashboard")
    print("=" * 60)
    print(f"📊 CSV Datei: {CSV_FILE}")
    print(f"🌐 Dashboard URL: http://localhost:5000")
    print("=" * 60)
    print("\nDrücke CTRL+C zum Beenden\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
