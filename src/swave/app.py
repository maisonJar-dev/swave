from audio.audio_engine import AudioEngine

from textual.app import App, ComposeResult, Binding
from textual.widgets import Footer, Header
from textual.widgets import Label
from textual.containers import Container, Center
from textual import work
from textual import on
from textual.widget import Widget

import sounddevice as sd
import numpy as np

from rich.text import Text
from rich.style import Style

import math

class Sidebar(Container):
    def compose(self) -> ComposeResult:
        yield Label("AUDIO SOURCE")
        yield Label("",id="audio_src")

    def update_device(self, name:str) -> None: 
        self.query_one("#audio_src",Label).update(name)
class Simulate(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.engine = None
        self._magnitudes = []

    def on_mount(self):
        self.set_interval(1/128, self.refresh)  # 30fps render loop

    def update_engine(self, engine: AudioEngine) -> None:
        self.engine = engine

    def render(self) -> Text:
        text = Text()

        if not self.engine or not len(self.engine.magnitudes):
            return Text("Waiting for audio...")

        magnitudes = self.engine.magnitudes
        width = self.size.width
        height = self.size.height
        cx = width // 2
        cy = height // 2
        num_particles = 64
        
        # build a grid of characters
        grid = [[(" ", "white") for _ in range(width)] for _ in range(height)]

        for i in range(num_particles):
            angle = (i / num_particles) * 2 * math.pi
            bin_index = int(i * len(magnitudes) / num_particles)
            magnitude = magnitudes[bin_index]
            
            # 1. Calculate the color based on the index (0 to 64)
            # We use RGB interpolation: Red (Bass) -> Green (Mids) -> Blue (Treble)
            r = int(max(0, 255 - (i * 4)))
            g = int(max(0, 255 - abs(i - 32) * 8))
            b = int(min(255, i * 4))
            color = f"rgb({r},{g},{b})"

            # 2. Calculate position
            radius = 5 + min(magnitude * 0.01, 20)
            x = int(cx + radius * math.cos(angle) * 2)
            y = int(cy + radius * math.sin(angle))

            # 3. Stamp the colored particle into the grid
            if 0 <= x < width and 0 <= y < height:
                grid[y][x] = ("●", color)

        # 4. Build the final Rich Text object
        for row in grid:
            for char, style in row:
                text.append(char, style=style)
            text.append("\n")

        return text

class SwaveApp(App):
    CSS_PATH = "assets/swave.css"
    
    BINDINGS = [
        Binding("d", "toggle_dark", "Toggle Dark Mode"), 
        Binding("ctrl+s", "toggle_sidebar")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Sidebar(classes="-hidden")
        yield Simulate()
        yield Footer()

    def on_mount(self) -> None:
        self.engine = AudioEngine()
        self.engine.start()
        self.query_one(Simulate).update_engine(self.engine)  # set it after
        #Store timer for later use
        self._device_timer = self.set_interval(0.1, self._try_set_device)
    
    def _try_set_device(self) -> None:
        if getattr(self.engine, "device_info", None):
            self.query_one(Sidebar).update_device(self.engine.device_info["name"])
            self.query_one(Simulate).update_engine(self.engine) 
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