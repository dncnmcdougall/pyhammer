from .base import Modifier as Modifier
from .options import (
    AttackOptions as AttackOptions,
)

from .attack import (
    attack as attack,
    torrent as torrent,
    rapid_fire as rapid_fire,
)
from .hit import (
    hit as hit,
    sustained_hits as sustained_hits,
    critical_hits as critical_hits,
    lethal_hits as lethal_hits,
    bypass_wound as bypass_wound,
    all_hits_critical as all_hits_critical,
    reroll_hit_1 as reroll_hit_1,
)
from .wound import (
    wound as wound,
    devastating_wounds as devastating_wounds,
    twin_linked as twin_linked,
    anti as anti,
    all_wounds_critical as all_wounds_critical,
)
from .damage import (
    damage as damage,
    melta as melta,
)
from .save import (
    save as save,
    bypass_save as bypass_save,
)
from .feel_no_pain import (
    feel_no_pain as feel_no_pain,
)
from .null import (
    indirect_fire as indirect_fire,
    ignores_cover as ignores_cover,
    hazardous as hazardous,
    pistol as pistol,
    precision as precision,
    blast as blast,
    mortal_wounds as mortal_wounds,
    one_shot as one_shot,
    assult as assult,
    heavy as heavy,
)
