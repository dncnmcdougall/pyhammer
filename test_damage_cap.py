# ruff: noqa: N802, N806

from icecream import ic

import roll as rl
from actions import AttackOptions
import actions
from outcomes import Dice
from events import cap_damage

from testutils import nearly, ExpectedOutcomes


def test_A1DN():
    options = AttackOptions(half_range=False, cover=False, anti_active=False, modifiers=tuple())

    fail_hit = 1 / 6
    pass_hit = 5 / 6

    fail_wound = 1 / 6
    pass_wound = 5 / 6

    damage_cap = 2

    for damage_char in range(1, 4):
        damage, all_possibilities = rl.attack_roll(
            attack_char=1,
            weapon_skill=2,
            strength_char=10,
            target_toughness=2,
            save_char=7,
            armour_penetration=0,
            damage_char=damage_char,
            fnp_char=7,
            options=options,
            reroll=True,
        )

        eo = ExpectedOutcomes()
        eo.add_expectation(damage=0, probability=fail_hit + (pass_hit * fail_wound))
        eo.add_expectation(damage=min(damage_char, damage_cap), probability=(pass_hit * pass_wound))
        eo.test(cap_damage(damage.outcomes(), damage_cap))


def test_Ad2D1():
    options = AttackOptions(half_range=False, cover=False, anti_active=False, modifiers=tuple())
    damage, all_possibilities = rl.attack_roll(
        attack_char=Dice(1, 2),
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

    A1_0 = fail_hit + (pass_hit * fail_wound)
    A1_1 = pass_hit * pass_wound

    A2_0 = A1_0 * A1_0
    A2_1 = 2 * A1_0 * A1_1
    A2_2 = A1_1 * A1_1

    damage_cap = 1

    eo = ExpectedOutcomes()
    eo.add_expectation(damage=0, probability=A1_0 * 0.5 + A2_0 * 0.5)
    eo.add_expectation(damage=1, probability=A1_1 * 0.5 + A2_1 * 0.5)
    eo.add_expectation(damage=2, probability=A2_2 * 0.5)

    eo.test(cap_damage(damage.outcomes(), damage_cap))


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

    fail_hit = 1 / 6
    pass_hit = 5 / 6

    fail_wound = 1 / 6
    pass_wound = 5 / 6

    eo = ExpectedOutcomes()
    eo.add_expectation(damage=0, probability=fail_hit + (pass_hit * fail_wound))
    eo.add_expectation(damage=1, probability=(pass_hit * pass_wound) * third)
    eo.add_expectation(damage=2, probability=(pass_hit * pass_wound) * 2 * third)

    damage_cap = 2
    eo.test(cap_damage(damage.outcomes(), damage_cap))


if __name__ == "__main__":
    test_A1DN()
    test_Ad2D1()
    test_A1Dd3()
