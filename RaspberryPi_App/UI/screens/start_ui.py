from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

from kivy.graphics import RoundedRectangle, Color
from kivy.app import App
from kivy.clock import Clock
from threading import Thread
import subprocess


class StartScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(name="start", **kwargs)

        root = BoxLayout(orientation="vertical", padding=40, spacing=20) # vertikale anordnung der Widgets

        top = AnchorLayout(anchor_x="center", anchor_y="center", size_hint_y=1, size_hint_x=1)
        logo = Label(   # Logo Label                               
            text="[b]E-MX[/b]\n[i]Fahrdatenlogger[/i]",    
            markup=True,
            font_size=52,
            color=(0, 0, 0, 1),
            halign="center",
            valign="middle"
        )
        logo.bind(size=lambda inst, *_: setattr(inst, "text_size", inst.size))
        top.add_widget(logo)

        mid = AnchorLayout(anchor_x="center", anchor_y="center", size_hint_y=0.45)  # Button zum Starten einer Fahrt
        self.start_btn = Button(
            text="Fahrt starten",
            size_hint=(None, None),
            size=(520, 110),
            font_size=35,
            markup=True,
            background_normal="",
            background_color=(0, 0, 0, 0), # Transbarent machen
            color=(0, 0, 0, 1)
        )
        with self.start_btn.canvas.before:
            self._btn_color = Color(0.95, 0.75, 0.10, 1)  # Startfarbe
            self._btn_bg = RoundedRectangle(
                pos=self.start_btn.pos,
                size=self.start_btn.size,
                radius=[30]
            )
        self.start_btn.bind(pos=self._update_btn_bg, size=self._update_btn_bg)
        self.start_btn.bind(on_release=self._start_ride)    # start ride Funktion an den button "binden"
        mid.add_widget(self.start_btn)

        root.add_widget(top)
        root.add_widget(mid)
        self.add_widget(root)

    def _update_btn_bg(self,*_):
        self._btn_bg.pos = self.start_btn.pos
        self._btn_bg.size = self.start_btn.size

    def _start_ride(self, *_):  # startet eigener Thread und springt in die start worker Funktion
        self.start_btn.disabled = True
        Thread(target=self._start_worker, daemon=True).start() 

    def _start_worker(self):    # startet den Fahrdatenlogger Service -> Datenübertragung
        subprocess.run(
            ["systemctl", "start", "fahrdatenlogger.service"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        Clock.schedule_once(self._go_dashboard, 0)  # wenn ausgeführt -> automatischer wechsel auf Dashboard UI

    def _go_dashboard(self, dt):    # wechsel auf Dashboard
        App.get_running_app().root.header.status.set_running(True)

        self.start_btn.disabled = False
        self.manager.current = "dashboard"
