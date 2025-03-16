from .base import action, modifier, Modifier
from .options import AttackOptions

from outcomes import Outcome, Dice
import outcomes as oc


@action("wound")
def wound(S: int, target_toughness: int, options: AttackOptions) -> list[Outcome]:
    return [
        Outcome(1, 1, oc.failure(), False, False),
        Outcome(1, 2, oc.success(S > 2 * target_toughness), False, False),
        Outcome(1, 3, oc.success(S > target_toughness), False, False),
        Outcome(1, 4, oc.success(S >= target_toughness), False, False),
        Outcome(1, 5, oc.success(2 * S > target_toughness), False, False),
        Outcome(1, 6, oc.critical(), False, False),
    ]


@modifier(wound)
def devastating_wounds(
    outcomes: list[Outcome],
    S: int,
    target_toughness: int,
    options: AttackOptions,
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


@modifier(wound, "twin-linked")
def twin_linked(
    outcomes: list[Outcome],
    S: int,
    target_toughness: int,
    options: AttackOptions,
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


def anti(keyword: str, amount: int) -> Modifier:
    @modifier(wound, f"anti_{keyword}_{amount}")
    def update(
        outcomes: list[Outcome],
        S: int,
        target_toughness: int,
        options: AttackOptions
    ) -> list[Outcome]:
        if options.anti_active:
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
        else:
            return outcomes

    return update

def critical_wounds(count: int) -> Modifier:
    @modifier(wound, f"critical_wounds_{count}")
    def update(outcomes: list[Outcome], S: int, target_toughness: int, options: AttackOptions) -> list[Outcome]:
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

    return update


@modifier(wound)
def all_wounds_critical(
    outcomes: list[Outcome], S: int, target_toughness: int, options: AttackOptions
) -> list[Outcome]:
    return [
        Outcome(
            o.value,
            o.roll_value,
            oc.critical() if o.success else o.success,
            o.bypass_next,
            o.reroll,
        )
        for o in outcomes
    ]
