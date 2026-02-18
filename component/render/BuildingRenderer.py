from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, Sequence
from component.geometry import Rect
from component.render.abstract.Renderable import Renderable
from domain.Building import Building


@dataclass(frozen=True)
class BuildingStyle:
    wall_col: int = 6
    wall_border_col: int = 5
    roof_col: int = 8
    roof_border_col: int = 7
    door_col: int = 4
    door_border_col: int = 1
    window_col: int = 12
    window_border_col: int = 1
    shadow_col: int = 1
    knob_col: int = 7


class BuildingRenderer(Renderable):
    def __init__(self, style: BuildingStyle | None = None):
        self.s = style or BuildingStyle()
        self._buildings: list[Building] = []

    def update(self, ctx) -> None:
        return

    def draw(self, ctx) -> None:
        self.draw_buildings(ctx, self._buildings)

    def set_buildings(self, buildings: Sequence[Building] | Iterable[Building]) -> None:
        self._buildings = list(buildings)

    def draw_buildings(self, ctx, buildings: Sequence[Building] | Iterable[Building]) -> None:
        for b in buildings:
            self.draw_building(ctx, b)

    def draw_building(self, ctx, b: Building) -> None:
        self._draw_shadow(ctx, b)
        self._draw_walls(ctx, b)
        self._draw_roof(ctx, b)
        self._draw_door(ctx, b)
        self._draw_windows(ctx, b)

    def _draw_shadow(self, ctx, b: Building) -> None:
        sh = Rect(b.wall.x + 2, b.wall.y + 2, b.wall.w, b.wall.h)
        sh.fill(ctx, self.s.shadow_col)

    def _draw_walls(self, ctx, b: Building) -> None:
        b.wall.fill(ctx, self.s.wall_col)
        b.wall.border(ctx, self.s.wall_border_col)

    def _draw_roof(self, ctx, b: Building) -> None:
        roof_h = max(3, b.roof_h)
        x0 = b.wall.x
        y0 = b.wall.y
        w = b.wall.w

        apex_x = x0 + w // 2
        apex_y = y0 - roof_h

        left_x = x0 - 1
        left_y = y0
        right_x = x0 + w
        right_y = y0

        ctx.tri(apex_x, apex_y, left_x, left_y, right_x, right_y, self.s.roof_col)
        ctx.line(apex_x, apex_y, left_x, left_y, self.s.roof_border_col)
        ctx.line(apex_x, apex_y, right_x, right_y, self.s.roof_border_col)
        ctx.line(left_x, left_y, right_x, right_y, self.s.roof_border_col)

    def _draw_door(self, ctx, b: Building) -> None:
        dw = max(3, b.door_w)
        dh = max(4, b.door_h)
        dx = b.wall.x + (b.wall.w - dw) // 2
        dy = b.wall.y + b.wall.h - dh

        door = Rect(dx, dy, dw, dh)
        door.fill(ctx, self.s.door_col)
        door.border(ctx, self.s.door_border_col)

        ctx.pset(dx + dw - 2, dy + dh // 2, self.s.knob_col)  # doorknob

    def _draw_windows(self, ctx, b: Building) -> None:
        ww = max(2, b.window_w)
        wh = max(2, b.window_h)
        cols = max(1, b.windows_per_row)
        rows = max(0, b.window_rows)

        pad_x = 3
        pad_y = 3

        top = b.wall.y + pad_y
        left = b.wall.x + pad_x
        right = b.wall.x + b.wall.w - pad_x
        bottom = b.wall.y + b.wall.h - pad_y

        door_top = b.wall.y + b.wall.h - max(4, b.door_h)
        bottom = min(bottom, door_top - 2)

        if bottom <= top or right <= left or rows == 0:
            return

        span_w = right - left
        span_h = bottom - top

        xs = self._window_x_positions(left=left, span_w=span_w, ww=ww, cols=cols)
        ys = self._window_y_positions(top=top, span_h=span_h, wh=wh, rows=rows)

        for y in ys:
            for x in xs:
                if x + ww > right or y + wh > bottom:
                    continue

                win = Rect(x, y, ww, wh)
                win.fill(ctx, self.s.window_col)
                win.border(ctx, self.s.window_border_col)

                # pane split
                ctx.line(x + ww // 2, y, x + ww // 2, y + wh - 1, self.s.window_border_col)
                ctx.line(x, y + wh // 2, x + ww - 1, y + wh // 2, self.s.window_border_col)

    @staticmethod
    def _window_x_positions(*, left: int, span_w: int, ww: int, cols: int) -> list[int]:
        if cols == 1:
            return [left + (span_w - ww) // 2]
        step_x = max(ww + 2, span_w // cols)
        return [left + i * step_x for i in range(cols)]

    @staticmethod
    def _window_y_positions(*, top: int, span_h: int, wh: int, rows: int) -> list[int]:
        if rows == 1:
            return [top + (span_h - wh) // 2]
        step_y = max(wh + 2, span_h // rows)
        return [top + r * step_y for r in range(rows)]
