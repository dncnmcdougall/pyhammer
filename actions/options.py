from typing import ParamSpec
from dataclasses import dataclass, field

from .base import Modifier

P = ParamSpec("P")


@dataclass(frozen=True)
class AttackOptions:
    half_range: bool
    cover: bool
    anti_active: bool

    modifiers: tuple[Modifier, ...]
