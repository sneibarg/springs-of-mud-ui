"""
Frame Generator Protocol.

Defines the interface for frame generation systems.
"""
from typing import Protocol
from component.animation.core.Frame import Frame


class FrameGenerator(Protocol):
    """
    Protocol for frame generators.

    Frame generators create sequences of frames programmatically,
    either procedurally (algorithmic) or via NLP (natural language).

    Implementations:
    - ProceduralGenerator: Creates frames using algorithms (walk cycles, bounces, etc.)
    - NLPGenerator (future): Creates frames from natural language descriptions
    """

    def generate(self, description: str, **kwargs) -> list[Frame]:
        """
        Generate a list of frames based on a description.

        Args:
            description: Description of the animation to generate
            **kwargs: Additional parameters specific to the generator

        Returns:
            List of Frame objects

        Examples:
            # Procedural generator
            frames = generator.generate("walk_cycle", frame_count=4, frame_width=32)

            # NLP generator (future)
            frames = generator.generate("character walking to the right")
        """
        ...
