from kivy.config import Config  # Zum sicherstellen das Borderless Fullscreen verwendet wird

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
from kivy.graphics import Color, Rectangle, RoundedRectangle
import subprocess
from datetime import datetime

from UI.widgets.status import LoggerStatus
from UI.screens.dashboard_ui import DashboardScreen
from UI.screens.start_ui import StartScreen
from UI.utils.live_client import LiveWSClient


class RootUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", **kwargs)

        self.ws = LiveWSClient()    # WS Client holen
        self.ws.start()             # WebSocket start
        print("LiveWSClient gestartet")

        self.header = HeaderBar()   # HeaderBar holen

        with self.canvas.before:
            Color(1, 1, 1, 1)   # Backgroundcolor für gesamtes Display weiß
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

        self.sm = ScreenManager()
        self.sm.add_widget(StartScreen())       # Start UI
        self.sm.add_widget(DashboardScreen())   # Dashboard UI

        self.add_widget(self.header)    # Zusammenbauen: HeaderBar und aktiver Screen
        self.add_widget(self.sm)

    def _update_bg(self, *_):
        self._bg.pos = self.pos
        self._bg.size = self.size


class HeaderBar(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(
            orientation="horizontal",
            size_hint_y=None,
            height=60, # Höhe
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
        self.clock_label = Label(
            text="[b]00:00[/b]",
            markup=True,
            font_size=28,
            color=(0, 0, 0, 1),
            halign="center",
            valign="middle",
            size_hint_x= 1
        )
        self.clock_label.bind(
            size=lambda inst, *_: setattr(inst, "text_size", inst.size)
        )
        self._update_clock()
        Clock.schedule_interval(self._update_clock,1)

        # --- RECHTER CONTAINER (Exit) ---
        right = BoxLayout(
            orientation="horizontal",
            size_hint_x=None,
            width=260 # Breite
        )
        
        # Spacer schiebt Button nach rechts
        right.add_widget(Widget())

        self.exit_btn = Button(
            text="X",
            size_hint=(None, None),
            width=60,
            height=60,
            font_size=36,
            background_normal="",
            background_color=(0, 0, 0, 0),
            color=(0, 0, 0, 1),
            pos_hint={"center_y": 0.5}
        )
        with self.exit_btn.canvas.before:
            self._btn_color = Color(1, 0, 0, 1)  
            self._btn_bg = RoundedRectangle(
                pos=self.exit_btn.pos,
                size=self.exit_btn.size,
                radius=[15]
            )
        self.exit_btn.bind(pos=self._update_btn_bg, size=self._update_btn_bg)
        self.exit_btn.bind(on_release=lambda *_: App.get_running_app().stop())

        right.add_widget(self.exit_btn)

        # --- ZUSAMMENBAU ---
        self.add_widget(left)
        self.add_widget(self.clock_label)
        self.add_widget(right)

    def _update_btn_bg(self,*_):
        self._btn_bg.pos = self.exit_btn.pos
        self._btn_bg.size = self.exit_btn.size
    
    def _update_clock(self, *_):
            now = datetime.now().strftime("%H:%M")
            self.clock_label.text = f"[b]{now}[/b]"



class FahrdatenloggerUI(App):
    def build(self):

        subprocess.run(["systemctl", "stop", "fahrdatenlogger.service"],    # sicherstellen das der Logger nach Boot "Off" ist
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # --- Fullscreen / Kiosk ---
        Window.fullscreen = True
        Window.borderless = True
        Window.show_cursor = False

        root = RootUI()

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
