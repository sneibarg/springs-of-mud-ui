from __future__ import annotations
from typing import Optional, List, Dict
from component.MessageDialog import MessageDialog
from component.geometry.Rect import Rect
from component.button.Button import Button
from component.input import TextInputField, TextInputModel
from component.list.ListBox import ListBox
from component.modal.ModalFrame import ModalFrame
from component.render.TextField import TextField
from net.rest import AuthClient

import base64
import json
import os


class ConnectionSettings:
    def __init__(self, x: int, y: int, width: int, height: int, message_dialog):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.visible = False
        self.message_dialog: MessageDialog = message_dialog
        self.status_message = ""
        self.status_color = 7
        self.password_visible = False
        self.saved_connections: List[Dict] = []
        self.selected_connection_idx: Optional[int] = None
        self.auth_client = AuthClient()
        self._load_connections()
        self.tf = TextField()
        self._ctx = None  # set in update()
        self._build_components()

    def show(self) -> None:
        self.visible = True
        self._blur_all_fields()

    def hide(self) -> None:
        self.visible = False
        self._blur_all_fields()

    def toggle(self) -> None:
        self.hide() if self.visible else self.show()

    def _build_components(self) -> None:
        # --- constants / rhythm ---
        pad = 10
        top_pad = 25  # below title bar
        field_h = 12
        label_to_field = 5  # label y -> field y
        row_gap = 18  # distance between field tops
        btn_h = 15
        bottom_pad = 10
        btn_row_gap = 8  # gap between last field area and buttons
        status_h = 10  # one line

        list_w = 100
        form_x = self.x + list_w + 5
        fw = self.width - list_w - 25

        panel = Rect(self.x, self.y, self.width, self.height)
        self.frame = ModalFrame(panel, "Connection Settings", text=self.tf)

        # --- anchor bottom elements first ---
        buttons_y = self.y + self.height - bottom_pad - btn_h
        status_y = buttons_y - btn_row_gap - status_h  # status sits just above buttons

        # --- list box height: stop above status/buttons area ---
        list_top = self.y + top_pad
        list_bottom = status_y - 6
        list_h = max(40, list_bottom - list_top)

        list_box = Rect(self.x + 5, list_top, list_w - 5, list_h)
        list_items = Rect(self.x + 5, list_top + 15, list_w - 5, list_h - 20)
        self.connections_list = ListBox(list_box, list_items, header="Connections", row_h=12, text=self.tf)

        # --- models (add telnet models) ---
        self.m_name = TextInputModel(value="", cursor=0, active=False)
        self.m_server = TextInputModel(value="http://localhost:8169", cursor=0, active=False)
        self.m_account = TextInputModel(value="", cursor=0, active=False)
        self.m_pass = TextInputModel(value="", cursor=0, active=False)
        self.m_tn_host = TextInputModel(value="localhost", cursor=0, active=False)
        self.m_tn_port = TextInputModel(value="4000", cursor=0, active=False)

        # --- field positions (top-anchored, consistent spacing) ---
        fields_top = self.y + top_pad + 5

        y_name = fields_top + 0 * row_gap
        y_server = fields_top + 2 * row_gap
        y_acct = fields_top + 4 * row_gap
        y_pass = fields_top + 6 * row_gap
        y_tnhost = fields_top + 8 * row_gap
        y_tnport = fields_top + 10 * row_gap

        # move telnet rows up if we’d collide with status/buttons
        last_field_bottom = (y_tnport + label_to_field + field_h)
        max_bottom = status_y - 6
        if last_field_bottom > max_bottom:
            # compress spacing to fit
            available = max(1, max_bottom - fields_top)
            steps = 10  # index of last row
            row_gap = max(14, available // steps)
            y_name = fields_top + 0 * row_gap
            y_server = fields_top + 2 * row_gap
            y_acct = fields_top + 4 * row_gap
            y_pass = fields_top + 6 * row_gap
            y_tnhost = fields_top + 8 * row_gap
            y_tnport = fields_top + 10 * row_gap

        # --- widgets ---
        self.in_name = TextInputField(Rect(form_x + pad, y_name + label_to_field, fw, field_h),
                                      self.m_name, max_len=50, text_field=self.tf)
        self.in_server = TextInputField(Rect(form_x + pad, y_server + label_to_field, fw, field_h),
                                        self.m_server, max_len=100, text_field=self.tf)
        self.in_account = TextInputField(Rect(form_x + pad, y_acct + label_to_field, fw, field_h),
                                         self.m_account, max_len=50, text_field=self.tf)
        self.in_pass = TextInputField(Rect(form_x + pad, y_pass + label_to_field, fw - 120, field_h),
                                      self.m_pass, max_len=50, text_field=self.tf, mask_char="*")

        # telnet host + port on one row (host wide, port narrow)
        port_w = 60
        gap = 6
        host_w = fw - port_w - gap

        self.tn_host = TextInputField(Rect(form_x + pad, y_tnhost + label_to_field, fw, field_h),
                                      self.m_tn_host, max_len=64, text_field=self.tf)
        self.tn_port = TextInputField(Rect(form_x + pad, y_tnport + label_to_field, port_w, field_h),
                                      self.m_tn_port, max_len=5, text_field=self.tf)

        # password toggle stays aligned with password row
        self.btn_toggle_pass = Button(
            Rect(self.x + self.width - 120, y_pass + label_to_field, 110, field_h),
            "Show Password", 6, 5, self._toggle_password_visibility
        )

        # --- buttons anchored to bottom ---
        self.btn_new = Button(Rect(form_x + pad, buttons_y, 40, btn_h), "New", 2, 6, self._clear_fields)
        self.btn_save = Button(Rect(form_x + pad + 50, buttons_y, 50, btn_h), "Save", 2, 3,
                               self._handle_save_connection)
        self.btn_connect = Button(Rect(form_x + pad + 110, buttons_y, 60, btn_h), "Connect", 3, 11,
                                  self._handle_connect)

        # --- cached label x’s and y’s for draw() ---
        self._form_x = form_x
        self._label_x = form_x + pad
        self._label_y = {
            "name": y_name,
            "server": y_server,
            "account": y_acct,
            "pass": y_pass,
            "tn_host": y_tnhost,
            "tn_port": y_tnport,
        }
        self._status_x = form_x + pad
        self._status_y = status_y

    def _blur_all_fields(self) -> None:
        for f in (self.in_name, self.in_server, self.in_account, self.in_pass, self.tn_host, self.tn_port):
            f.blur()

    def _toggle_password_visibility(self) -> None:
        self.password_visible = not self.password_visible
        self.in_pass.mask_char = None if self.password_visible else "*"
        self.btn_toggle_pass.text = "Hide Password" if self.password_visible else "Show Password"

    def _clear_fields(self) -> None:
        self.m_name.value = ""
        self.m_name.cursor = 0

        self.m_server.value = "http://localhost:8169"
        self.m_server.cursor = len(self.m_server.value)

        self.m_account.value = ""
        self.m_account.cursor = 0

        self.m_pass.value = ""
        self.m_pass.cursor = 0

        self.selected_connection_idx = None
        self.status_message = ""
        self.status_color = 7
        self._blur_all_fields()

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

    def _load_connection(self, idx: int) -> None:
        if 0 <= idx < len(self.saved_connections):
            conn = self.saved_connections[idx]

            self.m_name.value = conn.get("name", "")
            self.m_name.cursor = len(self.m_name.value)

            self.m_server.value = conn.get("server_url", "http://localhost:8169")
            self.m_server.cursor = len(self.m_server.value)

            self.m_account.value = conn.get("account_name", "")
            self.m_account.cursor = len(self.m_account.value)

            self.m_pass.value = self._deobfuscate_password(conn.get("password", ""))
            self.m_pass.cursor = len(self.m_pass.value)

            self.selected_connection_idx = idx
            self.status_message = f"Loaded '{self.m_name.value}'"
            self.status_color = 11

    def _handle_save_connection(self) -> None:
        name = self.m_name.value.strip()
        if not name:
            self.status_message = "Please enter a connection name"
            self.status_color = 8
            return

        connection = {
            "name": name,
            "server_url": self.m_server.value.strip(),
            "account_name": self.m_account.value.strip(),
            "password": self._obfuscate_password(self.m_pass.value),
        }

        if self.selected_connection_idx is not None:
            self.saved_connections[self.selected_connection_idx] = connection
        else:
            self.saved_connections.append(connection)

        self._save_connections()
        self.status_message = f"Saved '{name}'"
        self.status_color = 11
        self._clear_fields()

    def _handle_connect(self) -> None:
        # ctx is set by update()
        ctx = self._ctx

        account = self.m_account.value.strip()
        password = self.m_pass.value
        if not account or not password:
            self.message_dialog.show(ctx,"Connection Error", "Please enter account name and password")
            return

        try:
            server = self.m_server.value.strip()
            self.auth_client.base_url = server
            self.auth_client.auth_endpoint = f"{server}/api/auth/login"
            result = self.auth_client.login(account, password)

            self.status_message = f"Connected as {result.accountName}"
            self.status_color = 11

            if ctx is not None and result.playerCharacterList:
                ctx.set_character_list(result.playerCharacterList)

        except Exception as e:
            self.message_dialog.show(ctx, "Connection Failed", f"Failed to authenticate: {str(e)}")
            self.status_message = "Connection failed"
            self.status_color = 8

    def update(self, ctx) -> None:
        if not self.visible:
            return

        self._ctx = ctx  # IMPORTANT: makes _handle_connect work

        mx, my = ctx.input.mx, ctx.input.my
        click = ctx.input.click

        if self.frame.did_close(mx, my, click):
            self.hide()
            return

        labels = [c.get("name", "Unnamed") for c in self.saved_connections]

        self.connections_list.update_hover(ctx, len(labels))
        idx = self.connections_list.click_index(ctx, len(labels))
        if idx is not None:
            self._load_connection(idx)
            self._blur_all_fields()

        for f in (self.in_name, self.in_server, self.in_account, self.in_pass, self.tn_host, self.tn_port):
            f.update(ctx)

        self.btn_toggle_pass.update(ctx)
        self.btn_new.update(ctx)
        self.btn_save.update(ctx)
        self.btn_connect.update(ctx)

    def draw(self, ctx) -> None:
        if not self.visible:
            return

        self.frame.draw(ctx)

        labels = [c.get("name", "Unnamed") for c in self.saved_connections]
        self.connections_list.draw(ctx, items=labels, selected_idx=self.selected_connection_idx)

        lx = self._label_x
        y = self._label_y

        self.tf.draw_text(ctx, x=lx, y=y["name"], text="Authentication Connection Name:", col=7)
        self.in_name.draw(ctx)

        self.tf.draw_text(ctx, x=lx, y=y["server"], text="Authentication Server URL:", col=7)
        self.in_server.draw(ctx)

        self.tf.draw_text(ctx, x=lx, y=y["account"], text="Account Name:", col=7)
        self.in_account.draw(ctx)

        self.tf.draw_text(ctx, x=lx, y=y["pass"], text="Password:", col=7)
        self.in_pass.draw(ctx)
        self.btn_toggle_pass.draw(ctx)

        self.tf.draw_text(ctx, x=lx, y=y["tn_host"], text="Telnet Host:", col=7)
        self.tn_host.draw(ctx)

        self.tf.draw_text(ctx, x=lx, y=y["tn_port"], text="Telnet Port:", col=7)
        self.tn_port.draw(ctx)

        self.btn_new.draw(ctx)
        self.btn_save.draw(ctx)
        self.btn_connect.draw(ctx)

        if self.status_message:
            self.tf.draw_text(ctx, x=self._status_x, y=self._status_y, text=self.status_message, col=self.status_color)
