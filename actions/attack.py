from .base import action, modifier, Modifier
from .options import AttackOptions

from outcomes import Outcome, Dice
import outcomes as oc


@action("attack")
def attack(attach_char: int | Dice, options: AttackOptions) -> list[Outcome]:
    if isinstance(attach_char, Dice):
        return [Outcome(o.roll_value, o.roll_value, o.success, o.bypass_next, o.reroll) for o in attach_char()]
    else:
        return [Outcome(attach_char, -1, oc.success(), False, False)]


@modifier(attack)
def torrent(outcomes: list[Outcome], attach_char: int | Dice, options: AttackOptions) -> list[Outcome]:
    return [Outcome(o.value, o.roll_value, o.success, bool(o.success), o.reroll) for o in outcomes]


def rapid_fire(amount: int) -> Modifier:
    @modifier(attack, f"rapid_fire_{amount}")
    def update(outcomes: list[Outcome], attach_char: int | Dice, options: AttackOptions) -> list[Outcome]:
        if options.half_range:
            return [Outcome(o.value + amount, o.roll_value, o.success, o.bypass_next, o.reroll) for o in outcomes]
        else:
            return outcomes

    return update
