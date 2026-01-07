from kivy.uix.boxlayout import BoxLayout 
from kivy.uix.button import Button
import subprocess
from threading import Thread # Erlaubt parallele Ausführung von Code ohne das UI zu blockieren
from kivy.clock import Clock # Zeitsteuerung und Thread Updates
from kivy.app import App

from UI.widgets.status import LoggerStatus

# ----------------------------------- Startscreen UI Klasse -------------------------------
class StartScreen(BoxLayout): # gesamte Klasse erbt von Boxlayout
    # Konstruktur: initialisierung der Start / Stop und Exit Buttons
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", spacing=20, **kwargs) # vertikale anordnung

        self.status = LoggerStatus() # Logger Status Objekt erstellen
        self.add_widget(self.status) # Widget hinzufügen

        self.start_btn = Button( # Start / Stopp Button erstellen
            text="Fahrt starten / stoppen", 
            size_hint=(1, 0.3),
            font_size=28
        )
        self.start_btn.bind(on_release=self._toggle_logger) # Button auf toggle_logger "binden"

        self.exit_btn = Button( # Programm abschluss Button erstellen
            text="Programm beenden",
            size_hint=(1, 0.2),
            background_color=(1, 0, 0, 1),
            font_size=24
        )
        self.exit_btn.bind(on_release=self.exit_app) # Button auf exit_app "binden"

        self.add_widget(self.start_btn) # Widgets hinzufügen
        self.add_widget(self.exit_btn)

        Clock.schedule_interval(lambda dt: self.status.update(), 0.5)   # Status regelmäßig aktualisieren

    # ----------------------------- Start / Stop Button Logik ----------------------------
    # wird beim Drücken der Buttons ausgeführt. Startet eigenen Thread fürs bearbeiten der Services
    def _toggle_logger(self, *args):
        self.start_btn.disabled = True  # Mehrfachklick verhindern button "sperren"

        Thread( # startet neuen hintergrund Thread für Service Befehle
            target=self._toggle_logger_worker,
            daemon=True
        ).start()

    # ------------------------------ Bearbeiten der Services -----------------------------
    # Service commands könnten die UI einfrieren deshalb --> auslagern in eigenen Thread
    def _toggle_logger_worker(self): # eigener Thread  läuft nicht im UI Thread
        try:
            if self.status._is_logger_running():
                subprocess.run(
                    ["systemctl", "stop", "fahrdatenlogger.service"], # Service befehle (könnten blockieren)
                    check=True
                )
            else:
                subprocess.run(
                    ["systemctl", "start", "fahrdatenlogger.service"],
                    check=True
                )
        except Exception as e: # Fehler ausgabe
            print("Systemd Fehler:", e)

        # UI-Update sicher im Main-Thread
        Clock.schedule_once(self._after_toggle, 0) # Rücksprung in den Main Thread

    # ------------------------------ Toggle Update -----------------------------
    # Updatet die Buttons nach dem Drücken und gibt sie wieder "frei"
    def _after_toggle(self, dt): # Status-update nach dem Button toggle
        self.status.update()
        self.start_btn.disabled = False # Button wieder "frei geben"

    # ------------------------ App / Programm schließen -------------------------
    def exit_app(self, *args): # App beenden
        App.get_running_app().stop()
