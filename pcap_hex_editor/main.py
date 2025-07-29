"""
PCAP Hex Editor - A PCAP Hex Editor with Textual UI

A powerful packet capture file editor with hex editing capabilities,
built using Textual for the user interface and Scapy for packet manipulation.

Copyright (C) 2024 Christos Rikoudis <ricudis.christos@gmail.com>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
"""

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Vertical, Horizontal
from textual.widgets import Footer, Header, Static
from textual.reactive import reactive
from textual import events
from scapy.all import rdpcap, Packet, wrpcap, PcapReader
from scapy.all import Ether, Raw
from scapy.layers.inet import IP, TCP, UDP
from scapy.layers.l2 import Ether
from scapy.layers import *
from scapy.layers.inet import *
from scapy.layers.l2 import *
from scapy.layers.inet import *
import datetime
import sys

# Import all the panel classes
from .panels import (
    FocusablePanel,
    PacketListPanel,
    HexEditorPanel,
    DissectionPanel,
    ScapyCommandPanel
)
from .ui import HelpOverlay

SAMPLE_PCAP = "data/sample.pcap"  # Hardcoded for now

class PcapHexEditorApp(App):
    CSS = '''
    Horizontal.main-row {
        width: 1fr;
        height: 1fr;
    }
    Vertical.left-stack {
        width: 2fr;
        height: 1fr;
    }
    #panel-list {
        width: 1fr;
        height: 1fr;
    }
    #panel-hex {
        width: 1fr;
        height: 1fr;
    }
    #panel-hex ScrollableContainer {
        width: 1fr;
        height: 1fr;
    }
    #panel-hex Static {
        width: 1fr;
        padding: 1;
    }
    #panel-command {
        width: 1fr;
        height: 1fr;
    }
    #panel-command TextArea {
        width: 1fr;
        height: 1fr;
        border: none;
        background: transparent;
    }
    #panel-dissect {
        width: 1fr;
        height: 1fr;
    }
    #panel-dissect ScrollableContainer {
        width: 1fr;
        height: 1fr;
    }
    #panel-dissect Static {
        width: 1fr;
        padding: 1;
    }
    FocusablePanel {
        border: round $accent;
        content-align: left top;
        width: 1fr;
        background: darkblue;
    }
    #status-bar {
        width: 1fr;
        height: auto;
        margin: 0 1;
        background: blue;
    }
    HelpOverlay {
        background: rgba(0, 0, 0, 0.8);
    }
    #help-overlay {
        width: 1fr;
        height: 1fr;
        align: center middle;
    }
    #help-modal {
        width: 80%;
        height: 80%;
        background: $surface;
        border: double $accent;
        padding: 2;
    }
    #help-content {
        height: 1fr;
        padding: 1;
        background: $surface;
        color: $text;
    }
    #help-close-button {
        width: auto;
        margin: 1 0 0 0;
        dock: bottom;
    }
    
    /* Timestamp Input Modal Styles */
    #timestamp-modal-overlay {
        width: 1fr;
        height: 1fr;
        align: center middle;
        background: rgba(0, 0, 0, 0.8);
    }
    
    #timestamp-modal {
        width: 60%;
        height: auto;
        background: $surface;
        border: double $accent;
        padding: 2;
    }
    
    #modal-title {
        text-align: center;
        text-style: bold;
        margin-bottom: 1;
    }
    
    #current-timestamp {
        text-align: center;
        margin-bottom: 1;
        color: $text-muted;
    }
    
    #input-label {
        margin-bottom: 1;
    }
    
    #timestamp-input {
        margin-bottom: 2;
        border: round $accent;
    }
    
    #modal-buttons {
        height: auto;
        align: center;
    }
    
    #modal-buttons Button {
        margin: 0 1;
    }
    '''

    BINDINGS = [
        Binding(key="f1", action="show_help", description="Help"),
        Binding(key="f2", action="quit", description="Quit"),
        Binding(key="f3", action="save_pcap", description="Save"),
    ]

    def __init__(self, pcap_filename="sample.pcap"):
        super().__init__()
        self.pcap_filename = pcap_filename
        self.packets = []
        self.selected_index = 0
        self.status_message = ""
        self.save_filename = f"edited_{self.pcap_filename}"

    def compose(self) -> ComposeResult:
        self.packet_list_panel = PacketListPanel("Packet List", self.on_packet_select, self.on_packet_add, self.on_timestamp_edit, id="panel-list")
        self.hex_editor_panel = HexEditorPanel("Hex View", on_edit_callback=self.on_hex_edit, id="panel-hex")
        self.scapy_command_panel = ScapyCommandPanel("Edit Scapy Command", on_edit_callback=self.on_command_edit, id="panel-command")
        self.dissection_panel = DissectionPanel("Dissection", id="panel-dissect")

        yield Header("PCAP Hex Editor")
        with Horizontal(classes="main-row"):
            with Vertical(classes="left-stack"):
                yield self.packet_list_panel
                yield self.hex_editor_panel
                yield self.scapy_command_panel
            yield self.dissection_panel
        yield Static(f"Editing: {self.pcap_filename} | {self.status_message}", id="status-bar")
        yield Footer()

    def on_mount(self):
        try:
            # self.packets = PcapReader(self.pcap_filename)
            packet_list = rdpcap(self.pcap_filename)
            # Convert PacketList to regular list to allow item assignment
            self.packets = list(packet_list)
        except Exception as e:
            self.packets = []
            self.log(f"Failed to load {self.pcap_filename}: {e}")
            self.status_message = f"Failed to load {self.pcap_filename}: {e}"
        self.packet_list_panel.set_packets(self.packets)
        self.on_packet_select(0)

    def action_show_help(self) -> None:
        """Show the help overlay."""
        self.push_screen(HelpOverlay(on_close_callback=self.close_help))

    def action_quit(self) -> None:
        """Quit"""
        self.exit()

    def close_help(self):
        """Close the help overlay."""
        self.pop_screen()

    def on_packet_select(self, index):
        self.selected_index = index
        pkt = self.packets[index] if self.packets else None
        ts = getattr(pkt, 'time', None)
        if ts is not None:
            try:
                ts_str = datetime.datetime.fromtimestamp(ts).isoformat()
            except Exception:
                ts_str = str(ts)
        else:
            ts_str = None
        self.hex_editor_panel.set_packet(pkt)
        self.dissection_panel.set_packet(pkt)
        self.scapy_command_panel.set_packet(pkt)

    def on_packet_add(self, index, new_packet):
        """Handle new packet addition."""
        self.selected_index = index
        self.status_message = f"Added new packet at index {index}"
        # Update all panels with the new packet
        self.hex_editor_panel.set_packet(new_packet)
        self.dissection_panel.set_packet(new_packet)
        self.scapy_command_panel.set_packet(new_packet)
        self.refresh()

    def on_timestamp_edit(self, index, new_timestamp):
        """Handle timestamp editing for a packet."""
        try:
            new_ts = float(new_timestamp)
            
            # Update the packet timestamp
            if index < len(self.packets):
                self.packets[index].time = new_ts
                
                # Update all panels
                self.packet_list_panel.set_packets(self.packets)
                self.packet_list_panel.select(index)
                self.on_packet_select(index)
                
                self.status_message = f"Timestamp updated to {new_timestamp}"
            else:
                self.status_message = "Invalid packet index"
                
        except ValueError:
            self.status_message = "Invalid timestamp format. Use seconds.milliseconds (e.g., 1234567890.123456)"
        except Exception as e:
            self.status_message = f"Error updating timestamp: {e}"
        
        self.refresh()

    def on_hex_edit(self, new_bytes):
        self.log(f"on_hex_edit: {new_bytes}")
        # Update the selected packet by creating a new one from the raw bytes.
        # This assumes an Ethernet link-type, which is common.
        new_pkt = None
        try:
            # Re-create the packet from the link layer to ensure proper dissection
            new_pkt = Ether(new_bytes)
        except Exception:
            # If dissection fails, store as Raw bytes
            new_pkt = Raw(load=new_bytes)
        self.packets[self.selected_index] = new_pkt

        # Update the dissection panel with the new packet
        self.dissection_panel.set_packet(new_pkt)

        # Update the packet list panel to show the new summary
        self.packet_list_panel.set_packets(self.packets)
        self.packet_list_panel.select(self.selected_index)
        # Update the hex editor panel to reflect the changes
        self.hex_editor_panel.set_packet(new_pkt)

    def on_command_edit(self, new_command):
        self.log(f"on_command_edit: {new_command}")
        """Handle scapy command editing - evaluate command and replace current packet."""
        if not new_command or not new_command.strip():
            self.status_message = "Empty command"
            self.refresh()
            return
            
        try:
            # Evaluate the scapy command (scapy modules are already imported at module level)
            self.log(f"Evaluating command: {new_command.strip()}")
            new_packet = eval(new_command.strip())
            self.log(f"New packet: {new_packet}")

            # Check if the result is a valid packet
            if hasattr(new_packet, 'show'):
                # Replace the current packet
                self.packets[self.selected_index] = new_packet
                
                # Update all panels with the new packet
                self.hex_editor_panel.set_packet(new_packet)
                self.dissection_panel.set_packet(new_packet)
                self.scapy_command_panel.set_packet(new_packet)
                
                # Update the packet list panel to show the new summary
                self.packet_list_panel.set_packets(self.packets)
                self.packet_list_panel.select(self.selected_index)
                
                self.status_message = f"Packet updated: {new_command[:50]}{'...' if len(new_command) > 50 else ''}"
            else:
                self.status_message = "Command did not return a valid packet"
                
        except Exception as e:
            self.log(f"Error: {e}")
            # self.status_message = f"Error: {str(e)[:50]}{'...' if len(str(e)) > 50 else ''}"
            
        self.refresh()

    def action_save_pcap(self) -> None:
        try:
            wrpcap(self.save_filename, self.packets)
            self.status_message = f"Saved to {self.save_filename}"
        except Exception as e:
            self.status_message = f"Save failed: {e}"
        self.refresh()



def main():
    """Main entry point for the application."""
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = "data/sample.pcap"
    print(f"Loading {filename}...")
    PcapHexEditorApp(filename).run()

if __name__ == "__main__":
    main()