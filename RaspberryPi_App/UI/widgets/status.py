from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.graphics import Color, Ellipse
import subprocess

class LoggerStatus(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="horizontal", spacing= 20,**kwargs)

        self.size_hint_y = None
        self.height = 60
        self.canvas.before.clear()

        with self.canvas.before:
            self.color = Color(1,0,0) # Weiß
            self.circle = Ellipse(size = (30, 30), pos = self.pos) 
        
        self.label = Label(text="Logger Aus", font_size=24)
        self.add_widget(self.label)
        self.bind(pos=self._update_circle)

    def _update_circle(self, *args):
        self.circle.pos = (self.x, self.y + 15)

    def update(self):
        if self._is_logger_running():
            self.color.rgb = (0,1,0)
            self.label.text = "Logger Ein"
        else:
            self.color.rgb = (1,0,0)
            self.label.text = "Logger Aus"
    
    def _is_logger_running(self) -> bool:
        result = subprocess.run(
            ["systemctl", "is-active", "fahrdatenlogger.service"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL
        )
        state = result.stdout.decode().strip()
        return state == "active"