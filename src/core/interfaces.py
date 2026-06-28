from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ActionEvent:
    """A single input action with an optional hold duration."""

    action: str
    hold_seconds: float = 0.05


class InputBackend(Protocol):
    """Platform-specific adapter for input injection."""

    def press(self, action: str) -> None:
        ...

    def release(self, action: str) -> None:
        ...

    def flush(self) -> None:
        ...


class PerceptionBackend(Protocol):
    """Optional adapter for game-state sensing."""

    def sample(self) -> dict:
        ...
