# ruff: noqa: N802, N806

from icecream import ic

import roll as rl
from actions import AttackOptions
import actions
from outcomes import Dice
from events import average_damage

from testutils import nearly, ExpectedOutcomes


def test_A1D1():
    options = AttackOptions(half_range=False, cover=False, anti_active=False, modifiers=tuple())
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

    pass_hit = 5 / 6

    pass_wound = 5 / 6

    avg_dam = average_damage(damage.outcomes())

    nearly(avg_dam, (pass_hit * pass_wound))


def test_A1D2():
    options = AttackOptions(half_range=False, cover=False, anti_active=False, modifiers=tuple())
    damage, all_possibilities = rl.attack_roll(
        attack_char=1,
        weapon_skill=2,
        strength_char=10,
        target_toughness=2,
        save_char=7,
        armour_penetration=0,
        damage_char=2,
        fnp_char=7,
        options=options,
        reroll=True,
    )

    pass_hit = 5 / 6

    pass_wound = 5 / 6

    avg_dam = average_damage(damage.outcomes())

    nearly(avg_dam, (2 * pass_hit * pass_wound))


def test_A2D1():
    options = AttackOptions(half_range=False, cover=False, anti_active=False, modifiers=tuple())
    damage, all_possibilities = rl.attack_roll(
        attack_char=2,
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
    pass_hit = 5 / 6

    fail_wound = 1 / 6
    pass_wound = 5 / 6

    avg_dam = average_damage(damage.outcomes())

    nearly(
        avg_dam, (2 * (pass_hit * pass_wound) ** 2) + 2 * (pass_hit * pass_wound) * (pass_hit * fail_wound + fail_hit)
    )


def test_A1Dd3():
    options = AttackOptions(half_range=False, cover=False, anti_active=False, modifiers=tuple())
    damage, all_possibilities = rl.attack_roll(
        attack_char=1,
        weapon_skill=2,
        strength_char=10,
        target_toughness=2,
        save_char=7,
        armour_penetration=0,
        damage_char=Dice(1, 3),
        fnp_char=7,
        options=options,
        reroll=True,
    )

    third = 1 / 3

    pass_hit = 5 / 6

    pass_wound = 5 / 6

    avg_dam = average_damage(damage.outcomes())

    nearly(avg_dam, (1 + 2 + 3) * (pass_hit * pass_wound) * third)


if __name__ == "__main__":
    test_A1D1()
    test_A1D2()
    test_A2D1()
    test_A1Dd3()
