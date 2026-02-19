from __future__ import annotations
from dataclasses import dataclass
from component.render.TextRenderer import TextRenderer


@dataclass
class TextPane:
    text_renderer: TextRenderer
    title: str = "TEXT / COMMAND"
    z_index: int = 10

    def update(self, ctx) -> None:
        mx, my = ctx.input.mx, ctx.input.my
        over_text = (ctx.layout.ui_x <= mx < ctx.layout.ui_x + ctx.layout.ui_w and 10 <= my < ctx.layout.h)
        if not over_text:
            return

        if ctx.input.wheel > 0:
            ctx.scroll_offset = min(ctx.scroll_offset + 3, max(0, len(ctx.scrollback) - 1))
        elif ctx.input.wheel < 0:
            ctx.scroll_offset = max(0, ctx.scroll_offset - 3)

    def draw(self, ctx) -> None:
        blink_on = ((ctx.input.frame_count // 20) % 2 == 0)

        self.text_renderer.draw_pane(
            ctx,
            x0=ctx.layout.ui_x,
            y0=10,
            w=ctx.layout.ui_w,
            h=ctx.layout.h - 10,
            title=self.title,
            scrollback=ctx.scrollback,
            scroll_offset=ctx.scroll_offset,
            visible_lines=ctx.visible_lines,
            line_spacing=ctx.line_spacing,
            font_scale=ctx.font_scale,
            prompt="> ",
            input_buf=ctx.text_input.buf,
            input_cursor=ctx.text_input.cursor,
            has_selection=ctx.text_input.has_selection(),
            selection_start=ctx.text_input.selection_start,
            selection_end=ctx.text_input.selection_end,
            blink_on=blink_on,
        )
