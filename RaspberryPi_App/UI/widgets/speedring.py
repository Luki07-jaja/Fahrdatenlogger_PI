from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import NumericProperty, StringProperty
from kivy.graphics import Color, Line
from kivy.clock import Clock

class SpeedRing(FloatLayout):
    speed = NumericProperty(0.0)
    max_speed = NumericProperty(120.0)

    lean = NumericProperty(0.0)
    pitch = NumericProperty(0.0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.start_angle = 225
        self.sweep = 270

        # Internal "displayed" values
        self._displayed_speed = 0.0
        self._displayed_lean = 0.0
        self._displayed_pitch = 0.0
        
        # Target values 
        self._target_speed = 0.0
        self._target_lean = 0.0
        self._target_pitch = 0.0
        
        # Interpolation alpha (0.1 = smooth --> größer = schneller) 
        self.alpha_speed = 0.2   # Für Speed
        self.alpha_angle = 0.3  # Für Lean/Pitch 

        # Ring zeichnen
        with self.canvas.before:
            Color(0.85, 0.85, 0.85, 1)  # BG
            self.bg_line = Line(width=14, cap="round")

            Color(0.0, 0.75, 0.0, 1)    # FG (Speed)
            self.fg_line = Line(width=14, cap="round")

        # Labels IN den Ring
        self.speed_lbl = Label(
            text="[b]0[/b]",
            markup=True,
            font_size=110,
            color=(0, 0, 0, 1),
            halign="center",
            valign="middle",
            size_hint=(1, 1),
            pos_hint={"center_x": 0.5, "center_y": 0.6},
        )
        self.speed_lbl.bind(size=lambda inst, *_: setattr(inst, "text_size", inst.size))
        self.add_widget(self.speed_lbl)

        self.sub_lbl = Label(
            text="Lean: [color=#00aa00][b]0.0°[/b][/color]   |   Pitch: [color=#00aa00][b]0.0°[/b][/color]",
            font_size=26,
            markup=True,
            color=(0, 0, 0, 1),
            halign="center",
            valign="middle",
            size_hint=(1, 1),
            pos_hint={"center_x": 0.5, "center_y": 0.40},
        )
        self.sub_lbl.bind(size=lambda inst, *_: setattr(inst, "text_size", inst.size))
        self.add_widget(self.sub_lbl)

        # Redraw Hooks
        self.bind(pos=self._schedule_redraw, size=self._schedule_redraw)
        Clock.schedule_once(self._redraw, 0)
        
        # 60 FPS Interpolation Loop 
        Clock.schedule_interval(self._interpolate_values, 1/60.0)  # 60 FPS

    def _schedule_redraw(self, *_):
        Clock.unschedule(self._redraw)
        Clock.schedule_once(self._redraw, 0)

    def _interpolate_values(self, dt):
        """
        Läuft mit 60 FPS und interpoliert die angezeigten Werte
        sanft zu den Zielwerten (Low-Pass Filter).
        """
        # Speed interpolieren
        self._displayed_speed += (self._target_speed - self._displayed_speed) * self.alpha_speed
        
        # Lean/Pitch interpolieren
        self._displayed_lean += (self._target_lean - self._displayed_lean) * self.alpha_angle
        self._displayed_pitch += (self._target_pitch - self._displayed_pitch) * self.alpha_angle
        
        # Ring neu zeichnen mit interpolierten Werten
        self._redraw_with_displayed()
        
        # Labels aktualisieren
        self.speed_lbl.text = f"[b]{abs(self._displayed_speed):.0f}[/b]"
        self.sub_lbl.text = (
            f"Lean: [color=#00aa00][b]{abs(self._displayed_lean):.1f}°[/b][/color]   |   "
            f"Pitch: [color=#00aa00][b]{abs(self._displayed_pitch):.1f}°[/b][/color]"
        )

    def _redraw(self, *_):
        self._redraw_with_displayed()

    def _redraw_with_displayed(self):   #Ring mit aktuellen displayed values zeichnen
        cx, cy = self.center
        radius = min(self.width, self.height) * 0.45

        # BG
        self.bg_line.circle = (cx, cy, radius, self.start_angle, self.start_angle + self.sweep)

        # FG abhängig von displayed_speed
        s = max(0.0, min(self._displayed_speed, float(self.max_speed)))
        frac = 0.0 if self.max_speed <= 0 else (s / float(self.max_speed))
        end_angle = self.start_angle + (self.sweep * frac)

        if frac <= 0.001:
            self.fg_line.circle = (cx, cy, radius, self.start_angle, self.start_angle + 1)
        else:
            self.fg_line.circle = (cx, cy, radius, self.start_angle, end_angle)

    def set_values(self, speed, lean, pitch):
        """
        Wird vom Dashboard mit 10 Hz aufgerufen.
        Setzt nur die TARGET-Werte, die dann intern interpoliert werden.
        """
        self._target_speed = float(speed or 0.0)
        self._target_lean = float(lean or 0.0)
        self._target_pitch = float(pitch or 0.0)