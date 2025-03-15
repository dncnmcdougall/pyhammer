from .base import action, modifier, Modifier
from .options import AttackOptions

from outcomes import Outcome, Dice
import outcomes as oc


@action("damage")
def damage(D: int | Dice, options: AttackOptions) -> list[Outcome]:
    if callable(D):
        return [Outcome(o.roll_value, o.roll_value, o.success, o.bypass_next, o.reroll) for o in D()]
    return [Outcome(D, -1, oc.success(), False, False)]
