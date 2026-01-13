from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock

from threading import Thread
import subprocess

class DashboardScreen(Screen):
    def __init__(self, **kw):
        super().__init__(name = "dashboard", **kw)