from dataclasses import dataclass

from outcomes import Outcome


def torrent(outcomes: list[Outcome]) -> list[Outcome]:
    return [ Outcome(o.value, o.success, o.success) for o in outcomes ]

def sustained_dits(count:int) -> Callable[[list[Outcome]], list[Outcome]]:

    def update(outcomes: list[Outcome]) -> list[Outcome]:
        return [ Outcome(o.value, o.success, o.success) for o in outcomes ]
    return update







@dataclass
class SimpleWeapon:
    name: str
    A: int
    WS: int
    S: int
    AP: int
    D: int

    def attack(self, rng: int) -> list[Outcome]:
        return [ Outcome(self.A,True,False) ]

    def hit(self) -> list[Outcome]:
        return [ Outcome(1, i >= self.WS, False) for i in range(1,7) ]

    def wound(self, target_toughness: int) -> list[Outcome]:
        return [ 
                Outcome(1, False, False),
                Outcome(1, self.S > 2*target_toughness, False),
                Outcome(1, self.S > target_toughness, False),
                Outcome(1, self.S >= target_toughness, False),
                Outcome(1, 2*self.S > target_toughness , False),
                Outcome(1, True, False),
                ]

    def damage(self) -> list[Outcome]:
        return [ Outcome(self.D, True, False) ]

    def __str__(self) -> str:
        return f"{self.name}: A {self.A}, WS {self.WS}+, S {self.S}, AP -{self.AP}, D {self.D}"

@dataclass
class SimpleModel:
    name: str
    T: int
    S: int
    W: int

    def save(self, armour_piercing: int) -> list[Outcome]:
        return [ Outcome(1, i >= (self.S - armour_piercing), False) for i in range(1,7) ]

    def damage_modifier(self, damage: int) -> list[Outcome]:
        return [Outcome(damage, True, False) ]



    def __str__(self) -> str:
        return f"{self.name}: T {self.T}, S {self.S}+, W {self.W}"
