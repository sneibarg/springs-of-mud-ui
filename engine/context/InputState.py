from dataclasses import dataclass


@dataclass
class InputState:
    mx: int
    my: int
    click: bool
    wheel: int
    frame_count: int
    enter: bool = False