from __future__ import annotations

from collections import deque
from typing import Deque, List

from component.input.TextInput import TextInput
from component.render.PyxelGfx import PyxelGfx
from engine.context.EngineContext import EngineContext
from engine.context.GameComponent import GameComponent
from engine.PyxelDriver import PyxelDriver
from ui.layout import Layout


class MudClientApp:
    def __init__(
        self,
        *,
        title: str,
        layout: Layout,
        text_input: TextInput,
        scrollback: Deque[str],
        scroll_offset: int,
        visible_lines: int,
        line_spacing: int,
        font_scale: int,
        poll_callback=None,
    ):
        self.layout = layout
        self.text_input = text_input
        self.scrollback = scrollback
        self.scroll_offset = scroll_offset
        self.visible_lines = visible_lines
        self.line_spacing = line_spacing
        self.font_scale = font_scale
        self.poll_callback = poll_callback
        self.driver = PyxelDriver(title=title, w=layout.w, h=layout.h)
        self._components: List[GameComponent] = []
        self._character_list = []
        self._ctx = EngineContext(
            layout=self.layout,
            input=self.driver.sample_input(),
            text_input=self.text_input,
            scrollback=self.scrollback,
            scroll_offset=self.scroll_offset,
            visible_lines=self.visible_lines,
            line_spacing=self.line_spacing,
            font_scale=self.font_scale,
            log=self.log,
            quit=self.driver.quit,
            gfx=PyxelGfx(),
            apply_display_settings=self.apply_display_settings,
            set_character_list=self.set_character_list,
        )

    def add(self, c: GameComponent) -> None:
        self._components.append(c)
        self._components.sort(key=lambda x: getattr(x, "z_index", 0))

    def set_text_metrics(self, *, visible_lines: int, line_spacing: int, font_scale: int) -> None:
        self.visible_lines = visible_lines
        self.line_spacing = line_spacing
        self.font_scale = font_scale

    def set_scrollback(self, scrollback: Deque[str]) -> None:
        self.scrollback = scrollback

    def set_scroll_offset(self, v: int) -> None:
        self.scroll_offset = v

    def set_character_list(self, chars):
        self._character_list = list(chars)
        self._ctx.log(f"Character list updated: {len(self._character_list)} character(s) available.")

    def log(self, msg: str) -> None:
        self.scrollback.append(msg)

    def run(self) -> None:
        self.driver.run(self.update, self.draw)

    def update(self) -> None:
        # Poll for telnet messages if callback provided
        if self.poll_callback:
            self.poll_callback()

        self._ctx.input = self.driver.sample_input()
        self._ctx.scrollback = self.scrollback
        self._ctx.scroll_offset = self.scroll_offset
        self._ctx.visible_lines = self.visible_lines
        self._ctx.line_spacing = self.line_spacing
        self._ctx.font_scale = self.font_scale

        for c in self._components:
            c.update(self._ctx)

        self.scroll_offset = self._ctx.scroll_offset
        self.scrollback = self._ctx.scrollback

    def draw(self) -> None:
        self.driver.clear(0)
        for c in self._components:
            c.draw(self._ctx)

    def apply_display_settings(
            self,
            chars_per_line: int,
            visible_lines: int,
            font_scale: int,
            line_spacing: int,
            window_height: int | None = None,
            scroll_buffer: int | None = None,
            game_pane_width: int | None = None,
            text_pane_width: int | None = None,
            font_name: str | None = None,
    ) -> None:
        self.chars_per_line = int(chars_per_line)
        self.set_text_metrics(visible_lines=int(visible_lines), line_spacing=int(line_spacing), font_scale=int(font_scale))

        if scroll_buffer is not None and int(scroll_buffer) != self.scrollback.maxlen:
            old = list(self.scrollback)
            self.scrollback = deque(old, maxlen=int(scroll_buffer))

        if window_height is not None:
            self.layout.h = int(window_height)
            self.layout.game_h = int(window_height)

        if game_pane_width is not None:
            self.layout.game_w = int(game_pane_width)

        if text_pane_width is not None:
            self.layout.ui_w = int(text_pane_width)

        if font_name:
            self._ctx.log(f"Font requested: {font_name}")

        self._ctx.layout = self.layout
        self._ctx.scrollback = self.scrollback

        self._ctx.log(
            f"Settings applied: chars/line={self.chars_per_line}, "
            f"visible_lines={self.visible_lines}, font_scale={self.font_scale}, "
            f"line_spacing={self.line_spacing}, game_w={self.layout.game_w}, ui_w={self.layout.ui_w}, h={self.layout.h}"
        )

