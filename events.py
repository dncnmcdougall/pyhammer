from typing import Self, Any
from collections import defaultdict
from enum import Enum
from dataclasses import dataclass
from abc import ABC, abstractmethod

from icecream import ic

Probablility = float

class EventSuccess(Enum):
    SUPERPOSITION = -1
    FAILURE = 0
    SUCCESS = 1

    def __repr__(self) -> str:
        match self.value:
            case self.SUCCESS.value:
                return 'S'
            case self.FAILURE.value:
                return 'F'
            case self.SUPERPOSITION.value:
                return '-'
            case _:
                raise ValueError(f'No value found for {self.value}')

    def __lt__(self, other) ->bool:
        return self.value < other.value


@dataclass
class CollapsedSuperposition:
    success: Probablility
    failure: Probablility

    def __repr__(self) -> str:
        return f'({self.success:.2f}, {self.failure:.2f})'

def success() -> EventSuccess:
    return EventSuccess.SUCCESS

def failure() -> EventSuccess:
    return EventSuccess.FAILURE

@dataclass(frozen=True)
class EventsKey:
    outcomes: tuple[EventSuccess]

    def __repr__(self) -> str:
        return ''.join( repr(o) for o in self.outcomes)

    @staticmethod
    def join(first, second) -> Self:
        return EventsKey( tuple([*first.outcomes, *second.outcomes]))

class EventSet(ABC):

    def __init__(self, events: list["EventSet"], name="", meta:dict[str,Any] = {}):
        self.events = events
        self.name = name
        self.meta = meta

    @abstractmethod
    def outcomes(self) -> dict[EventsKey, Probablility]:
        ...

    @abstractmethod
    def _title(self) -> str:
        ...

    def __repr__(self) -> str:
        prefix = f"{self.name}:" if len(self.name) else ""
        inner = '\n'.join( f'|   {p}' for e in self.events for p in repr(e).split("\n") )

        return f"{self._title()}({prefix}\n{inner}\n)"

class Leaf(EventSet):

    def __init__(self, name:str , outcome: EventSuccess):
        super().__init__([], name=name)
        self.outcome = outcome

    def _title(self) -> str:
        return 'L'

    def __repr__(self) -> str:
        return f'{self.name}:{repr(self.outcome)}'

    def outcomes(self) -> dict[EventsKey, Probablility]:
        return { EventsKey((self.outcome,)): 1}


class All(EventSet):

    def _title(self) -> str:
        return 'A'

    def outcomes(self) -> dict[EventsKey, Probablility]:
        outcomes:list[tuple[float,EventsKey]] = []
        for event in self.events:
            set_outcomes = event.outcomes()
            if len(outcomes) == 0:
                for key, prob in set_outcomes.items():
                    outcomes.append((prob, key))
            else:
                new_outcomes = []
                for prob,key in outcomes:
                    for this_key, this_prob in set_outcomes.items():
                        new_outcomes.append( (prob*this_prob, EventsKey.join(key,this_key)) )
                outcomes = new_outcomes
        outcome_map = defaultdict(float)
        for prob, key in outcomes:
            outcome_map[EventsKey(tuple(sorted(key.outcomes)))] += prob
        return outcome_map

class Together(EventSet):

    def _title(self) -> str:
        return 'T'

    def outcomes(self) -> dict[EventsKey, Probablility]:
        fractional_probability = 1.0/len(self.events)

        outcome_map = defaultdict(float)
        for events in self.events:
            event_outcomes = events.outcomes()
            for key, prob in event_outcomes.items():
                outcome_map[key] += prob*fractional_probability

        assert abs(sum(outcome_map.values()) -1) < 1e-7
        return outcome_map



