from kivy.config import Config

Config.set("graphics", "fullscreen", "auto")   # echtes fullscreen
Config.set("graphics", "borderless", "1")      # keine Fensterdeko
Config.set("graphics", "resizable", "0")       # keine Resize-Artefakte
Config.set("graphics", "width", "1024")        # passt zu X
Config.set("graphics", "height", "600")        # passt zu X

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
import subprocess

from UI.widgets.status import LoggerStatus
from UI.screens.dashboard_ui import DashboardScreen
from UI.screens.start_ui import StartScreen


class RootUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", **kwargs)

        self.header = HeaderBar()

        with self.canvas.before:
            Color(1, 1, 1, 1)   # weiß
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

        self.sm = ScreenManager()
        self.sm.add_widget(StartScreen())
        self.sm.add_widget(DashboardScreen())

        self.add_widget(self.header)
        self.add_widget(self.sm)

    def _update_bg(self, *_):
        self._bg.pos = self.pos
        self._bg.size = self.size


class HeaderBar(BoxLayout):
     def __init__(self, **kwargs):
        super().__init__(
            orientation="horizontal",
            size_hint_y=None,
            height=70, # Höhe
            padding=(15, 15, 10, 0), # links, oben, rechts, unten
            spacing=0,
            **kwargs
        )

        # --- LINKER CONTAINER (Status) ---
        left = BoxLayout(
            orientation="horizontal",
            size_hint_x=None,
            width=260 # Breite 
        )

        self.status = LoggerStatus() # Loggerstatus Objekt erstellen / zuweisen
        left.add_widget(self.status) # Status hinzufügen

        # --- MITTE (Titel) ---
        self.titel = Label(
            text="[b]E-MX[/b]",
            markup=True,
            font_size=28,
            color=(0, 0, 0, 1),
            halign="center",
            valign="middle",
            size_hint_x= 1
        )
        self.titel.bind(
            size=lambda inst, *_: setattr(inst, "text_size", inst.size)
        )

        # --- RECHTER CONTAINER (Exit) ---
        right = BoxLayout(
            orientation="horizontal",
            size_hint_x=None,
            width=260 # Breite
        )
        
        # Spacer schiebt Button nach rechts
        right.add_widget(Widget())

        self.exit_button = Button(
            text="X",
            size_hint=(None, None),
            width=60,
            height=60,
            font_size=36,
            background_normal="",
            background_color=(1, 0, 0, 1),
            color=(0, 0, 0, 1),
            pos_hint={"center_y": 0.5}
        )
        self.exit_button.bind(
            on_release=lambda *_: App.get_running_app().stop()
        )

        right.add_widget(self.exit_button)

        # --- ZUSAMMENBAU ---
        self.add_widget(left)
        self.add_widget(self.titel)
        self.add_widget(right)


class FahrdatenloggerUI(App):
    def build(self):
        # --- Fullscreen / Kiosk ---
        Window.fullscreen = True
        Window.borderless = True
        Window.show_cursor = False

        root = RootUI()

        # --- Status regelmäßig aktualisieren (sonst bleibt LED rot / Text alt) ---
        Clock.schedule_interval(lambda dt: root.header.status.update(), 0.5)

        # Optional: Beim Screenwechsel Status sofort updaten
        root.sm.bind(current=lambda *_: root.header.status.update())

        # initialer Status
        root.header.status.update()

        return root

    def on_stop(self):
        print("UI wird beendet")
        subprocess.run(
            ["sudo", "systemctl", "stop", "fahrdatenlogger.service"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )


if __name__ == "__main__":
    FahrdatenloggerUI().run()
