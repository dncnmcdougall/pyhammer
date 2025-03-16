from collections import defaultdict
from dataclasses import dataclass
from abc import ABC, abstractmethod


Probability = float


@dataclass(frozen=True)
class EventSuccess:
    value: int
    spill: bool
    # SUPERPOSITION = -1
    # FAILURE = 0
    # SUCCESS = 1
    #
    # def __repr__(self) -> str:
    #     match self.value:
    #         case self.SUCCESS.value:
    #             return 'S'
    #         case self.FAILURE.value:
    #             return 'F'
    #         case self.SUPERPOSITION.value:
    #             return '-'
    #         case _:
    #             raise ValueError(f'No value found for {self.value}')

    def __repr__(self) -> str:
        if self.value == 0:
            return "- "
        else:
            return f"{str(self.value)}{'*' if self.spill else ' '}"

    def __lt__(self, other) -> bool:
        if self.value == other.value:
            return self.spill < other.spill
        else:
            return self.value < other.value


# @dataclass
# class CollapsedSuperposition:
#     success: Probability
#     failure: Probability
#
#     def __repr__(self) -> str:
#         return f'({self.success:.2f}, {self.failure:.2f})'


def success() -> EventSuccess:
    return EventSuccess(1, False)


def failure() -> EventSuccess:
    return EventSuccess(0, False)


@dataclass(frozen=True)
class EventsKey:
    outcomes: tuple[EventSuccess, ...]

    def __repr__(self) -> str:
        return "".join(repr(o) for o in self.outcomes)

    @staticmethod
    def join(first, second) -> "EventsKey":
        return EventsKey(tuple([*first.outcomes, *second.outcomes]))

    def summarise(self) -> "EventsKey":
        non_spill = []
        total_spill = 0
        for key in self.outcomes:
            if key.value == 0:
                continue
            if key.spill:
                total_spill += key.value
            else:
                non_spill.append(key.value)
        non_spill.sort()
        keys = [EventSuccess(v, False) for v in non_spill]
        if len(keys) == 0 or total_spill > 0:
            keys.append(EventSuccess(total_spill, True))
        return EventsKey(tuple(keys))


class EventSet(ABC):
    def __init__(self, events: tuple["EventSet", ...] | list["EventSet"], name="", probability: Probability = 1.0):
        self.events = events if isinstance(events, tuple) else tuple(events)
        self.name = name
        self.probability = probability

    @abstractmethod
    def outcomes(self) -> dict[EventsKey, Probability]: ...

    @abstractmethod
    def _title(self) -> str: ...

    def __repr__(self) -> str:
        prefix = f"{self.name}:" if len(self.name) else ""
        inner = "\n".join(f"|   {p}" for e in self.events for p in repr(e).split("\n"))

        return f"{self._title()}({prefix}\n{inner}\n)"


class Leaf(EventSet):
    def __init__(self, name: str, outcome: EventSuccess, probability: Probability = 1.0):
        super().__init__(tuple(), name=name, probability=probability)
        self.outcome = outcome

    def _title(self) -> str:
        return "L"

    def __repr__(self) -> str:
        return f"{self.name}:{repr(self.outcome)}"

    def outcomes(self) -> dict[EventsKey, Probability]:
        return {EventsKey((self.outcome,)): self.probability}


class All(EventSet):
    def _title(self) -> str:
        return "A"

    def outcomes(self) -> dict[EventsKey, Probability]:
        outcomes: list[tuple[float, EventsKey]] = []
        for event in self.events:
            set_outcomes = event.outcomes()
            if len(outcomes) == 0:
                for key, prob in set_outcomes.items():
                    outcomes.append((prob, key))
            else:
                new_outcomes = []
                for prob, key in outcomes:
                    for this_key, this_prob in set_outcomes.items():
                        new_outcomes.append((prob * this_prob, EventsKey.join(key, this_key)))
                outcomes = new_outcomes
        outcome_map = defaultdict(float)
        for prob, key in outcomes:
            outcome_map[key.summarise()] += prob
        return outcome_map


class Together(EventSet):
    def _title(self) -> str:
        return "T"

    def outcomes(self) -> dict[EventsKey, Probability]:
        total_prob = sum(e.probability for e in self.events)
        fractional_probability = 1.0 / total_prob

        outcome_map = defaultdict(float)
        for event in self.events:
            event_outcomes = event.outcomes()
            for key, prob in event_outcomes.items():
                outcome_map[key.summarise()] += prob * fractional_probability

        if abs(sum(outcome_map.values()) - 1) > 1e-7:
            raise ValueError(f"Expected outcome ({abs(sum(outcome_map.values()) - 1)}) to be < 1e-7")
        return outcome_map
