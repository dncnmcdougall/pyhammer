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

    def damage_modifier(self, damage: int) -> list[Outcome]:
        return [Outcome(damage, -1, oc.success(), False, False)]

    def __str__(self) -> str:
        return f"{self.name}: T {self.T}, S {self.S}+, W {self.W}"
