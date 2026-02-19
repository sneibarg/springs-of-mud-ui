"""
Abstract base class for renderable components.
"""
from abc import ABC, abstractmethod


class Renderable(ABC):
    """
    Abstract base class for components that can be rendered.

    All renderable components must implement update() and draw() methods.
    The update() method handles logic and input, while draw() handles rendering.
    """

    @abstractmethod
    def update(self, ctx) -> None:
        """
        Update the component's state.

        Args:
            ctx: Engine context containing input state and other data
        """
        pass

    @abstractmethod
    def draw(self, ctx) -> None:
        """
        Draw the component.

        Args:
            ctx: Engine context containing graphics interface (ctx.gfx)
        """
        pass
