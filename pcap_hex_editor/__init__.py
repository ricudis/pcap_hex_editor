"""
PCAP Hex Editor - A PCAP Hex Editor with Textual UI

A powerful packet capture file editor with hex editing capabilities,
built using Textual for the user interface and Scapy for packet manipulation.
"""

__version__ = "1.0.0"
__author__ = "Christos Rikoudis <ricudis.christos@gmail.com>"
__description__ = "A PCAP Hex Editor with Textual UI"

from .main import PcapHexEditorApp

__all__ = ["PcapHexEditorApp"] 