from __future__ import annotations
from component.animation.core.AnimatedSprite import AnimatedSprite


class StateAnimator:
    def __init__(self, sprite: AnimatedSprite):
        self.sprite = sprite
        self.state_map: dict[str, str] = {}  # state → animation name
        self.current_state: str | None = None

    def register_state(self, state: str, animation_name: str) -> None:
        self.state_map[state] = animation_name

    def set_state(self, state: str) -> None:
        if state == self.current_state:
            return

        if state not in self.state_map:
            raise ValueError(f"State '{state}' not registered")

        self.current_state = state
        animation_name = self.state_map[state]
        self.sprite.play(animation_name)

    def update(self, delta_time: float) -> None:
        self.sprite.update(delta_time)

    def draw(self, ctx) -> None:
        self.sprite.draw(ctx)