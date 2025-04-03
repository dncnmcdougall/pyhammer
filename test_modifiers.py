# ruff: noqa: N802, N806

from icecream import ic

import roll as rl
from actions import AttackOptions
import actions
from outcomes import Dice

from testutils import nearly, ExpectedOutcomes


def test_A1D1SH1():
    options = AttackOptions(half_range=False, cover=False, anti_active=False, modifiers=(actions.sustained_hits(1),))
    damage, all_possibilities = rl.attack_roll(
        attack_char=1,
        weapon_skill=2,
        strength_char=10,
        target_toughness=2,
        save_char=7,
        armour_penetration=0,
        damage_char=1,
        fnp_char=7,
        options=options,
        reroll=True,
    )

    fail_hit = 1 / 6
    pass_hit = 4 / 6
    crit_hit = 1 / 6

    fail_wound = 1 / 6
    pass_wound = 5 / 6

    eo = ExpectedOutcomes()
    eo.add_expectation(damage=0, probability=fail_hit + (pass_hit * fail_wound) + (crit_hit * fail_wound * fail_wound))
    eo.add_expectation(damage=1, probability=(pass_hit * pass_wound) + (crit_hit * 2 * pass_wound * fail_wound))
    eo.add_expectation(damage=2, probability=crit_hit * pass_wound * pass_wound)
    eo.test(damage.outcomes())


def test_A1D1LH1():
    options = AttackOptions(half_range=False, cover=False, anti_active=False, modifiers=(actions.lethal_hits,))
    damage, all_possibilities = rl.attack_roll(
        attack_char=1,
        weapon_skill=2,
        strength_char=10,
        target_toughness=2,
        save_char=7,
        armour_penetration=0,
        damage_char=1,
        fnp_char=7,
        options=options,
        reroll=True,
    )

    fail_hit = 1 / 6
    pass_hit = 4 / 6
    crit_hit = 1 / 6

    fail_wound = 1 / 6
    pass_wound = 5 / 6

    eo = ExpectedOutcomes()
    eo.add_expectation(damage=0, probability=fail_hit + (pass_hit * fail_wound))
    eo.add_expectation(damage=1, probability=(pass_hit * pass_wound) + crit_hit)
    eo.test(damage.outcomes())


if __name__ == "__main__":
    test_A1D1SH1()
    test_A1D1LH1()
