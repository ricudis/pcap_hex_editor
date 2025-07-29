# PCAP Hex Editor

A powerful packet capture file editor with hex editing capabilities, built using Textual for the user interface and Scapy for packet manipulation.

## Features

- **Hex Editor**: Edit packet bytes directly in hex format with real-time ASCII preview
- **Packet List**: Browse and select packets from PCAP files
- **Packet Dissection**: View detailed packet analysis using Scapy
- **Scapy Command Editor**: Create and modify packets using Scapy syntax
- **Modern TUI**: Beautiful terminal user interface built with Textual
- **Real-time Updates**: See changes immediately across all panels

## Installation

### From Source

1. Clone the repository:

```bash
git clone <repository-url>
cd pcap_hex_editor
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Install the package:

```bash
pip install -e .
```

## Usage

### Command Line

Run the application with a PCAP file:

```bash
# Using the installed command
pcap-hex-editor data/sample.pcap

# Or using Python module
python -m pcap_hex_editor.main data/sample.pcap
```

### Interactive Controls

#### Packet List Panel

- **↑/↓**: Navigate packets
- **PgUp/PgDn**: Page through packets
- **Shift+↑/↓**: Reorder packets

#### Hex Editor Panel

- **↑/↓/←/→**: Navigate hex bytes
- **0-9, a-f**: Edit hex values
- **Enter**: Commit changes
- **Escape**: Abort changes

#### Scapy Command Panel

- **Type**: Edit Scapy commands
- **Enter**: Execute command and replace packet

#### Dissection Panel

- **↑/↓**: Scroll through dissection
- **PgUp/PgDn**: Page through dissection
- **Home/End**: Jump to top/bottom

#### Global Controls

- **F1**: Show help
- **F2**: Quit application
- **F3**: Save PCAP file
- **Tab**: Switch between panels

## Project Structure

```
pcap_hex_editor/
├── README.md              # This file
├── setup.py               # Package setup
├── requirements.txt       # Dependencies
├── pcap_hex_editor/       # Main package
│   ├── __init__.py       # Package initialization
│   ├── main.py           # Main application
│   ├── panels/           # UI panel components
│   │   ├── __init__.py
│   │   ├── focusable_panel.py
│   │   ├── packet_list_panel.py
│   │   ├── hex_editor_panel.py
│   │   ├── dissection_panel.py
│   │   └── scapy_command_panel.py
│   └── ui/               # UI components
│       ├── __init__.py
│       └── help_overlay.py
├── data/                 # Sample data files
│   ├── sample.pcap
│   └── test.pcap
└── tests/                # Test files
    └── __init__.py
```

## Dependencies

- **textual**: Modern terminal UI framework
- **scapy**: Packet manipulation library
- **rich**: Rich text and formatting

### Code Style

The project follows PEP 8 style guidelines.

## License

GNU General Public License v2.0 (GPL-2.0-only) - see LICENSE file for details.

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Author

**Christos Rikoudis** <your-email@example.com>

## Acknowledgments

- Built with [Textual](https://textual.textualize.io/) for the TUI
- Uses [Scapy](https://scapy.net/) for packet manipulation
- Inspired by traditional hex editors and packet analyzers
- 90% of the code was vibe coded using Cursor!
