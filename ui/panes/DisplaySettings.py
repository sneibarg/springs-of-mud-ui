from __future__ import annotations
from component.button.Button import Button
from component.input import NumberField
from component.geometry.Rect import Rect
from component.modal.Dropdown import Dropdown
from component.modal.ModalFrame import ModalFrame
from component.render.TextField import TextField

import json
import os


class DisplaySettings:
    def __init__(self, x: int, y: int, width: int, height: int, message_dialog=None, mud_client_ui=None):
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
        self.tf = TextField()
        self._build_components()

    def show(self) -> None:
        self.visible = True
        self._blur_all_fields()
        self._close_all_dropdowns()

    def hide(self) -> None:
        self.visible = False
        self._close_all_dropdowns()
        self._blur_all_fields()

    def toggle(self) -> None:
        self.hide() if self.visible else self.show()

    def _build_components(self) -> None:
        fx = self.x + 20
        fw = self.width - 40
        h = 12

        panel = Rect(self.x, self.y, self.width, self.height)
        self.frame = ModalFrame(panel, "Display Settings", text=self.tf)
        self.f_chars = NumberField(Rect(fx, self.y + 43, fw, h), self.chars_per_line, 20, 200)
        self.f_lines = NumberField(Rect(fx, self.y + 76, fw, h), self.visible_lines, 10, 100)
        self.dd_font_scale = Dropdown(Rect(fx, self.y + 109, fw, h), self.font_scale_options, f"{self.font_scale}x")
        self.dd_line_spacing = Dropdown(Rect(fx, self.y + 142, fw, h), self.line_spacing_options, str(self.line_spacing))
        self.dd_font = Dropdown(Rect(fx, self.y + 175, fw, h), self.font_options, self.font_name)

        self.f_window_h = NumberField(Rect(fx, self.y + 208, fw, h), self.window_height, 200, 800)
        self.f_scroll = NumberField(Rect(fx, self.y + 241, fw, h), self.scroll_buffer, 100, 10000)
        self.f_game_w = NumberField(Rect(fx, self.y + 274, fw, h), self.game_pane_width, 100, 1920)
        self.f_text_w = NumberField(Rect(fx, self.y + 307, fw, h), self.text_pane_width, 160, 1920)

        by = self.y + self.height - 30
        self.btn_reset = Button(Rect(self.x + 20, by, 50, 15), "Reset", 2, 6, self._reset_settings)
        self.btn_save = Button(Rect(self.x + 80, by, 50, 15), "Save", 2, 3, self._save_settings)
        self.btn_apply = Button(Rect(self.x + 140, by, 60, 15), "Apply", 3, 11, self._apply_settings)
        self._status_x = self.x + 20
        self._status_y = self.y + self.height - 10

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

            else:
                return

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

            # save implies apply
            self._apply_settings()
            self._set_status("Settings saved and applied", 11)

        except Exception as e:
            self._set_status(f"Failed to save: {str(e)[:40]}", 8)

    def _apply_settings(self) -> None:
        self._sync_from_widgets()
        if self._last_ctx is not None:
            self._last_ctx.apply_display_settings(
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
        self._set_status("Settings applied (restart for full effect)", 11)

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
        self._set_status("Settings reset to defaults", 11)

    def update(self, ctx) -> None:
        if not self.visible:
            return

        self._ctx = ctx
        self._last_ctx = ctx

        mx, my, click = ctx.input.mx, ctx.input.my, ctx.input.click

        if self.frame.did_close(mx, my, click):
            self.hide()
            return

        for f in (self.f_chars, self.f_lines, self.f_window_h, self.f_scroll, self.f_game_w, self.f_text_w):
            f.update(ctx)

        self.dd_font_scale.update(ctx)
        if self.dd_font_scale.open:
            self.dd_line_spacing.close()
            self.dd_font.close()

        self.dd_line_spacing.update(ctx)
        if self.dd_line_spacing.open:
            self.dd_font_scale.close()
            self.dd_font.close()

        self.dd_font.update(ctx)
        if self.dd_font.open:
            self.dd_font_scale.close()
            self.dd_line_spacing.close()

        self.btn_reset.update(ctx)
        self.btn_save.update(ctx)
        self.btn_apply.update(ctx)

    def draw(self, ctx) -> None:
        if not self.visible:
            return

        self.frame.draw(ctx)

        self.f_chars.draw(ctx, "Characters per line:")
        self.f_lines.draw(ctx, "Visible lines:")

        self.dd_font_scale.draw(ctx, "Font scale:")
        self.dd_line_spacing.draw(ctx, "Line spacing:")
        self.dd_font.draw(ctx, "Font:")

        self.f_window_h.draw(ctx, "Window height:")
        self.f_scroll.draw(ctx, "Scroll buffer (lines):")
        self.f_game_w.draw(ctx, "Game pane width (px):")
        self.f_text_w.draw(ctx, "Text pane width (px):")

        self.btn_reset.draw(ctx)
        self.btn_save.draw(ctx)
        self.btn_apply.draw(ctx)

        self.dd_font_scale.draw_popup(ctx)
        self.dd_line_spacing.draw_popup(ctx)
        self.dd_font.draw_popup(ctx)

        if self.status_message:
            self.tf.draw_text(ctx, x=self._status_x, y=self._status_y, text=self.status_message, col=self.status_color)

    def _set_status(self, msg: str, col: int) -> None:
        self.status_message = msg
        self.status_color = col

    _ctx = None
