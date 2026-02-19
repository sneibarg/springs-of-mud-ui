from __future__ import annotations
from collections import deque
from typing import Optional
from clipboard.Clipboard import Clipboard, default_clipboard
import component.input.Keys as Keys

import pyxel


class TextInput:
    """
    Minimal, robust-ish line editor.
    - ASCII subset: letters, digits, space, basic punctuation
    - Backspace deletes
    - Enter submits
    - Up/Down navigate history
    - Ctrl+A select all
    - Ctrl+C copy (requires clipboard)
    - Ctrl+X cut  (requires clipboard)
    - Ctrl+V paste (requires clipboard)
    """

    def __init__(self, max_len: int = 120, history_cap: int = 200, clipboard: Optional[Clipboard] = None):
        self.buf: str = ""
        self.cursor: int = 0
        self.max_len = max_len
        self.history: deque[str] = deque(maxlen=history_cap)
        self.hist_idx: int | None = None  # None means "not browsing history"
        self.selection_start: int | None = None
        self.selection_end: int | None = None

        self.clipboard: Optional[Clipboard] = clipboard if clipboard is not None else default_clipboard()

    def _ctrl_down(self) -> bool:
        return pyxel.btn(Keys.KEY_LCTRL) or pyxel.btn(Keys.KEY_RCTRL)

    def _consume_text(self) -> None:
        # Letters A-Z
        for i in range(26):
            key = getattr(Keys, f"KEY_{chr(ord('A') + i)}")
            if pyxel.btnp(key):
                ch = chr(ord("a") + i)
                if pyxel.btn(Keys.KEY_LSHIFT) or pyxel.btn(Keys.KEY_RSHIFT):
                    ch = ch.upper()
                self.insert(ch)

        # Digits 0-9
        for i in range(10):
            key = getattr(Keys, f"KEY_{i}")
            if pyxel.btnp(key):
                self.insert(str(i))

        # Space
        if pyxel.btnp(Keys.KEY_SPACE):
            self.insert(" ")

        # Punctuation
        punct = [
            (Keys.KEY_MINUS, "-"),
            (Keys.KEY_EQUALS, "="),
            (Keys.KEY_LEFTBRACKET, "["),
            (Keys.KEY_RIGHTBRACKET, "]"),
            (Keys.KEY_BACKSLASH, "\\"),
            (Keys.KEY_SEMICOLON, ";"),
            (Keys.KEY_APOSTROPHE, "'"),
            (Keys.KEY_COMMA, ","),
            (Keys.KEY_PERIOD, "."),
            (Keys.KEY_SLASH, "/"),
            (Keys.KEY_GRAVE, "`"),
        ]
        for key, ch in punct:
            if pyxel.btnp(key):
                self.insert(ch)

    def insert(self, s: str) -> None:
        if not s:
            return

        # If selection exists, replace it (standard editor behavior)
        if self.has_selection():
            self.delete_selection()

        if len(self.buf) >= self.max_len:
            return
        s = s[: self.max_len - len(self.buf)]
        self.buf = self.buf[: self.cursor] + s + self.buf[self.cursor :]
        self.cursor += len(s)
        self.hist_idx = None

    def backspace(self) -> None:
        if self.has_selection():
            self.delete_selection()
            return
        if self.cursor <= 0:
            return
        self.buf = self.buf[: self.cursor - 1] + self.buf[self.cursor :]
        self.cursor -= 1
        self.hist_idx = None

    def move_cursor(self, delta: int) -> None:
        self.cursor = max(0, min(len(self.buf), self.cursor + delta))

    def set_buffer(self, s: str) -> None:
        self.buf = s[: self.max_len]
        self.cursor = len(self.buf)

    def push_history(self, cmd: str) -> None:
        if cmd and (not self.history or self.history[-1] != cmd):
            self.history.append(cmd)
        self.hist_idx = None

    def history_prev(self) -> None:
        if not self.history:
            return
        if self.hist_idx is None:
            self.hist_idx = len(self.history) - 1
        else:
            self.hist_idx = max(0, self.hist_idx - 1)
        self.set_buffer(self.history[self.hist_idx])

    def history_next(self) -> None:
        if self.hist_idx is None:
            return
        if self.hist_idx >= len(self.history) - 1:
            self.hist_idx = None
            self.set_buffer("")
        else:
            self.hist_idx += 1
            self.set_buffer(self.history[self.hist_idx])

    def select_all(self) -> None:
        if self.buf:
            self.selection_start = 0
            self.selection_end = len(self.buf)
            self.cursor = len(self.buf)

    def clear_selection(self) -> None:
        self.selection_start = None
        self.selection_end = None

    def has_selection(self) -> bool:
        return self.selection_start is not None and self.selection_end is not None and self.selection_start != self.selection_end

    def _sel_range(self) -> tuple[int, int]:
        assert self.selection_start is not None and self.selection_end is not None
        return min(self.selection_start, self.selection_end), max(self.selection_start, self.selection_end)

    def selected_text(self) -> str:
        if not self.has_selection():
            return ""
        start, end = self._sel_range()
        return self.buf[start:end]

    def delete_selection(self) -> None:
        if not self.has_selection():
            return
        start, end = self._sel_range()
        self.buf = self.buf[:start] + self.buf[end:]
        self.cursor = start
        self.clear_selection()

    def _copy_selection(self) -> None:
        if self.clipboard is None:
            return
        txt = self.selected_text()
        if txt:
            self.clipboard.copy(txt)

    def _cut_selection(self) -> None:
        if not self.has_selection():
            return
        self._copy_selection()
        self.delete_selection()

    def _paste_clipboard(self) -> None:
        if self.clipboard is None:
            return
        txt = self.clipboard.paste()
        if not txt:
            return

        # Normalize paste for a single-line command clipboard:
        txt = txt.replace("\r\n", "\n").replace("\r", "\n")
        txt = txt.split("\n", 1)[0]  # keep first line only

        # Optional: you can filter to ASCII if you want strict 8-bit style
        # txt = "".join(ch for ch in txt if 32 <= ord(ch) <= 126)

        self.insert(txt)

    def update(self) -> str | None:
        # --- clipboard / editor shortcuts ---
        if self._ctrl_down():
            if pyxel.btnp(Keys.KEY_A):
                self.select_all()
                return None

            if pyxel.btnp(Keys.KEY_C):
                self._copy_selection()
                return None

            if pyxel.btnp(Keys.KEY_X):
                self._cut_selection()
                return None

            if pyxel.btnp(Keys.KEY_V):
                self._paste_clipboard()
                return None

        # Cursor movement
        if pyxel.btnp(Keys.KEY_LEFT, 18, 2):
            self.clear_selection()
            self.move_cursor(-1)
        if pyxel.btnp(Keys.KEY_RIGHT, 18, 2):
            self.clear_selection()
            self.move_cursor(+1)

        # History
        if pyxel.btnp(Keys.KEY_UP):
            self.clear_selection()
            self.history_prev()
        if pyxel.btnp(Keys.KEY_DOWN):
            self.clear_selection()
            self.history_next()

        # Backspace / Delete
        if pyxel.btnp(Keys.KEY_BACKSPACE, 18, 2) or pyxel.btnp(Keys.KEY_DELETE, 18, 2):
            self.backspace()

        # Text entry
        # If typing over a selection, insert() already replaces it, so just consume text.
        self._consume_text()

        # Submit
        if pyxel.btnp(Keys.KEY_RETURN) or pyxel.btnp(Keys.KEY_ENTER):
            cmd = self.buf.strip()
            self.set_buffer("")
            self.clear_selection()
            if cmd:
                self.push_history(cmd)
                return cmd

        return None
