from Hardware.rs485_interface import run_frame_checker
from utils.logger import Datalogger
import sys
from datetime import datetime
import os


def main():
    # --------------- Logger Initialisieren ---------------
    logger = Datalogger()

    # --------------- Debug-Datei vorbereiten -------------
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_dir = "/home/luki/Fahrdatenlogger/RaspberryPi_App/logs"
    os.makedirs(log_dir, exist_ok=True)

    log_path = f"{log_dir}/run_{timestamp}_debug.log"
    debug_file = open(log_path, "w", buffering=1)
    print(f"Debug-Logfile erstellt: {log_path}")

    running_under_systemd = "INVOCATION_ID" in os.environ

    if running_under_systemd:
        # Nur in Datei loggen (so wie Hybrid C definiert)
        sys.stdout = debug_file
        sys.stderr = debug_file
    else:
        # Manuell gestartet → Dual Logging (Terminal + Datei)
        class Tee:
            def __init__(self, *streams):
                self.streams = streams

            def write(self, data):
                for s in self.streams:
                    s.write(data)
                    s.flush()

            def flush(self):
                for s in self.streams:
                    s.flush()

        sys.stdout = Tee(sys.__stdout__, debug_file)
        sys.stderr = Tee(sys.__stderr__, debug_file)

    print("Starte Fahrdatenlogger...")

    # --------------- Hauptablauf --------------------------
    try:
        run_frame_checker(logger)
    except KeyboardInterrupt:
        print("\nProgramm mit STRG+C beendet")
    except Exception as e:
        print(f"UNERWARTETER FEHLER: {e}")
    finally:
        # CSV usw. schließen
        logger.close()
        print("Logging beendet → CSV exportiert")

        # Debug-Datei schließen
        debug_file.close()

if __name__ == "__main__":
    main()
