from .focusable_panel import FocusablePanel
from textual import events
from textual import events
from textual.app import App, ComposeResult
from textual.reactive import reactive
from textual.widgets import TextArea

class TextAreaEnter(TextArea):
    def __init__(self, *args, on_edit_callback=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.on_edit_callback = on_edit_callback

    def _on_key(self, event: events.Key) -> None:
        if event.key == "enter":
            self.on_edit_callback(self.text)
            event.prevent_default()

class ScapyCommandPanel(FocusablePanel):
    """Panel to display and edit the Scapy command for the current packet."""
    packet = reactive(None)
    command_text = reactive("")
    on_edit_callback = None

    def __init__(self, title, *args, on_edit_callback=None, **kwargs):
        kwargs.setdefault('id', 'panel-command')
        super().__init__(*args, **kwargs)
        self.on_edit_callback = on_edit_callback
        self.original_title = title
        self.border_title = title
        self.text_area = TextAreaEnter(id="text-area", on_edit_callback=on_edit_callback)

    def on_focus(self, event: events.Focus) -> None:
        super().on_focus(event)
        self.text_area.focus()
        # Update border title to show helpful keystrokes
        self.border_title = f"{self.original_title} (type to edit, enter to commit)"
        self.refresh()

    def on_blur(self, event: events.Blur) -> None:
        """When the panel loses focus, restore original title."""
        super().on_blur(event)
        # Restore original border title
        self.border_title = self.original_title
        self.refresh()

    def set_packet(self, packet):
        self.packet = packet
        if packet is not None:
            try:
                self.command_text = packet.command()
            except Exception:
                self.command_text = "Error generating command"
        else:
            self.command_text = "No packet selected"
        self.text_area.text = self.command_text

    def compose(self) -> ComposeResult:
        yield self.text_area

    def on_text_area_changed(self, event: TextArea.Changed) -> None:
        """Handle text changes in the TextArea."""
        # Store the current text but don't call callback yet
        self.command_text = event.text_area.text
