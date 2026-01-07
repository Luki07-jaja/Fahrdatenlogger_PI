from kivy.app import App
from UI.screens.start_ui import StartScreen
import subprocess

# -------------------------------- EMX UI -----------------------------------
class FahrdatenloggerUI(App): # Klasse erbt von Kivy App

    def build(self):        # UI builden 
        return StartScreen()   

    def on_stop(self):      # Sicherheitsnet: Service Immer beenden bei schließen / Crash ...
        print("UI wird beendet")
        subprocess.run(
            ["sudo", "systemctl", "stop", "fahrdatenlogger.service"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )


if __name__ == "__main__":
    FahrdatenloggerUI().run()
