from .base import action, modifier, Modifier
from .options import AttackOptions

from outcomes import Outcome, Dice
import outcomes as oc


@action("feel_no_pain_char")
def feel_no_pain(feel_no_pain_char: int, options: AttackOptions) -> list[Outcome]:
    if feel_no_pain_char == 0:
        return [Outcome(1, -1, oc.failure(), False, False)]
    else:
        return [Outcome(1, ii, oc.success(ii >= feel_no_pain_char), False, False) for ii in range(1, 7)]
