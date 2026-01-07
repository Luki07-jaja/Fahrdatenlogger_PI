import sqlite3      # DB
import datetime     # Timestamps
import os           # für Paths
import csv         

# ------------------------------------ Datenlogger Klasse ------------------------------------
class Datalogger: 

    # ---------------------- Initailisierung --------------------
    def __init__(self):    
        base_path = os.path.join(os.path.dirname(__file__), "..", "logs")   # zum richtigen directory führen
        os.makedirs(base_path, exist_ok=True)   # directory erstellen fals es nicht existiert

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")       # Dateien erstellen mit aktuellem Datum
        self.sqlite_filename = os.path.join(base_path, f"{timestamp}_fahrt.sqlite")
        self.csv_filename = os.path.join(base_path, f"{timestamp}_fahrt.csv")

        self.conn = sqlite3.connect(self.sqlite_filename)   # DB öffnen / connecten und Cursor erstellen
        self.cursor = self.conn.cursor()

        # --------------------- DB Spalten erstellen --------------------
        # Spalten für Sensordaten erstellen / beschriften --> einmalig bei start
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS sensor_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pi_timestamp TEXT,
                esp_timestamp,
                bmp_temp REAL,
                bmp_pressure REAL,
                bmp_alt REAL,
                g_lat REAL,
                g_long REAL,
                g_vert REAL,
                lean_deg REAL,
                heading_deg REAL,
                pitch_deg REAL,
                gps_lat REAL,
                gps_long REAL,
                gps_alt REAL,
                gps_speed REAL,
                gps_heading REAL,
                gps_firstfix INTEGER,
                esp_counter INTEGER
            );
        """)

        self.conn.commit()  # ausführen

    # --------------------------- Frame logging ---------------------------
    def frame_logging(self, sensor):        # logged einen Frame in die DB
        
        pi_timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]  # gute Pi Timestamps erstellen

        # ------------------------- DB Spalten befüllen ----------------------
        # SQLite befüllen / schreibt alle Daten des Frames in die DB spalten
        self.cursor.execute("""     
                INSERT INTO sensor_log (
                    pi_timestamp, esp_timestamp, bmp_temp, bmp_pressure, bmp_alt,
                    g_lat, g_long, g_vert, lean_deg, heading_deg, pitch_deg,
                    gps_lat, gps_long, gps_alt, gps_speed, gps_heading,
                    gps_firstfix, esp_counter
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);
            """, (
                pi_timestamp,
                sensor.esp_timestamp,
                sensor.bmp_temp,
                sensor.bmp_pressure,
                sensor.bmp_alt,
                sensor.g_lat,
                sensor.g_long,
                sensor.g_vert,
                sensor.lean_deg,
                sensor.heading_deg,
                sensor.pitch_deg,
                sensor.gps_lat,
                sensor.gps_long,
                sensor.gps_alt,
                sensor.gps_speed,
                sensor.gps_heading,
                int(sensor.gps_firstfix),   # ist 0 oder 1 = False / True
                sensor.esp_counter
            ))

        self.conn.commit()      # bestätigen

    # -------------------------- DB Daten --> CSV -----------------------------
    def export_csv(self):       # exportiert die loggs aus SQLite DB in CSV
        cur = self.conn.cursor()    # mit DB cursor Connecten

        cur.execute("SELECT * FROM sensor_log")     # alle Daten auslesen
        rows = cur.fetchall()

        column_names = [d[0] for d in cur.description]  # spalten namen holen aus dem Header der DB

        with open(self.csv_filename, "w", newline="", encoding="utf-8") as f:   # CSV schreiben
            writer = csv.writer(f, delimiter=';')
            writer.writerow(column_names)   # Spalten Namen
            writer.writerows(rows)          # Daten

        print(f"CSV exportiert ->{self.csv_filename}")

    # ------------------------ Schließen / CSV erstellen ---------------------
    def close(self):         
        self.export_csv()       # erstellt die CSV
        self.conn.close()       # schließt die DB