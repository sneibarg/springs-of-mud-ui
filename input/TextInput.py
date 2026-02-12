from __future__ import annotations
from collections import deque
from typing import Optional
from input.Clipboard import Clipboard, default_clipboard

import pyxel


class TextInput:
    """
    Minimal, robust-ish line editor for Pyxel.
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

    def _k(self, name: str, default: int | None = None) -> int | None:
        return getattr(pyxel, name, default)

    def _ctrl_down(self) -> bool:
        k_lctrl = self._k("KEY_LCTRL")
        k_rctrl = self._k("KEY_RCTRL")
        return (k_lctrl is not None and pyxel.btn(k_lctrl)) or (k_rctrl is not None and pyxel.btn(k_rctrl))

    def _consume_text(self) -> None:
        # Letters A-Z
        for i in range(26):
            key = self._k(f"KEY_{chr(ord('A') + i)}")
            if key is None:
                continue
            if pyxel.btnp(key):
                ch = chr(ord("a") + i)
                lshift = self._k("KEY_LSHIFT")
                rshift = self._k("KEY_RSHIFT")
                if (lshift is not None and pyxel.btn(lshift)) or (rshift is not None and pyxel.btn(rshift)):
                    ch = ch.upper()
                self.insert(ch)

        # Digits 0-9
        for i in range(10):
            key = self._k(f"KEY_{i}")
            if key is None:
                continue
            if pyxel.btnp(key):
                self.insert(str(i))

        # Space
        k_space = self._k("KEY_SPACE")
        if k_space is not None and pyxel.btnp(k_space):
            self.insert(" ")

        punct = [
            ("KEY_MINUS", "-"),
            ("KEY_EQUALS", "="),
            ("KEY_LEFTBRACKET", "["),
            ("KEY_RIGHTBRACKET", "]"),
            ("KEY_BACKSLASH", "\\"),
            ("KEY_SEMICOLON", ";"),
            ("KEY_APOSTROPHE", "'"),
            ("KEY_COMMA", ","),
            ("KEY_PERIOD", "."),
            ("KEY_SLASH", "/"),
            ("KEY_GRAVE", "`"),
        ]
        for kname, ch in punct:
            key = self._k(kname)
            if key is not None and pyxel.btnp(key):
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
        return (min(self.selection_start, self.selection_end), max(self.selection_start, self.selection_end))

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

        # Normalize paste for a single-line command input:
        txt = txt.replace("\r\n", "\n").replace("\r", "\n")
        txt = txt.split("\n", 1)[0]  # keep first line only

        # Optional: you can filter to ASCII if you want strict 8-bit style
        # txt = "".join(ch for ch in txt if 32 <= ord(ch) <= 126)

        self.insert(txt)

    def update(self) -> str | None:
        # --- clipboard / editor shortcuts ---
        if self._ctrl_down():
            k_a = self._k("KEY_A")
            k_c = self._k("KEY_C")
            k_x = self._k("KEY_X")
            k_v = self._k("KEY_V")

            if k_a is not None and pyxel.btnp(k_a):
                self.select_all()
                return None

            if k_c is not None and pyxel.btnp(k_c):
                self._copy_selection()
                return None

            if k_x is not None and pyxel.btnp(k_x):
                self._cut_selection()
                return None

            if k_v is not None and pyxel.btnp(k_v):
                self._paste_clipboard()
                return None

        # Cursor movement
        k_left = self._k("KEY_LEFT")
        k_right = self._k("KEY_RIGHT")
        if k_left is not None and pyxel.btnp(k_left, 18, 2):
            self.clear_selection()
            self.move_cursor(-1)
        if k_right is not None and pyxel.btnp(k_right, 18, 2):
            self.clear_selection()
            self.move_cursor(+1)

        # History
        k_up = self._k("KEY_UP")
        k_down = self._k("KEY_DOWN")
        if k_up is not None and pyxel.btnp(k_up):
            self.clear_selection()
            self.history_prev()
        if k_down is not None and pyxel.btnp(k_down):
            self.clear_selection()
            self.history_next()

        # Backspace / Delete
        k_bs = self._k("KEY_BACKSPACE") or self._k("KEY_DELETE")
        if k_bs is not None and pyxel.btnp(k_bs, 18, 2):
            self.backspace()

        # Text entry
        # If typing over a selection, insert() already replaces it, so just consume text.
        self._consume_text()

        # Submit
        k_enter = self._k("KEY_RETURN") or self._k("KEY_ENTER")
        if k_enter is not None and pyxel.btnp(k_enter):
            cmd = self.buf.strip()
            self.set_buffer("")
            self.clear_selection()
            if cmd:
                self.push_history(cmd)
                return cmd

        return None