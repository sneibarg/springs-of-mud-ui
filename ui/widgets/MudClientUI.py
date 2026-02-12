from collections import deque
from input.TextInput import TextInput
from ui.layout.Layout import Layout
from ui.widgets.MenuBar import MenuBar
from ui.panes.ConnectionSettingsPane import ConnectionSettingsPane

import pyxel


class MudClientUI:
    def __init__(self) -> None:
        self.l = Layout()
        pyxel.init(self.l.w, self.l.h, title="Pyxel MUD Client (graphics + ui)", fps=60, display_scale=3)
        pyxel.mouse(True)

        self.input = TextInput()
        self.scrollback: deque[str] = deque(maxlen=500)
        self.menu_bar = MenuBar(x=0, y=0, width=self.l.w, height=10)

        settings_menu = self.menu_bar.add_menu("Settings")
        settings_menu.add_item("Connections", self.show_connection_settings)

        pane_width = min(300, self.l.w - 40)
        pane_height = 180
        pane_x = (self.l.w - pane_width) // 2
        pane_y = (self.l.h - pane_height) // 2
        self.connection_settings = ConnectionSettingsPane(pane_x, pane_y, pane_width, pane_height)

        self.player_x = self.l.game_w // 2
        self.player_y = self.l.game_h // 2

        self.log("Connected (demo). Type 'help' and press Enter.")
        self.log("Left pane is your render surface; right pane is scrollback + input.")

        pyxel.run(self.update, self.draw)  # :contentReference[oaicite:2]{index=2}

    def show_connection_settings(self) -> None:
        self.connection_settings.show()

    def log(self, msg: str) -> None:
        chars_per_line = max(10, (self.l.ui_w - 8) // 4)  # Pyxel font is small; 4px/char is a decent heuristic
        for line in msg.splitlines() or [""]:
            while len(line) > chars_per_line:
                self.scrollback.append(line[:chars_per_line])
                line = line[chars_per_line:]
            self.scrollback.append(line)

    def handle_command(self, cmd: str) -> None:
        # Placeholder: in your architecture, enqueue to your Python/Java networking layer here.
        self.log(f"> {cmd}")

        if cmd == "help":
            self.log("Commands: help, look, say <msg>, move <n/s/e/w>")
        elif cmd == "look":
            self.log("You are in a featureless demo room. (Hook this to your MUD world state.)")
        elif cmd.startswith("say "):
            self.log(f'You say, "{cmd[4:]}"')
        elif cmd.startswith("move "):
            self.log(f"You attempt to move {cmd[5:]}. (Wire to server; update left-pane camera.)")
        else:
            self.log("Unknown command. Type 'help'.")

    def update(self) -> None:
        self.menu_bar.update()
        self.connection_settings.update()

        if self.connection_settings.visible:
            return

        if pyxel.btn(pyxel.KEY_W):
            self.player_y -= 1
        if pyxel.btn(pyxel.KEY_S):
            self.player_y += 1
        if pyxel.btn(pyxel.KEY_A):
            self.player_x -= 1
        if pyxel.btn(pyxel.KEY_D):
            self.player_x += 1

        self.player_x = max(0, min(self.l.game_w - 1, self.player_x))
        self.player_y = max(0, min(self.l.game_h - 1, self.player_y))

        cmd = self.input.update()
        if cmd is not None:
            self.handle_command(cmd)

    def draw(self) -> None:
        pyxel.cls(0)

        self.draw_game_pane()
        self.draw_text_pane()

        pyxel.rect(self.l.game_w, 10, self.l.gutter, self.l.h - 10, 5)

        # Draw menu bar on top of game panes
        self.menu_bar.draw()

        # Draw connection settings on top of everything
        self.connection_settings.draw()

        # Draw custom cursor last
        self.draw_custom_cursor()

    def draw_game_pane(self) -> None:
        pyxel.clip(self.l.game_x, 10, self.l.game_w, self.l.game_h - 10)

        for y in range(10, self.l.game_h, 8):
            for x in range(0, self.l.game_w, 8):
                col = 1 if ((x // 8 + y // 8) % 2 == 0) else 2
                pyxel.rect(x, y, 8, 8, col)

        pyxel.circ(self.player_x, self.player_y + 10, 3, 10)
        pyxel.text(4, 14, "GAME PANE (WASD demo)", 7)
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
        line_h = 7
        max_lines = max(1, scroll_h // line_h)
        lines = list(self.scrollback)[-max_lines:]
        y = scroll_y0 + (scroll_h - len(lines) * line_h)
        for line in lines:
            pyxel.text(x0 + pad, y, line, 7)
            y += line_h

        box_y = self.l.h - input_h
        pyxel.rect(x0, box_y, self.l.ui_w, input_h, 1)
        pyxel.rectb(x0 + 1, box_y + 1, self.l.ui_w - 2, input_h - 2, 5)

        prompt = "> "
        pyxel.text(x0 + pad, box_y + 5, prompt + self.input.buf, 7)

        if (pyxel.frame_count // 20) % 2 == 0:
            cursor_x = x0 + pad + 4 * (len(prompt) + self.input.cursor)
            pyxel.rect(cursor_x, box_y + 12, 3, 1, 7)

        pyxel.clip()

    def draw_custom_cursor(self) -> None:
        mx, my = pyxel.mouse_x, pyxel.mouse_y

        # Simple larger arrow cursor with outline
        # Outline
        pyxel.line(mx - 1, my, mx - 1, my + 9, 0)
        pyxel.line(mx + 1, my, mx + 1, my + 9, 0)
        pyxel.line(mx, my - 1, mx + 6, my + 5, 0)
        pyxel.line(mx, my + 1, mx + 6, my + 7, 0)
        pyxel.line(mx, my + 9, mx + 4, my + 7, 0)

        # Main cursor
        pyxel.line(mx, my, mx, my + 8, 7)
        pyxel.line(mx, my, mx + 5, my + 5, 7)
        pyxel.line(mx, my + 8, mx + 3, my + 6, 7)

        # Fill
        pyxel.line(mx + 1, my + 3, mx + 3, my + 5, 10)
        pyxel.line(mx + 1, my + 4, mx + 2, my + 5, 10)