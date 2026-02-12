from dataclasses import dataclass
import serial
import struct
import time

# -------------------- Datenstruktur --------------------
@dataclass
class Sensordata:
    esp_timestamp: int = 0
    bmp_temp: float = 0.0
    bmp_pressure: float = 0.0
    bmp_alt: float = 0.0
    g_lat: float = 0.0
    g_long: float = 0.0
    g_vert: float = 0.0
    lean_deg: float = 0.0
    heading_deg: float = 0.0
    pitch_deg: float = 0.0
    gps_long: float = 0.0
    gps_lat: float = 0.0
    gps_alt: float = 0.0
    gps_speed: float = 0.0
    gps_heading: float = 0.0
    gps_firstfix: bool = False
    batt_voltage: float = 0.0
    batt_temp1: float = 0.0
    batt_temp2: float = 0.0
    batt_temp3: float = 0.0
    batt_temp4: float = 0.0
    esp_counter: int = 0

# ---------------- UART Einstellungen --------------------
START_BYTE = 0xAA
END_BYTE   = 0x55
FRAME_SIZE = 87     # passt zu: <I + 19f + ? + B> = 4 + 76 + 1 + 1 = 82 payload, + start/len/crc/end => 87

PORT = '/dev/ttyS0'
BAUD = 115200

ser = serial.Serial(PORT, BAUD, timeout=0.1)
ser.reset_input_buffer()
ser.reset_output_buffer()
buffer = bytearray()

# ---------------- CRC --------------------
def calc_crc(data: bytes) -> int:
    crc = 0xFFFF
    for i in data:
        crc ^= i
    return crc & 0xFFFF

# ---------------- Handshake --------------------
def handshake() -> bool:
    print("Handshake anfordern...")
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    start_time = time.time()

    while time.time() - start_time < 60:
        ser.write(b"Hello ESP\n")
       
        while ser.in_waiting:
            resp = ser.readline().decode('utf-8',errors='ignore').strip()
            print("RX: ", resp)
            if resp == "":  # wenn input buffer leer dann überspringen
                continue

            if resp == "Hello PI":
                print("Handshake erfolgreich!")
                return True
        time.sleep(0.5)

    print("Handshake fehlgeschlagen")
    return False

# ------------------------- Steuer CMDs -----------------------
def streaming_start() -> bool:
    ser.reset_input_buffer()
    ser.write(b"START\n")
    print("START gesendet -> warte auf Frames...")
    start_time = time.time()

    while time.time() - start_time < 5:
        resp = ser.readline().decode(errors='ignore').strip()
        print("RX:", resp)

        if resp == "START OK":
            print("Streaming läuft")
            return True
        time.sleep(0.2)

    print("Keine START-Bestätigung erhalten")
    return False

# ---------------- Frames + Heartbeat --------------------
def recv_frames(logger):
    global buffer
    print("Warte auf Frames...")

    last_frame_time = time.time()
    last_hb_time = time.time()
    hb_counter = 0

    last_esp_counter = None

    while True:
        now = time.time()

        # -------- Heartbeat senden --------    --> für ESP (ESP kontroliert damit PI)
        if time.time() - last_hb_time > 0.5:
            ser.write(bytes([0xFE, hb_counter & 0xFF]))
            hb_counter += 1     # überflüssig?
            last_hb_time = now

        # -------- Daten einlesen --------
        chunk = ser.read(ser.in_waiting or 1)
        if chunk:
            buffer += chunk

        # -------- Frames suchen und dekodieren --------
        while True:
            if len(buffer) < FRAME_SIZE:
                break

            start_idx = buffer.find(bytes([START_BYTE]))
            if start_idx == -1:
                buffer.clear()
                break

            if len(buffer) < start_idx + FRAME_SIZE:
                break

            frame = buffer[start_idx:start_idx + FRAME_SIZE]
            buffer = buffer[start_idx + FRAME_SIZE:]

            if frame[-1] != END_BYTE:
                print("Ungültiger Frame --> flasches Endbyte")
                continue

            length = frame[1]
            if length != FRAME_SIZE - 5:
                print(f"Ungültige Länge ({length})")
                continue

            start = frame[0]
            length = frame[1]

            if length != FRAME_SIZE - 5:
                print(f"Ungültige Länge ({length} Bytes, erwartet {FRAME_SIZE - 5})")
                continue

            data = frame[2:2 + length]
            crc_recv = int.from_bytes(frame[2 + length:2 + length + 2], 'little')
            crc_calc = calc_crc(frame[1:2 + length])

            if crc_calc != crc_recv:
                print("CRC falsch!")
                continue

            # ---------- Gültigen Frame verarbeiten ----------
            last_frame_time = now

            # Alive-Counter vom Frame zurückbekommen
            last_esp_counter = unpack_frame(logger, data, last_esp_counter)  # übergibt den counter wert des letzten Frames

        if now - last_frame_time > 2.0:
            print("Heartbeat Timeout -> ESP sendet keine Frames mehr")
            return False


