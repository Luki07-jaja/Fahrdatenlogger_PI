from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.graphics import Rectangle, Color, Line
from kivy.clock import Clock
from kivy.app import App

from threading import Thread
import subprocess



class DashboardScreen(Screen):
    def __init__(self, **kw):
        super().__init__(name="dashboard", **kw)

        self.logger_running = False
        Clock.schedule_interval(self._update_live, 0.1)  # Live refresh

        # ---------------------- ROOT -> Alles unter HeaderBar -----------------------------
        root = BoxLayout(orientation="vertical", padding=(10, 10), spacing=10)

        # ---------------------- Top -> Drive Time ------------------------
        top = AnchorLayout(anchor_x="center", anchor_y="center", size_hint_y=None, height=55)
        self.drive_time_lbl = Label(
            text="00:00:00:000",
            font_size=28,
            markup=True,
            color=(0, 0, 0, 1),
            halign="center",
            valign="middle"
        )
        self.drive_time_lbl.bind(size=lambda inst, *_: setattr(inst, "text_size", inst.size))
        top.add_widget(self.drive_time_lbl)

        # ------------- Mid -> Akku-Box + Speed/Lean/Distance --------------
        # WICHTIG: FloatLayout, damit Center wirklich auf dem ganzen Screen zentriert
        mid = FloatLayout()

        # Mid-Left: Akku-Box
        self.batt_box = BoxLayout(
            orientation="vertical",
            size_hint=(None, None),
            size=(dp(190), dp(160)),
            pos_hint={"x": 0, "center_y": 0.5},   # linkes center im Mid-Bereich
            padding=(12, 12),
            spacing=8
        )

        with self.batt_box.canvas.before:   # Hintergrund + Rahmen
            Color(0.95, 0.95, 0.95, 1)
            self._b_bg = Rectangle(pos=self.batt_box.pos, size=self.batt_box.size)
            Color(0, 0, 0, 1)
            self._b_border = Line(rectangle=(self.batt_box.x, self.batt_box.y, self.batt_box.width, self.batt_box.height), width=1.2)
        self.batt_box.bind(pos=self._update_batt_bg, size=self._update_batt_bg)

        self.batt_lbl = Label(
            text="[b]Akku-Daten[/b]\n\nTemp: 40°C\nVoltage: 72V\nCharge: 90%\n",
            markup=True,
            font_size=22,
            color=(0, 0, 0, 1),
            halign="left",
            valign="top"
        )
        self.batt_lbl.bind(size=lambda inst, *_: setattr(inst, "text_size", inst.size))
        self.batt_box.add_widget(self.batt_lbl)

        # Mid-Center: Speed/Lean/Pitch
        center = AnchorLayout(
            anchor_x="center",
            anchor_y="center",
            size_hint=(None, None),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            size=(dp(520), dp(260))
        )

        center_col = BoxLayout(
            orientation="vertical",
            size_hint=(1, 1),
            spacing=0
        )

        self.speed_lbl = Label(
            text="[b]0[/b]",
            markup=True,
            font_size=120,
            color=(0, 0, 0, 1),
            halign="center",
            valign="middle"
        )
        self.speed_lbl.bind(size=lambda inst, *_: setattr(inst, "text_size", inst.size))

        self.sub_lbl = Label(
            text="Lean: 0.0°   |   Pitch: 0.0 °",
            font_size=26,
            color=(0, 0, 0, 1),
            halign="center",
            valign="middle"
        )
        self.sub_lbl.bind(size=lambda inst, *_: setattr(inst, "text_size", inst.size))

        center_col.add_widget(self.speed_lbl)
        center_col.add_widget(self.sub_lbl)
        center.add_widget(center_col)

        mid.add_widget(self.batt_box)
        mid.add_widget(center)

        # --------------- Bottom -> Fahrt-toggle Button ----------------
        bottom = AnchorLayout(anchor_x="center", anchor_y="bottom", size_hint_y=None, height=130)
        self.toggle_btn = Button(
            text="Fahrt beenden",
            size_hint=(None, None),
            size=(480, 100),
            font_size=30,
            background_normal="",
            background_color=(0, 0, 0, 1),
            color=(1, 1, 1, 1)
        )
        self.toggle_btn.bind(on_release=self._toggle_ride)
        bottom.add_widget(self.toggle_btn)

        # ----------- UI Zusammenbauen ---------------
        root.add_widget(top)
        root.add_widget(mid)
        root.add_widget(bottom)
        self.add_widget(root)

        Clock.schedule_once(lambda dt: self._sync_state(), 0)


    def _update_batt_bg(self, *_):
        self._b_bg.pos = self.batt_box.pos
        self._b_bg.size = self.batt_box.size
        self._b_border.rectangle = (self.batt_box.x, self.batt_box.y, self.batt_box.width, self.batt_box.height)

    def on_pre_enter(self, *args):
        self.logger_running = self._is_running()
        # bei jedem Betreten sicherheitshalber neu synchronisieren
        self._sync_state()

    def _sync_state(self):
        running = self.logger_running

        self.toggle_btn.text = "Fahrt beenden" if running else "Fahrt starten"
        self.toggle_btn.background_color = (0, 0, 0, 1) if running else (0.95, 0.75, 0.10, 1)
        self.toggle_btn.color = (1, 1, 1, 1) if running else (0, 0, 0, 1)

    def _toggle_ride(self, *_):
        self.toggle_btn.disabled = True
        Thread(target=self._toggle_worker, daemon=True).start()

    def _toggle_worker(self):
        if self.logger_running:
            subprocess.run(
                ["systemctl", "stop", "fahrdatenlogger.service"],
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.DEVNULL
            )
            self.logger_running = False
        else:
            subprocess.run(
                ["systemctl", "start", "fahrdatenlogger.service"],
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.DEVNULL
            )
            self.logger_running = True

        Clock.schedule_once(self._after_toggle, 0)

    def _reset_live_ui(self):
        self.speed_lbl.text = "[b]0[/b]"
        self.sub_lbl.text = "Lean: 0.0°   |   Pitch: 0.0°"

    def _after_toggle(self, dt):
        self._sync_state()

        App.get_running_app().root.header.status.set_running(self.logger_running)

        if not self.logger_running:
            self._reset_live_ui()

        self.toggle_btn.disabled = False

    def _is_running(self) -> bool:
        try:
            result = subprocess.run(
                ["systemctl", "is-active", "fahrdatenlogger.service"],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                timeout=0.25
            )
            return result.stdout.decode().strip() == "active"
        except subprocess.TimeoutExpired:
            return self.logger_running # Fallback
    
    
    def _update_live(self, dt):
        if not self.logger_running:  # Wenn Logger nicht aktiv: keine Updates
            return
        
        root = App.get_running_app().root
        data = root.ws.latest if hasattr(root, "ws") else {}
        if not data:
            return
        
        drive_time = data.get("drive_time")
        if drive_time:
            self.drive_time_lbl.text = f"[b]{drive_time}[/b]"

        speed = data.get("gps_speed")
        if speed is None:
            speed = 0.0

        self.speed_lbl.text = f"[b]{speed:.0f}[/b]"

        lean = data.get("lean_deg", 0.0) or 0.0
        pitch = data.get("pitch_deg", 0.0) or 0.0

        #if distance >= 1000:
        #    distance_txt = f"{distance/1000:.2f} km"
        #else:
        #    distance_txt = f"{distance:.1f} m"

        self.sub_lbl.text = f"Lean: {abs(lean):.1f}°   |   Pitch: {abs(pitch):.1f}"