from typing import Protocol

from engine.context.EngineContext import EngineContext


class GameComponent(Protocol):
    z_index: int

    def update(self, ctx: EngineContext) -> None: ...
    def draw(self, ctx: EngineContext) -> None: ...