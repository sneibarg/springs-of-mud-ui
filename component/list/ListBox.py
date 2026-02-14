from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Tuple
from component.geometry.Rect import Rect
from component.field.TextField import TextField


@dataclass(frozen=True)
class ListBoxTheme:
    fill: int = 0
    border: int = 5
    header_col: int = 7
    text_col: int = 7
    hover_fill: int = 2
    selected_fill: int = 5


class ListBox:
    """
    Displays a vertical list and returns clicked index.
    - No pane-side manual row math.
    - Drawing uses Rect/TextField only.
    """
    def __init__(self, box: Rect, items_rect: Rect, *, header: str, row_h: int = 12, max_rows: Optional[int] = None,
                 text: Optional[TextField] = None, theme: Optional[ListBoxTheme] = None):
        self.box = box
        self.items_rect = items_rect
        self.header = header
        self.row_h = row_h
        self.max_rows = max_rows
        self.tf = text or TextField()
        self.t = theme or ListBoxTheme()
        self.hovered_idx: Optional[int] = None

    def update_hover(self, mx: int, my: int, item_count: int) -> None:
        self.hovered_idx = self._index_at(mx, my, item_count)

    def click_index(self, mx: int, my: int, click: bool, item_count: int) -> Optional[int]:
        if not click:
            return None
        return self._index_at(mx, my, item_count)

    def _index_at(self, mx: int, my: int, item_count: int) -> Optional[int]:
        if not self.items_rect.contains(mx, my):
            return None
        idx = (my - self.items_rect.y) // self.row_h
        if idx < 0 or idx >= item_count:
            return None
        if self.max_rows is not None and idx >= self.max_rows:
            return None
        return idx

    def draw(self, *, items: List[str], selected_idx: Optional[int]) -> None:
        self.box.fill(self.t.fill)
        self.box.border(self.t.border)
        self.tf.draw_text(x=self.box.x + 3, y=self.box.y + 3, text=self.header, col=self.t.header_col)

        y = self.items_rect.y
        rows = items
        if self.max_rows is not None:
            rows = rows[: self.max_rows]

        max_chars = max(1, (self.items_rect.w - 10) // self.tf.s.char_w)

        for idx, label in enumerate(rows):
            row = Rect(self.items_rect.x + 1, y, self.items_rect.w - 2, self.row_h - 1)

            if idx == selected_idx:
                row.fill(self.t.selected_fill)
            elif idx == self.hovered_idx:
                row.fill(self.t.hover_fill)

            txt = label
            if len(txt) > max_chars:
                txt = txt[: max_chars - 2] + ".."

            self.tf.draw_text(x=self.items_rect.x + 3, y=y + 2, text=txt, col=self.t.text_col)
            y += self.row_h
