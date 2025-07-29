from textual.app import ComposeResult, Screen
from textual.containers import Vertical
from textual.widgets import Static, Button
from textual.binding import Binding

class HelpOverlay(Screen):
    """Modal help overlay that appears in the center of the screen."""

    HELP_TEXT = '''
PCAP Hex Editor - Help

Navigation:
  Up/Down         - Select packet
  Shift+Up/Down   - Move packet up/down
  Tab             - Cycle focus between panels
  F1              - Show this help
  F2              - Quit

Hex Editor:
  Left/Right/Up/Down - Move cursor
  0-9, a-f           - Edit hex digit

Dissection Panel:
  Up/Down         - Scroll up/down
  Page Up/Down    - Page up/down
  Home/End        - Scroll to top/bottom

Scapy Command Panel:
  Direct text editing with TextArea widget
  Changes are automatically applied

General:
  s               - Save to edited_sample.pcap
  Esc             - Close help
'''

    BINDINGS = [
        Binding(key="escape", action="close_help", description="Close help"),
        Binding(key="f1", action="close_help", description="Close help"),
    ]

    def __init__(self, on_close_callback=None):
        super().__init__()
        self.on_close_callback = on_close_callback

    def compose(self) -> ComposeResult:
        with Vertical(id="help-overlay"):
            with Vertical(id="help-modal"):
                yield Static(self.HELP_TEXT, id="help-content")
                yield Button("Close (Esc)", id="help-close-button")

    def on_mount(self):
        # Focus the close button
        self.query_one("#help-close-button").focus()

    def action_close_help(self) -> None:
        """Close the help overlay."""
        self.on_close_callback() 