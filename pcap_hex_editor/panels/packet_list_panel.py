from textual.app import ComposeResult
from textual.widgets import ListView, ListItem, Static
from textual.reactive import reactive
from textual import events
import datetime
from .focusable_panel import FocusablePanel
from scapy.all import Ether, IP, UDP, Raw

class PacketListPanel(FocusablePanel):
    """Panel to display and select packets."""
    packets = reactive([])
    selected_index = reactive(0)

    def __init__(self, title, on_select_callback=None, on_packet_add_callback=None, *args, **kwargs):
        kwargs.setdefault('id', 'panel-list')
        super().__init__(*args, **kwargs)
        self.list_view = ListView()
        self.packets = []
        self.on_select_callback = on_select_callback
        self.on_packet_add_callback = on_packet_add_callback
        self.original_title = title
        self.border_title = title

    def on_focus(self, event: events.Focus) -> None:
        super().on_focus(event)
        self.list_view.focus()
        # Update border title to show helpful keystrokes
        self.border_title = f"{self.original_title} (↑↓: move, pgup/pgdn: move page, a: add packet)"
        self.refresh()

    def on_blur(self, event: events.Blur) -> None:
        super().on_blur(event)
        # Restore original border title
        self.border_title = self.original_title
        self.refresh()

    def set_packets(self, packets):
        self.packets = packets
        self.list_view.clear()
        for i, pkt in enumerate(packets):
            summary = pkt.summary()
            # Get timestamp for this packet
            ts = getattr(pkt, 'time', None)
            if ts is not None:
                try:
                    ts_str = datetime.datetime.fromtimestamp(ts).strftime("%H:%M:%S.%f")[:-3]  # HH:MM:SS.mmm
                except Exception:
                    ts_str = str(ts)
            else:
                ts_str = "N/A"
            self.list_view.append(ListItem(Static(f"{i}: [{ts_str}] {summary}")))
        self.refresh()
        self.select(self.selected_index if self.packets else 0)

    def select(self, index):
        if not self.packets:
            return
        self.selected_index = max(0, min(index, len(self.packets) - 1))
        self.list_view.index = self.selected_index
        if self.on_select_callback:
            self.on_select_callback(self.selected_index)

    def validate_index(self, index):
        """Validate and return a valid index within bounds."""
        if not self.packets:
            return 0
        return max(0, min(index, len(self.packets) - 1))

    def compose(self) -> ComposeResult:
        yield self.list_view

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        # Get the index from the list view's current index
        index = self.list_view.index
        self.select(index)

    def on_key(self, event: events.Key) -> None:
        if not self.packets:
            return

        # Calculate page size based on visible area
        page_size = max(1, self.size.height - 3)
        if event.key == "page_up":
            # Move selected packet up by page size
            new_index = self.validate_index(self.selected_index - page_size)
            self.select(new_index)
        elif event.key == "page_down":
            # Move selected packet down by page size
            new_index = self.validate_index(self.selected_index + page_size)
            self.select(new_index)
        elif event.key == "a":
            # Add new packet
            self.add_new_packet()

    def add_new_packet(self):
        """Add a new packet with Ethernet, IPv4, and UDP layers after the currently selected packet."""
        if not self.packets:
            return
        
        # Generate new packet with default layers
        new_packet = Ether() / IP() / UDP() / Raw(load=b"New packet data")
        
        # Calculate timestamp as middle value between current and next packet
        current_ts = getattr(self.packets[self.selected_index], 'time', 0)
        
        if self.selected_index < len(self.packets) - 1:
            # There's a next packet, calculate middle timestamp
            next_ts = getattr(self.packets[self.selected_index + 1], 'time', current_ts + 1)
            new_ts = (current_ts + next_ts) / 2
        else:
            # This is the last packet, add 1 second to current timestamp
            new_ts = current_ts + 1
        
        # Set the timestamp on the new packet
        new_packet.time = new_ts
        
        # Insert the new packet after the currently selected packet
        insert_index = self.selected_index + 1
        self.packets.insert(insert_index, new_packet)
        
        # Call the callback to notify the main app about the new packet
        if self.on_packet_add_callback:
            self.on_packet_add_callback(insert_index, new_packet)
        
        # Update the display and select the new packet
        self.set_packets(self.packets)
        self.select(insert_index)