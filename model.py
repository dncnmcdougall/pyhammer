from dataclasses import dataclass
from outcomes import Outcome 
import outcomes as oc

@dataclass
class SimpleModel:
    name: str
    T: int
    S: int
    W: int

    def save(self, armour_piercing: int) -> list[Outcome]:
        successes = [ i >= (self.S - armour_piercing) for i in range(1,7) ]
        return [ Outcome(1 if success else 0, oc.success(success), False) for success in successes ]

    def damage_modifier(self, damage: int) -> list[Outcome]:
        return [Outcome(damage, oc.success(), False) ]

    def feel_no_pain(self) -> list[Outcome]:
        return [Outcome(1, oc.failure(), False) ]



    def __str__(self) -> str:
        return f"{self.name}: T {self.T}, S {self.S}+, W {self.W}"
