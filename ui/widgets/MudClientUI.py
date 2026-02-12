from collections import deque
from input.TextInput import TextInput
from ui.layout.Layout import Layout

import pyxel


class MudClientUI:
    def __init__(self) -> None:
        self.l = Layout()
        pyxel.init(self.l.w, self.l.h, title="Pyxel MUD Client (graphics + ui)", fps=60, display_scale=3)  # :contentReference[oaicite:1]{index=1}

        self.input = TextInput()
        self.scrollback: deque[str] = deque(maxlen=500)

        # Demo state for the left pane
        self.player_x = self.l.game_w // 2
        self.player_y = self.l.game_h // 2

        # Seed some output
        self.log("Connected (demo). Type 'help' and press Enter.")
        self.log("Left pane is your render surface; right pane is scrollback + input.")

        pyxel.run(self.update, self.draw)  # :contentReference[oaicite:2]{index=2}

    def log(self, msg: str) -> None:
        # naive wrap to keep UI readable
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
        # Demo movement in the left pane (WASD)
        if pyxel.btn(pyxel.KEY_W):
            self.player_y -= 1
        if pyxel.btn(pyxel.KEY_S):
            self.player_y += 1
        if pyxel.btn(pyxel.KEY_A):
            self.player_x -= 1
        if pyxel.btn(pyxel.KEY_D):
            self.player_x += 1

        # Clamp to game pane
        self.player_x = max(0, min(self.l.game_w - 1, self.player_x))
        self.player_y = max(0, min(self.l.game_h - 1, self.player_y))

        # Text input
        cmd = self.input.update()
        if cmd is not None:
            self.handle_command(cmd)

    def draw(self) -> None:
        pyxel.cls(0)

        # Vertical separator
        pyxel.rect(self.l.game_w, 0, self.l.gutter, self.l.h, 5)

        self.draw_game_pane()
        self.draw_text_pane()

    def draw_game_pane(self) -> None:
        # Constrain drawing to game pane
        pyxel.clip(self.l.game_x, 0, self.l.game_w, self.l.game_h)

        # Simple checkered background
        for y in range(0, self.l.game_h, 8):
            for x in range(0, self.l.game_w, 8):
                col = 1 if ((x // 8 + y // 8) % 2 == 0) else 2
                pyxel.rect(x, y, 8, 8, col)

        # Player marker
        pyxel.circ(self.player_x, self.player_y, 3, 10)
        pyxel.text(4, 4, "GAME PANE (WASD demo)", 7)

        pyxel.clip()  # reset

    def draw_text_pane(self) -> None:
        x0 = self.l.ui_x
        pyxel.clip(x0, 0, self.l.ui_w, self.l.h)

        # Pane background + title bar
        pyxel.rect(x0, 0, self.l.ui_w, self.l.h, 0)
        pyxel.rect(x0, 0, self.l.ui_w, 9, 1)
        pyxel.text(x0 + 4, 2, "TEXT / COMMAND", 7)

        # Scrollback area
        pad = 4
        input_h = 16
        scroll_y0 = 10
        scroll_h = self.l.h - scroll_y0 - input_h

        # draw scrollback ui from bottom up
        line_h = 7
        max_lines = max(1, scroll_h // line_h)
        lines = list(self.scrollback)[-max_lines:]
        y = scroll_y0 + (scroll_h - len(lines) * line_h)
        for line in lines:
            pyxel.text(x0 + pad, y, line, 7)
            y += line_h

        # Input box
        box_y = self.l.h - input_h
        pyxel.rect(x0, box_y, self.l.ui_w, input_h, 1)
        pyxel.rectb(x0 + 1, box_y + 1, self.l.ui_w - 2, input_h - 2, 5)

        prompt = "> "
        pyxel.text(x0 + pad, box_y + 5, prompt + self.input.buf, 7)

        # Cursor (blink)
        if (pyxel.frame_count // 20) % 2 == 0:
            cursor_x = x0 + pad + 4 * (len(prompt) + self.input.cursor)
            pyxel.rect(cursor_x, box_y + 12, 3, 1, 7)

        pyxel.clip()  # reset