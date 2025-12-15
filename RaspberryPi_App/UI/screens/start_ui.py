from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.app import App
import subprocess
from threading import Thread
from kivy.clock import Clock
from kivy.app import App

from UI.widgets.status import LoggerStatus

class StartScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", spacing=20, **kwargs)

        self.status = LoggerStatus()
        self.add_widget(self.status)

        self.start_btn = Button(
            text="Fahrt starten / stoppen",
            size_hint=(1, 0.3),
            font_size=28
        )
        self.start_btn.bind(on_release=self._toggle_logger)

        self.exit_btn = Button(
            text="Programm beenden",
            size_hint=(1, 0.2),
            background_color=(1, 0, 0, 1),
            font_size=24
        )
        self.exit_btn.bind(on_release=self.exit_app)

        self.add_widget(self.start_btn)
        self.add_widget(self.exit_btn)

        # Status regelmäßig aktualisieren
        Clock.schedule_interval(lambda dt: self.status.update(), 0.5)

    # BUTTON LOGIK (NICHT BLOCKIEREND)
    def _toggle_logger(self, *args):
        self.start_btn.disabled = True  # Mehrfachklick verhindern

        Thread(
            target=self._toggle_logger_worker,
            daemon=True
        ).start()

    def _toggle_logger_worker(self):
        try:
            if self.status._is_logger_running():
                subprocess.run(
                    ["systemctl", "stop", "fahrdatenlogger.service"],
                    check=True
                )
            else:
                subprocess.run(
                    ["systemctl", "start", "fahrdatenlogger.service"],
                    check=True
                )
        except Exception as e:
            print("Systemd Fehler:", e)

        # UI-Update sicher im Main-Thread
        Clock.schedule_once(self._after_toggle, 0)

    def _after_toggle(self, dt):
        self.status.update()
        self.start_btn.disabled = False

    def exit_app(self, *args):
        App.get_running_app().stop()
