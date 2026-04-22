from dataclasses import dataclass
from component.animation.core.Frame import Frame


@dataclass
class Animation:
    name: str
    frames: list[Frame]
    loop: bool = True
    speed: float = 1.0

    def __post_init__(self):
        if not self.frames:
            raise ValueError("Animation must have at least one frame")
        if self.speed <= 0:
            raise ValueError(f"Animation speed must be positive, got {self.speed}")

    def duration(self) -> float:
        return sum(f.duration for f in self.frames) / self.speed

    def get_frame_at(self, time: float) -> Frame:
        if not self.frames:
            raise ValueError("Animation has no frames")

        if not self.loop and time >= self.duration():
            return self.frames[-1]

        time = time % self.duration() if self.loop else time
        elapsed = 0.0
        for frame in self.frames:
            frame_duration = frame.duration / self.speed
            if elapsed + frame_duration > time:
                return frame
            elapsed += frame_duration

        return self.frames[-1]

    def get_frame_index_at(self, time: float) -> int:
        if not self.frames:
            raise ValueError("Animation has no frames")

        if not self.loop and time >= self.duration():
            return len(self.frames) - 1

        time = time % self.duration() if self.loop else time
        elapsed = 0.0

        for i, frame in enumerate(self.frames):
            frame_duration = frame.duration / self.speed
            if elapsed + frame_duration > time:
                return i
            elapsed += frame_duration

        return len(self.frames) - 1

    def frame_count(self) -> int:
        return len(self.frames)

    def with_speed(self, speed: float) -> 'Animation':
        return Animation(name=self.name, frames=self.frames, loop=self.loop, speed=speed)

    def reversed(self) -> 'Animation':
        return Animation(name=f"{self.name}_reversed", frames=list(reversed(self.frames)), loop=self.loop, speed=self.speed)
