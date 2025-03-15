from .options import AttackOptions

from .attack import attack, torrent, rapid_fire
from .hit import hit, sustained_hits, critical_hits, lethal_hits, bypass_wound, all_hits_critical, reroll_hit_1
from .wound import wound, devastating_wounds, twin_linked, anti, melta, all_wounds_critical
from .damage import damage
from .save import save, bypass_save
from .feel_no_pain import feel_no_pain
from .null import (
    indirect_fire,
    ignores_cover,
    hazardous,
    pistol,
    precision,
    blast,
    mortal_wounds,
    one_shot,
    assult,
    heavy,
)
