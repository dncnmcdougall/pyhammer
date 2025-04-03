# ruff: noqa: N802, N806

from icecream import ic

import roll as rl
from actions import AttackOptions
import actions
from outcomes import Dice

from testutils import nearly, ExpectedOutcomes


def test_A1D1():
    options = AttackOptions(half_range=False, cover=False, anti_active=False, modifiers=tuple())

    pass_hit_dict = {2: 5 / 6, 3: 4 / 6, 4: 3 / 6, 5: 2 / 6, 6: 1 / 6}
    pass_wound_dict = {9: 5 / 6, 5: 4 / 6, 4: 3 / 6, 3: 2 / 6, 2: 1 / 6}

    for ws, pass_hit in pass_hit_dict.items():
        fail_hit = 1 - pass_hit
        for st, pass_wound in pass_wound_dict.items():
            fail_wound = 1 - pass_wound

            damage, all_possibilities = rl.attack_roll(
                attack_char=1,
                weapon_skill=ws,
                strength_char=st,
                target_toughness=4,
                save_char=7,
                armour_penetration=0,
                damage_char=1,
                fnp_char=7,
                options=options,
                reroll=True,
            )

            eo = ExpectedOutcomes()
            eo.add_expectation(damage=0, probability=fail_hit + (pass_hit * fail_wound))
            eo.add_expectation(damage=1, probability=(pass_hit * pass_wound))
            eo.test(damage.outcomes())


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

    fail_hit = 1 / 6
    pass_hit = 5 / 6

    fail_wound = 1 / 6
    pass_wound = 5 / 6

    eo = ExpectedOutcomes()
    eo.add_expectation(damage=0, probability=fail_hit + (pass_hit * fail_wound))
    eo.add_expectation(damage=2, probability=(pass_hit * pass_wound))
    eo.test(damage.outcomes())


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

    eo = ExpectedOutcomes()
    eo.add_expectation(damage=0, probability=(pass_hit * fail_wound + fail_hit) ** 2)
    eo.add_expectation(damage=1, probability=2 * (pass_hit * pass_wound) * (pass_hit * fail_wound + fail_hit))
    eo.add_expectation(damage=2, probability=(pass_hit * pass_wound) ** 2)
    eo.test(damage.outcomes())


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
    eo.add_expectation(damage=2, probability=(pass_hit * pass_wound) * third)
    eo.add_expectation(damage=3, probability=(pass_hit * pass_wound) * third)
    eo.test(damage.outcomes())


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

    eo = ExpectedOutcomes()
    eo.add_expectation(damage=0, probability=A1_0 * 0.5 + A2_0 * 0.5)
    eo.add_expectation(damage=1, probability=A1_1 * 0.5 + A2_1 * 0.5)
    eo.add_expectation(damage=2, probability=A2_2 * 0.5)
    eo.test(damage.outcomes())


def test_Ad3D1():
    options = AttackOptions(half_range=False, cover=False, anti_active=False, modifiers=tuple())
    damage, all_possibilities = rl.attack_roll(
        attack_char=Dice(1, 3),
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

    A3_0 = A1_0 * A1_0 * A1_0
    A3_1 = 3 * A1_0 * A1_0 * A1_1
    A3_2 = 3 * A1_0 * A1_1 * A1_1
    A3_3 = A1_1 * A1_1 * A1_1

    third = 1 / 3.0

    eo = ExpectedOutcomes()
    eo.add_expectation(damage=0, probability=A1_0 * third + A2_0 * third + A3_0 * third)
    eo.add_expectation(damage=1, probability=A1_1 * third + A2_1 * third + A3_1 * third)
    eo.add_expectation(damage=2, probability=A2_2 * third + A3_2 * third)
    eo.add_expectation(damage=3, probability=A3_3 * third)
    eo.test(damage.outcomes())


if __name__ == "__main__":
    test_A1D1()
    test_A1D2()
    test_A2D1()
    test_A1Dd3()
    test_Ad2D1()
    test_Ad3D1()
