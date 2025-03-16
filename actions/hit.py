from .base import action, modifier, Modifier
from .options import AttackOptions

from outcomes import Outcome, Dice
import outcomes as oc


@action("hit")
def hit(WS: int, options: AttackOptions) -> list[Outcome]:
    return [
        Outcome(1, 1, oc.failure(), False, False),
        Outcome(1, 2, oc.success(2 >= WS), False, False),
        Outcome(1, 3, oc.success(3 >= WS), False, False),
        Outcome(1, 4, oc.success(4 >= WS), False, False),
        Outcome(1, 5, oc.success(5 >= WS), False, False),
        Outcome(1, 6, oc.critical(), False, False),
    ]


def sustained_hits(count: int | Dice) -> Modifier:
    if isinstance(count, int):

        @modifier(hit, f"sustained_hits_{str(count)}")
        def update(outcomes: list[Outcome], WS: int, options: AttackOptions) -> list[Outcome]:
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
    else:

        @modifier(hit, f"sustained_hits_{count}")
        def update(outcomes: list[Outcome], WS: int, options: AttackOptions) -> list[Outcome]:
            output = []

            roll = count()

            for o in outcomes:
                if o.success.critical():
                    for r in roll:
                        output.append(Outcome(o.value + r.roll_value, o.roll_value, o.success, o.bypass_next, o.reroll))
                else:
                    output.append(o)
            return output

    return update


def critical_hits(count: int) -> Modifier:
    @modifier(hit, f"critical_hits_{count}")
    def update(outcomes: list[Outcome], WS: int, options: AttackOptions) -> list[Outcome]:
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


@modifier(hit)
def all_hits_critical(outcomes: list[Outcome], WS: int, options: AttackOptions) -> list[Outcome]:
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


@modifier(hit, "re-roll hit 1")
def reroll_hit_1(outcomes: list[Outcome], WS: int, options: AttackOptions) -> list[Outcome]:
    return [
        Outcome(
            o.value,
            o.roll_value,
            oc.critical() if o.success else o.success,
            o.bypass_next,
            o.reroll if o.roll_value != 1 else True,
        )
        for o in outcomes
    ]


@modifier(hit)
def lethal_hits(outcomes: list[Outcome], WS: int, options: AttackOptions) -> list[Outcome]:
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


@modifier(hit)
def bypass_wound(outcomes: list[Outcome], WS: int, options: AttackOptions) -> list[Outcome]:
    return [
        Outcome(
            o.value,
            o.roll_value,
            o.success,
            True,
            o.reroll,
        )
        for o in outcomes
    ]
