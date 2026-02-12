import pyxel
import json
import os
from typing import Optional, Dict


class DisplaySettingsPane:
    def __init__(self, x: int, y: int, width: int, height: int, message_dialog, mud_client_ui=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.visible = False
        self.message_dialog = message_dialog
        self.mud_client_ui = mud_client_ui
        
        # Display settings (stored as strings for editing)
        self.chars_per_line = "40"
        self.visible_lines = "20"
        self.font_scale = 1  # Pyxel supports font scaling
        self.line_spacing = 7
        self.window_height = "400"  # Increased default to fit display settings pane
        self.scroll_buffer = "500"
        self.game_pane_width = "256"
        self.text_pane_width = "400"  # Increased default for better visibility
        
        # UI state
        self.active_field: Optional[str] = None
        self.cursor_pos = 0
        self.status_message = ""
        self.status_color = 7
        
        # Button hover states
        self.save_button_hovered = False
        self.reset_button_hovered = False
        self.apply_button_hovered = False
        
        # Dropdown states
        self.font_scale_options = [1, 2, 3]
        self.line_spacing_options = [6, 7, 8, 9, 10]
        self.font_scale_dropdown_open = False
        self.line_spacing_dropdown_open = False
        
        self._load_settings()

    def show(self) -> None:
        self.visible = True

    def hide(self) -> None:
        self.visible = False
        self.font_scale_dropdown_open = False
        self.line_spacing_dropdown_open = False

    def toggle(self) -> None:
        self.visible = not self.visible

    def _get_settings_path(self) -> str:
        resources_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "resources")
        os.makedirs(resources_dir, exist_ok=True)
        return os.path.join(resources_dir, "display_settings.json")

    def _load_settings(self) -> None:
        try:
            settings_path = self._get_settings_path()
            if os.path.exists(settings_path):
                with open(settings_path, "r") as f:
                    settings = json.load(f)
                    self.chars_per_line = str(settings.get("chars_per_line", 40))
                    self.visible_lines = str(settings.get("visible_lines", 20))
                    self.font_scale = settings.get("font_scale", 1)
                    self.line_spacing = settings.get("line_spacing", 7)
                    self.window_height = str(settings.get("window_height", 400))
                    self.scroll_buffer = str(settings.get("scroll_buffer", 500))
                    self.game_pane_width = str(settings.get("game_pane_width", 256))
                    self.text_pane_width = str(settings.get("text_pane_width", 400))
        except Exception as e:
            print(f"Failed to load display settings: {e}")

    def _save_settings(self) -> None:
        try:
            settings = {
                "chars_per_line": int(self.chars_per_line),
                "visible_lines": int(self.visible_lines),
                "font_scale": self.font_scale,
                "line_spacing": self.line_spacing,
                "window_height": int(self.window_height),
                "scroll_buffer": int(self.scroll_buffer),
                "game_pane_width": int(self.game_pane_width),
                "text_pane_width": int(self.text_pane_width)
            }
            settings_path = self._get_settings_path()
            with open(settings_path, "w") as f:
                json.dump(settings, f, indent=2)

            # Also apply the settings when saving
            self._apply_settings()
            self.status_message = "Settings saved and applied"
            self.status_color = 11
        except Exception as e:
            self.status_message = f"Failed to save: {str(e)[:20]}"
            self.status_color = 8

    def _apply_settings(self) -> None:
        if self.mud_client_ui:
            self.mud_client_ui.apply_display_settings(
                int(self.chars_per_line),
                int(self.visible_lines),
                self.font_scale,
                self.line_spacing,
                int(self.window_height),
                int(self.scroll_buffer),
                int(self.game_pane_width),
                int(self.text_pane_width)
            )
            self.status_message = "Settings applied (restart for full effect)"
            self.status_color = 11

    def _reset_settings(self) -> None:
        self.chars_per_line = "40"
        self.visible_lines = "20"
        self.font_scale = 1
        self.line_spacing = 7
        self.window_height = "400"
        self.scroll_buffer = "500"
        self.game_pane_width = "256"
        self.text_pane_width = "400"
        self.status_message = "Settings reset to defaults"
        self.status_color = 11

    def _handle_number_input(self, field: str, current_value: str, min_val: int, max_val: int) -> str:
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

        # Only allow digits
        for i in range(10):
            key = getattr(pyxel, f"KEY_{i}", None)
            if key and pyxel.btnp(key):
                result = result[:self.cursor_pos] + str(i) + result[self.cursor_pos:]
                self.cursor_pos += 1

        # Validate the number is within range
        if result:
            try:
                val = int(result)
                if val > max_val:
                    result = str(max_val)
                    self.cursor_pos = len(result)
            except ValueError:
                result = str(min_val)
                self.cursor_pos = len(result)
        else:
            result = "0"
            self.cursor_pos = 1

        return result

    def update(self) -> None:
        if not self.visible:
            return

        mx, my = pyxel.mouse_x, pyxel.mouse_y
        
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            # Close button
            if self.x + self.width - 15 <= mx < self.x + self.width - 5 and self.y + 5 <= my < self.y + 15:
                self.hide()
                return
            
            # Chars per line field
            elif self.x + 20 <= mx < self.x + self.width - 20 and self.y + 43 <= my < self.y + 55:
                self.active_field = "chars_per_line"
                self.cursor_pos = len(self.chars_per_line)
                self.font_scale_dropdown_open = False
                self.line_spacing_dropdown_open = False

            # Visible lines field
            elif self.x + 20 <= mx < self.x + self.width - 20 and self.y + 76 <= my < self.y + 88:
                self.active_field = "visible_lines"
                self.cursor_pos = len(self.visible_lines)
                self.font_scale_dropdown_open = False
                self.line_spacing_dropdown_open = False

            # Font scale dropdown
            elif self.x + 20 <= mx < self.x + self.width - 20 and self.y + 109 <= my < self.y + 121:
                self.active_field = None
                self.font_scale_dropdown_open = not self.font_scale_dropdown_open
                self.line_spacing_dropdown_open = False
            elif self.font_scale_dropdown_open:
                # Check dropdown items
                for idx, option in enumerate(self.font_scale_options):
                    option_y = self.y + 121 + idx * 12
                    if self.x + 20 <= mx < self.x + self.width - 20 and option_y <= my < option_y + 12:
                        self.font_scale = option
                        self.font_scale_dropdown_open = False
                        break

            # Line spacing dropdown
            elif self.x + 20 <= mx < self.x + self.width - 20 and self.y + 142 <= my < self.y + 154:
                self.active_field = None
                self.line_spacing_dropdown_open = not self.line_spacing_dropdown_open
                self.font_scale_dropdown_open = False
            elif self.line_spacing_dropdown_open:
                # Check dropdown items
                for idx, option in enumerate(self.line_spacing_options):
                    option_y = self.y + 154 + idx * 12
                    if self.x + 20 <= mx < self.x + self.width - 20 and option_y <= my < option_y + 12:
                        self.line_spacing = option
                        self.line_spacing_dropdown_open = False
                        break

            # Window height field
            elif self.x + 20 <= mx < self.x + self.width - 20 and self.y + 175 <= my < self.y + 187:
                self.active_field = "window_height"
                self.cursor_pos = len(self.window_height)
                self.font_scale_dropdown_open = False
                self.line_spacing_dropdown_open = False

            # Scroll buffer field
            elif self.x + 20 <= mx < self.x + self.width - 20 and self.y + 208 <= my < self.y + 220:
                self.active_field = "scroll_buffer"
                self.cursor_pos = len(self.scroll_buffer)
                self.font_scale_dropdown_open = False
                self.line_spacing_dropdown_open = False

            # Game pane width field
            elif self.x + 20 <= mx < self.x + self.width - 20 and self.y + 241 <= my < self.y + 253:
                self.active_field = "game_pane_width"
                self.cursor_pos = len(self.game_pane_width)
                self.font_scale_dropdown_open = False
                self.line_spacing_dropdown_open = False

            # Text pane width field
            elif self.x + 20 <= mx < self.x + self.width - 20 and self.y + 274 <= my < self.y + 286:
                self.active_field = "text_pane_width"
                self.cursor_pos = len(self.text_pane_width)
                self.font_scale_dropdown_open = False
                self.line_spacing_dropdown_open = False

            # Reset button
            elif self.x + 20 <= mx < self.x + 70 and self.y + self.height - 30 <= my < self.y + self.height - 15:
                self._reset_settings()
                self.font_scale_dropdown_open = False
                self.line_spacing_dropdown_open = False
            
            # Save button
            elif self.x + 80 <= mx < self.x + 130 and self.y + self.height - 30 <= my < self.y + self.height - 15:
                self._save_settings()
                self.font_scale_dropdown_open = False
                self.line_spacing_dropdown_open = False
            
            # Apply button
            elif self.x + 140 <= mx < self.x + 200 and self.y + self.height - 30 <= my < self.y + self.height - 15:
                self._apply_settings()
                self.font_scale_dropdown_open = False
                self.line_spacing_dropdown_open = False
            
            else:
                self.active_field = None
                self.font_scale_dropdown_open = False
                self.line_spacing_dropdown_open = False

        # Handle text input for number fields
        if self.active_field == "chars_per_line":
            self.chars_per_line = self._handle_number_input("chars_per_line", self.chars_per_line, 20, 200)
        elif self.active_field == "visible_lines":
            self.visible_lines = self._handle_number_input("visible_lines", self.visible_lines, 10, 100)
        elif self.active_field == "window_height":
            self.window_height = self._handle_number_input("window_height", self.window_height, 200, 800)
        elif self.active_field == "scroll_buffer":
            self.scroll_buffer = self._handle_number_input("scroll_buffer", self.scroll_buffer, 100, 10000)
        elif self.active_field == "game_pane_width":
            self.game_pane_width = self._handle_number_input("game_pane_width", self.game_pane_width, 100, 1920)
        elif self.active_field == "text_pane_width":
            self.text_pane_width = self._handle_number_input("text_pane_width", self.text_pane_width, 160, 1920)

        # Update button hover states
        self.reset_button_hovered = (self.x + 20 <= mx < self.x + 70 and self.y + self.height - 30 <= my < self.y + self.height - 15)
        self.save_button_hovered = (self.x + 80 <= mx < self.x + 130 and self.y + self.height - 30 <= my < self.y + self.height - 15)
        self.apply_button_hovered = (self.x + 140 <= mx < self.x + 200 and self.y + self.height - 30 <= my < self.y + self.height - 15)

    def draw(self) -> None:
        if not self.visible:
            return

        # Semi-transparent overlay
        for y in range(0, pyxel.height, 2):
            for x in range(0, pyxel.width, 2):
                pyxel.pset(x, y, 0)

        # Main panel
        pyxel.rect(self.x, self.y, self.width, self.height, 1)
        pyxel.rectb(self.x, self.y, self.width, self.height, 5)

        # Title bar
        pyxel.rect(self.x, self.y, self.width, 20, 5)
        pyxel.text(self.x + 10, self.y + 7, "Display Settings", 7)

        # Close button
        pyxel.rect(self.x + self.width - 15, self.y + 5, 10, 10, 8)
        pyxel.text(self.x + self.width - 13, self.y + 7, "X", 7)

        # Chars per line
        pyxel.text(self.x + 20, self.y + 30, "Characters per line:", 7)
        self._draw_number_field(self.x + 20, self.y + 43, self.width - 40, 12,
                                self.chars_per_line, self.active_field == "chars_per_line")

        # Visible lines
        pyxel.text(self.x + 20, self.y + 63, "Visible lines:", 7)
        self._draw_number_field(self.x + 20, self.y + 76, self.width - 40, 12,
                                self.visible_lines, self.active_field == "visible_lines")

        # Font scale dropdown
        pyxel.text(self.x + 20, self.y + 96, "Font scale:", 7)
        self._draw_dropdown(self.x + 20, self.y + 109, self.width - 40, 12,
                           f"{self.font_scale}x", self.font_scale_dropdown_open)
        if self.font_scale_dropdown_open:
            for idx, option in enumerate(self.font_scale_options):
                option_y = self.y + 121 + idx * 12
                pyxel.rect(self.x + 20, option_y, self.width - 40, 12, 2)
                pyxel.rectb(self.x + 20, option_y, self.width - 40, 12, 7)
                pyxel.text(self.x + 24, option_y + 3, f"{option}x", 7)

        # Line spacing dropdown
        pyxel.text(self.x + 20, self.y + 129, "Line spacing:", 7)
        self._draw_dropdown(self.x + 20, self.y + 142, self.width - 40, 12,
                           str(self.line_spacing), self.line_spacing_dropdown_open)
        if self.line_spacing_dropdown_open:
            for idx, option in enumerate(self.line_spacing_options):
                option_y = self.y + 154 + idx * 12
                pyxel.rect(self.x + 20, option_y, self.width - 40, 12, 2)
                pyxel.rectb(self.x + 20, option_y, self.width - 40, 12, 7)
                pyxel.text(self.x + 24, option_y + 3, str(option), 7)

        # Window height
        pyxel.text(self.x + 20, self.y + 162, "Window height:", 7)
        self._draw_number_field(self.x + 20, self.y + 175, self.width - 40, 12,
                                self.window_height, self.active_field == "window_height")

        # Scroll buffer
        pyxel.text(self.x + 20, self.y + 195, "Scroll buffer (lines):", 7)
        self._draw_number_field(self.x + 20, self.y + 208, self.width - 40, 12,
                                self.scroll_buffer, self.active_field == "scroll_buffer")

        # Game pane width
        pyxel.text(self.x + 20, self.y + 228, "Game pane width (px):", 7)
        self._draw_number_field(self.x + 20, self.y + 241, self.width - 40, 12,
                                self.game_pane_width, self.active_field == "game_pane_width")

        # Text pane width
        pyxel.text(self.x + 20, self.y + 261, "Text pane width (px):", 7)
        self._draw_number_field(self.x + 20, self.y + 274, self.width - 40, 12,
                                self.text_pane_width, self.active_field == "text_pane_width")

        # Action buttons
        reset_color = 6 if self.reset_button_hovered else 2
        pyxel.rect(self.x + 20, self.y + self.height - 30, 50, 15, reset_color)
        pyxel.rectb(self.x + 20, self.y + self.height - 30, 50, 15, 7)
        pyxel.text(self.x + 30, self.y + self.height - 25, "Reset", 7)

        save_color = 3 if self.save_button_hovered else 2
        pyxel.rect(self.x + 80, self.y + self.height - 30, 50, 15, save_color)
        pyxel.rectb(self.x + 80, self.y + self.height - 30, 50, 15, 7)
        pyxel.text(self.x + 91, self.y + self.height - 25, "Save", 7)

        apply_color = 11 if self.apply_button_hovered else 3
        pyxel.rect(self.x + 140, self.y + self.height - 30, 60, 15, apply_color)
        pyxel.rectb(self.x + 140, self.y + self.height - 30, 60, 15, 7)
        pyxel.text(self.x + 149, self.y + self.height - 25, "Apply", 7)

        # Status message
        if self.status_message:
            pyxel.text(self.x + 20, self.y + self.height - 10, self.status_message, self.status_color)

    def _draw_number_field(self, x: int, y: int, w: int, h: int, value: str, is_active: bool) -> None:
        pyxel.rect(x, y, w, h, 0)
        border_color = 11 if is_active else 5
        pyxel.rectb(x, y, w, h, border_color)

        # Display the string value
        display_text = value
        visible_text = display_text[-((w - 8) // 4):] if len(display_text) * 4 > w - 8 else display_text
        pyxel.text(x + 4, y + 3, visible_text, 7)

        if is_active and (pyxel.frame_count // 20) % 2 == 0:
            # Show cursor at cursor position
            cursor_offset = min(self.cursor_pos, len(visible_text))
            cursor_x = x + 4 + cursor_offset * 4
            if cursor_x < x + w - 2:
                pyxel.rect(cursor_x, y + 3, 3, 5, 7)

    def _draw_dropdown(self, x: int, y: int, w: int, h: int, text: str, is_open: bool) -> None:
        pyxel.rect(x, y, w, h, 0)
        border_color = 11 if is_open else 5
        pyxel.rectb(x, y, w, h, border_color)
        pyxel.text(x + 4, y + 3, text, 7)
        # Draw dropdown arrow
        arrow = "v" if not is_open else "^"
        pyxel.text(x + w - 8, y + 3, arrow, 7)
