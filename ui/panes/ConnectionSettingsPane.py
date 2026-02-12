import pyxel
from typing import Optional
from net.client.AuthClient import AuthClient


class ConnectionSettingsPane:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.visible = False
        self.server_url = "http://localhost:8169"
        self.account_name = ""
        self.password = ""
        self.password_visible = False
        self.active_field: Optional[str] = None  # "server", "account", "password"
        self.cursor_pos = 0
        self.status_message = ""
        self.status_color = 7
        self.auth_client = AuthClient()
        self.connect_button_hovered = False
        self.toggle_password_hovered = False

    def show(self) -> None:
        self.visible = True

    def hide(self) -> None:
        self.visible = False

    def toggle(self) -> None:
        self.visible = not self.visible

    def _handle_text_input(self, field: str, current_value: str, max_len: int = 100) -> str:
        result = current_value
        if pyxel.btnp(pyxel.KEY_BACKSPACE, 18, 2) and self.cursor_pos > 0:
            result = current_value[:self.cursor_pos - 1] + current_value[self.cursor_pos:]
            self.cursor_pos -= 1

        if pyxel.btnp(pyxel.KEY_DELETE) and self.cursor_pos < len(current_value):
            result = current_value[:self.cursor_pos] + current_value[self.cursor_pos + 1:]

        if pyxel.btnp(pyxel.KEY_LEFT, 18, 2):
            self.cursor_pos = max(0, self.cursor_pos - 1)
        if pyxel.btnp(pyxel.KEY_RIGHT, 18, 2):
            self.cursor_pos = min(len(result), self.cursor_pos + 1)

        if len(result) < max_len:
            for i in range(26):
                key = getattr(pyxel, f"KEY_{chr(ord('A') + i)}", None)
                if key and pyxel.btnp(key):
                    ch = chr(ord('a') + i)
                    if pyxel.btn(pyxel.KEY_SHIFT):
                        ch = ch.upper()
                    result = result[:self.cursor_pos] + ch + result[self.cursor_pos:]
                    self.cursor_pos += 1

            for i in range(10):
                key = getattr(pyxel, f"KEY_{i}", None)
                if key and pyxel.btnp(key):
                    result = result[:self.cursor_pos] + str(i) + result[self.cursor_pos:]
                    self.cursor_pos += 1

            chars = [
                (getattr(pyxel, "KEY_PERIOD", None), "."),
                (getattr(pyxel, "KEY_COLON", None), ":"),
                (getattr(pyxel, "KEY_SLASH", None), "/"),
                (getattr(pyxel, "KEY_MINUS", None), "-"),
                (getattr(pyxel, "KEY_APOSTROPHE", None), "@" if pyxel.btn(pyxel.KEY_SHIFT) else "'"),
            ]
            for key, char in chars:
                if key is not None and pyxel.btnp(key):
                    result = result[:self.cursor_pos] + char + result[self.cursor_pos:]
                    self.cursor_pos += 1

        return result

    def update(self) -> None:
        if not self.visible:
            return

        mx, my = pyxel.mouse_x, pyxel.mouse_y
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            if (self.x + 10 <= mx < self.x + self.width - 10 and
                self.y + 30 <= my < self.y + 42):
                self.active_field = "server"
                self.cursor_pos = len(self.server_url)

            elif (self.x + 10 <= mx < self.x + self.width - 10 and
                  self.y + 60 <= my < self.y + 72):
                self.active_field = "account"
                self.cursor_pos = len(self.account_name)

            elif (self.x + 10 <= mx < self.x + self.width - 130 and
                  self.y + 90 <= my < self.y + 102):
                self.active_field = "password"
                self.cursor_pos = len(self.password)

            elif (self.x + self.width - 120 <= mx < self.x + self.width - 10 and
                  self.y + 90 <= my < self.y + 102):
                self.password_visible = not self.password_visible

            elif (self.x + self.width // 2 - 30 <= mx < self.x + self.width // 2 + 30 and
                  self.y + 120 <= my < self.y + 135):
                self._handle_connect()

            elif (self.x + self.width - 15 <= mx < self.x + self.width - 5 and
                  self.y + 5 <= my < self.y + 15):
                self.hide()

            else:
                self.active_field = None

        if self.active_field == "server":
            self.server_url = self._handle_text_input("server", self.server_url, 100)
        elif self.active_field == "account":
            self.account_name = self._handle_text_input("account", self.account_name, 50)
        elif self.active_field == "password":
            self.password = self._handle_text_input("password", self.password, 50)

        if pyxel.btnp(pyxel.KEY_TAB):
            if self.active_field == "server":
                self.active_field = "account"
                self.cursor_pos = len(self.account_name)
            elif self.active_field == "account":
                self.active_field = "password"
                self.cursor_pos = len(self.password)
            elif self.active_field == "password":
                self.active_field = "server"
                self.cursor_pos = len(self.server_url)

        if pyxel.btnp(pyxel.KEY_RETURN):
            self._handle_connect()

        self.connect_button_hovered = (
            self.x + self.width // 2 - 30 <= mx < self.x + self.width // 2 + 30 and
            self.y + 120 <= my < self.y + 135
        )
        self.toggle_password_hovered = (
            self.x + self.width - 120 <= mx < self.x + self.width - 10 and
            self.y + 90 <= my < self.y + 102
        )

    def _handle_connect(self) -> None:
        if not self.account_name or not self.password:
            self.status_message = "Please enter account name and password"
            self.status_color = 8
            return

        try:
            self.auth_client.base_url = self.server_url
            self.auth_client.auth_endpoint = f"{self.server_url}/api/auth/login"

            result = self.auth_client.login(self.account_name, self.password)

            self.status_message = f"Connected as {result.accountName}"
            self.status_color = 11
        except Exception as e:
            self.status_message = f"Connection failed: {str(e)[:30]}"
            self.status_color = 8

    def draw(self) -> None:
        if not self.visible:
            return

        for y in range(0, pyxel.height, 2):
            for x in range(0, pyxel.width, 2):
                pyxel.pset(x, y, 0)

        pyxel.rect(self.x, self.y, self.width, self.height, 1)
        pyxel.rectb(self.x, self.y, self.width, self.height, 5)

        pyxel.rect(self.x, self.y, self.width, 20, 5)
        pyxel.text(self.x + 10, self.y + 7, "Connection Settings", 7)

        pyxel.rect(self.x + self.width - 15, self.y + 5, 10, 10, 8)
        pyxel.text(self.x + self.width - 13, self.y + 7, "X", 7)

        pyxel.text(self.x + 10, self.y + 25, "Server URL:", 7)
        self._draw_text_field(
            self.x + 10, self.y + 30, self.width - 20, 12,
            self.server_url, self.active_field == "server"
        )

        pyxel.text(self.x + 10, self.y + 55, "Account Name:", 7)
        self._draw_text_field(
            self.x + 10, self.y + 60, self.width - 20, 12,
            self.account_name, self.active_field == "account"
        )

        pyxel.text(self.x + 10, self.y + 85, "Password:", 7)
        display_text = self.password if self.password_visible else "*" * len(self.password)
        self._draw_text_field(
            self.x + 10, self.y + 90, self.width - 130, 12,
            display_text, self.active_field == "password"
        )

        btn_color = 5 if self.toggle_password_hovered else 6
        pyxel.rect(self.x + self.width - 120, self.y + 90, 110, 12, btn_color)
        pyxel.rectb(self.x + self.width - 120, self.y + 90, 110, 12, 7)
        btn_text = "Hide" if self.password_visible else "Show"
        pyxel.text(self.x + self.width - 100, self.y + 93, f"{btn_text} Password", 7)

        btn_color = 11 if self.connect_button_hovered else 3
        pyxel.rect(self.x + self.width // 2 - 30, self.y + 120, 60, 15, btn_color)
        pyxel.rectb(self.x + self.width // 2 - 30, self.y + 120, 60, 15, 7)
        pyxel.text(self.x + self.width // 2 - 18, self.y + 125, "Connect", 7)

        if self.status_message:
            pyxel.text(self.x + 10, self.y + 145, self.status_message, self.status_color)

    def _draw_text_field(self, x: int, y: int, w: int, h: int, text: str, is_active: bool) -> None:
        pyxel.rect(x, y, w, h, 0)
        border_color = 11 if is_active else 5
        pyxel.rectb(x, y, w, h, border_color)
        visible_text = text[-((w - 8) // 4):] if len(text) * 4 > w - 8 else text
        pyxel.text(x + 4, y + 3, visible_text, 7)

        if is_active and (pyxel.frame_count // 20) % 2 == 0:
            cursor_x = x + 4 + len(visible_text) * 4
            if cursor_x < x + w - 2:
                pyxel.rect(cursor_x, y + 3, 3, 5, 7)
