import pyxel
import json
import os
import base64

from typing import Optional, List, Dict
from net.client.AuthClient import AuthClient


class ConnectionSettingsPane:
    def __init__(self, x: int, y: int, width: int, height: int, message_dialog):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.visible = False
        self.message_dialog = message_dialog
        self.connection_name = ""
        self.server_url = "http://localhost:8169"
        self.account_name = ""
        self.password = ""
        self.password_visible = False
        self.saved_connections: List[Dict] = []
        self.selected_connection_idx: Optional[int] = None
        self.hovered_connection_idx: Optional[int] = None
        self.active_field: Optional[str] = None  # "name", "server", "account", "password"
        self.cursor_pos = 0
        self.status_message = ""
        self.status_color = 7
        self.auth_client = AuthClient()
        self.connect_button_hovered = False
        self.save_button_hovered = False
        self.new_button_hovered = False
        self.toggle_password_hovered = False
        self._load_connections()

    def show(self) -> None:
        self.visible = True

    def hide(self) -> None:
        self.visible = False

    def toggle(self) -> None:
        self.visible = not self.visible

    def _clear_connection_fields(self) -> None:
        """Clear all connection fields and deselect."""
        self.connection_name = ""
        self.server_url = "http://localhost:8169"
        self.account_name = ""
        self.password = ""
        self.selected_connection_idx = None
        self.active_field = None

    def _obfuscate_password(self, password: str) -> str:
        """Obfuscate password using base64 encoding."""
        if not password:
            return ""
        return base64.b64encode(password.encode('utf-8')).decode('utf-8')

    def _deobfuscate_password(self, obfuscated: str) -> str:
        """Deobfuscate password from base64 encoding."""
        if not obfuscated:
            return ""
        try:
            return base64.b64decode(obfuscated.encode('utf-8')).decode('utf-8')
        except Exception:
            return ""

    def _get_connections_path(self) -> str:
        """Get the path to the connections file in the resources folder."""
        resources_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "resources")
        os.makedirs(resources_dir, exist_ok=True)
        return os.path.join(resources_dir, "connections.json")

    def _load_connections(self) -> None:
        """Load saved connections from file."""
        try:
            connections_path = self._get_connections_path()
            if os.path.exists(connections_path):
                with open(connections_path, "r") as f:
                    self.saved_connections = json.load(f)
        except Exception as e:
            print(f"Failed to load connections: {e}")
            self.saved_connections = []

    def _save_connections(self) -> None:
        """Save connections to file."""
        try:
            connections_path = self._get_connections_path()
            with open(connections_path, "w") as f:
                json.dump(self.saved_connections, f, indent=2)
        except Exception as e:
            self.status_message = f"Failed to save: {str(e)[:20]}"
            self.status_color = 8

    def _handle_save_connection(self) -> None:
        """Save current connection to the list."""
        if not self.connection_name:
            self.status_message = "Please enter a connection name"
            self.status_color = 8
            return

        # Create connection dict with obfuscated password
        connection = {
            "name": self.connection_name,
            "server_url": self.server_url,
            "account_name": self.account_name,
            "password": self._obfuscate_password(self.password)
        }

        if self.selected_connection_idx is not None:
            self.saved_connections[self.selected_connection_idx] = connection
        else:
            self.saved_connections.append(connection)

        self._save_connections()
        self.status_message = f"Saved '{self.connection_name}'"
        self.status_color = 11

        # Clear fields and deselect to allow creating new connection
        self._clear_connection_fields()

    def _load_connection(self, idx: int) -> None:
        """Load a connection from the saved list."""
        if 0 <= idx < len(self.saved_connections):
            conn = self.saved_connections[idx]
            self.connection_name = conn.get("name", "")
            self.server_url = conn.get("server_url", "http://localhost:8169")
            self.account_name = conn.get("account_name", "")
            # Deobfuscate password when loading
            self.password = self._deobfuscate_password(conn.get("password", ""))
            self.selected_connection_idx = idx
            self.status_message = f"Loaded '{self.connection_name}'"
            self.status_color = 11

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
        list_width = 100
        form_x = self.x + list_width + 5
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            # Check saved connections list clicks (items start at y + 40)
            if self.x + 5 <= mx < self.x + list_width and self.y + 40 <= my < self.y + self.height - 5:
                list_y = self.y + 40
                for idx in range(len(self.saved_connections)):
                    if list_y <= my < list_y + 12:
                        self._load_connection(idx)
                        break
                    list_y += 12
            elif form_x + 10 <= mx < self.x + self.width - 10 and self.y + 30 <= my < self.y + 42:
                self.active_field = "name"
                self.cursor_pos = len(self.connection_name)
            elif form_x + 10 <= mx < self.x + self.width - 10 and self.y + 60 <= my < self.y + 72:
                self.active_field = "server"
                self.cursor_pos = len(self.server_url)
            elif form_x + 10 <= mx < self.x + self.width - 10 and self.y + 90 <= my < self.y + 102:
                self.active_field = "account"
                self.cursor_pos = len(self.account_name)
            elif form_x + 10 <= mx < self.x + self.width - 130 and self.y + 120 <= my < self.y + 132:
                self.active_field = "password"
                self.cursor_pos = len(self.password)
            elif self.x + self.width - 120 <= mx < self.x + self.width - 10 and self.y + 120 <= my < self.y + 132:
                self.password_visible = not self.password_visible
            elif form_x + 10 <= mx < form_x + 50 and self.y + 145 <= my < self.y + 160:
                self._clear_connection_fields()
            elif form_x + 60 <= mx < form_x + 110 and self.y + 145 <= my < self.y + 160:
                self._handle_save_connection()
            elif form_x + 120 <= mx < form_x + 180 and self.y + 145 <= my < self.y + 160:
                self._handle_connect()
            elif self.x + self.width - 15 <= mx < self.x + self.width - 5 and self.y + 5 <= my < self.y + 15:
                self.hide()
            else:
                self.active_field = None

        if self.active_field == "name":
            self.connection_name = self._handle_text_input("name", self.connection_name, 50)
        elif self.active_field == "server":
            self.server_url = self._handle_text_input("server", self.server_url, 100)
        elif self.active_field == "account":
            self.account_name = self._handle_text_input("account", self.account_name, 50)
        elif self.active_field == "password":
            self.password = self._handle_text_input("password", self.password, 50)

        # Tab navigation
        if pyxel.btnp(pyxel.KEY_TAB):
            if self.active_field == "name":
                self.active_field = "server"
                self.cursor_pos = len(self.server_url)
            elif self.active_field == "server":
                self.active_field = "account"
                self.cursor_pos = len(self.account_name)
            elif self.active_field == "account":
                self.active_field = "password"
                self.cursor_pos = len(self.password)
            elif self.active_field == "password":
                self.active_field = "name"
                self.cursor_pos = len(self.connection_name)

        self.new_button_hovered = (form_x + 10 <= mx < form_x + 50 and self.y + 145 <= my < self.y + 160)
        self.save_button_hovered = (form_x + 60 <= mx < form_x + 110 and self.y + 145 <= my < self.y + 160)
        self.connect_button_hovered = (form_x + 120 <= mx < form_x + 180 and self.y + 145 <= my < self.y + 160)
        self.toggle_password_hovered = (self.x + self.width - 120 <= mx < self.x + self.width - 10 and self.y + 120 <= my < self.y + 132)

        # Track hovered connection in list (items start at y + 40 to account for header)
        self.hovered_connection_idx = None
        if self.x + 5 <= mx < self.x + list_width and self.y + 40 <= my < self.y + self.height - 5:
            list_y = self.y + 40
            for idx in range(len(self.saved_connections)):
                if list_y <= my < list_y + 12:
                    self.hovered_connection_idx = idx
                    break
                list_y += 12

    def _handle_connect(self) -> None:
        if not self.account_name or not self.password:
            self.message_dialog.show(
                "Connection Error",
                "Please enter account name and password"
            )
            return

        try:
            self.auth_client.base_url = self.server_url
            self.auth_client.auth_endpoint = f"{self.server_url}/api/auth/login"

            result = self.auth_client.login(self.account_name, self.password)

            self.status_message = f"Connected as {result.accountName}"
            self.status_color = 11
        except Exception as e:
            error_message = str(e)
            self.message_dialog.show(
                "Connection Failed",
                f"Failed to authenticate: {error_message}"
            )
            self.status_message = "Connection failed"
            self.status_color = 8

    def draw(self) -> None:
        if not self.visible:
            return

        for y in range(0, pyxel.height, 2):
            for x in range(0, pyxel.width, 2):
                pyxel.pset(x, y, 0)

        def main():
            pyxel.rect(self.x, self.y, self.width, self.height, 1)
            pyxel.rectb(self.x, self.y, self.width, self.height, 5)

        def title():
            pyxel.rect(self.x, self.y, self.width, 20, 5)
            pyxel.text(self.x + 10, self.y + 7, "Connection Settings", 7)

        def close():
            pyxel.rect(self.x + self.width - 15, self.y + 5, 10, 10, 8)
            pyxel.text(self.x + self.width - 13, self.y + 7, "X", 7)

        def form_fields():
            pyxel.text(form_x + 10, self.y + 25, "Connection Name:", 7)
            self._draw_text_field(form_x + 10, self.y + 30, self.width - list_width - 25, 12, self.connection_name,
                                  self.active_field == "name")

        def show_password():
            btn_color = 5 if self.toggle_password_hovered else 6
            pyxel.rect(self.x + self.width - 120, self.y + 120, 110, 12, btn_color)
            pyxel.rectb(self.x + self.width - 120, self.y + 120, 110, 12, 7)
            btn_text = "Hide" if self.password_visible else "Show"
            pyxel.text(self.x + self.width - 100, self.y + 123, f"{btn_text} Password", 7)

        def action_buttons():
            new_color = 6 if self.new_button_hovered else 2
            pyxel.rect(form_x + 10, self.y + 145, 40, 15, new_color)
            pyxel.rectb(form_x + 10, self.y + 145, 40, 15, 7)
            pyxel.text(form_x + 18, self.y + 150, "New", 7)

            save_color = 3 if self.save_button_hovered else 2
            pyxel.rect(form_x + 60, self.y + 145, 50, 15, save_color)
            pyxel.rectb(form_x + 60, self.y + 145, 50, 15, 7)
            pyxel.text(form_x + 70, self.y + 150, "Save", 7)

            connect_color = 11 if self.connect_button_hovered else 3
            pyxel.rect(form_x + 120, self.y + 145, 60, 15, connect_color)
            pyxel.rectb(form_x + 120, self.y + 145, 60, 15, 7)
            pyxel.text(form_x + 126, self.y + 150, "Connect", 7)

        main()
        title()
        close()

        list_width = 100
        form_x = self.x + list_width + 5
        self._draw_connections_list(list_width)

        form_fields()

        pyxel.text(form_x + 10, self.y + 55, "Server URL:", 7)
        self._draw_text_field(form_x + 10, self.y + 60, self.width - list_width - 25, 12, self.server_url,
                              self.active_field == "server")

        pyxel.text(form_x + 10, self.y + 85, "Account Name:", 7)
        self._draw_text_field(form_x + 10, self.y + 90, self.width - list_width - 25, 12, self.account_name,
                              self.active_field == "account")

        pyxel.text(form_x + 10, self.y + 115, "Password:", 7)
        display_text = self.password if self.password_visible else "*" * len(self.password)
        self._draw_text_field(form_x + 10, self.y + 120, self.width - list_width - 145, 12, display_text,
                              self.active_field == "password")

        show_password()
        action_buttons()

        if self.status_message:
            pyxel.text(form_x + 10, self.y + 165, self.status_message, self.status_color)

    def _draw_connections_list(self, list_width: int) -> None:
        def connection_list():
            pyxel.rect(self.x + 5, self.y + 25, list_width - 5, self.height - 30, 0)
            pyxel.rectb(self.x + 5, self.y + 25, list_width - 5, self.height - 30, 5)
            pyxel.text(self.x + 8, self.y + 28, "Connections", 7)

        def connection_items():
            list_y = self.y + 40
            for idx, conn in enumerate(self.saved_connections):
                if list_y + 12 > self.y + self.height - 5:
                    break

                if idx == self.selected_connection_idx:
                    pyxel.rect(self.x + 6, list_y, list_width - 7, 11, 5)
                elif idx == self.hovered_connection_idx:
                    pyxel.rect(self.x + 6, list_y, list_width - 7, 11, 2)

                name = conn.get("name", "Unnamed")
                max_chars = (list_width - 12) // 4
                if len(name) > max_chars:
                    name = name[:max_chars - 2] + ".."
                pyxel.text(self.x + 8, list_y + 2, name, 7)

                list_y += 12

        connection_list()
        connection_items()

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
