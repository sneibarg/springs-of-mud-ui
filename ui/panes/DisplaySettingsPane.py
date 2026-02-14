import json
import os
import pyxel

from component.button.Button import Button
from component.Dropdown import UIDropdown
from component.field.NumberField import NumberField
from component.geometry.Rect import Rect


class DisplaySettingsPane:
    def __init__(self, x: int, y: int, width: int, height: int, message_dialog, mud_client_ui=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.visible = False
        self.message_dialog = message_dialog
        self.mud_client_ui = mud_client_ui
        self.status_message = ""
        self.status_color = 7
        self.font_scale_options = ["1x", "2x", "3x"]
        self.line_spacing_options = ["6", "7", "8", "9", "10"]
        self.font_options = ["pyxel_default", "dos_8x8", "press_start_2p"]
        self.chars_per_line = "40"
        self.visible_lines = "20"
        self.font_scale = 1
        self.line_spacing = 7
        self.window_height = "400"
        self.scroll_buffer = "500"
        self.game_pane_width = "256"
        self.text_pane_width = "400"
        self.font_name = "pyxel_default"
        self._load_settings()
        self._build_components()

    def show(self) -> None:
        self.visible = True

    def hide(self) -> None:
        self.visible = False
        self._close_all_dropdowns()
        self._blur_all_fields()

    def _build_components(self) -> None:
        fx = self.x + 20
        fw = self.width - 40
        h = 12

        self.panel = Rect(self.x, self.y, self.width, self.height)
        self.title_bar = Rect(self.x, self.y, self.width, 20)
        self.close_btn = Rect(self.x + self.width - 15, self.y + 5, 10, 10)

        self.f_chars = NumberField(Rect(fx, self.y + 43, fw, h), self.chars_per_line, 20, 200)
        self.f_lines = NumberField(Rect(fx, self.y + 76, fw, h), self.visible_lines, 10, 100)

        self.dd_font_scale = UIDropdown(Rect(fx, self.y + 109, fw, h), self.font_scale_options, f"{self.font_scale}x")
        self.dd_line_spacing = UIDropdown(Rect(fx, self.y + 142, fw, h), self.line_spacing_options, str(self.line_spacing))
        self.dd_font = UIDropdown(Rect(fx, self.y + 175, fw, h), self.font_options, self.font_name)

        self.f_window_h = NumberField(Rect(fx, self.y + 208, fw, h), self.window_height, 200, 800)
        self.f_scroll = NumberField(Rect(fx, self.y + 241, fw, h), self.scroll_buffer, 100, 10000)
        self.f_game_w = NumberField(Rect(fx, self.y + 274, fw, h), self.game_pane_width, 100, 1920)
        self.f_text_w = NumberField(Rect(fx, self.y + 307, fw, h), self.text_pane_width, 160, 1920)

        by = self.y + self.height - 30
        self.btn_reset = Button(Rect(self.x + 20, by, 50, 15), "Reset", 2, 6, self._reset_settings)
        self.btn_save = Button(Rect(self.x + 80, by, 50, 15), "Save", 2, 3, self._save_settings)
        self.btn_apply = Button(Rect(self.x + 140, by, 60, 15), "Apply", 3, 11, self._apply_settings)

    def _close_all_dropdowns(self) -> None:
        self.dd_font_scale.close()
        self.dd_line_spacing.close()
        self.dd_font.close()

    def _blur_all_fields(self) -> None:
        for f in (self.f_chars, self.f_lines, self.f_window_h, self.f_scroll, self.f_game_w, self.f_text_w):
            f.blur()

    @staticmethod
    def _get_settings_path() -> str:
        resources_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "resources")
        os.makedirs(resources_dir, exist_ok=True)
        return os.path.join(resources_dir, "display_settings.json")

    def _load_settings(self) -> None:
        try:
            p = self._get_settings_path()
            if os.path.exists(p):
                with open(p, "r") as f:
                    s = json.load(f)
                self.chars_per_line = str(s.get("chars_per_line", 40))
                self.visible_lines = str(s.get("visible_lines", 20))
                self.font_scale = int(s.get("font_scale", 1))
                self.line_spacing = int(s.get("line_spacing", 7))
                self.window_height = str(s.get("window_height", 400))
                self.scroll_buffer = str(s.get("scroll_buffer", 500))
                self.game_pane_width = str(s.get("game_pane_width", 256))
                self.text_pane_width = str(s.get("text_pane_width", 400))
                self.font_name = s.get("font_name", "pyxel_default")
        except Exception as e:
            print(f"Failed to load display settings: {e}")

    def _sync_from_widgets(self) -> None:
        self.chars_per_line = self.f_chars.value
        self.visible_lines = self.f_lines.value
        self.window_height = self.f_window_h.value
        self.scroll_buffer = self.f_scroll.value
        self.game_pane_width = self.f_game_w.value
        self.text_pane_width = self.f_text_w.value

        self.font_scale = int(str(self.dd_font_scale.value).replace("x", ""))
        self.line_spacing = int(str(self.dd_line_spacing.value))
        self.font_name = str(self.dd_font.value)

    def _save_settings(self) -> None:
        try:
            self._sync_from_widgets()
            settings = {
                "chars_per_line": int(self.chars_per_line),
                "visible_lines": int(self.visible_lines),
                "font_scale": int(self.font_scale),
                "line_spacing": int(self.line_spacing),
                "window_height": int(self.window_height),
                "scroll_buffer": int(self.scroll_buffer),
                "game_pane_width": int(self.game_pane_width),
                "text_pane_width": int(self.text_pane_width),
                "font_name": self.font_name,
            }
            p = self._get_settings_path()
            with open(p, "w") as f:
                json.dump(settings, f, indent=2)

            self._apply_settings()
            self.status_message = "Settings saved and applied"
            self.status_color = 11
        except Exception as e:
            self.status_message = f"Failed to save: {str(e)[:20]}"
            self.status_color = 8

    def _apply_settings(self) -> None:
        self._sync_from_widgets()
        if self.mud_client_ui:
            self.mud_client_ui.apply_display_settings(
                int(self.chars_per_line),
                int(self.visible_lines),
                int(self.font_scale),
                int(self.line_spacing),
                int(self.window_height),
                int(self.scroll_buffer),
                int(self.game_pane_width),
                int(self.text_pane_width),
                self.font_name,
            )
        self.status_message = "Settings applied (restart for full effect)"
        self.status_color = 11

    def _reset_settings(self) -> None:
        self.f_chars.value = "40"
        self.f_lines.value = "20"
        self.dd_font_scale.value = "1x"
        self.dd_line_spacing.value = "7"
        self.dd_font.value = "pyxel_default"
        self.f_window_h.value = "400"
        self.f_scroll.value = "500"
        self.f_game_w.value = "256"
        self.f_text_w.value = "400"
        self.status_message = "Settings reset to defaults"
        self.status_color = 11

    def update(self) -> None:
        if not self.visible:
            return

        mx, my = pyxel.mouse_x, pyxel.mouse_y
        click = pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT)
        if click and self.close_btn.contains(mx, my):
            self.hide()
            return

        self._update_fields(mx, my, click)
        self._update_dropdowns(mx, my, click)
        self._update_buttons(mx, my, click)

    def _update_fields(self, mx: int, my: int, click: bool) -> None:
        for f in (self.f_chars, self.f_lines, self.f_window_h, self.f_scroll, self.f_game_w, self.f_text_w):
            f.update(mx, my, click)

    def _update_dropdowns(self, mx: int, my: int, click: bool) -> None:
        self.dd_font_scale.update(mx, my, click)
        if self.dd_font_scale.open:
            self.dd_line_spacing.close()
            self.dd_font.close()

        self.dd_line_spacing.update(mx, my, click)
        if self.dd_line_spacing.open:
            self.dd_font_scale.close()
            self.dd_font.close()

        self.dd_font.update(mx, my, click)
        if self.dd_font.open:
            self.dd_font_scale.close()
            self.dd_line_spacing.close()

    def _update_buttons(self, mx: int, my: int, click: bool) -> None:
        self.btn_reset.update(mx, my, click)
        self.btn_save.update(mx, my, click)
        self.btn_apply.update(mx, my, click)

    def draw(self) -> None:
        if not self.visible:
            return

        self._draw_overlay()
        self._draw_frame()
        self._draw_title()
        self._draw_close()
        self._draw_widgets()
        self._draw_buttons()
        self._draw_dropdown_popups()
        self._draw_status()

    @staticmethod
    def _draw_overlay() -> None:
        for y in range(0, pyxel.height, 2):
            for x in range(0, pyxel.width, 2):
                pyxel.pset(x, y, 0)

    def _draw_frame(self) -> None:
        self.panel.fill(1)
        self.panel.border(5)

    def _draw_title(self) -> None:
        self.title_bar.fill(5)
        pyxel.text(self.x + 10, self.y + 7, "Display Settings", 7)

    def _draw_close(self) -> None:
        self.close_btn.fill(8)
        pyxel.text(self.close_btn.x + 2, self.close_btn.y + 2, "X", 7)

    def _draw_widgets(self) -> None:
        self.f_chars.draw("Characters per line:")
        self.f_lines.draw("Visible lines:")

        self.dd_font_scale.draw("Font scale:")
        self.dd_line_spacing.draw("Line spacing:")
        self.dd_font.draw("Font:")

        self.f_window_h.draw("Window height:")
        self.f_scroll.draw("Scroll buffer (lines):")
        self.f_game_w.draw("Game pane width (px):")
        self.f_text_w.draw("Text pane width (px):")

    def _draw_buttons(self) -> None:
        self.btn_reset.draw()
        self.btn_save.draw()
        self.btn_apply.draw()

    def _draw_dropdown_popups(self) -> None:  # Popups LAST so they sit above the dim/background/panel
        self.dd_font_scale.draw_popup()
        self.dd_line_spacing.draw_popup()
        self.dd_font.draw_popup()

    def _draw_status(self) -> None:
        if self.status_message:
            pyxel.text(self.x + 20, self.y + self.height - 10, self.status_message, self.status_color)
