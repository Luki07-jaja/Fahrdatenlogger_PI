from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse
import subprocess


class LedDot(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (32, 32)

        with self.canvas:
            self._color = Color(1, 0, 0, 1)  # rot default
            self._ellipse = Ellipse(pos=self.pos, size=self.size)

        self.bind(pos=self._update, size=self._update)

    def _update(self, *_):
        self._ellipse.pos = self.pos
        self._ellipse.size = self.size

    def set_rgb(self, r, g, b):
        self._color.rgb = (r, g, b)


class LoggerStatus(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="horizontal", spacing=12, **kwargs)
        self.size_hint_y = None
        self.height = 60

        self.led = LedDot()

        self.label = Label(
            text="Logger Aus", 
            font_size=24, 
            color=(0, 0, 0, 1), 
            halign="left", 
            valign="middle"
        )
        self.label.bind(size=lambda inst, *_: setattr(inst, "text_size", inst.size))

        self.add_widget(self.led)
        self.add_widget(self.label)

    def update(self):
        if self._is_logger_running():
            self.led.set_rgb(0, 1, 0)
            self.label.text = "Logger Ein"
        else:
            self.led.set_rgb(1, 0, 0)
            self.label.text = "Logger Aus"

    def _is_logger_running(self) -> bool:
        result = subprocess.run(
            ["systemctl", "is-active", "fahrdatenlogger.service"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL
        )
        return result.stdout.decode().strip() == "active"
