from kivy.app import App
from kivy.uix.label import Label
from kivy.core.window import Window

class TestApp(App):
    def build(self):
        Window.fullscreen = 'auto'
        return Label(text = "Kivy läuft", font_size  = 60)
    
if __name__ == "__main__":
    TestApp().run()