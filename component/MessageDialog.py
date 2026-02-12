import pyxel

from typing import Optional, Callable


class MessageDialog:
    def __init__(self):
        self.visible = False
        self.title = ""
        self.message = ""
        self.x = 0
        self.y = 0
        self.width = 200
        self.height = 100
        self.ok_button_hovered = False
        self.on_close: Optional[Callable] = None

    def show(self, title: str, message: str, on_close: Optional[Callable] = None) -> None:
        self.title = title
        self.message = message
        self.visible = True
        self.on_close = on_close

        self.x = (pyxel.width - self.width) // 2  # Center the dialog
        self.y = (pyxel.height - self.height) // 2

    def hide(self) -> None:
        self.visible = False
        if self.on_close:
            self.on_close()

    def update(self) -> None:
        if not self.visible:
            return

        mx, my = pyxel.mouse_x, pyxel.mouse_y
        ok_button_x = self.x + self.width // 2 - 20
        ok_button_y = self.y + self.height - 25

        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            if ok_button_x <= mx < ok_button_x + 40 and ok_button_y <= my < ok_button_y + 15:
                self.hide()

        self.ok_button_hovered = (ok_button_x <= mx < ok_button_x + 40 and ok_button_y <= my < ok_button_y + 15)
        if pyxel.btnp(pyxel.KEY_RETURN):
            self.hide()

    def draw(self) -> None:
        if not self.visible:
            return

        for y in range(0, pyxel.height, 2):
            for x in range(0, pyxel.width, 2):
                pyxel.pset(x, y, 0)

        def dialogue_background():
            pyxel.rect(self.x, self.y, self.width, self.height, 1)
            pyxel.rectb(self.x, self.y, self.width, self.height, 8)

        def title_bar():
            pyxel.rect(self.x, self.y, self.width, 15, 8)
            title_x = self.x + (self.width - len(self.title) * 4) // 2
            pyxel.text(title_x, self.y + 5, self.title, 7)

        dialogue_background()
        title_bar()

        self._draw_wrapped_text()

        ok_button_x = self.x + self.width // 2 - 20
        ok_button_y = self.y + self.height - 25

        btn_color = 11 if self.ok_button_hovered else 3
        pyxel.rect(ok_button_x, ok_button_y, 40, 15, btn_color)
        pyxel.rectb(ok_button_x, ok_button_y, 40, 15, 7)
        pyxel.text(ok_button_x + 14, ok_button_y + 5, "OK", 7)

    def _draw_wrapped_text(self) -> None:
        def draw_lines():
            text_y = self.y + 25
            for line in lines[:5]:
                pyxel.text(self.x + 10, text_y, line, 7)
                text_y += 8

        max_chars_per_line = (self.width - 20) // 4
        words = self.message.split()
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            if len(test_line) <= max_chars_per_line:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        draw_lines()
