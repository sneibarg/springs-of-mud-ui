import time
import pyxel

from collections import deque
from component.input.TextInput import TextInput
from ui.layout.Layout import Layout
from component.menu.MenuBar import MenuBar
from component.MessageDialog import MessageDialog
from ui.panes.ConnectionSettingsPane import ConnectionSettingsPane
from ui.panes.DisplaySettingsPane import DisplaySettingsPane
from component.render.TextRenderer import TextRenderer
from component.render.CursorRenderer import CursorRenderer


class MudClientUI:
    def __init__(self) -> None:
        self.text_font_name = None
        self.layout = Layout()

        temp_settings = DisplaySettingsPane(0, 0, 100, 100, None, None)
        self.layout.game_w = int(temp_settings.game_pane_width)
        self.layout.ui_w = int(temp_settings.text_pane_width)
        self.layout.h = int(temp_settings.window_height)
        self.layout.game_h = int(temp_settings.window_height)

        pyxel.init(self.layout.w, self.layout.h, title="Pyxel MUD Client (graphics + ui)", fps=60, display_scale=3)
        pyxel.mouse(True)

        self.text_renderer = TextRenderer()
        self.cursor_renderer = CursorRenderer()
        self.input = TextInput(max_len=2000)
        self.scrollback: deque[str] = deque(maxlen=500)

        self.menu_bar = MenuBar(x=0, y=0, width=self.layout.w, height=10)
        settings_menu = self.menu_bar.add_menu("Settings")
        settings_menu.add_item("Connections", self.show_connection_settings)
        settings_menu.add_item("Display", self.show_display_settings)

        pane_width = min(300, self.layout.w - 40)
        pane_height = 180
        pane_x = (self.layout.w - pane_width) // 2
        pane_y = (self.layout.h - pane_height) // 2

        self.message_dialog = MessageDialog()
        self.connection_settings = ConnectionSettingsPane(pane_x, pane_y, pane_width, pane_height, self.message_dialog, self)

        # Display settings pane needs more height for all fields (now includes pane width settings)
        display_pane_height = min(380, self.layout.h - 20)
        display_pane_y = max(10, (self.layout.h - display_pane_height) // 2)

        self.display_settings = DisplaySettingsPane(pane_x, display_pane_y, pane_width, display_pane_height, self.message_dialog, self)
        self.character_list = []

        # Display settings - load from display_settings pane
        self.chars_per_line = int(self.display_settings.chars_per_line)
        self.visible_lines = int(self.display_settings.visible_lines)
        self.font_scale = self.display_settings.font_scale
        self.line_spacing = self.display_settings.line_spacing

        # Recreate scrollback with correct buffer size from settings
        scroll_buffer_size = int(self.display_settings.scroll_buffer)
        self.scrollback = deque(maxlen=scroll_buffer_size)

        # Scrollback control
        self.scroll_offset = 0  # 0 = bottom (most recent), positive = scrolled up

        self.log("Connected. Type 'help' and press Enter.")
        self.log("Left pane is your render surface; right pane is scrollback + clipboard.")
        self.log(f"Scroll buffer initialized: {self.scrollback.maxlen} lines")
        self.log(f"Text wrapping at: {self.chars_per_line} chars per line")
        self.log(f"Text pane width: {self.layout.ui_w}px (~{self.layout.ui_w // 4} chars visible)")

        pyxel.run(self.update, self.draw)

    def show_connection_settings(self) -> None:
        self.connection_settings.show()

    def show_display_settings(self) -> None:
        self.display_settings.show()

    def update_character_list(self, characters) -> None:
        self.character_list = characters
        if characters:
            self.log(f"Character list updated: {len(characters)} character(s) available.")

    def apply_display_settings(self, chars_per_line: int, visible_lines: int, font_scale: int, line_spacing: int,
                               window_height: int = None, scroll_buffer: int = None, game_pane_width: int = None,
                               text_pane_width: int = None, font_name: str = None) -> None:
        self.chars_per_line = chars_per_line
        self.visible_lines = visible_lines
        self.font_scale = font_scale
        self.line_spacing = line_spacing
        self.input.max_len = 2000

        if scroll_buffer and scroll_buffer != self.scrollback.maxlen:
            old_messages = list(self.scrollback)
            self.scrollback = deque(old_messages, maxlen=scroll_buffer)

        if window_height and window_height != self.layout.h:
            self.layout.h = window_height
            self.layout.game_h = window_height

        if game_pane_width:
            self.layout.game_w = game_pane_width

        if text_pane_width:
            self.layout.ui_w = text_pane_width

        if font_name:
            self.text_font_name = font_name

        self.log(
            f"Settings applied: {chars_per_line} chars/line, game_w={game_pane_width}px, text_w={text_pane_width}px")

    def log(self, msg: str) -> None:
        chars_per_line = self.chars_per_line
        for line in msg.splitlines() or [""]:
            while len(line) > chars_per_line:
                self.scrollback.append(line[:chars_per_line])
                line = line[chars_per_line:]
            self.scrollback.append(line)

    def handle_command(self, cmd: str) -> None:
        self.log(f"> {cmd}")

        if cmd == "help":
            self.log("Commands: help, list, logon, quit")
        elif cmd == "logon":
            self.log("You must pass a valid player character name to the logon command.")
        elif cmd == "list":
            if not self.character_list:
                self.log("No characters available. Please connect to the server first.")
            else:
                self.log("Available characters:")
                for char in self.character_list:
                    self.log(f"  - {char.name}")
        elif cmd == "quit":
            self.log("Quitting the game. Goodbye!")
            time.sleep(1.5)
            pyxel.quit()
        else:
            self.log("Unknown command. Type 'help'.")

    def update(self) -> None:
        self.menu_bar.update()
        self.message_dialog.update()

        mx, my = pyxel.mouse_x, pyxel.mouse_y
        click = pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT)
        self.connection_settings.update(mx, my, click)

        self.display_settings.update()

        if self.connection_settings.visible or self.message_dialog.visible or self.display_settings.visible:
            return

        mx, my = pyxel.mouse_x, pyxel.mouse_y
        if self.layout.ui_x <= mx < self.layout.ui_x + self.layout.ui_w and 10 <= my < self.layout.h:
            if pyxel.mouse_wheel > 0:
                self.scroll_offset = min(self.scroll_offset + 3, max(0, len(self.scrollback) - 1))
            elif pyxel.mouse_wheel < 0:
                self.scroll_offset = max(0, self.scroll_offset - 3)

        cmd = self.input.update()
        if cmd is not None:
            self.scroll_offset = 0
            self.handle_command(cmd)

    def draw(self) -> None:
        pyxel.cls(0)

        self.draw_game_pane()
        self.text_renderer.draw(
            x0=self.layout.ui_x,
            y0=10,
            w=self.layout.ui_w,
            h=self.layout.h - 10,
            title="TEXT / COMMAND",
            scrollback=self.scrollback,
            scroll_offset=self.scroll_offset,
            visible_lines=self.visible_lines,
            line_spacing=self.line_spacing,
            font_scale=self.font_scale,
            prompt="> ",
            input_buf=self.input.buf,
            input_cursor=self.input.cursor,
            has_selection=self.input.has_selection(),
            selection_start=self.input.selection_start,
            selection_end=self.input.selection_end,
            blink_on=((pyxel.frame_count // 20) % 2 == 0),
        )

        pyxel.rect(self.layout.game_w, 10, self.layout.gutter, self.layout.h - 10, 5)

        self.menu_bar.draw()
        self.connection_settings.draw()
        self.display_settings.draw()
        self.message_dialog.draw()

        self.cursor_renderer.draw()

    def draw_game_pane(self) -> None:
        pyxel.clip(self.layout.game_x, 10, self.layout.game_w, self.layout.game_h - 10)

        for y in range(10, self.layout.game_h, 8):
            for x in range(0, self.layout.game_w, 8):
                col = 1 if ((x // 8 + y // 8) % 2 == 0) else 2
                pyxel.rect(x, y, 8, 8, col)

        pyxel.clip()
