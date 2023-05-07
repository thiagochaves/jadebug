from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Label, Button

class Jadebug(App):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title = "Jadebug"
        self.label_status = Label("Status")

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Button(label="Connect")
            yield self.label_status

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.label_status.update("Connected")

if __name__ == "__main__":
    app = Jadebug()
    app.run()
