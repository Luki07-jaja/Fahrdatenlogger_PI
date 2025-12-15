from kivy.app import App
from UI.screens.start_ui import StartScreen
import subprocess

class FahrdatenloggerUI(App):

    def build(self):
        return StartScreen()   

    def on_stop(self):
        print("UI wird beendet")
        subprocess.run(
            ["sudo", "systemctl", "stop", "fahrdatenlogger.service"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )


if __name__ == "__main__":
    FahrdatenloggerUI().run()
