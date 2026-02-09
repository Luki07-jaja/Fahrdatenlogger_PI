from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

from kivy.clock import Clock
from threading import Thread
import subprocess

from UI.utils.live_client import LiveWSClient


class DashboardScreen(Screen):
    def __init__(self, **kw):
        super().__init__(name="dashboard", **kw)

        self.ws = LiveWSClient()
        self.ws.start()
        Clock.schedule_interval(self._update_live, 0.1) # 10Hz 

        root = BoxLayout(orientation="vertical", padding=10, spacing=10)

        center = AnchorLayout(anchor_x="center", anchor_y="center")
        self.info = Label(
            text="Dashboard UI\n(Speed-Ring / Accel-Ring / Akku)",
            font_size=26,
            halign="center",
            valign="middle",
            color=(0, 0, 0, 1)
        )
        self.info.bind(size=lambda inst, *_: setattr(inst, "text_size", inst.size))
        center.add_widget(self.info)

        bottom = AnchorLayout(anchor_x="center", anchor_y="bottom", size_hint_y=None, height=140)
        self.toggle_btn = Button(
            text="Fahrt beenden",
            size_hint=(None, None),
            size=(520, 110),
            font_size=32,
            background_normal="",
            background_color=(0, 0, 0, 1),
            color=(1, 1, 1, 1)
        )
        self.toggle_btn.bind(on_release=self._toggle_ride)
        bottom.add_widget(self.toggle_btn)

        root.add_widget(center)
        root.add_widget(bottom)
        self.add_widget(root)

        Clock.schedule_once(lambda dt: self._sync_state(), 0)

    def on_pre_enter(self, *args):
        # bei jedem Betreten sicherheitshalber neu synchronisieren
        self._sync_state()

    def _sync_state(self):
        running = self._is_running()
        self.toggle_btn.text = "Fahrt beenden" if running else "Fahrt starten"
        self.toggle_btn.background_color = (0, 0, 0, 1) if running else (0.95, 0.75, 0.10, 1)
        self.toggle_btn.color = (1, 1, 1, 1) if running else (0, 0, 0, 1)

    def _toggle_ride(self, *_):
        self.toggle_btn.disabled = True
        Thread(target=self._toggle_worker, daemon=True).start()

    def _toggle_worker(self):
        if self._is_running():
            subprocess.run(
                ["systemctl", "stop", "fahrdatenlogger.service"],
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.DEVNULL
            )
        else:
            subprocess.run(
                ["systemctl", "start", "fahrdatenlogger.service"],
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.DEVNULL
            )

        Clock.schedule_once(self._after_toggle, 0)

    def _after_toggle(self, dt):
        self._sync_state()
        self.toggle_btn.disabled = False

    def _is_running(self) -> bool:
        result = subprocess.run(
            ["systemctl", "is-active", "fahrdatenlogger.service"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL
        )
        return result.stdout.decode().strip() == "active"
    
    def _update_live(self, dt):
        data = self.ws.latest
        if not data:
            return
        print("UI LIVE:", data.get("gps_speed"), data.get("lean_deg")) # Test: Verbindung zwischen WS zu UI
