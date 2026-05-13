from __future__ import annotations
from collections import deque
from component.input import TextInput
from component.menu import MenuBar
from component.modal.MessageDialog import MessageDialog
from component.render import CursorRenderer, TextRenderer
from component.app import GameWorld, ModalGate, TextPane, InputCommand, Divider, UIOverlay, Cursor
from engine import MudClientApp
from net.telnet import TelnetClient, TelnetConfig
from net.rest import AuthResponse
from domain import CharacterCreation, PlayerCharacter
from ui.layout import Layout
from ui.panes import ConnectionSettings, DisplaySettings

import time
import json
import requests
from urllib.parse import urlparse


class MudClientUI:
    API_VERSION = "/api/v1"
    ENDPOINTS = {
        "characters": "/characters",
    }

    def __init__(self, install_dir: str, verbose: bool = False) -> None:
        self.verbose = verbose
        self.install_dir = install_dir

        if self.verbose:
            print(f"[MudClientUI] Using installation directory: {self.install_dir}")

        self._telnet_host:str = "localhost"
        self._telnet_port: int = 6969
        self._api_base_url: str = "http://localhost:9080"
        self._telnet: TelnetClient | None = None
        self._auth_data: AuthResponse | None = None
        self._character_creation: CharacterCreation | None = None
        self.text_font_name = None
        self.layout = Layout()
        self._show_graphics = True
        self._configured_gutter = self.layout.gutter
        self._toggle_graphics_menu_item = None
        # Create DisplaySettings with install_dir so it can load from the correct location
        self.settings = DisplaySettings(0, 0, 100, 100, None, None, install_dir=self.install_dir)
        self._configured_game_w = int(self.settings.game_pane_width)
        self._configured_ui_w = int(self.settings.text_pane_width)
        self.layout.game_w = self._configured_game_w
        self.layout.ui_w = self._configured_ui_w
        self.layout.h = int(self.settings.window_height)
        self.layout.game_h = int(self.settings.window_height)
        self.text_input = TextInput(max_len=2000)
        self.scroll_buffer_size = int(self.settings.scroll_buffer)
        self.scrollback: deque[str] = deque(maxlen=self.scroll_buffer_size)
        self.menu_bar = MenuBar(x=0, y=0, width=self.layout.w, height=10)
        self._setup_menus()
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
                                font_scale=self.font_scale,
                                poll_callback=self._poll_telnet_messages)
        self.gate = ModalGate([self.connection_settings, self.display_settings, self.message_dialog])
        self._mount_components()

        self.log("Connected. Type 'help' and press Enter.")
        self.log("Left pane is your render surface; right pane is scrollback + clipboard.")
        self.log(f"Scroll buffer initialized: {self.scrollback.maxlen} lines")
        self.log(f"Text wrapping at: {self.chars_per_line} chars per line")
        self.log(f"Text pane width: {self.layout.ui_w}px (~{self.layout.ui_w // 4} chars visible)")

        self.app.run()

    def _poll_telnet_messages(self) -> None:
        if self._telnet and self._telnet.connected:
            line = self._telnet.poll_line()
            if line is not None:
                self.log(line)

    def _on_connection_established(self, connection_info: dict) -> None:
        self._auth_data = connection_info["auth_data"]
        self._telnet_host = connection_info["telnet_host"]
        self._telnet_port = connection_info["telnet_port"]
        print(f"Connection info: {connection_info}")
        self._api_base_url = self._build_api_base_url(
            server_url=connection_info.get("server_url", self._api_base_url),
            api_port=connection_info.get("api_port"),
        )
        print(f"API_base_url: {self._api_base_url}")
        self._character_creation = CharacterCreation(api_base_url=self._api_base_url, account_id=self._auth_data.id)
        self._refresh_player_character_list()

        self.log(f"Authenticated as {self._auth_data.firstName} {self._auth_data.lastName}")
        self.log(f"Telnet server: {self._telnet_host}:{self._telnet_port}")
        self.log(f"Loaded {len(self._auth_data.playerCharacterList)} character(s)")
        self.log("Type 'list' to see your characters, then 'logon <name>' to play")
        self.log("Use 'create-char help' for ROM-style character creation commands.")
        self.log(f"Create-character API base: {self._api_base_url}")

    @staticmethod
    def _build_api_base_url(server_url: str, api_port) -> str:
        parsed = urlparse(server_url if "://" in server_url else f"http://{server_url}")
        scheme = parsed.scheme or "http"
        netloc = parsed.netloc or parsed.path
        host = (netloc.split("@")[-1].split(":")[0] if netloc else "").strip()
        port_value = str(api_port).strip() if api_port is not None else ""

        if not host:
            print(f"Server URL: {server_url}")
            return server_url
        if not port_value:
            print(f"Port value: {scheme}://{host} (no port specified in URL or in settings")
            return f"{scheme}://{host}"
        print(f"API url: {scheme}://{host}:{port_value}")
        return f"{scheme}://{host}:{port_value}"

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
            self._configured_game_w = game_pane_width

        if text_pane_width:
            self._configured_ui_w = text_pane_width

        if font_name:
            self.text_font_name = font_name

        self._refresh_render_mode_layout()
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
        self.log(f"{cmd}")
        raw = cmd.strip()
        if self._character_creation and self._character_creation.active and raw:
            low = raw.lower()
            if low not in ("close-ui", "ui-help") and not low.startswith("create-char"):
                for line in self._character_creation.handle_input(raw):
                    self.log(line)
                return

        parts = raw.split()
        if not parts:
            if self._telnet and self._telnet.connected:
                try:
                    self._telnet.send_line("")
                except Exception as e:
                    self.log(f"Send failed: {e}")
            else:
                self.log("")  # Just show a blank line
            return

        verb = parts[0].lower()
        if verb == "ui-help":
            self.log("Commands: ui-help, list-connections, connect <name>, list, logon <name>, create-char <...>, close-ui")
            self.log("Use Settings -> Connections to authenticate first")
            return
        if verb == "list-connections":
            self._handle_list_connections_command()
            return
        if verb == "connect":
            self._handle_connect_command(parts[1:])
            return
        if verb == "create-char":
            self._handle_create_character_command(parts[1:])
            return

        if verb == "ui-list":
            if not self._auth_data:
                self.log("Please authenticate first via Settings -> Connections")
                return

            self.log(" ")
            self.log("Available characters:")
            for character in self._auth_data.playerCharacterList:
                character_class = getattr(character, "characterClass", getattr(character, "character_class", "Unknown"))
                self.log(f"- {character.name} (Level {character.level} {character.race} {character_class})")
            return

        if verb == "logon":
            if len(parts) < 2:
                self.log("Usage: logon <characterName>")
                return

            if not self._auth_data:
                self.log("Please authenticate first via Settings -> Connections")
                return

            char_name = parts[1]
            selected_char = None
            for char in self._auth_data.playerCharacterList:
                if char.name.lower() == char_name.lower():
                    selected_char = char
                    break

            if not selected_char:
                self.log(f"Character '{char_name}' not found. Use 'list' to see available characters.")
                return

            try:
                t = self._ensure_telnet()
                self.log(f"Connecting to {self._telnet_host}:{self._telnet_port} as {selected_char.name}...")

                # Build payload for server
                payload = {
                    "accountId": self._auth_data.id,
                    "characterId": selected_char.id,
                    "characterName": selected_char.name
                }

                # Send as "logon <JSON>"
                payload_json = json.dumps(payload)
                t.send_line(f"logon {payload_json}")

            except Exception as e:
                self.log(f"Logon failed: {e}")
            return

        if verb == "close-ui":
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

    def _create_char_help(self) -> None:
        if not self._character_creation:
            self.log("Please authenticate first via Settings -> Connections")
            return
        for line in self._character_creation.help_lines():
            self.log(line)

    def _handle_list_connections_command(self) -> None:
        connections = self.connection_settings.list_saved_connections()
        if not connections:
            self.log("No saved connections found.")
            return

        self.log("Saved connections:")
        for connection in connections:
            name = str(connection.get("name", "Unnamed")).strip() or "Unnamed"
            server_url = str(connection.get("server_url", "")).strip()
            api_port = str(connection.get("api_port", "")).strip()
            telnet_host = str(connection.get("telnet_host", "")).strip()
            telnet_port = str(connection.get("telnet_port", "")).strip()
            self.log(f"- {name} | auth={server_url}:{api_port} | telnet={telnet_host}:{telnet_port}")

    def _handle_connect_command(self, args: list[str]) -> None:
        if not args:
            self.log("Usage: connect <connection-name>")
            return

        connection_name = " ".join(args).strip()
        try:
            self.connection_settings.connect_saved_connection(connection_name)
            self.log(f"Connected using saved connection '{connection_name}'.")
        except Exception as e:
            self.log(f"Connect failed: {e}")

    def _handle_create_character_command(self, args: list[str]) -> None:
        if not self._auth_data:
            self.log("Please authenticate first via Settings -> Connections")
            return
        if not self._character_creation:
            self._character_creation = CharacterCreation(api_base_url=self._api_base_url, account_id=self._auth_data.id)

        action = args[0].lower() if args else "help"
        if action == "help":
            self._create_char_help()
            return
        if action == "cancel":
            for line in self._character_creation.cancel():
                self.log(line)
            return
        if action == "show":
            for line in self._character_creation.show_lines():
                self.log(line)
            return
        if action == "submit":
            character = self._character_creation.build_player_character()
            if character is None:
                self.log("Character creation is not complete yet.")
                return
            payload = self._character_creation.build_payload_dict()
            if payload is None:
                self.log("Character creation payload could not be built.")
                return
            self.log("Character creation payload:")
            self.log(json.dumps(payload))
            self._submit_character_payload(payload)
            return
        if action == "start":
            for line in self._character_creation.start():
                self.log(line)
            return
        self._create_char_help()

    def _api_url(self, endpoint: str) -> str:
        base = self._api_base_url.rstrip("/")
        api = self.API_VERSION.strip("/")
        suffix = endpoint.strip("/")
        return f"{base}/{api}/{suffix}"

    def _fetch_json(self, endpoint: str):
        headers = {}
        if hasattr(self, "connection_settings") and self.connection_settings is not None:
            headers = self.connection_settings.auth_client.get_auth_headers()
        response = requests.get(self._api_url(endpoint), headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()

    def _post_json(self, endpoint: str, payload_json: str):
        headers = {"Content-Type": "application/json"}
        if hasattr(self, "connection_settings") and self.connection_settings is not None:
            headers.update(self.connection_settings.auth_client.get_auth_headers())
        response = requests.post(self._api_url(endpoint), headers=headers, data=payload_json, timeout=10)
        response.raise_for_status()
        if response.content:
            return response.json()
        return None

    def _submit_character_payload(self, payload: PlayerCharacter | dict) -> None:
        payload_json = payload.to_json() if isinstance(payload, PlayerCharacter) else json.dumps(payload)
        try:
            result = self._post_json(self.ENDPOINTS["characters"], payload_json)
            self._refresh_player_character_list()
            self.log("Character creation request submitted.")
            if isinstance(result, dict):
                name = result.get("name", payload.name if isinstance(payload, PlayerCharacter) else payload.get("name", ""))
                self.log(f"Created character: {name}")
            self.log("Use 'list' after reconnect/auth refresh if your new character is not yet shown.")
        except requests.HTTPError as e:
            response = getattr(e, "response", None)
            status_code = getattr(response, "status_code", None)
            if isinstance(status_code, int) and status_code >= 400:
                self.log(f"Character creation payload on HTTP {status_code}:")
                self.log(payload_json)
                response_text = getattr(response, "text", "")
                if response_text:
                    self.log(f"Character creation error response: {response_text}")
                    print(f"Payload for failed request: {payload_json}")
            self.log(f"Character creation submit failed: {e}")
        except Exception as e:
            self.log(f"Character creation submit failed: {e}")
            print(f"Payload for failed request: {payload_json}")

    def _refresh_player_character_list(self) -> None:
        if not self._auth_data:
            return
        try:
            characters = self._fetch_json(f"/characters/account/{self._auth_data.id}")
            if isinstance(characters, list):
                self._auth_data.playerCharacterList = [
                    PlayerCharacter.from_dict(character, from_camel_case=True)
                    for character in characters
                    if isinstance(character, dict)
                ]
        except Exception as e:
            self.log(f"Unable to refresh character list from API: {e}")

    def _ensure_telnet(self) -> TelnetClient:
        if self._telnet is None:
            self._telnet = TelnetClient(TelnetConfig(host=self._telnet_host, port=self._telnet_port), on_status=self.log)
        if not self._telnet.connected:
            self._telnet.connect()
        return self._telnet

    def toggle_graphics(self) -> None:
        self._show_graphics = not self._show_graphics
        self._refresh_render_mode_layout()
        self._mount_components()
        self._update_graphics_menu_item_label()

        if self._show_graphics:
            self.log("Graphics enabled. Game board restored.")
        else:
            self.log("Graphics disabled. Telnet client is now the only rendered pane.")

    def _refresh_render_mode_layout(self) -> None:
        total_width = self._configured_game_w + self._configured_ui_w + self._configured_gutter

        if self._show_graphics:
            self.layout.game_w = self._configured_game_w
            self.layout.ui_w = self._configured_ui_w
            self.layout.gutter = self._configured_gutter
        else:
            self.layout.game_w = 0
            self.layout.ui_w = total_width
            self.layout.gutter = 0

        self.menu_bar.width = self.layout.w

    def _mount_components(self) -> None:
        self.app.clear_components()

        if self._show_graphics:
            self.app.add(GameWorld())

        self.app.add(TextPane(text_renderer=TextRenderer()))

        if self._show_graphics:
            self.app.add(Divider())

        self.app.add(InputCommand(gate=self.gate, on_command=self.handle_command))
        self.app.add(UIOverlay(
            menu_bar=self.menu_bar,
            message_dialog=self.message_dialog,
            connection_settings=self.connection_settings,
            display_settings=self.display_settings,
        ))
        self.app.add(Cursor(cursor_renderer=CursorRenderer()))

    def _update_graphics_menu_item_label(self) -> None:
        if self._toggle_graphics_menu_item is None:
            return
        self._toggle_graphics_menu_item.label = "Hide Graphics" if self._show_graphics else "Show Graphics"

    def _setup_menus(self) -> None:
        file_menu = self.menu_bar.add_menu("File")
        file_menu.add_item("Hide Graphics", self.toggle_graphics)
        self._toggle_graphics_menu_item = file_menu.items[-1]
        file_menu.add_item("Close", self.close_app)
        settings_menu = self.menu_bar.add_menu("Settings")
        settings_menu.add_item("Connections", self.show_connection_settings)
        settings_menu.add_item("Display", self.show_display_settings)
        pane_width = min(300, self.layout.w - 40)
        pane_height = 300
        pane_x = (self.layout.w - pane_width) // 2
        pane_y = (self.layout.h - pane_height) // 2

        self.message_dialog = MessageDialog()
        self.connection_settings = ConnectionSettings(pane_x, pane_y, pane_width, pane_height, self.message_dialog,
                                                      on_connect_callback=self._on_connection_established,
                                                      install_dir=self.install_dir)

        display_pane_height = min(380, self.layout.h - 20)
        display_pane_y = max(10, (self.layout.h - display_pane_height) // 2)

        self.display_settings = DisplaySettings(pane_x, display_pane_y, pane_width, display_pane_height, self.message_dialog, self, install_dir=self.install_dir)
