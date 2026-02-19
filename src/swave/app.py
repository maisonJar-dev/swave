from audio.audio_engine import AudioEngine
from textual.app import App, ComposeResult, Binding
from textual.widgets import Footer, Header, Label
from textual.widgets import Static
from textual.containers import Container
from textual.widget import Widget
from rich.text import Text
import numpy as np
import math
import time

class Sidebar(Container):
    def compose(self) -> ComposeResult:
        yield Label("AUDIO SOURCE", classes="sb_src")
        yield Label("", id="audio_src", classes="sb_src")
        yield SourceIcon()
        yield Label("VibeCoded By: Maison Gulyas", id="credit")

    def update_device(self, name: str) -> None:
        self.query_one("#audio_src", Label).update(name)


class Simulate(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.engine = None
        self._smoothed_mags = None
        self._peaks = {}

    def on_mount(self) -> None:
        self.set_interval(1/120, self.refresh)

    def update_engine(self, engine) -> None:
        self.engine = engine

    def render(self) -> Text:
        width, height = self.size.width, self.size.height
        if width <= 0 or height <= 0: return Text("")

        # 1. Faster Data Handling
        padding = width // 4
        active_width = width - (padding * 2)
        if active_width <= 0: return Text("")

        # Ensure we have data
        if self.engine is None or self.engine.magnitudes is None or self.engine.magnitudes.size == 0:
            raw = np.zeros(active_width)
        else:
            raw = np.array(self.engine.magnitudes, dtype=float)

        # 2. Faster Smoothing
        # Reducing convolution window for speed; increasing temporal lerp for "Liquid" feel
        # LERP - Linear Interpolation, is a way of smoothly moving fron one value toward another over time
        smoothed_spatial = np.convolve(raw, np.ones(3) / 3, mode='same')
        
        if self._smoothed_mags is None or len(self._smoothed_mags) != len(smoothed_spatial):
            self._smoothed_mags = smoothed_spatial
        else:
            # 0.90 lerp creates that "viscous" high-end studio look
            self._smoothed_mags = self._smoothed_mags * 0.90 + smoothed_spatial * 0.10
        
        mags = self._smoothed_mags
        cy = height // 2
        t = time.time()
        
        # 3. Create a Row-Buffer (Much faster than a 2D Grid)
        # We initialize each row as a list of spaces to allow direct indexing
        rows = [[" "] * width for _ in range(height)]
        row_colors = [[None] * width for _ in range(height)]

        # Pre-calculate horizontal gradient base
        # This avoids doing the math inside the nested y-loop
        for x in range(padding, width - padding):
            x_rel = x - padding
            x_ratio = x_rel / active_width
            
            # Map frequency to magnitude
            bin_idx = int(x_ratio * (len(mags) - 1))
            mag = mags[bin_idx]

            # Physics & "Alive" Logic
            # Sine wave phase shifted by X for a "rolling" effect
            # Look SIN!!! (SWAVE) Get it, idk man
            idle = math.sin(t * 5.0 + x * 0.3) * 1.2
            h = int(min(max(0, (mag * 0.4) + idle) / 2, cy - 1)) + 1

            # Base colors for this column
            r_base = int(140 - (x_ratio * 120))
            g_base = int(60 + (x_ratio * 160))
            
            for y_off in range(h):
                yu, yd = cy - y_off, cy + y_off
                
                # Vertical tip brightening
                v_bright = int((y_off / cy) * 40)
                color = f"rgb({min(255, r_base + v_bright)},{min(255, g_base + v_bright)},255)"
                
                # Use Box-drawing for the root to close the gap
                char = "┃"
                
                if 0 <= yu < height:
                    rows[yu][x] = char
                    row_colors[yu][x] = color
                if 0 <= yd < height:
                    rows[yd][x] = char
                    row_colors[yd][x] = color

        # 4. Final Fast Assembly
        output = Text()
        for y in range(height):
            for x in range(width):
                output.append(rows[y][x], style=row_colors[y][x])
            if y < height - 1:
                output.append("\n")
        
        return output

class SourceIcon(Static):
    def render(self):
        return (
        "███████╗██╗    ██╗ █████╗ ██╗   ██╗███████╗\n"
        "██╔════╝██║    ██║██╔══██╗██║   ██║██╔════╝\n"
        "███████╗██║ █╗ ██║███████║██║   ██║█████╗  \n"
        "╚════██║██║███╗██║██╔══██║╚██╗ ██╔╝██╔══╝  \n"
        "███████║╚███╔███╔╝██║  ██║ ╚████╔╝ ███████╗\n"
        "╚══════╝ ╚══╝╚══╝ ╚═╝  ╚═╝  ╚═══╝  ╚══════╝\n"
    )
    
class SwaveApp(App):
    TITLE = "∿"
    CSS_PATH = "assets/swave.css"

    BINDINGS = [
        Binding("d", "toggle_dark", "Toggle Dark Mode"),
        Binding("ctrl+s", "toggle_sidebar", "Audio Source")
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Sidebar(classes="-hidden")
        yield Simulate()
        yield Footer()

    def on_mount(self) -> None:
        self.engine = AudioEngine()
        self.engine.start()
        self.query_one(Simulate).update_engine(self.engine)
        self._device_timer = self.set_interval(0.1, self._try_set_device)

    def _try_set_device(self) -> None:
        if getattr(self.engine, "device_info", None):
            self.query_one(Sidebar).update_device(self.engine.device_info["name"])
            self.query_one(Simulate).update_engine(self.engine)
            self._device_timer.stop()

    def action_toggle_dark(self) -> None:
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

    def action_toggle_sidebar(self) -> None:
        self.query_one(Sidebar).toggle_class("-hidden")


if __name__ == "__main__":
    SwaveApp().run()

def main():
    SwaveApp().run()