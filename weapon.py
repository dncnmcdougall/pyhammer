import functools
from typing import Callable, ParamSpec, TypeVar
from dataclasses import dataclass, field

from outcomes import Outcome 
import outcomes as oc

from icecream import ic

P = ParamSpec('P')
R = TypeVar('R')

RollFunc = Callable[P, list[Outcome]]

def modify(roll: str) -> Callable[[RollFunc], RollFunc]:

    def dec(func: RollFunc) -> RollFunc:
        @functools.wraps(func)
        def dec_impl(self, *args: P.args, **kwargs:P.kwargs) -> list[Outcome]:
            results = func(self, *args, **kwargs)
            for modifier in self.modifiers:
                if modifier.roll == roll:
                    results = modifier(self, *args, results, **kwargs)
            return results

        return dec_impl
    return dec

@dataclass
class AttackOptions:
    rng: int
    cover: bool

class dice:

    def __init__(self, sides:int, addition:int =0):
        self.sides = sides
        self.addition = addition

    def __call__(self, options:AttackOptions) -> list[Outcome]:
        return [ Outcome(ii + self.addition, oc.success(), False, False) for ii in range(1, self.sides+1) ]

    def __str__(self):
        results = f'd{self.sides}'
        if self.addition > 0:
            return f'{results}+{self.addition}'
        else:
            return results

@dataclass
class SimpleWeapon:
    name: str
    R: int
    A: int|dice
    WS: int
    S: int
    AP: int
    D: int|dice

    modifiers: list[RollFunc] = field(default_factory=list)

    def statLine(self) -> str:
        return f'R:{self.R}" A:{self.A} WS:{self.WS} S:{self.S} AP:{self.AP} D:{self.D}'

    def keywords(self) -> str:
        return ','.join( [mod.__name__ for mod in self.modifiers] )

    @modify("attack")
    def attack(self, options: AttackOptions) -> list[Outcome]:
        if isinstance(self.A, dice):
            return self.A(options)
        else:
            return [ Outcome(self.A,oc.success(),False, False) ]

    @modify("hit")
    def hit(self, options: AttackOptions) -> list[Outcome]:
        return [ 
            Outcome(1, oc.failure(), False, False),
            Outcome(1, oc.success(2 >= self.WS), False, False),
            Outcome(1, oc.success(3 >= self.WS), False, False),
            Outcome(1, oc.success(4 >= self.WS), False, False),
            Outcome(1, oc.success(5 >= self.WS), False, False),
            Outcome(1, oc.critical(), False, False),
        ]

    @modify("wound")
    def wound(self, target_toughness: int, options:AttackOptions) -> list[Outcome]:
        return [ 
                Outcome(1, oc.failure(), False, False),
                Outcome(2, oc.success(self.S > 2*target_toughness), False, False),
                Outcome(3, oc.success(self.S > target_toughness), False, False),
                Outcome(4, oc.success(self.S >= target_toughness), False, False),
                Outcome(5, oc.success(2*self.S > target_toughness) , False, False),
                Outcome(6, oc.critical(), False, False),
                ]

    @modify("damage")
    def damage(self, options:AttackOptions) -> list[Outcome]:
        if callable(self.D):
            return self.D(options)
        return [ Outcome(self.D, oc.success(), False, False) ]

    def __str__(self) -> str:
        return f"{self.name}: A {self.A}, WS {self.WS}+, S {self.S}, AP -{self.AP}, D {self.D}"



Modifier = Callable[[SimpleWeapon, AttackOptions, list[Outcome]], list[Outcome]]
AttackModifier = Callable[[SimpleWeapon, AttackOptions, list[Outcome]], list[Outcome]]
WoundModifier = Callable[[SimpleWeapon, int, AttackOptions, list[Outcome]], list[Outcome]]

def attack_modifier(func: AttackModifier) -> AttackModifier:
    setattr(func, "roll", "attack")
    return func

def wound_modifier(func: WoundModifier) -> WoundModifier:
    setattr(func, "roll", "wound")
    return func

def modifier(roll: str) -> Callable[[Modifier], Modifier]:
    def modify(func: Modifier) -> Modifier:
        setattr(func, "roll", roll)
        return func
    return modify


@attack_modifier
def torrent(weapon: SimpleWeapon, options: AttackOptions, outcomes: list[Outcome]) -> list[Outcome]:
    return [ Outcome(o.value, o.success, bool(o.success), o.reroll) for o in outcomes ]

def rapid_fire(amount:int) -> AttackModifier:

    @attack_modifier
    def update(weapon: SimpleWeapon, options: AttackOptions, outcomes: list[Outcome]) -> list[Outcome]:
        if options.rng*2 <=  weapon.R:
            return [ Outcome(o.value + amount , o.success, o.bypass_next, o.reroll) for o in outcomes ]
        else:
            return outcomes

    return update

def sustained_hits(count:int) -> Modifier:

    @modifier('hit')
    def update(weapon: SimpleWeapon, options: AttackOptions, outcomes: list[Outcome]) -> list[Outcome]:
        return [ Outcome(o.value + (count if o.success.critical() else 0), o.success, o.bypass_next, o.reroll) for o in outcomes ]

    return update

@modifier('hit')
def lethal_hits(weapon: SimpleWeapon, options: AttackOptions, outcomes: list[Outcome]) -> list[Outcome]:
    return [ Outcome(o.value, o.success, o.success.critical() or o.bypass_next, o.reroll) for o in outcomes ]


@wound_modifier
def devestating_wounds(weapon: SimpleWeapon, target_toughness:int, options: AttackOptions, outcomes: list[Outcome]) -> list[Outcome]:
    return [ Outcome(o.value, o.success, o.success.critical() or o.bypass_next, o.reroll) for o in outcomes ]

@wound_modifier
def twin_linked(weapon: SimpleWeapon, target_toughness:int, options: AttackOptions, outcomes: list[Outcome]) -> list[Outcome]:
    return [ Outcome(o.value, o.success, o.success.critical() or o.bypass_next, True) for o in outcomes ]

def anti(amount:int) -> WoundModifier:

    @wound_modifier
    def update(weapon: SimpleWeapon, target_toughtness:int, options: AttackOptions, outcomes: list[Outcome]) -> list[Outcome]:
        return [ Outcome(o.value , oc.critical() if o.value >= amount else o.success, o.bypass_next, o.reroll) for o in outcomes ]

    return update

def melta(count:int) -> Modifier:

    @modifier('damage')
    def update(weapon: SimpleWeapon, options: AttackOptions, outcomes: list[Outcome]) -> list[Outcome]:
        if options.rng*2 <=  weapon.R:
            return [ Outcome(o.value + count, o.success, o.bypass_next, o.reroll) for o in outcomes ]
        else:
            return outcomes

    return update


