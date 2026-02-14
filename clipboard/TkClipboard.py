class TkClipboard:
    """
    Fallback clipboard using tkinter.
    Note: creates a hidden Tk root on first use.
    """
    def __init__(self) -> None:
        import tkinter as tk
        self._tk = tk
        self._root = tk.Tk()
        self._root.withdraw()

    def copy(self, text: str) -> None:
        self._root.clipboard_clear()
        self._root.clipboard_append(text)
        self._root.update()

    def paste(self) -> str:
        try:
            return self._root.clipboard_get() or ""
        except Exception:
            return ""
