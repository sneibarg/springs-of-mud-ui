"""
Abstract base class for geometric shapes.
Provides a common interface for all shapes with bounds, contains, and drawing methods.
"""
from __future__ import annotations
from abc import ABC, abstractmethod


class Shape(ABC):
    """
    Abstract base class for all geometric shapes.

    All shapes must implement:
    - bounds(): Return bounding box as (x, y, width, height)
    - contains(): Check if a point is inside the shape
    - At least one drawing method (draw, fill, or border)
    """

    @abstractmethod
    def bounds(self) -> tuple[int, int, int, int]:
        """
        Get the bounding box of the shape.

        Returns:
            Tuple of (x, y, width, height) representing the smallest rectangle
            that completely contains the shape.
        """
        pass

    @abstractmethod
    def contains(self, mx: int, my: int) -> bool:
        """
        Check if a point is inside the shape.

        Args:
            mx: X coordinate of the point
            my: Y coordinate of the point

        Returns:
            True if the point is inside the shape, False otherwise
        """
        pass

    def intersects(self, other: Shape) -> bool:
        """
        Check if this shape intersects with another shape.
        Default implementation uses bounding box intersection.
        Override for more precise collision detection.

        Args:
            other: Another shape to check intersection with

        Returns:
            True if the shapes intersect, False otherwise
        """
        x1, y1, w1, h1 = self.bounds()
        x2, y2, w2, h2 = other.bounds()

        return not (x1 + w1 < x2 or  # self is left of other
                   x2 + w2 < x1 or  # self is right of other
                   y1 + h1 < y2 or  # self is above other
                   y2 + h2 < y1)    # self is below other

    def center(self) -> tuple[int, int]:
        """
        Get the center point of the shape.

        Returns:
            Tuple of (x, y) representing the center of the bounding box
        """
        x, y, w, h = self.bounds()
        return x + w // 2, y + h // 2


class Drawable(ABC):
    """
    Abstract base class for shapes that can be drawn.
    Subclasses should implement at least one drawing method.
    """

    def draw(self, ctx, col: int) -> None:
        """
        Draw the shape. Default implementation calls fill().

        Args:
            ctx: Engine context with gfx attribute
            col: Color to draw with
        """
        self.fill(ctx, col)

    def fill(self, ctx, col: int) -> None:
        """
        Draw a filled version of the shape.

        Args:
            ctx: Engine context with gfx attribute
            col: Color to fill with
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not implement fill()")

    def border(self, ctx, col: int) -> None:
        """
        Draw only the border/outline of the shape.

        Args:
            ctx: Engine context with gfx attribute
            col: Color for the border
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not implement border()")
