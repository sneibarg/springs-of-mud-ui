"""
Animation package for sprite and tile animation.
"""
# Import core classes
from .core.Frame import Frame
from .core.Animation import Animation

# Don't import PyxelSpriteSheet here to avoid circular imports
# It can be imported directly when needed: from component.animation.PyxelSpriteSheet import PyxelSpriteSheet

__all__ = ["Frame", "Animation"]
