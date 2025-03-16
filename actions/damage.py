from .base import action, modifier, Modifier
from .options import AttackOptions

from outcomes import Outcome, Dice
import outcomes as oc


@action("damage")
def damage(damage_char: int | Dice, options: AttackOptions) -> list[Outcome]:
    if callable(damage_char):
        return [Outcome(o.roll_value, o.roll_value, o.success, o.bypass_next, o.reroll) for o in damage_char()]
    return [Outcome(damage_char, -1, oc.success(), False, False)]


def melta(count: int) -> Modifier:
    @modifier(damage, f"melta_{count}")
    def update(outcomes: list[Outcome], damage_char: int | Dice, options: AttackOptions) -> list[Outcome]:
        if options.half_range:
            return [Outcome(o.value + count, o.roll_value, o.success, o.bypass_next, o.reroll) for o in outcomes]
        else:
            return outcomes

    return update
