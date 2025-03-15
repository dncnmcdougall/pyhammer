import functools
from typing import Callable, ParamSpec, TypeVar
from dataclasses import dataclass, field

from outcomes import Outcome, Dice
import outcomes as oc


P = ParamSpec("P")
R = TypeVar("R")

RollFunc = Callable[P, list[Outcome]]


@dataclass(frozen=True)
class SimpleWeapon:
    name: str
    R: int
    A: int | Dice
    WS: int
    S: int
    AP: int
    D: int | Dice

    modifiers: tuple[RollFunc]

    def stat_line(self) -> str:
        return f'R:{self.R}" A:{self.A} WS:{self.WS} S:{self.S} AP:{self.AP} D:{self.D}'

    def keywords(self) -> str:
        return ", ".join([mod.name for mod in self.modifiers])

    def __str__(self) -> str:
        return f"{self.name}: A {self.A}, WS {self.WS}+, S {self.S}, AP -{self.AP}, D {self.D}"
