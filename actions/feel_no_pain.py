from .base import action, modifier, Modifier
from .options import AttackOptions

from outcomes import Outcome, Dice
import outcomes as oc


@action("FNP")
def feel_no_pain(FNP: int, options: AttackOptions) -> list[Outcome]:
    if FNP == 0:
        return [Outcome(1, -1, oc.failure(), False, False)]
    else:
        return [Outcome(1, ii, oc.success(ii >= FNP), False, False) for ii in range(1, 7)]
