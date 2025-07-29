from textual.app import ComposeResult, Screen
from textual.containers import Vertical, Horizontal
from textual.widgets import Static, Button, Input
from textual.binding import Binding
from textual import events

class TimestampInputModal(Screen):
    """Modal input dialog for editing packet timestamps."""

    BINDINGS = [
        Binding(key="escape", action="cancel", description="Cancel"),
        Binding(key="enter", action="accept", description="Accept"),
    ]

    def __init__(self, current_timestamp, on_accept_callback=None, on_cancel_callback=None):
        super().__init__()
        self.current_timestamp = current_timestamp
        self.on_accept_callback = on_accept_callback
        self.on_cancel_callback = on_cancel_callback
        self.input_widget = None

    def compose(self) -> ComposeResult:
        with Vertical(id="timestamp-modal-overlay"):
            with Vertical(id="timestamp-modal"):
                yield Static("Edit Packet Timestamp", id="modal-title")
                yield Static(f"Current: {self.current_timestamp}", id="current-timestamp")
                yield Static("Enter new timestamp (epoch seconds.milliseconds):", id="input-label")
                self.input_widget = Input(value=self.current_timestamp, id="timestamp-input")
                yield self.input_widget
                with Horizontal(id="modal-buttons"):
                    yield Button("Cancel (Esc)", id="cancel-button")
                    yield Button("Accept (Enter)", id="accept-button")

    def on_mount(self):
        """Focus the input widget when the modal is mounted."""
        if self.input_widget:
            self.input_widget.focus()
            # Select all text for easy editing
            self.input_widget.selection = (0, len(self.current_timestamp))

    def action_cancel(self) -> None:
        """Cancel the timestamp editing."""
        if self.on_cancel_callback:
            self.on_cancel_callback()
        self.dismiss()

    def action_accept(self) -> None:
        """Accept the timestamp input."""
        if self.input_widget and self.on_accept_callback:
            new_timestamp = self.input_widget.value
            self.on_accept_callback(new_timestamp)
        self.dismiss()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "cancel-button":
            self.action_cancel()
        elif event.button.id == "accept-button":
            self.action_accept()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission (Enter key)."""
        self.action_accept() 