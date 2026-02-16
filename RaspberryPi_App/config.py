import os
import glob

# Basis-Pfade
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGS_DIR = os.path.join(BASE_DIR, "logs")

# Dashboard Integration
DASHBOARD_WATCH_FILE = os.path.join(LOGS_DIR, "latest_csv.txt")
DASHBOARD_ENABLED = True
DASHBOARD_HOST = "0.0.0.0"
DASHBOARD_PORT = 8080

# Log-Rotation
MAX_FAHRT_PAARE = 5  # Anzahl der Fahrten die behalten werden sollen

# Stelle sicher, dass logs Verzeichnis existiert
os.makedirs(LOGS_DIR, exist_ok=True)


def cleanup_old_logs(max_trips=MAX_FAHRT_PAARE):
    """
    Löscht alte Fahrt-Dateien und behält nur die neuesten max_trips Fahrten.
    
    Jede Fahrt besteht aus 3 Dateien:
    - YYYY-MM-DD_HH-MM-SS_fahrt.csv
    - YYYY-MM-DD_HH-MM-SS_fahrt.sqlite
    - run_YYYY-MM-DD_HH-MM-SS_debug.log
    """
    try:
        csv_files = glob.glob(os.path.join(LOGS_DIR, "*_fahrt.csv"))
        csv_files.sort(key=os.path.getmtime, reverse=True)
        
        if len(csv_files) > max_trips:
            files_to_delete = csv_files[max_trips:]
            
            for csv_file in files_to_delete:
                basename = os.path.basename(csv_file)
                timestamp = basename.replace('_fahrt.csv', '')
                
                for file_path in [
                    os.path.join(LOGS_DIR, f"{timestamp}_fahrt.csv"),
                    os.path.join(LOGS_DIR, f"{timestamp}_fahrt.sqlite"),
                    os.path.join(LOGS_DIR, f"run_{timestamp}_debug.log")
                ]:
                    if os.path.exists(file_path):
                        os.remove(file_path)
            
            print(f"Log-Cleanup: {len(files_to_delete)} alte Fahrten gelöscht, {len(csv_files) - len(files_to_delete)} behalten")
            
    except Exception as e:
        print(f"Cleanup-Fehler: {e}")