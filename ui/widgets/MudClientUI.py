import time

import pyxel

from collections import deque
from input.TextInput import TextInput
from ui.layout.Layout import Layout
from ui.widgets.MenuBar import MenuBar
from ui.widgets.MessageDialog import MessageDialog
from ui.panes.ConnectionSettingsPane import ConnectionSettingsPane
from ui.panes.DisplaySettingsPane import DisplaySettingsPane


class MudClientUI:
    def __init__(self) -> None:
        # Create layout - will be updated with saved settings
        self.l = Layout()

        # Load display settings to get saved pane widths BEFORE initializing pyxel
        from ui.panes.DisplaySettingsPane import DisplaySettingsPane
        temp_settings = DisplaySettingsPane(0, 0, 100, 100, None, None)
        self.l.game_w = int(temp_settings.game_pane_width)
        self.l.ui_w = int(temp_settings.text_pane_width)
        self.l.h = int(temp_settings.window_height)
        self.l.game_h = int(temp_settings.window_height)

        pyxel.init(self.l.w, self.l.h, title="Pyxel MUD Client (graphics + ui)", fps=60, display_scale=3)
        pyxel.mouse(True)

        # Allow very long input - wrapping happens in log display
        self.input = TextInput(max_len=2000)
        # Temporary scrollback - will be recreated with correct size after loading settings
        self.scrollback: deque[str] = deque(maxlen=500)
        self.menu_bar = MenuBar(x=0, y=0, width=self.l.w, height=10)

        settings_menu = self.menu_bar.add_menu("Settings")
        settings_menu.add_item("Connections", self.show_connection_settings)
        settings_menu.add_item("Display", self.show_display_settings)

        pane_width = min(300, self.l.w - 40)
        pane_height = 180
        pane_x = (self.l.w - pane_width) // 2
        pane_y = (self.l.h - pane_height) // 2

        self.message_dialog = MessageDialog()
        self.connection_settings = ConnectionSettingsPane(pane_x, pane_y, pane_width, pane_height, self.message_dialog, self)

        # Display settings pane needs more height for all fields (now includes pane width settings)
        display_pane_height = min(380, self.l.h - 20)  # Increased to fit all fields
        display_pane_y = max(10, (self.l.h - display_pane_height) // 2)
        self.display_settings = DisplaySettingsPane(pane_x, display_pane_y, pane_width, display_pane_height, self.message_dialog, self)

        self.player_x = self.l.game_w // 2
        self.player_y = self.l.game_h // 2
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

        self.log("Connected (demo). Type 'help' and press Enter.")
        self.log("Left pane is your render surface; right pane is scrollback + input.")
        self.log(f"Scroll buffer initialized: {self.scrollback.maxlen} lines")
        self.log(f"Text wrapping at: {self.chars_per_line} chars per line")
        self.log(f"Text pane width: {self.l.ui_w}px (~{self.l.ui_w // 4} chars visible)")

        pyxel.run(self.update, self.draw)

    def show_connection_settings(self) -> None:
        self.connection_settings.show()

    def show_display_settings(self) -> None:
        self.display_settings.show()

    def update_character_list(self, characters) -> None:
        self.character_list = characters
        if characters:
            self.log(f"Character list updated: {len(characters)} character(s) available.")

    def apply_display_settings(self, chars_per_line: int, visible_lines: int, font_scale: int, line_spacing: int, window_height: int = None, scroll_buffer: int = None, game_pane_width: int = None, text_pane_width: int = None) -> None:
        # Update settings
        self.chars_per_line = chars_per_line
        self.visible_lines = visible_lines
        self.font_scale = font_scale
        self.line_spacing = line_spacing

        # Keep input max length large - wrapping happens in display
        # Don't limit typing length to chars_per_line
        self.input.max_len = 2000  # Allow very long commands

        # Update scroll buffer size
        if scroll_buffer and scroll_buffer != self.scrollback.maxlen:
            # Save existing messages
            old_messages = list(self.scrollback)
            # Create new deque with new size
            self.scrollback = deque(old_messages, maxlen=scroll_buffer)

        # Update layout dimensions (requires restart for full effect)
        if window_height and window_height != self.l.h:
            self.l.h = window_height
            self.l.game_h = window_height

        if game_pane_width:
            self.l.game_w = game_pane_width

        if text_pane_width:
            self.l.ui_w = text_pane_width

        self.log(f"Settings applied: {chars_per_line} chars/line, game_w={game_pane_width}px, text_w={text_pane_width}px")

    def log(self, msg: str) -> None:
        chars_per_line = self.chars_per_line
        for line in msg.splitlines() or [""]:
            # Wrap line if it exceeds chars_per_line
            while len(line) > chars_per_line:
                self.scrollback.append(line[:chars_per_line])
                line = line[chars_per_line:]
            # Append remaining line (could be empty, partial, or full line)
            if line or not msg:  # Always append at least one line
                self.scrollback.append(line)

    def handle_command(self, cmd: str) -> None:
        # Placeholder: in your architecture, enqueue to your Python/Java networking layer here.
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
        elif cmd.split()[0] == "logon" and cmd.split()[1] in self.character_list:
            self.log(f"Logging you onto the server as your existing player character {cmd.split()[1]}...")
        elif cmd == "quit":
            self.log("Quitting the game. Goodbye!")
            time.sleep(1.5)
            pyxel.quit()
        else:
            self.log("Unknown command. Type 'help'.")

    def update(self) -> None:
        self.menu_bar.update()
        self.message_dialog.update()
        self.connection_settings.update()
        self.display_settings.update()

        if self.connection_settings.visible or self.message_dialog.visible or self.display_settings.visible:
            return

        # Handle mouse wheel scrolling in text pane (using mouse wheel value)
        mx, my = pyxel.mouse_x, pyxel.mouse_y
        if self.l.ui_x <= mx < self.l.ui_x + self.l.ui_w and 10 <= my < self.l.h:
            # Pyxel uses mouse_wheel: positive = scroll up, negative = scroll down
            if pyxel.mouse_wheel > 0:
                # Allow scrolling through entire scrollback buffer
                self.scroll_offset = min(self.scroll_offset + 3, len(self.scrollback) - 1)
            elif pyxel.mouse_wheel < 0:
                self.scroll_offset = max(0, self.scroll_offset - 3)

        # if pyxel.btn(pyxel.KEY_W):
        #     self.player_y -= 1
        # if pyxel.btn(pyxel.KEY_S):
        #     self.player_y += 1
        # if pyxel.btn(pyxel.KEY_A):
        #     self.player_x -= 1
        # if pyxel.btn(pyxel.KEY_D):
        #     self.player_x += 1

        # self.player_x = max(0, min(self.l.game_w - 1, self.player_x))
        # self.player_y = max(0, min(self.l.game_h - 1, self.player_y))

        cmd = self.input.update()
        if cmd is not None:
            self.scroll_offset = 0  # Auto-scroll to bottom on new input
            self.handle_command(cmd)

    def draw(self) -> None:
        pyxel.cls(0)

        self.draw_game_pane()
        self.draw_text_pane()

        pyxel.rect(self.l.game_w, 10, self.l.gutter, self.l.h - 10, 5)

        self.menu_bar.draw()
        self.connection_settings.draw()
        self.display_settings.draw()
        self.message_dialog.draw()
        self.draw_custom_cursor()

    def draw_game_pane(self) -> None:
        pyxel.clip(self.l.game_x, 10, self.l.game_w, self.l.game_h - 10)

        for y in range(10, self.l.game_h, 8):
            for x in range(0, self.l.game_w, 8):
                col = 1 if ((x // 8 + y // 8) % 2 == 0) else 2
                pyxel.rect(x, y, 8, 8, col)

        pyxel.circ(self.player_x, self.player_y + 10, 3, 10)
        # pyxel.text(4, 14, "GAME PANE (WASD demo)", 7)
        pyxel.clip()

    def draw_text_pane(self) -> None:
        x0 = self.l.ui_x
        pyxel.clip(x0, 10, self.l.ui_w, self.l.h - 10)

        pyxel.rect(x0, 10, self.l.ui_w, self.l.h - 10, 0)
        pyxel.rect(x0, 10, self.l.ui_w, 9, 1)
        pyxel.text(x0 + 4, 12, "TEXT / COMMAND", 7)

        pad = 4
        input_h = 16
        scroll_y0 = 20
        scroll_h = self.l.h - scroll_y0 - input_h
        line_h = self.line_spacing
        max_lines = min(self.visible_lines, max(1, scroll_h // line_h))

        # Apply scroll offset
        total_lines = len(self.scrollback)
        if self.scroll_offset > 0:
            # Scrolled up - show older messages
            end_idx = total_lines - self.scroll_offset
            start_idx = max(0, end_idx - max_lines)
            lines = list(self.scrollback)[start_idx:end_idx]
        else:
            # At bottom - show most recent
            lines = list(self.scrollback)[-max_lines:]

        y = scroll_y0 + (scroll_h - len(lines) * line_h)

        # Apply font scale by drawing text multiple times with offsets
        if self.font_scale > 1:
            for line in lines:
                # Draw text with "bold" effect by drawing multiple times
                for dx in range(self.font_scale):
                    for dy in range(self.font_scale):
                        if dx == 0 and dy == 0:
                            # Main text
                            pyxel.text(x0 + pad, y, line, 7)
                        else:
                            # Shadow/bold effect
                            pyxel.text(x0 + pad + dx, y + dy, line, 7)
                y += line_h * self.font_scale
        else:
            # Normal rendering without scaling
            for line in lines:
                pyxel.text(x0 + pad, y, line, 7)
                y += line_h

        box_y = self.l.h - input_h
        pyxel.rect(x0, box_y, self.l.ui_w, input_h, 1)
        pyxel.rectb(x0 + 1, box_y + 1, self.l.ui_w - 2, input_h - 2, 5)

        prompt = "> "
        prompt_width = len(prompt) * 4
        input_box_width = self.l.ui_w - (pad * 2) - prompt_width

        # Calculate visible portion of text (horizontal scroll)
        max_visible_chars = input_box_width // 4
        cursor_pos = self.input.cursor

        # Scroll the view to keep cursor visible
        if cursor_pos < max_visible_chars:
            view_start = 0
        else:
            view_start = cursor_pos - max_visible_chars + 1

        visible_text = self.input.buf[view_start:view_start + max_visible_chars]

        # Draw prompt
        pyxel.text(x0 + pad, box_y + 5, prompt, 7)

        # Draw selection highlight if exists
        if self.input.has_selection():
            sel_start = min(self.input.selection_start, self.input.selection_end)
            sel_end = max(self.input.selection_start, self.input.selection_end)

            # Adjust for view window
            visible_sel_start = max(0, sel_start - view_start)
            visible_sel_end = min(len(visible_text), sel_end - view_start)

            if visible_sel_start < len(visible_text) and visible_sel_end > 0:
                sel_x = x0 + pad + prompt_width + visible_sel_start * 4
                sel_width = (visible_sel_end - visible_sel_start) * 4
                pyxel.rect(sel_x, box_y + 5, sel_width, 5, 12)  # Blue highlight

        # Draw visible text
        pyxel.text(x0 + pad + prompt_width, box_y + 5, visible_text, 7)

        # Draw cursor
        if (pyxel.frame_count // 20) % 2 == 0:
            visible_cursor = cursor_pos - view_start
            cursor_x = x0 + pad + prompt_width + visible_cursor * 4
            pyxel.rect(cursor_x, box_y + 12, 3, 1, 7)

        pyxel.clip()

    @staticmethod
    def draw_custom_cursor() -> None:
        mx, my = pyxel.mouse_x, pyxel.mouse_y

        def outline() -> None:
            pyxel.line(mx - 1, my, mx - 1, my + 9, 0)
            pyxel.line(mx + 1, my, mx + 1, my + 9, 0)
            pyxel.line(mx, my - 1, mx + 6, my + 5, 0)
            pyxel.line(mx, my + 1, mx + 6, my + 7, 0)
            pyxel.line(mx, my + 9, mx + 4, my + 7, 0)

        def main() -> None:
            pyxel.rect(mx - 1, my, 3, 9, 7)
            pyxel.line(mx, my, mx, my + 8, 7)
            pyxel.line(mx, my, mx + 5, my + 5, 7)
            pyxel.line(mx, my + 8, mx + 3, my + 6, 7)

        def fill() -> None:
            pyxel.line(mx + 1, my + 3, mx + 3, my + 5, 10)
            pyxel.line(mx + 1, my + 4, mx + 2, my + 5, 10)

        outline()
        main()
        fill()
