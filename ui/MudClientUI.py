from __future__ import annotations
from collections import deque
from component.app.GameWorld import GameWorld
from component.input.TextInput import TextInput
from component.menu import MenuBar
from component.MessageDialog import MessageDialog
from component.render import CursorRenderer, TextRenderer
from component.app.ModalGate import ModalGate
from component.app.TextPane import TextPaneComponent
from component.app.InputCommand import InputCommand
from component.app.Divider import Divider
from component.app.UIOverlay import UIOverlay
from component.app.Cursor import Cursor
from engine.MudClientApp import MudClientApp
from net.telnet.TelnetClient import TelnetClient, TelnetConfig
from ui.layout.Layout import Layout
from ui.panes.ConnectionSettings import ConnectionSettings
from ui.panes.DisplaySettings import DisplaySettings

import time


class MudClientUI:
    def __init__(self) -> None:
        self._telnet_host:str = "localhost"
        self._telnet_port: int = 6969
        self._telnet: TelnetClient | None = None
        self.text_font_name = None
        self.layout = Layout()
        self.settings = DisplaySettings(0, 0, 100, 100, None, None)
        self.layout.game_w = int(self.settings.game_pane_width)
        self.layout.ui_w = int(self.settings.text_pane_width)
        self.layout.h = int(self.settings.window_height)
        self.layout.game_h = int(self.settings.window_height)
        self.text_input = TextInput(max_len=2000)
        self.scroll_buffer_size = int(self.settings.scroll_buffer)
        self.scrollback: deque[str] = deque(maxlen=self.scroll_buffer_size)
        self.menu_bar = MenuBar(x=0, y=0, width=self.layout.w, height=10)

        file_menu = self.menu_bar.add_menu("File")
        file_menu.add_item("Close", self.close_app)
        settings_menu = self.menu_bar.add_menu("Settings")
        settings_menu.add_item("Connections", self.show_connection_settings)
        settings_menu.add_item("Display", self.show_display_settings)
        pane_width = min(300, self.layout.w - 40)
        pane_height = 300
        pane_x = (self.layout.w - pane_width) // 2
        pane_y = (self.layout.h - pane_height) // 2

        self.message_dialog = MessageDialog()
        self.connection_settings = ConnectionSettings(pane_x, pane_y, pane_width, pane_height, self.message_dialog)

        display_pane_height = min(380, self.layout.h - 20)
        display_pane_y = max(10, (self.layout.h - display_pane_height) // 2)

        self.display_settings = DisplaySettings(pane_x, display_pane_y, pane_width, display_pane_height, self.message_dialog, self)

        self.chars_per_line = int(self.display_settings.chars_per_line)
        self.visible_lines = int(self.display_settings.visible_lines)
        self.font_scale = int(self.display_settings.font_scale)
        self.line_spacing = int(self.display_settings.line_spacing)

        self.scroll_offset = 0
        self.app = MudClientApp(title="Pyxel MUD Client (graphics + ui)",
                                layout=self.layout,
                                text_input=self.text_input,
                                scrollback=self.scrollback,
                                scroll_offset=self.scroll_offset,
                                visible_lines=self.visible_lines,
                                line_spacing=self.line_spacing,
                                font_scale=self.font_scale)

        text_renderer = TextRenderer()
        cursor_renderer = CursorRenderer()
        gate = ModalGate([self.connection_settings, self.display_settings, self.message_dialog])

        self.app.add(GameWorld())
        self.app.add(TextPaneComponent(text_renderer=text_renderer))
        self.app.add(Divider())
        self.app.add(InputCommand(gate=gate, on_command=self.handle_command))
        self.app.add(UIOverlay(menu_bar=self.menu_bar, message_dialog=self.message_dialog,
                                        connection_settings=self.connection_settings, display_settings=self.display_settings))
        self.app.add(Cursor(cursor_renderer=cursor_renderer))

        self.log("Connected. Type 'help' and press Enter.")
        self.log("Left pane is your render surface; right pane is scrollback + clipboard.")
        self.log(f"Scroll buffer initialized: {self.scrollback.maxlen} lines")
        self.log(f"Text wrapping at: {self.chars_per_line} chars per line")
        self.log(f"Text pane width: {self.layout.ui_w}px (~{self.layout.ui_w // 4} chars visible)")

        self.app.run()

    def show_connection_settings(self) -> None:
        self.connection_settings.show()

    def show_display_settings(self) -> None:
        self.display_settings.show()

    def close_app(self) -> None:
        self.app._ctx.quit()

    def apply_display_settings(self, chars_per_line: int, visible_lines: int, font_scale: int, line_spacing: int,
                               window_height: int = None, scroll_buffer: int = None, game_pane_width: int = None,
                               text_pane_width: int = None, font_name: str = None) -> None:
        self.chars_per_line = chars_per_line
        self.visible_lines = visible_lines
        self.font_scale = font_scale
        self.line_spacing = line_spacing
        self.text_input.max_len = 2000

        if scroll_buffer and scroll_buffer != self.scrollback.maxlen:
            old = list(self.scrollback)
            self.scrollback = deque(old, maxlen=scroll_buffer)
            self.app.set_scrollback(self.scrollback)

        if window_height and window_height != self.layout.h:
            self.layout.h = window_height
            self.layout.game_h = window_height
            # requires restart for pyxel.init resize; keep your “restart for full effect” message

        if game_pane_width:
            self.layout.game_w = game_pane_width

        if text_pane_width:
            self.layout.ui_w = text_pane_width

        if font_name:
            self.text_font_name = font_name

        self.app.set_text_metrics(visible_lines=self.visible_lines, line_spacing=self.line_spacing, font_scale=self.font_scale)
        self.log(f"Settings applied: {chars_per_line} chars/line, game_w={game_pane_width}px, text_w={text_pane_width}px")

    def log(self, msg: str) -> None:
        chars_per_line = self.chars_per_line
        for line in msg.splitlines() or [""]:
            while len(line) > chars_per_line:
                self.scrollback.append(line[:chars_per_line])
                line = line[chars_per_line:]
            self.scrollback.append(line)

    def handle_command(self, cmd: str) -> None:
        self.log(f"> {cmd}")

        parts = cmd.strip().split()
        if not parts:
            return

        verb = parts[0].lower()
        if verb == "help":
            self.log("Commands: help, list, logon <name>, quit")
            return

        if verb == "list":
            self.log(" ")
            for character in self.app._character_list:
                self.log(f"- {character.name}")
            return

        if verb == "logon":
            if len(parts) < 2:
                self.log("Usage: logon <characterName>")
                return

            char_name = parts[1]
            try:
                t = self._ensure_telnet()
                self._session_character = char_name
                self.log(f"Starting session for '{char_name}'...")
                t.send_line(f"logon {char_name}")

            except Exception as e:
                self.log(f"Logon failed: {e}")
            return

        if verb == "quit":
            self.log("Quitting the game. Goodbye!")
            time.sleep(0.5)
            self.close_app()
            return

        if self._telnet and self._telnet.connected:
            try:
                self._telnet.send_line(cmd)
            except Exception as e:
                self.log(f"Send failed: {e}")
        else:
            self.log("Unknown command. Type 'help'. (Not connected to telnet session.)")

    def _ensure_telnet(self) -> TelnetClient:
        if self._telnet is None:
            self._telnet = TelnetClient(TelnetConfig(host=self._telnet_host, port=self._telnet_port), on_status=self.log)
        if not self._telnet.connected:
            self._telnet.connect()
        return self._telnet

