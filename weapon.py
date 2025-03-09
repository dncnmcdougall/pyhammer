import functools
from typing import Callable, ParamSpec, TypeVar
from dataclasses import dataclass, field

from outcomes import Outcome, Dice
import outcomes as oc


P = ParamSpec("P")
R = TypeVar("R")

RollFunc = Callable[P, list[Outcome]]


def modify(roll: str) -> Callable[[RollFunc], RollFunc]:
    def dec(func: RollFunc) -> RollFunc:
        @functools.wraps(func)
        def dec_impl(self, *args: P.args, **kwargs: P.kwargs) -> list[Outcome]:
            results = func(self, *args, **kwargs)
            for modifier in self.modifiers:
                if modifier.roll == roll:
                    results = modifier(self, *args, results, **kwargs)
            return results

        return dec_impl

    return dec


@dataclass(frozen=True)
class AttackOptions:
    rng: int
    cover: bool


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
        return ",".join([mod.__name__ for mod in self.modifiers])

    @modify("attack")
    def attack(self, options: AttackOptions) -> list[Outcome]:
        if isinstance(self.A, Dice):
            return [Outcome(o.roll_value, o.roll_value, o.success, o.bypass_next, o.reroll) for o in self.A()]
        else:
            return [Outcome(self.A, -1, oc.success(), False, False)]

    @modify("hit")
    def hit(self, options: AttackOptions) -> list[Outcome]:
        return [
            Outcome(1, 1, oc.failure(), False, False),
            Outcome(1, 2, oc.success(2 >= self.WS), False, False),
            Outcome(1, 3, oc.success(3 >= self.WS), False, False),
            Outcome(1, 4, oc.success(4 >= self.WS), False, False),
            Outcome(1, 5, oc.success(5 >= self.WS), False, False),
            Outcome(1, 6, oc.critical(), False, False),
        ]

    @modify("wound")
    def wound(self, target_toughness: int, options: AttackOptions) -> list[Outcome]:
        return [
            Outcome(1, 1, oc.failure(), False, False),
            Outcome(1, 2, oc.success(self.S > 2 * target_toughness), False, False),
            Outcome(1, 3, oc.success(self.S > target_toughness), False, False),
            Outcome(1, 4, oc.success(self.S >= target_toughness), False, False),
            Outcome(1, 5, oc.success(2 * self.S > target_toughness), False, False),
            Outcome(1, 6, oc.critical(), False, False),
        ]

    @modify("damage")
    def damage(self, options: AttackOptions) -> list[Outcome]:
        if callable(self.D):
            return [Outcome(o.roll_value, o.roll_value, o.success, o.bypass_next, o.reroll) for o in self.D()]
        return [Outcome(self.D, -1, oc.success(), False, False)]

    def __str__(self) -> str:
        return f"{self.name}: A {self.A}, WS {self.WS}+, S {self.S}, AP -{self.AP}, D {self.D}"


Modifier = Callable[[SimpleWeapon, AttackOptions, list[Outcome]], list[Outcome]]
AttackModifier = Callable[[SimpleWeapon, AttackOptions, list[Outcome]], list[Outcome]]
WoundModifier = Callable[[SimpleWeapon, int, AttackOptions, list[Outcome]], list[Outcome]]


def attack_modifier(func: AttackModifier) -> AttackModifier:
    func.roll = "attack"
    return func


def wound_modifier(func: WoundModifier) -> WoundModifier:
    func.roll = "wound"
    return func


def modifier(roll: str) -> Callable[[Modifier], Modifier]:
    def modify(func: Modifier) -> Modifier:
        func.roll = roll
        return func

    return modify

@modifier("null")
def indirect_fire(weapon: SimpleWeapon, options: AttackOptions, outcomes: list[Outcome]) -> list[Outcome]:
    return outcomes

@modifier("null")
def ignores_cover(weapon: SimpleWeapon, options: AttackOptions, outcomes: list[Outcome]) -> list[Outcome]:
    return outcomes


@modifier("null")
def hazardous(weapon: SimpleWeapon, options: AttackOptions, outcomes: list[Outcome]) -> list[Outcome]:
    return outcomes


