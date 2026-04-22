from typing import Protocol, Optional
from clipboard.TkClipboard import TkClipboard
from clipboard.PyperClipboard import PyperclipClipboard


class Clipboard(Protocol):
    def copy(self, text: str) -> None: ...
    def paste(self) -> str: ...


def default_clipboard() -> Optional[Clipboard]:
    try:
        return PyperclipClipboard()
    except Exception:
        pass
    try:
        return TkClipboard()
    except Exception:
        return None