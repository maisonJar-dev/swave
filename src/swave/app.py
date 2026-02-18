from audio.audio_engine import AudioEngine

from textual.app import App, ComposeResult, Binding
from textual.widgets import Static, Footer, Header
from textual.widgets import Label, Log
from textual.containers import Container
from textual import work
from textual import on

import sounddevice as sd
import numpy as np

class Sidebar(Container):
    def compose(self) -> ComposeResult:
        yield Label("AUDIO SOURCE")
        yield Label("",id="audio_src")

    def update_device(self, name:str) -> None: 
        self.query_one("#audio_src",Label).update(name)

class SwaveApp(App):
    CSS_PATH = "assets/swave.css"
    
    BINDINGS = [
        Binding("d", "toggle_dark", "Toggle Dark Mode"), 
        Binding("ctrl+s", "toggle_sidebar")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Sidebar(classes="-hidden")
        yield Footer()

    def on_mount(self) -> None:
        self.engine = AudioEngine()
        self.engine.start()
        #Store timer for later use
        self._device_timer = self.set_interval(0.1, self._try_set_device)
    
    def _try_set_device(self) -> None:
        if getattr(self.engine, "device_info", None):
            self.query_one(Sidebar).update_device(self.engine.device_info["name"])
            self._device_timer.stop()   # stop the interval
    
    def action_toggle_dark(self) -> None:
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

    def action_toggle_sidebar(self) -> None:
        self.query_one(Sidebar).toggle_class("-hidden")

    
if __name__ == "__main__":
    app = SwaveApp()
    app.run()

def main():
    SwaveApp().run()