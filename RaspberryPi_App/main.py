from Hardware.UART_interface import run_frame_checker
from utils.live_ws_publisher import LiveWSPublisher
from utils.logger import Datalogger
import sys
from datetime import datetime
import os
import time
import gpiod

# --- ESP Reset über GPIO (BCM 17) ---
def reset_esp(pulse_s=0.1, boot_wait_s=0.3):
    chip_path = "/dev/gpiochip0"
    line = 17  # BCM17 = Pin 11

    # Wenn GPIO-Chip nicht da ist: Logger soll trotzdem starten
    if not os.path.exists(chip_path):
        print(f"GPIO reset übersprungen: {chip_path} nicht gefunden")
        return

    try:
        with gpiod.Chip(chip_path) as chip:
            req = chip.request_lines(
                consumer="esp-reset",
                config={
                    line: gpiod.LineSettings(
                        direction=gpiod.line.Direction.OUTPUT,
                        output_value=gpiod.line.Value.INACTIVE,  # LOW
                    )
                },
            )

            # Reset-Puls: HIGH -> LOW (mit Transistor: HIGH zieht ESP RST/EN nach GND)
            req.set_value(line, gpiod.line.Value.ACTIVE)    # HIGH
            time.sleep(pulse_s)
            req.set_value(line, gpiod.line.Value.INACTIVE)  # LOW

        time.sleep(boot_wait_s)

    except Exception as e:
        # Niemals den Logger killen, nur weil Reset nicht geht
        print(f"GPIO reset fehlgeschlagen (läuft trotzdem weiter): {e}")

def main():
    publisher = LiveWSPublisher("ws://127.0.0.1:8765")
    publisher.start()
    logger = Datalogger(publisher=publisher)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_dir = "/home/luki/Fahrdatenlogger/RaspberryPi_App/logs"
    os.makedirs(log_dir, exist_ok=True)

    log_path = f"{log_dir}/run_{timestamp}_debug.log"
    debug_file = open(log_path, "w", buffering=1)
    print(f"Debug-Logfile erstellt: {log_path}")

    running_under_systemd = "INVOCATION_ID" in os.environ

    if running_under_systemd:
        sys.stdout = debug_file
        sys.stderr = debug_file
    else:
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

    try:
        print("Starte Fahrdatenlogger...")
        reset_esp()
        run_frame_checker(logger)
    except KeyboardInterrupt:
        print("\nProgramm mit STRG+C beendet")
    except Exception as e:
        print(f"UNERWARTETER FEHLER: {e}")
    finally:
        logger.close()
        print("Logging beendet → CSV exportiert")
        if publisher:
            publisher.stop()
        print("Live WebSocket übertragung beendet")
        debug_file.close()


if __name__ == "__main__":
    main()
