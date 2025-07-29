from textual.widgets import Static
from textual import events

class FocusablePanel(Static):
    can_focus = True # Allow focus switching with Tab#
    def on_focus(self, event: events.Focus) -> None:
        self.styles.border = ("double", "lightgreen")
        self.refresh()
    def on_blur(self, event: events.Blur) -> None:
        self.styles.border = ("round", "orange")
        self.refresh()
    def on_descendant_blur(self, event: events.DescendantBlur) -> None:
        self.on_blur(event)
    def on_descendant_focus(self, event: events.DescendantFocus) -> None:
        self.on_focus(event) 