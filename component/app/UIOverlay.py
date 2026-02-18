from __future__ import annotations
from dataclasses import dataclass

from component.menu import MenuBar
from component.MessageDialog import MessageDialog
from ui.panes.ConnectionSettingsPane import ConnectionSettingsPane
from ui.panes.DisplaySettingsPane import DisplaySettingsPane


@dataclass
class UIOverlay:
    menu_bar: MenuBar
    message_dialog: MessageDialog
    connection_settings: ConnectionSettingsPane
    display_settings: DisplaySettingsPane
    z_index: int = 30

    def update(self, ctx) -> None:
        self.menu_bar.update(ctx)
        self.message_dialog.update(ctx)
        self.connection_settings.update(ctx)
        self.display_settings.update(ctx)

    def draw(self, ctx) -> None:
        self.menu_bar.draw(ctx)
        self.connection_settings.draw(ctx)
        self.display_settings.draw(ctx)
        self.message_dialog.draw(ctx)
