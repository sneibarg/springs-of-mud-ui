class PyperclipClipboard:
    def __init__(self) -> None:
        import pyperclip
        self._pyperclip = pyperclip

    def copy(self, text: str) -> None:
        self._pyperclip.copy(text)

    def paste(self) -> str:
        return self._pyperclip.paste() or ""
