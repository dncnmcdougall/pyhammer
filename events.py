from collections import defaultdict
from dataclasses import dataclass
from abc import ABC, abstractmethod

Probability = float

max_damage = 20


@dataclass(frozen=True)
class EventResult:
    """
    Stores a damage result
    The damage is stored as a list.
    The position
    """

    results: tuple[int, ...] = (0,) * max_damage
    count: int = 0

    @staticmethod
    def join(first, second) -> "EventResult":
        values = [first.results[ii] + second.results[ii] for ii in range(max_damage)]
        count = max([ii + 1 if v else 0 for ii, v in enumerate(values)])
        return EventResult(tuple(values), count)

    def total(self) -> int:
        return sum([(ii + 1) * v for ii, v in enumerate(self.results)])

    def reduce_to_max(self, amount: int) -> "EventResult":
        assert amount <= max_damage
        values = [0 for _ in range(amount)]
        for ii, v in enumerate(self.results):
            if ii >= (amount - 1):
                values[amount - 1] += v
            else:
                values[ii] += v
        return EventResult(tuple(values), count=amount)


def success(amount: int = 1) -> EventResult:
    assert amount <= max_damage
    return EventResult(tuple([1 if ii + 1 == amount else 0 for ii in range(max_damage)]), count=amount)


def failure() -> EventResult:
    return EventResult(tuple([0 for _ in range(max_damage)]), count=0)


class EventSet(ABC):
    def __init__(self, events: tuple["EventSet", ...] | list["EventSet"], name="", probability: Probability = 1.0):
        self.events = events if isinstance(events, tuple) else tuple(events)
        self.name = name
        self.probability = probability

    @abstractmethod
    def outcomes(self) -> dict[EventResult, Probability]: ...

    @abstractmethod
    def _title(self) -> str: ...

    def __repr__(self) -> str:
        prefix = f"{self.name}:" if len(self.name) else ""
        inner = "\n".join(f"|   {p}" for e in self.events for p in repr(e).split("\n"))

        return f"{self._title()}({prefix}\n{inner}\n)"


class Leaf(EventSet):
    def __init__(self, name: str, outcome: EventResult, probability: Probability = 1.0):
        super().__init__(tuple(), name=name, probability=probability)
        self.outcome = outcome

    def _title(self) -> str:
        return "L"

    def __repr__(self) -> str:
        return f"{self.name}:{repr(self.outcome)}"

    def outcomes(self) -> dict[EventResult, Probability]:
        return {self.outcome: self.probability}


class All(EventSet):
    def _title(self) -> str:
        return "A"

    def outcomes(self) -> dict[EventResult, Probability]:
        outcome_map = defaultdict(float)

        for ii, event in enumerate(self.events):
            set_outcomes = event.outcomes()
            if ii == 0:
                for key, prob in set_outcomes.items():
                    outcome_map[key] += prob
            else:
                new_outcome_map = defaultdict(float)
                for key, prob in outcome_map.items():
                    for this_key, this_prob in set_outcomes.items():
                        new_key = EventResult.join(key, this_key)
                        new_outcome_map[new_key] += prob * this_prob
                outcome_map = new_outcome_map
        return outcome_map


class Together(EventSet):
    def _title(self) -> str:
        return "T"

    def outcomes(self) -> dict[EventResult, Probability]:
        total_prob = sum(e.probability for e in self.events)
        fractional_probability = 1.0 / total_prob

        outcome_map = defaultdict(float)
        for event in self.events:
            event_outcomes = event.outcomes()
            for key, prob in event_outcomes.items():
                outcome_map[key] += prob * fractional_probability

        if abs(sum(outcome_map.values()) - 1) > 1e-7:
            raise ValueError(f"Expected outcome ({abs(sum(outcome_map.values()) - 1)}) to be < 1e-7")
        return outcome_map


def collapse_tree(tree: dict[EventResult, Probability] | EventSet | list[EventSet], name: str = "") -> Together:
    map: dict[EventResult, Probability] = {}
    if isinstance(tree, dict):
        map = tree
    elif isinstance(tree, EventSet):
        map = tree.outcomes()
    elif isinstance(tree, list):
        map = Together(tree).outcomes()

    res = []
    for key, prob in map.items():
        res.append(Leaf("a", key, probability=prob))
    return Together(res, name=name)


def cap_damage(
    tree: dict[EventResult, Probability] | EventSet | list[EventSet], cap: int
) -> dict[EventResult, Probability]:
    map: dict[EventResult, Probability] = {}
    if isinstance(tree, dict):
        map = tree
    elif isinstance(tree, EventSet):
        map = tree.outcomes()
    elif isinstance(tree, list):
        map = Together(tree).outcomes()

    res = defaultdict(float)
    for key, prob in map.items():
        capped_key = key.reduce_to_max(cap)
        res[capped_key] += prob
    return res


def average_damage(tree: dict[EventResult, Probability] | EventSet | list[EventSet]) -> float:
    map: dict[EventResult, Probability] = {}
    if isinstance(tree, dict):
        map = tree
    elif isinstance(tree, EventSet):
        map = tree.outcomes()
    elif isinstance(tree, list):
        map = Together(tree).outcomes()

    average_damage = 0
    res = defaultdict(float)
    for key, prob in map.items():
        average_damage += key.total() * prob
    return average_damage
