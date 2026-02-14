import base64
import json
import os
import pyxel

from typing import Optional, List, Dict
from component.geometry.Rect import Rect
from component.button.Button import Button
from net.client.AuthClient import AuthClient


class ConnectionSettingsPane:
    def __init__(self, x: int, y: int, width: int, height: int, message_dialog, mud_client_ui=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.visible = False
        self.message_dialog = message_dialog
        self.mud_client_ui = mud_client_ui
        self.connection_name = ""
        self.server_url = "http://localhost:8169"
        self.account_name = ""
        self.password = ""
        self.password_visible = False
        self.saved_connections: List[Dict] = []
        self.selected_connection_idx: Optional[int] = None
        self.hovered_connection_idx: Optional[int] = None
        self.active_field: Optional[str] = None
        self.cursor_pos = 0
        self.status_message = ""
        self.status_color = 7
        self.auth_client = AuthClient()
        self._load_connections()
        self._rebuild_layout()

    def show(self) -> None:
        self.visible = True

    def hide(self) -> None:
        self.visible = False
        self.active_field = None

    def toggle(self) -> None:
        self.visible = not self.visible
        if not self.visible:
            self.active_field = None

    def _rebuild_layout(self) -> None:
        self._list_width = 100
        self._form_x = self.x + self._list_width + 5

        self.panel = Rect(self.x, self.y, self.width, self.height)
        self.title_bar = Rect(self.x, self.y, self.width, 20)
        self.close_btn = Rect(self.x + self.width - 15, self.y + 5, 10, 10)

        self.list_box = Rect(self.x + 5, self.y + 25, self._list_width - 5, self.height - 30)
        self.list_items = Rect(self.x + 5, self.y + 40, self._list_width - 5, self.height - 45)

        fw = self.width - self._list_width - 25
        self.f_name = Rect(self._form_x + 10, self.y + 30, fw, 12)
        self.f_server = Rect(self._form_x + 10, self.y + 60, fw, 12)
        self.f_account = Rect(self._form_x + 10, self.y + 90, fw, 12)
        self.f_pass = Rect(self._form_x + 10, self.y + 120, fw - 120, 12)
        self.btn_toggle_pass = Rect(self.x + self.width - 120, self.y + 120, 110, 12)

        self.btn_new = Button(Rect(self._form_x + 10, self.y + 145, 40, 15), "New", 2, 6, self._clear_connection_fields)
        self.btn_save = Button(Rect(self._form_x + 60, self.y + 145, 50, 15), "Save", 2, 3, self._handle_save_connection)
        self.btn_connect = Button(Rect(self._form_x + 120, self.y + 145, 60, 15), "Connect", 3, 11, self._handle_connect)

    def _clear_connection_fields(self) -> None:
        self.connection_name = ""
        self.server_url = "http://localhost:8169"
        self.account_name = ""
        self.password = ""
        self.selected_connection_idx = None
        self.active_field = None

    @staticmethod
    def _obfuscate_password(password: str) -> str:
        if not password:
            return ""
        return base64.b64encode(password.encode("utf-8")).decode("utf-8")

    @staticmethod
    def _deobfuscate_password(obfuscated: str) -> str:
        if not obfuscated:
            return ""
        try:
            return base64.b64decode(obfuscated.encode("utf-8")).decode("utf-8")
        except Exception:
            return ""

    @staticmethod
    def _get_connections_path() -> str:
        resources_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "resources")
        os.makedirs(resources_dir, exist_ok=True)
        return os.path.join(resources_dir, "connections.json")

    def _load_connections(self) -> None:
        try:
            path = self._get_connections_path()
            if os.path.exists(path):
                with open(path, "r") as f:
                    self.saved_connections = json.load(f)
        except Exception as e:
            print(f"Failed to load connections: {e}")
            self.saved_connections = []

    def _save_connections(self) -> None:
        try:
            path = self._get_connections_path()
            with open(path, "w") as f:
                json.dump(self.saved_connections, f, indent=2)
        except Exception as e:
            self.status_message = f"Failed to save: {str(e)[:20]}"
            self.status_color = 8

    def _handle_save_connection(self) -> None:
        if not self.connection_name:
            self.status_message = "Please enter a connection name"
            self.status_color = 8
            return

        connection = {
            "name": self.connection_name,
            "server_url": self.server_url,
            "account_name": self.account_name,
            "password": self._obfuscate_password(self.password),
        }

        if self.selected_connection_idx is not None:
            self.saved_connections[self.selected_connection_idx] = connection
        else:
            self.saved_connections.append(connection)

        self._save_connections()
        self.status_message = f"Saved '{self.connection_name}'"
        self.status_color = 11
        self._clear_connection_fields()

    def _load_connection(self, idx: int) -> None:
        if 0 <= idx < len(self.saved_connections):
            conn = self.saved_connections[idx]
            self.connection_name = conn.get("name", "")
            self.server_url = conn.get("server_url", "http://localhost:8169")
            self.account_name = conn.get("account_name", "")
            self.password = self._deobfuscate_password(conn.get("password", ""))
            self.selected_connection_idx = idx
            self.status_message = f"Loaded '{self.connection_name}'"
            self.status_color = 11

    def _handle_text_input(self, current_value: str, max_len: int = 100) -> str:
        result = current_value

        if pyxel.btnp(pyxel.KEY_BACKSPACE, 18, 2) and self.cursor_pos > 0:
            result = current_value[: self.cursor_pos - 1] + current_value[self.cursor_pos :]
            self.cursor_pos -= 1

        if pyxel.btnp(pyxel.KEY_DELETE) and self.cursor_pos < len(current_value):
            result = current_value[: self.cursor_pos] + current_value[self.cursor_pos + 1 :]

        if pyxel.btnp(pyxel.KEY_LEFT, 18, 2):
            self.cursor_pos = max(0, self.cursor_pos - 1)
        if pyxel.btnp(pyxel.KEY_RIGHT, 18, 2):
            self.cursor_pos = min(len(result), self.cursor_pos + 1)

        if len(result) < max_len:
            for i in range(26):
                key = getattr(pyxel, f"KEY_{chr(ord('A') + i)}", None)
                if key and pyxel.btnp(key):
                    ch = chr(ord("a") + i)
                    if pyxel.btn(pyxel.KEY_SHIFT):
                        ch = ch.upper()
                    result = result[: self.cursor_pos] + ch + result[self.cursor_pos :]
                    self.cursor_pos += 1

            for i in range(10):
                key = getattr(pyxel, f"KEY_{i}", None)
                if key and pyxel.btnp(key):
                    result = result[: self.cursor_pos] + str(i) + result[self.cursor_pos :]
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
                    result = result[: self.cursor_pos] + char + result[self.cursor_pos :]
                    self.cursor_pos += 1

        return result

    def _handle_click_focus(self, mx: int, my: int) -> None:
        if self.f_name.contains(mx, my):
            self.active_field = "name"
            self.cursor_pos = len(self.connection_name)
        elif self.f_server.contains(mx, my):
            self.active_field = "server"
            self.cursor_pos = len(self.server_url)
        elif self.f_account.contains(mx, my):
            self.active_field = "account"
            self.cursor_pos = len(self.account_name)
        elif self.f_pass.contains(mx, my):
            self.active_field = "password"
            self.cursor_pos = len(self.password)
        else:
            self.active_field = None

    def _tab_advance(self) -> None:
        if not pyxel.btnp(pyxel.KEY_TAB):
            return

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
        else:
            self.active_field = "name"
            self.cursor_pos = len(self.connection_name)

    def _update_hovered_connection(self, mx: int, my: int) -> None:
        self.hovered_connection_idx = None
        if not self.list_items.contains(mx, my):
            return

        list_y = self.list_items.y
        for idx in range(len(self.saved_connections)):
            if list_y <= my < list_y + 12:
                self.hovered_connection_idx = idx
                return
            list_y += 12

    def _handle_list_click(self, mx: int, my: int) -> bool:
        if not self.list_items.contains(mx, my):
            return False

        list_y = self.list_items.y
        for idx in range(len(self.saved_connections)):
            if list_y <= my < list_y + 12:
                self._load_connection(idx)
                return True
            list_y += 12
        return False

    def _handle_connect(self) -> None:
        if not self.account_name or not self.password:
            self.message_dialog.show("Connection Error", "Please enter account name and password")
            return

        try:
            self.auth_client.base_url = self.server_url
            self.auth_client.auth_endpoint = f"{self.server_url}/api/auth/login"
            result = self.auth_client.login(self.account_name, self.password)

            self.status_message = f"Connected as {result.accountName}"
            self.status_color = 11

            if self.mud_client_ui and result.playerCharacterList:
                self.mud_client_ui.update_character_list(result.playerCharacterList)
        except Exception as e:
            self.message_dialog.show("Connection Failed", f"Failed to authenticate: {str(e)}")
            self.status_message = "Connection failed"
            self.status_color = 8

    def update(self) -> None:
        if not self.visible:
            return

        mx, my = pyxel.mouse_x, pyxel.mouse_y
        click = pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT)

        if click:
            if self.close_btn.contains(mx, my):
                self.hide()
                return

            if self.btn_toggle_pass.contains(mx, my):
                self.password_visible = not self.password_visible

            if self._handle_list_click(mx, my):
                self.active_field = None
            else:
                self._handle_click_focus(mx, my)

        self.btn_new.update(mx, my, click)
        self.btn_save.update(mx, my, click)
        self.btn_connect.update(mx, my, click)

        if self.active_field == "name":
            self.connection_name = self._handle_text_input(self.connection_name, 50)
        elif self.active_field == "server":
            self.server_url = self._handle_text_input(self.server_url, 100)
        elif self.active_field == "account":
            self.account_name = self._handle_text_input(self.account_name, 50)
        elif self.active_field == "password":
            self.password = self._handle_text_input(self.password, 50)

        self._tab_advance()
        self._update_hovered_connection(mx, my)

    def draw(self) -> None:
        if not self.visible:
            return

        self._draw_modal_overlay()
        self._draw_panel()
        self._draw_title_bar()
        self._draw_close_button()

        self._draw_connections_list()
        self._draw_form()

        self.btn_new.draw()
        self.btn_save.draw()
        self.btn_connect.draw()

        self._draw_status()

    @staticmethod
    def _draw_modal_overlay() -> None:
        for y in range(0, pyxel.height, 2):
            for x in range(0, pyxel.width, 2):
                pyxel.pset(x, y, 0)

    def _draw_panel(self) -> None:
        self.panel.fill(1)
        self.panel.border(5)

    def _draw_title_bar(self) -> None:
        self.title_bar.fill(5)
        pyxel.text(self.x + 10, self.y + 7, "Connection Settings", 7)

    def _draw_close_button(self) -> None:
        self.close_btn.fill(8)
        pyxel.text(self.close_btn.x + 2, self.close_btn.y + 2, "X", 7)

    def _draw_connections_list(self) -> None:
        self.list_box.fill(0)
        self.list_box.border(5)
        pyxel.text(self.list_box.x + 3, self.list_box.y + 3, "Connections", 7)

        y = self.list_items.y
        for idx, conn in enumerate(self.saved_connections):
            if y + 12 > self.list_box.y + self.list_box.h - 5:
                break

            row = Rect(self.list_items.x + 1, y, self.list_items.w - 2, 11)
            if idx == self.selected_connection_idx:
                row.fill(5)
            elif idx == self.hovered_connection_idx:
                row.fill(2)

            name = conn.get("name", "Unnamed")
            max_chars = (self._list_width - 12) // 4
            if len(name) > max_chars:
                name = name[: max_chars - 2] + ".."
            pyxel.text(self.list_box.x + 3, y + 2, name, 7)

            y += 12

    def _draw_form(self) -> None:
        pyxel.text(self._form_x + 10, self.y + 25, "Connection Name:", 7)
        self._draw_text_field(self.f_name, self.connection_name, self.active_field == "name")

        pyxel.text(self._form_x + 10, self.y + 55, "Server URL:", 7)
        self._draw_text_field(self.f_server, self.server_url, self.active_field == "server")

        pyxel.text(self._form_x + 10, self.y + 85, "Account Name:", 7)
        self._draw_text_field(self.f_account, self.account_name, self.active_field == "account")

        pyxel.text(self._form_x + 10, self.y + 115, "Password:", 7)
        display_text = self.password if self.password_visible else "*" * len(self.password)
        self._draw_text_field(self.f_pass, display_text, self.active_field == "password")

        self._draw_password_toggle()

    def _draw_password_toggle(self) -> None:
        hover = self.btn_toggle_pass.contains(pyxel.mouse_x, pyxel.mouse_y)
        self.btn_toggle_pass.fill(5 if hover else 6)
        self.btn_toggle_pass.border(7)

        btn_text = "Hide" if self.password_visible else "Show"
        pyxel.text(self.btn_toggle_pass.x + 20, self.btn_toggle_pass.y + 3, f"{btn_text} Password", 7)

    def _draw_status(self) -> None:
        if self.status_message:
            pyxel.text(self._form_x + 10, self.y + 165, self.status_message, self.status_color)

    @staticmethod
    def _draw_text_field(r: Rect, text: str, is_active: bool) -> None:
        r.fill(0)
        r.border(11 if is_active else 5)

        visible_text = text[-((r.w - 8) // 4):] if len(text) * 4 > r.w - 8 else text
        pyxel.text(r.x + 4, r.y + 3, visible_text, 7)

        if not is_active:
            return

        if (pyxel.frame_count // 20) % 2 != 0:
            return

        cursor_x = r.x + 4 + len(visible_text) * 4
        if cursor_x < r.x + r.w - 2:
            Rect(cursor_x, r.y + 3, 3, 5).fill(7)
