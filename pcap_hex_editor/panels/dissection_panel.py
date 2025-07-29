from textual.app import ComposeResult
from textual.containers import ScrollableContainer
from textual.widgets import Static
from textual.reactive import reactive
from textual import events
from .focusable_panel import FocusablePanel

class DissectionPanel(FocusablePanel):
    """Panel to show Scapy dissection of the selected packet."""
    packet = reactive(None)

    def __init__(self, title, *args, **kwargs):
        kwargs.setdefault('id', 'panel-dissect')
        super().__init__(*args, **kwargs)
        self.original_title = title
        self.border_title = title
        self.content_widget = Static()
        self.scroll_container = ScrollableContainer()

    def on_focus(self, event: events.Focus) -> None:
        super().on_focus(event)
        self.scroll_container.focus()
        # Update border title to show helpful keystrokes
        self.border_title = f"{self.original_title} (↑↓: scroll, pgup/pgdn: page, home/end: top/bottom)"
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
            self.content_widget.update(f"{packet.show(dump=True)}")
        else:
            self.content_widget.update("No packet selected.")

    def compose(self) -> ComposeResult:
        with self.scroll_container:
            yield self.content_widget

    def on_key(self, event: events.Key) -> None:
        # Handle scroll events for the dissection panel
        if not self.scroll_container:
            return

        if event.key == "up":
            # Scroll up by one line
            self.scroll_container.scroll_up()
        elif event.key == "down":
            # Scroll down by one line
            self.scroll_container.scroll_down()
        elif event.key == "page_up":
            # Page up
            self.scroll_container.scroll_page_up()
        elif event.key == "page_down":
            # Page down
            self.scroll_container.scroll_page_down()
        elif event.key == "home":
            # Scroll to top
            self.scroll_container.scroll_home()
        elif event.key == "end":
            # Scroll to bottom
            self.scroll_container.scroll_end() 