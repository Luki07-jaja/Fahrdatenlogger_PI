import serial
import binascii
import time

# -------- UART Einstellungen ----------
START_BYTE = 0xAA
END_BYTE = 0x55
FRAME_SIZE = 61             # vom ESP gemessene Framegröße
PORT = '/dev/ttyS0'
BAUD = 115200

# -------- UART öffnen ----------
ser = serial.Serial(PORT, BAUD, timeout=1)
buffer = bytearray()

print("Warte auf eingehende Frames...\n")

# -------- Haupt-Loop ----------
try:
    while True:
        if serial.in_waiting > 0:
            data = serial.readline().decode().strip()   # oder serial.read() für binary
            if data:
                print("Empfang: ",data)
        time.sleep(0.1)
except KeyboardInterrupt:
    print("Empfang beenden ...")
finally:
    serial.close()
