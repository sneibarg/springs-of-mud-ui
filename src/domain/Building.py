from dataclasses import dataclass
from component.geometry import Rect


@dataclass(frozen=True)
class Building:
    """
    World/screen-space building footprint.

    x,y,w,h describe the wall rectangle (not counting roof overhang).
    roof_h is the height of the roof triangle.
    """
    wall: Rect
    roof_h: int = 8
    door_w: int = 6
    door_h: int = 10
    window_w: int = 4
    window_h: int = 4
    windows_per_row: int = 3
    window_rows: int = 2