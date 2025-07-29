#!/usr/bin/env python3
"""
PCAP Hex Editor - Entry Point

This script provides a clean entry point to run the PCAP Hex Editor
without circular import issues.
"""

import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pcap_hex_editor.main import main

if __name__ == "__main__":
    main() 