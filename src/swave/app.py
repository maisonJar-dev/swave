from textual.app import App, ComposeResult
from textual.widgets import Static, Footer, Header
from textual.widgets import Log, Button
from textual.containers import Container
from textual import work
from textual import on

import sounddevice as sd
import numpy as np

class Sidebar(Container):
    def compose(self) -> ComposeResult:
        yield Log()

    def log_to_sidebar(self, msg:str) -> None: 
        self.query_one(Log).write_line(msg)

class SwaveApp(App):
    
    BINDINGS = [("d", "toggle_dark", "Toggle Dark Mode")]
    CSS_PATH = "assets/swave.css"
    
    BINDINGS = [
        ("d", "toggle_dark", "Toggle Dark Mode"), 
        ("ctrl+s", "toggle_sidebar")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Sidebar(classes="-hidden")
        yield Button.success("Yes!")
        yield Button.error("No...")
        yield Footer()
    
    def action_toggle_dark(self) -> None:
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

    def action_toggle_sidebar(self) -> None:
        self.query_one(Sidebar).toggle_class("-hidden")

    @on(Button.Pressed)
    def log_button_press(self, event: Button.Pressed) -> None:
        self.query_one(Sidebar).log_to_sidebar(str(event.button.label))

    
if __name__ == "__main__":
    app = SwaveApp()
    app.run()

def main():
    SwaveApp().run()