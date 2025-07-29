"""
Basic tests for PCAP Hex Editor package
"""

import pytest
from pcap_hex_editor import PcapHexEditorApp


def test_import():
    """Test that the package can be imported."""
    assert PcapHexEditorApp is not None


def test_app_creation():
    """Test that the app can be created."""
    app = PcapHexEditorApp("data/sample.pcap")
    assert app is not None
    assert app.pcap_filename == "data/sample.pcap"


if __name__ == "__main__":
    pytest.main([__file__]) 