from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

from kivy.metrics import dp
from kivy.graphics import Rectangle, Color, Line, RoundedRectangle
from kivy.clock import Clock
from kivy.app import App
from threading import Thread
import subprocess

from UI.widgets.speedring import SpeedRing


class DashboardScreen(Screen):
    def __init__(self, **kw):
        super().__init__(name="dashboard", **kw)

        self.logger_running = False
        Clock.schedule_interval(self._update_live, 1/15)  # Live refresh 15Hz

        # ---------------------- ROOT -> Alles unter HeaderBar -----------------------------
        root = BoxLayout(orientation="vertical", padding=(10, 10), spacing=10)

        # ---------------------- Top -> Drive Time ------------------------
        top = AnchorLayout(anchor_x="center", anchor_y="center", size_hint_y=None, height=40)
        self.drive_time_lbl = Label(
            text="00:00:00:000",
            font_size=28,
            markup=True,
            color=(0, 0, 0, 1),
            halign="center",
            valign="top"
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
            size=(dp(200), dp(200)),
            pos_hint={"x": 0, "center_y": 0.55},   # linkes center im Mid-Bereich
            padding=(12, 12),
            spacing=2
        )

        with self.batt_box.canvas.before:   # Hintergrund/Rahmen/Rundung
            Color(1, 1, 1, 1)  # 0.95, 0.95, 0.95, 1 Hellgrau
            self._b_bg = RoundedRectangle(
                pos=self.batt_box.pos,
                size=self.batt_box.size,
                radius=[20]   
            )

            Color(0, 0, 0, 1)
            self._b_border = Line(
                rounded_rectangle=(
                    self.batt_box.x,
                    self.batt_box.y,
                    self.batt_box.width,
                    self.batt_box.height,
                    20  # gleicher Radius
                ),
            width=1.2
        )
        self.batt_box.bind(pos=self._update_batt_bg, size=self._update_batt_bg)

        self.batt_lbl = Label(
            text="[b]Akku-Daten[/b]\n",
            markup=True,
            font_size=30,
            color=(0.95, 0.75, 0.10, 1),
            halign="center",
            valign="top"
        )
        self.batt_lbl.bind(size=lambda inst, *_: setattr(inst, "text_size", inst.size))

        self.batt_temp_lbl = Label(
            text="Temp: [color=#ff0000][b]0.0°C[/b][/color]",
            markup=True,
            font_size=25,
            color=(0, 0, 0, 1),
            halign="center",
            valign="center"
        )
        self.batt_temp_lbl.bind(size=lambda inst, *_: setattr(inst, "text_size", inst.size))

        self.batt_voltage_lbl = Label(
            text="Voltage: [color=#0000ff][b]0.0 V[/b][/color]",
            markup=True,
            font_size=25,
            color=(0, 0, 0, 1),
            halign="center",
            valign="bottom"
        )
        self.batt_voltage_lbl.bind(size=lambda inst, *_: setattr(inst, "text_size", inst.size))

        # ---------- Assamble Mid-Left -------------
        self.batt_box.add_widget(self.batt_lbl)
        self.batt_box.add_widget(self.batt_temp_lbl)
        self.batt_box.add_widget(self.batt_voltage_lbl)

        # Mid-Center: Speedring + Speed/Lean/Pitch
        self.ring = SpeedRing(
            size_hint=(None,None),
            size=(dp(420), dp(420)),
            pos_hint={"center_x": 0.5, "center_y": 0.40}
        )

        # --------- Assamble Mid-Center ------------
        mid.add_widget(self.ring)
        mid.add_widget(self.batt_box)

        # --------------- Bottom -> Fahrt-toggle Button ----------------
        bottom = AnchorLayout(anchor_x="center", anchor_y="bottom", size_hint_y=None, height=130)
        self.toggle_btn = Button(
            text="Fahrt beenden",
            size_hint=(None, None),
            size=(480, 100),
            font_size=30,
            markup=True,
            background_normal="",
            background_color=(0, 0, 0, 0), # Transbarent machen
            color=(1, 1, 1, 1)
        )
        with self.toggle_btn.canvas.before:
            self._btn_color = Color(0, 0, 0, 1)  # Startfarbe
            self._btn_bg = RoundedRectangle(
                pos=self.toggle_btn.pos,
                size=self.toggle_btn.size,
                radius=[30]
            )

        self.toggle_btn.bind(pos=self._update_btn_bg, size=self._update_btn_bg)
        self.toggle_btn.bind(on_release=self._toggle_ride)
        bottom.add_widget(self.toggle_btn)

        # ----------- UI Zusammenbauen ---------------
        root.add_widget(top)
        root.add_widget(mid)
        root.add_widget(bottom)
        self.add_widget(root)

        Clock.schedule_once(lambda dt: self._sync_state(), 0)

    def _update_btn_bg(self,*_):    # Position Update für Fahrt-toggle-Button BG
        self._btn_bg.pos = self.toggle_btn.pos
        self._btn_bg.size = self.toggle_btn.size

    def _update_batt_bg(self, *_):  # Position Update für Akku-Box BG/Rahmen
        self._b_bg.pos = self.batt_box.pos
        self._b_bg.size = self.batt_box.size

        self._b_border.rounded_rectangle = (
            self.batt_box.x,
            self.batt_box.y,
            self.batt_box.width,
            self.batt_box.height,
            20
        )

    def on_pre_enter(self, *args):
        self.logger_running = self._is_running()    # Systemcall: Service Status (einmalig)
        # bei jedem Betreten sicherheitshalber neu synchronisieren
        self._sync_state()

    def _sync_state(self):
        running = self.logger_running

        # Fahrt-Toggle-Button Schrift und Farbe je nach State ändern
        self.toggle_btn.text = "Fahrt beenden" if running else "Fahrt starten"
        if running:
            self._btn_color.rgba = (0, 0, 0, 1)
            self.toggle_btn.color = (1, 1, 1, 1)
        else:
            self._btn_color.rgba = (0.95, 0.75, 0.10, 1)
            self.toggle_btn.color = (0, 0, 0, 1)

    def _toggle_ride(self, *_): # Funktion um Logger-Service zu togglen
        self.toggle_btn.disabled = True # Button blockieren
        Thread(target=self._toggle_worker, daemon=True).start() # startet neuen Thread für Systemcall Befehle

    def _toggle_worker(self):   # Funktion um Systemcall Befehle auszufüren (eigener Thread)
        if self.logger_running: # Wenn ON --> Off
            subprocess.run(
                ["systemctl", "stop", "fahrdatenlogger.service"],
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.DEVNULL
            )
            self.logger_running = False # Logger status neu setzten 
        else:   # Wenn Off --> On
            subprocess.run(
                ["systemctl", "start", "fahrdatenlogger.service"],
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.DEVNULL
            )
            self.logger_running = True  # Logger status neu setzten

        Clock.schedule_once(self._after_toggle, 0)  # Nach toggle: neu syncronisieren/reset

    def _reset_live_ui(self):   # Funktion um UI Werte zu reseten
        self.ring.set_values(0.0, 0.0, 0.0)

    def _after_toggle(self, dt):    # Funktion um nach toggle UI zu syncronisieren/reseten
        self._sync_state()  # Syncronisieren

        App.get_running_app().root.header.status.set_running(self.logger_running)

        if not self.logger_running: # Wenn Logger Off --> UI Reset
            self._reset_live_ui()

        self.toggle_btn.disabled = False    # Button freigeben

    def _is_running(self) -> bool:  # Funktion um Logger-Status herrauszufinden (Systemcall)
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
    
    
    def _update_live(self, dt): # Funktion um UI werte zu updaten (aus WS Json Dump)
        if not self.logger_running:  # Wenn Logger nicht aktiv: keine Updates
            return
        
        root = App.get_running_app().root
        data = root.ws.latest if hasattr(root, "ws") else {}
        if not data:
            return
        
        drive_time = data.get("drive_time")
        if drive_time:
            self.drive_time_lbl.text = f"[b]{drive_time}[/b]"

        speed = data.get("speed")
        if speed is None:
            speed = 0.0

        lean = data.get("lean_deg", 0.0) or 0.0
        pitch = data.get("pitch_deg", 0.0) or 0.0

        self.ring.set_values(speed, lean, pitch)

        max_batt_temp = data.get("max_batt_temp", 0.0) or 0.0
        self.batt_temp_lbl.text = f'Temp: [color=#ff0000][b]{max_batt_temp:.1f}°C[/b][/color]'

        batt_voltage = data.get("batt_voltage", 0.0) or 0.0
        self.batt_voltage_lbl.text = f'Voltage: [color=#0000ff][b]{batt_voltage:.1f} V[/b][/color]'

        #if distance >= 1000:
        #    distance_txt = f"{distance/1000:.2f} km"
        #else:
        #    distance_txt = f"{distance:.1f} m"