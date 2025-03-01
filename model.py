from dataclasses import dataclass
from outcomes import Outcome 
import outcomes as oc

@dataclass
class SimpleModel:
    name: str
    T: int
    S: int
    W: int
    FNP: int

    def save(self, armour_piercing: int) -> list[Outcome]:
        successes = [ i >= (self.S - armour_piercing) for i in range(1,7) ]
        return [ Outcome(1 if success else 0, oc.success(success), False, False) for success in successes ]

    def damage_modifier(self, damage: int) -> list[Outcome]:
        return [Outcome(damage, oc.success(), False, False) ]

    def feel_no_pain(self) -> list[Outcome]:
        if self.FNP == 0 :
            return [Outcome(1, oc.failure(), False, False) ]
        else:
            return [ Outcome(1, oc.success(i >= self.FNP), False, False) for i in range(1,7) ]




    def __str__(self) -> str:
        return f"{self.name}: T {self.T}, S {self.S}+, W {self.W}"
