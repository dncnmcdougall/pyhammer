from copy import deepcopy
from dataclasses import dataclass

from icecream import ic

import roll as rl
from actions import AttackOptions
import actions
from outcomes import Dice


def nearly(a: float, b: float) -> bool:
    res = abs(a - b) < 1e-5
    assert res, f"{a} != {b}"


@dataclass
class ExpectedOutcome:
    damage: int
    probability: float
    count: int


class ExpectedOutcomes:
    def __init__(self):
        self.original_dict = {}
        self.test_dict = {}

    def add_expectation(self, damage, probability):
        assert damage not in self.original_dict
        self.original_dict[damage] = ExpectedOutcome(damage, probability, 1)

    def check_counts(self):
        for damage, test in self.test_dict.items():
            assert test.count == 0, f"Unused damage: {damage}"

    def test(self, outcomes) -> None:
        results = outcomes.items()
        assert len(results) == len(self.original_dict), (
            f"Expected {len(self.original_dict)} outcomes, but found {len(results)}"
        )
        self._init_for_testing()
        for key, prob in results:
            self._test(key, prob)
        self.check_counts()

    def _init_for_testing(self):
        total_prob = sum([v.probability for v in self.original_dict.values()])
        nearly(total_prob, 1.0)

        self.test_dict = deepcopy(self.original_dict)

    def _test(self, key, prob):
        damage = key.total()
        assert damage in self.test_dict, f"Incorrect damage: {damage}"
        nearly(self.test_dict[damage].probability, prob)
        self.test_dict[damage].count -= 1


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

    fail_hit = 1 / 6
    pass_hit = 5 / 6

    fail_wound = 1 / 6
    pass_wound = 5 / 6

    eo = ExpectedOutcomes()
    eo.add_expectation(damage=0, probability=fail_hit + (pass_hit * fail_wound))
    eo.add_expectation(damage=1, probability=(pass_hit * pass_wound))
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
    test_A1D1()
    test_A2D1()
    test_A1Dd3()
    test_Ad2D1()
    test_Ad3D1()
    test_A1D1SH1()
    test_A1D1LH1()
