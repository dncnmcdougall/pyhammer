from .base import action, modifier, Modifier
from .options import AttackOptions

from outcomes import Outcome, Dice
import outcomes as oc


@action("save")
def save(SV: int, armour_piercing: int, options: AttackOptions) -> list[Outcome]:
    successes = [ii >= (SV - armour_piercing) for ii in range(1, 7)]
    return [
        Outcome(1 if success else 0, ii + 1, oc.success(success), False, False) for ii, success in enumerate(successes)
    ]


@modifier("save")
def bypass_save(outcomes: list[Outcome], SV: int, armour_piercing: int, options: AttackOptions) -> list[Outcome]:
    return [Outcome(1, 0, oc.failure(), False, False)]
