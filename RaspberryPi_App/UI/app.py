from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color
import subprocess

from UI.widgets.status import LoggerStatus
from UI.screens.dashboard_ui import DashboardScreen
from UI.screens.start_ui import StartScreen

# -------------------------------- Root UI Class ----------------------------
# einbindung der einzelenen Screens und des Headers (für Status) --> UI
class RootUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation = "vertical",**kwargs)

        # Header immer sichtbar
        self.header = HeaderBar()

        # Screens
        self.sm = ScreenManager()
        self.sm.add_widget(StartScreen())
        self.sm.add_widget(DashboardScreen())

        # Screenmanager und Header einbinden
        self.add_widget(self.header)
        self.add_widget(self.sm)

# ----------------------------- UI Header Function -----------------------------
# Header der Universal auf allen Screens sichtbar ist mit Loggerstatus anzeige
# Titel und Exit Button
class HeaderBar(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(
            orientation = "horizontal",
            size_hint_y = None,
            height = 60,
            padding = (20,10),
            spacing = 15,
            **kwargs
            )
        
        self.status = LoggerStatus()
        self.status.size_hint_x = None
        self.status.width = 220

        self.titel = Label(
            text = "[b]E-MX[/b]",
            markup = True,
            font_size = 28,
            Color = (0,0,0,1)
        )

        self.exit_button = Button(
            text="✕",
            size_hint = (None, 1),
            width = 80,
            font_size = 20,
            background_normal = "",
            background_color = (0,0,0,1),
            Color = (1,1,1,1)
        )

        self.exit_button.bind(on_release = lambda *_: App.get_running_app().stop())

        self.add_widget(self.status())
        self.add_widget(self.titel())
        self.add_widget(self.exit_button())


# ------------------------------- EMX UI APP -----------------------------------
class FahrdatenloggerUI(App): # Klasse erbt von Kivy App

    def build(self):        # UI builden 
        return RootUI()     # Root funktion ausführen (Screens und Header)

    def on_stop(self):      # Sicherheitsnet: Service Immer beenden bei schließen / Crash ...
        print("UI wird beendet")
        subprocess.run(
            ["sudo", "systemctl", "stop", "fahrdatenlogger.service"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )


if __name__ == "__main__":
    FahrdatenloggerUI().run()
