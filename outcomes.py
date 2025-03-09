from enum import Enum
from typing import TypeVar

from dataclasses import dataclass

T = TypeVar("T")


def collect(items: list[T]) -> dict[T, int]:
    collection = {}
    for item in items:
        if item not in collection:
            collection[item] = 1
        else:
            collection[item] += 1
    return collection


class Success(Enum):
    FAILURE = 0
    SUCCESS = 1
    CRITICAL = 2

    def __bool__(self) -> bool:
        return self.value > 0

    def critical(self) -> bool:
        return self.value == Success.CRITICAL.value

    @staticmethod
    def from_bool(value: bool) -> "Success":
        return Success.SUCCESS if value else Success.FAILURE

    def __lt__(self, other) -> bool:
        return self.value < other.value

    def __repr__(self) -> str:
        return self.name


def failure() -> Success:
    return Success.FAILURE


def success(value: bool = True) -> Success:
    if value:
        return Success.SUCCESS
    return Success.FAILURE


def critical() -> Success:
    return Success.CRITICAL


@dataclass(frozen=True)
class Outcome:
    value: int
    roll_value: int
    success: Success
    bypass_next: bool
    reroll: bool

    def __lt__(self, other) -> bool:
        if self.value < other.value:
            return True
        if self.success < other.success:
            return True
        if self.bypass_next < other.bypass_next:
            return True
        if self.reroll < other.reroll:
            return True
        return False

    def __repr__(self) -> str:
        values = [
            repr(self.success)[0],
            "B" if self.bypass_next else "-",
            "R" if self.reroll else "-",
        ]
        return f"O({self.value} [{self.roll_value}], {''.join(values)})"


class Dice:
    def __init__(self, sides: int, addition: int = 0):
        self.sides = sides
        self.addition = addition

    def __call__(self) -> list[Outcome]:
        return [Outcome(1, ii + self.addition, success(), False, False) for ii in range(1, self.sides + 1)]

    def __str__(self):
        results = f"D{self.sides}"
        if self.addition > 0:
            return f"{results}+{self.addition}"
        else:
            return results

    @staticmethod
    def from_str(s: str) -> "Dice":
        parts = [p.strip() for p in s.split("+")]
        assert (len(parts) >= 1) and (len(parts) <= 2)
        assert parts[0][0].lower() == "d"
        sides = int(parts[0][1:])
        if len(parts) > 1:
            addition = int(parts[1])
        else:
            addition = 0
        return Dice(sides, addition)
