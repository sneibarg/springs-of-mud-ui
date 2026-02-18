from dataclasses import dataclass
from typing import Deque, Callable, Sequence, Any
from component.input import TextInput
from component.render.api.Graphics import Graphics
from engine.context.InputState import InputState
from ui.layout.Layout import Layout


@dataclass
class EngineContext:
    layout: Layout
    input: InputState
    text_input: TextInput
    scrollback: Deque[str]
    scroll_offset: int
    visible_lines: int
    line_spacing: int
    font_scale: int
    log: Callable[[str], None]
    quit: Callable[[], None]
    gfx: Graphics
    apply_display_settings: Callable[..., None]
    set_character_list: Callable[[Sequence[Any]], None] = lambda _chars: None