# ---------------- Frame-Daten Dekodieren --------------------
def unpack_frame(logger, data: bytes, last_esp_counter):
    structure = "<Iffffffffffffff?fffffB"  # 32 bit int + 19 Floats + ? = 1xbool + 1 x 8 Bit int

    try:
        unpacked = struct.unpack(structure, data)
    except struct.error as e:
        print(f"Fehler beim Entpacken: {e}")
        return last_esp_counter

    sensor = Sensordata(*unpacked)

    # ------------------ Werte runden --------------------
    sensor.bmp_temp = round(sensor.bmp_temp, 2)
    sensor.bmp_pressure = round(sensor.bmp_pressure, 2)
    sensor.bmp_alt = round(sensor.bmp_alt, 2)

    sensor.g_lat = round(sensor.g_lat, 4)
    sensor.g_long = round(sensor.g_long, 4)
    sensor.g_vert = round(sensor.g_vert, 4)
    sensor.lean_deg = round(sensor.lean_deg, 3)
    sensor.heading_deg = round(sensor.heading_deg, 3)
    sensor.pitch_deg = round(sensor.pitch_deg, 3)

    sensor.gps_lat = round(sensor.gps_lat, 8)
    sensor.gps_long = round(sensor.gps_long, 8)
    sensor.gps_alt = round(sensor.gps_alt, 2)
    sensor.gps_speed = round(sensor.gps_speed, 2)
    sensor.gps_heading = round(sensor.gps_heading, 2)

    sensor.batt_voltage = round(sensor.batt_voltage, 2)
    sensor.batt_temp1 = round(sensor.batt_temp1, 2)
    sensor.batt_temp2 = round(sensor.batt_temp2, 2)
    sensor.batt_temp3 = round(sensor.batt_temp3, 2)
    sensor.batt_temp4 = round(sensor.batt_temp4, 2)

    print("-" * 60)
    print(f"Time: {sensor.esp_timestamp}s | ESP-Alive-Counter: {sensor.esp_counter}")

    # Counter prüfen
    if last_esp_counter is not None:
        diff = (sensor.esp_counter - last_esp_counter) & 0xFF
        if diff != 1:
            print(f"⚠ Unerwarteter Counter-Sprung: +{diff}")

    # Sensorwerte ausgeben
    print(f"Temp: {sensor.bmp_temp:.2f} °C")
    print(f"Druck: {sensor.bmp_pressure:.2f} hPa")
    print(f"GPS Status: {sensor.gps_firstfix}")
    print(f"Höhe: {sensor.bmp_alt:.2f} m")
    print(f"G: long={sensor.g_long:.2f}, lat={sensor.g_lat:.2f}, vert={sensor.g_vert:.2f}")
    print(f"Lean: {sensor.lean_deg:.2f}° | Heading: {sensor.heading_deg:.2f}° | Pitch: {sensor.pitch_deg:.2f}°")
    print(f"GPS: lat={sensor.gps_lat:.6f}, lon={sensor.gps_long:.6f}, speed={sensor.gps_speed:.2f} km/h")
    print(f"Battery Voltage: {sensor.batt_voltage:.2f} V | Temperatures: {sensor.batt_temp1:.2f}°C, {sensor.batt_temp2:.2f}°C, {sensor.batt_temp3:.2f}°C, {sensor.batt_temp4:.2f}°C")

    logger.frame_logging(sensor)

    return sensor.esp_counter

# ---------------- "MAIN" FUNCTION --------------------
def run_frame_checker(logger):
    while True:
        if handshake() and streaming_start():
            ok = recv_frames(logger)
            if not ok:
                print("Neu verbinden...")
                time.sleep(1)
                continue
        else:
            print("Handshake/Start fehlgeschlagen, neuer Versuch in 2s...")
            time.sleep(2)
