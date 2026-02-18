from textual.app import App, ComposeResult, Binding
from textual.widgets import Static, Footer, Header
from textual.widgets import Log, Label, ListItem, ListView
from textual.containers import Container
from textual import work
from textual import on

import sounddevice as sd
import numpy as np

class Sidebar(Container):
    def compose(self) -> ComposeResult:
        yield Label("AUDIO SOURCE")
        yield ListView(
            ListItem(Label("System Audio"), id="sys_audio"),
            ListItem(Label("Microphone"), id="mic"),
            id="audio_list"
        )

    def log_to_sidebar(self, msg:str) -> None: 
        self.query_one(Log).write_line(msg)

    def on_mount(self) -> None: 
        #At the moment System Audio is focus so let user see that is what is set
        self.query_one("#audio_list", ListView).index = 0

class SwaveApp(App):
    
    CSS_PATH = "assets/swave.css"
    
    BINDINGS = [
        Binding("d", "toggle_dark", "Toggle Dark Mode"), 
        Binding("ctrl+s", "toggle_sidebar")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Sidebar(classes="-hidden")
        yield Footer()
    
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