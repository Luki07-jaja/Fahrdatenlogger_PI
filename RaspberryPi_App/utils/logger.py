import sqlite3      # DB
import datetime     # Timestamps
import os           # für Paths
import csv    
import math         # für Strecken berechnung     

# ------------------------------------ Datenlogger Klasse ------------------------------------
class Datalogger: 

    # ---------------------- Initailisierung --------------------
    def __init__(self, publisher=None):   
        self.publisher = publisher 
        self.start_time = datetime.datetime.now()
        self.drive_distance = 0
        self.prev_gps = None

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
                drive_time TEXT,
                drive_distance REAL,           
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

    def distance_m(self, lat1, lon1, lat2, lon2):
        R = 6371000.0
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 -lat1)
        dlambda = math.radians(lon2 - lon1)
        a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2

        return 2 * R * math.asin(math.sqrt(a))

    # --------------------------- Frame logging ---------------------------
    def frame_logging(self, sensor):        # logged einen Frame in die DB
        
        pi_timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]  # gute Pi Timestamps erstellen

        elapsed_time = datetime.datetime.now() - self.start_time # vergangene Zeit seit Programmstart

        total_seconds = int(elapsed_time.total_seconds())    # vergangene Zeit in Sekunden
        milliseconds = int(elapsed_time.microseconds/1000)   # vergangen Zeit in Millisekunden

        hours = total_seconds // 3600           # Stunden berechnen 
        minutes = (total_seconds % 3600) // 60  # Minuten berechnen
        seconds = total_seconds % 60            # Sekunden berechnen

        drive_time = f"{hours:02}:{minutes:02}:{seconds:02}:{milliseconds:03}"  # Fahrt-Zeit zusammenbauen

        gps_motion = False
        if sensor.gps_firstfix and sensor.gps_speed is not None:
            gps_motion = sensor.gps_speed > 1.5

        imu_motion = (abs(sensor.g_long) + abs(sensor.g_lat) + abs(sensor.g_vert)) > 0.05
        moving = gps_motion or imu_motion

        if sensor.gps_firstfix and sensor.gps_lat is not None and sensor.gps_long is not None:
            cur_gps = (sensor.gps_lat, sensor.gps_long)

            if self.prev_gps is not None and cur_gps != self.prev_gps and moving:
                d = self.distance_m(self.prev_gps[0], self.prev_gps[1], cur_gps[0], cur_gps[1])
                
                if 0.2 <= d <= 50:
                    self.drive_distance += d

            self.prev_gps = cur_gps

        # ------------------------- DB Spalten befüllen ----------------------
        # SQLite befüllen / schreibt alle Daten des Frames in die DB spalten
        self.cursor.execute("""     
                INSERT INTO sensor_log (
                    pi_timestamp, drive_time, drive_distance, bmp_temp, bmp_pressure, bmp_alt,
                    g_lat, g_long, g_vert, lean_deg, heading_deg, pitch_deg,
                    gps_lat, gps_long, gps_alt, gps_speed, gps_heading,
                    gps_firstfix, esp_counter
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);
            """, (
                pi_timestamp,
                drive_time,
                round(self.drive_distance, 2),
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

        # -------- Live Push (Websocket) ----------------
        if self.publisher is not None:
            self.publisher.publish({
                "pi_timestamp": pi_timestamp,
                "drive_time": drive_time,
                "drive_distance_m": round(self.drive_distance, 2),
                "gps_firstfix": int(sensor.gps_firstfix),
                "gps_speed": sensor.gps_speed,
                "gps_heading": sensor.gps_heading,
                "gps_lat": sensor.gps_lat,
                "gps_long": sensor.gps_long,
                "lean_deg": sensor.lean_deg,
                "heading_deg": sensor.heading_deg,
                "pitch_deg": sensor.pitch_deg,
                # Akkudaten zukünfitig
            })


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