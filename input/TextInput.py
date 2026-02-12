from __future__ import annotations
from collections import deque

import pyxel


class TextInput:
    """
    Minimal, robust-ish line editor for Pyxel.
    - ASCII subset: letters, digits, space, basic punctuation
    - Backspace deletes
    - Enter submits
    - Up/Down navigate history
    """

    def __init__(self, max_len: int = 120, history_cap: int = 200):
        self.buf: str = ""
        self.cursor: int = 0
        self.max_len = max_len
        self.history: deque[str] = deque(maxlen=history_cap)
        self.hist_idx: int | None = None  # None means "not browsing history"

    def _k(self, name: str, default: int | None = None) -> int | None:
        return getattr(pyxel, name, default)

    def _consume_text(self) -> None:
        # Letters A-Z
        for i in range(26):
            key = self._k(f"KEY_{chr(ord('A') + i)}")
            if key is None:
                continue
            if pyxel.btnp(key):
                ch = chr(ord("a") + i)
                # Shift: if either shift exists, uppercase
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

        # Common punctuation (US keyboard-ish). If a constant is missing, it simply won’t work.
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
        if len(self.buf) >= self.max_len:
            return
        # truncate insert if needed
        s = s[: self.max_len - len(self.buf)]
        self.buf = self.buf[: self.cursor] + s + self.buf[self.cursor :]
        self.cursor += len(s)
        self.hist_idx = None

    def backspace(self) -> None:
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

    def update(self) -> str | None:
        # Cursor movement
        k_left = self._k("KEY_LEFT")
        k_right = self._k("KEY_RIGHT")
        if k_left is not None and pyxel.btnp(k_left, 18, 2):
            self.move_cursor(-1)
        if k_right is not None and pyxel.btnp(k_right, 18, 2):
            self.move_cursor(+1)

        # History
        k_up = self._k("KEY_UP")
        k_down = self._k("KEY_DOWN")
        if k_up is not None and pyxel.btnp(k_up):
            self.history_prev()
        if k_down is not None and pyxel.btnp(k_down):
            self.history_next()

        # Edit keys
        k_bs = self._k("KEY_BACKSPACE") or self._k("KEY_DELETE")
        if k_bs is not None and pyxel.btnp(k_bs, 18, 2):
            self.backspace()

        # Text entry
        self._consume_text()

        # Submit
        k_enter = self._k("KEY_RETURN") or self._k("KEY_ENTER")
        if k_enter is not None and pyxel.btnp(k_enter):
            cmd = self.buf.strip()
            self.set_buffer("")
            if cmd:
                self.push_history(cmd)
                return cmd

        return None