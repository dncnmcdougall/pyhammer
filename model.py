from dataclasses import dataclass
from outcomes import Outcome
import outcomes as oc


@dataclass(frozen=True)
class SimpleModel:
    name: str
    T: int
    S: int
    W: int
    FNP: int

    def save(self, armour_piercing: int) -> list[Outcome]:
        successes = [ii >= (self.S - armour_piercing) for ii in range(1, 7)]
        return [
            Outcome(1 if success else 0, ii + 1, oc.success(success), False, False)
            for ii, success in enumerate(successes)
        ]

    def damage_modifier(self, damage: int) -> list[Outcome]:
        return [Outcome(damage, -1, oc.success(), False, False)]

    def feel_no_pain(self) -> list[Outcome]:
        if self.FNP == 0:
            return [Outcome(1, -1, oc.failure(), False, False)]
        else:
            return [Outcome(1, ii, oc.success(ii >= self.FNP), False, False) for ii in range(1, 7)]

    def __str__(self) -> str:
        return f"{self.name}: T {self.T}, S {self.S}+, W {self.W}"
