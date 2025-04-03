from copy import deepcopy
from dataclasses import dataclass


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
