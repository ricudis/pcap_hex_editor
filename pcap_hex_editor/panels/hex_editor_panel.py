from textual.app import ComposeResult
from textual.containers import ScrollableContainer
from textual.widgets import Static
from textual.reactive import reactive
from textual import events
import binascii
from .focusable_panel import FocusablePanel

class HexEditorPanel(FocusablePanel):
    """Panel to display and edit packet bytes in hex"""
    packet = reactive(None)
    hex_str = reactive("")
    working_hex_str = reactive("")  # Working copy for edits
    cursor_line = reactive(0)  # Current line (0-based)
    cursor_pos = reactive(0)   # Position within the line (0-15 for bytes, 0-31 for hex digits)
    on_edit_callback = None

    def __init__(self, title, *args, on_edit_callback=None, **kwargs):
        kwargs.setdefault('id', 'panel-hex')
        super().__init__(*args, **kwargs)
        self.on_edit_callback = on_edit_callback
        self.original_title = title
        self.border_title = title
        self.content_widget = Static()
        self.scroll_container = ScrollableContainer()
        self.visible_lines = 0  # Number of lines currently visible

    def on_focus(self, event: events.Focus) -> None:
        """When the panel gets focus, focus the scroll container."""
        super().on_focus(event)
        self.scroll_container.focus()
        # Update border title to show helpful keystrokes
        self.border_title = f"{self.original_title} (↑↓←→: move, 0-9a-f: edit, enter: commit, esc: abort)"
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
            raw_bytes = bytes(packet)
            self.hex_str = binascii.hexlify(raw_bytes).decode()
            self.working_hex_str = self.hex_str  # Initialize working copy
            self.cursor_line = 0
            self.cursor_pos = 0
        else:
            self.hex_str = ""
            self.working_hex_str = ""
            self.cursor_line = 0
            self.cursor_pos = 0
        self.update_content()
        self.refresh()

    def compose(self) -> ComposeResult:
        with self.scroll_container:
            yield self.content_widget

    def render(self) -> str:
        if self.packet is None:
            return "No packet selected."

        # Use working hex string for display, fallback to original if empty
        display_hex = self.working_hex_str if self.working_hex_str else self.hex_str
        if not display_hex:
            return "Empty packet."
        
        # Convert hex string back to bytes for display
        try:
            raw_bytes = binascii.unhexlify(display_hex)
        except Exception:
            # If hex string is invalid, use original packet bytes
            raw_bytes = bytes(self.packet)

        lines = []
        # Process 16 bytes per line
        for line_idx, offset in enumerate(range(0, len(raw_bytes), 16)):
            # Get 16 bytes for this line
            line_bytes = raw_bytes[offset:offset + 16]

            # Format offset (8 hex digits)
            offset_str = f"{offset:08x}"

            # Format hex bytes (16 bytes, 2 chars each, space separated)
            hex_parts = []
            for i, byte in enumerate(line_bytes):
                # Check if this is the current cursor position
                if line_idx == self.cursor_line and i == self.cursor_pos // 2:
                    hex_parts.append(f"[reverse]{byte:02x}[/reverse]")
                else:
                    hex_parts.append(f"{byte:02x}")
            # Pad with spaces if less than 16 bytes
            while len(hex_parts) < 16:
                hex_parts.append("  ")
            hex_str = " ".join(hex_parts)

            # Format ASCII representation
            ascii_parts = []
            for i, byte in enumerate(line_bytes):
                # Check if this is the current cursor position (same byte as hex)
                is_cursor_position = (line_idx == self.cursor_line and i == self.cursor_pos // 2)

                if 32 <= byte <= 126:  # Printable ASCII
                    char = chr(byte)
                    # Escape markup characters that could confuse Textual
                    if char in '[]':
                        char = f"\\{char}"
                    # Highlight if this is the cursor position
                    if is_cursor_position:
                        ascii_parts.append(f"[reverse]{char}[/reverse]")
                    else:
                        ascii_parts.append(char)
                else:
                    # Non-printable as dot
                    if is_cursor_position:
                        ascii_parts.append("[reverse].[/reverse]")
                    else:
                        ascii_parts.append(".")
            ascii_str = "".join(ascii_parts)

            # Combine: offset | hex | ascii
            line = f"{offset_str}  {hex_str}  |{ascii_str}|"
            lines.append(line)
        return '\n'.join(lines)

    def update_content(self):
        self.content_widget.update(self.render())

    def scroll_to_cursor(self):
        """Scroll to ensure the cursor is visible."""
        if not self.packet:
            return

        # Calculate total lines in the data
        raw_bytes = bytes(self.packet)
        total_lines = (len(raw_bytes) + 15) // 16  # Ceiling division

        # Estimate visible lines based on panel height
        try:
            panel_height = self.size.height
            # Subtract some space for borders and padding
            self.visible_lines = max(1, panel_height - 4)
        except Exception:
            self.visible_lines = 10  # Fallback

        # Get current scroll position
        try:
            current_scroll_y = self.scroll_container.scroll_offset.y
        except Exception:
            current_scroll_y = 0

        # Check if cursor is outside the visible area
        cursor_visible_start = current_scroll_y
        cursor_visible_end = current_scroll_y + self.visible_lines

        # Only scroll if cursor is outside visible area
        if self.cursor_line < cursor_visible_start or self.cursor_line >= cursor_visible_end:
            # Calculate the line that should be at the top to show the cursor
            target_top_line = max(0, self.cursor_line - self.visible_lines // 2)

            # Ensure we don't scroll past the beginning
            target_top_line = min(target_top_line, total_lines - self.visible_lines)
            target_top_line = max(0, target_top_line)

            # Scroll to the target line
            try:
                self.scroll_container.scroll_to(0, target_top_line)
            except Exception:
                pass  # Ignore scroll errors

    def on_key(self, event: events.Key) -> None:
        if not self.hex_str:
            return

        # Calculate total bytes and lines
        total_bytes = len(self.hex_str) // 2
        total_lines = (total_bytes + 15) // 16  # Ceiling division

        if event.key == "left":
            if self.cursor_pos > 0:
                self.cursor_pos -= 1
                self.update_content()
            elif self.cursor_line > 0:
                # Move to end of previous line
                self.cursor_line -= 1
                self.cursor_pos = 31  # Last position in line (15 bytes * 2 hex digits)
                self.update_content()
                self.scroll_to_cursor()
        elif event.key == "right":
            max_pos_in_line = min(31, (total_bytes - self.cursor_line * 16) * 2 - 1)
            if self.cursor_pos < max_pos_in_line:
                self.cursor_pos += 1
                self.update_content()
            elif self.cursor_line < total_lines - 1:
                # Move to beginning of next line
                self.cursor_line += 1
                self.cursor_pos = 0
                self.update_content()
                self.scroll_to_cursor()
        elif event.key == "up":
            if self.cursor_line > 0:
                self.cursor_line -= 1
                # Keep same position within line, but clamp to line bounds
                max_pos_in_line = min(31, (total_bytes - self.cursor_line * 16) * 2 - 1)
                self.cursor_pos = min(self.cursor_pos, max_pos_in_line)
                self.update_content()
                self.scroll_to_cursor()
        elif event.key == "down":
            if self.cursor_line < total_lines - 1:
                self.cursor_line += 1
                # Keep same position within line, but clamp to line bounds
                max_pos_in_line = min(31, (total_bytes - self.cursor_line * 16) * 2 - 1)
                self.cursor_pos = min(self.cursor_pos, max_pos_in_line)
                self.update_content()
                self.scroll_to_cursor()
        elif event.key in "0123456789abcdefABCDEF":
            # Calculate absolute position in hex string
            abs_pos = self.cursor_line * 32 + self.cursor_pos
            if abs_pos < len(self.working_hex_str):
                # Edit the current digit in working copy
                new_hex = (
                    self.working_hex_str[:abs_pos] + event.key.lower() + self.working_hex_str[abs_pos+1:]
                )
                self.working_hex_str = new_hex
                # Move cursor right
                max_pos_in_line = min(31, (len(self.working_hex_str) // 2 - self.cursor_line * 16) * 2 - 1)
                if self.cursor_pos < max_pos_in_line:
                    self.cursor_pos += 1
                elif self.cursor_line < total_lines - 1:
                    # Move to beginning of next line
                    self.cursor_line += 1
                    self.cursor_pos = 0
                self.update_content()
                # Only scroll if we moved to a new line
                if self.cursor_pos == 0 and self.cursor_line > 0:
                    self.scroll_to_cursor()
        elif event.key == "enter":
            # Apply changes to the actual packet
            if self.working_hex_str and self.working_hex_str != self.hex_str:
                try:
                    new_bytes = binascii.unhexlify(self.working_hex_str)
                    # Update the packet in the main app
                    if self.on_edit_callback:
                        self.on_edit_callback(new_bytes)
                        self.log(f"Packet updated: {new_bytes}")
                except Exception as e:
                    self.log(f"Error updating packet: {e}")
                    # Revert working hex string on error
                    self.working_hex_str = self.hex_str
                    self.update_content()
        elif event.key == "escape":
            # Discard changes and revert to original
            if self.working_hex_str != self.hex_str:
                self.working_hex_str = self.hex_str
                self.update_content()
        elif event.key == "page_up":
            # Page up - move cursor up by visible lines
            if self.cursor_line >= self.visible_lines:
                self.cursor_line -= self.visible_lines
            else:
                self.cursor_line = 0
            self.update_content()
            self.scroll_to_cursor()
        elif event.key == "page_down":
            # Page down - move cursor down by visible lines
            self.cursor_line = min(self.cursor_line + self.visible_lines, total_lines - 1)
            self.update_content()
            self.scroll_to_cursor() 