@modifier("null")
def pistol(weapon: SimpleWeapon, options: AttackOptions, outcomes: list[Outcome]) -> list[Outcome]:
    return outcomes


@modifier("null")
def precision(weapon: SimpleWeapon, options: AttackOptions, outcomes: list[Outcome]) -> list[Outcome]:
    return outcomes


@modifier("null")
def blast(weapon: SimpleWeapon, options: AttackOptions, outcomes: list[Outcome]) -> list[Outcome]:
    return outcomes


@attack_modifier
def torrent(weapon: SimpleWeapon, options: AttackOptions, outcomes: list[Outcome]) -> list[Outcome]:
    return [Outcome(o.value, o.roll_value, o.success, bool(o.success), o.reroll) for o in outcomes]


def rapid_fire(amount: int) -> AttackModifier:
    @attack_modifier
    def update(weapon: SimpleWeapon, options: AttackOptions, outcomes: list[Outcome]) -> list[Outcome]:
        return outcomes

        # if options.rng * 2 <= weapon.R:
        #     return [Outcome(o.value + amount, o.roll_value, o.success, o.bypass_next, o.reroll) for o in outcomes]
        # else:
        #     return outcomes

    update.__name__ = f"rapid_fire_{amount}"

    return update


def sustained_hits(count: int) -> Modifier:
    @modifier("hit")
    def update(weapon: SimpleWeapon, options: AttackOptions, outcomes: list[Outcome]) -> list[Outcome]:
        return [
            Outcome(
                o.value + (count if o.success.critical() else 0),
                o.roll_value,
                o.success,
                o.bypass_next,
                o.reroll,
            )
            for o in outcomes
        ]

    update.__name__ = f"sustained_hits_{count}"
    return update


def critical_hits(count: int) -> Modifier:
    @modifier("hit")
    def update(weapon: SimpleWeapon, options: AttackOptions, outcomes: list[Outcome]) -> list[Outcome]:
        return [
            Outcome(
                o.value,
                o.roll_value,
                o.success if o.roll_value < count else oc.critical(),
                o.bypass_next,
                o.reroll,
            )
            for o in outcomes
        ]

    update.__name__ = f"critical_hits_{count}"

    return update


@modifier("hit")
def lethal_hits(weapon: SimpleWeapon, options: AttackOptions, outcomes: list[Outcome]) -> list[Outcome]:
    return [
        Outcome(
            o.value,
            o.roll_value,
            o.success,
            o.success.critical() or o.bypass_next,
            o.reroll,
        )
        for o in outcomes
    ]


@wound_modifier
def devastating_wounds(
    weapon: SimpleWeapon,
    target_toughness: int,
    options: AttackOptions,
    outcomes: list[Outcome],
) -> list[Outcome]:
    return [
        Outcome(
            o.value,
            o.roll_value,
            o.success,
            o.success.critical() or o.bypass_next,
            o.reroll,
        )
        for o in outcomes
    ]


@wound_modifier
def twin_linked(
    weapon: SimpleWeapon,
    target_toughness: int,
    options: AttackOptions,
    outcomes: list[Outcome],
) -> list[Outcome]:
    return [
        Outcome(
            o.value,
            o.roll_value,
            o.success,
            o.success.critical() or o.bypass_next,
            True,
        )
        for o in outcomes
    ]


twin_linked.__name__ = "twin-linked"


def anti(amount: int) -> WoundModifier:
    @wound_modifier
    def update(
        weapon: SimpleWeapon,
        target_toughtness: int,
        options: AttackOptions,
        outcomes: list[Outcome],
    ) -> list[Outcome]:
        return [
            Outcome(
                o.value,
                o.roll_value,
                oc.critical() if o.value >= amount else o.success,
                o.bypass_next,
                o.reroll,
            )
            for o in outcomes
        ]

    update.__name__ = f"anti_{amount}"

    return update


def melta(count: int) -> Modifier:
    @modifier("damage")
    def update(weapon: SimpleWeapon, options: AttackOptions, outcomes: list[Outcome]) -> list[Outcome]:
        if options.rng * 2 <= weapon.R:
            return [Outcome(o.value + count, o.roll_value, o.success, o.bypass_next, o.reroll) for o in outcomes]
        else:
            return outcomes

    update.__name__ = f"melta_{count}"

    return update
