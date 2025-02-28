from enum import Enum
from dataclasses import dataclass

Probablility = float

class EventSuccess(Enum):
    SUPERPOSITION = -1
    FAILURE = 0
    SUCCESS = 1

@dataclass
class CollapsedSuperposition:
    success: Probablility
    failure: Probablility

@dataclass
class EventOutcome:
    success: EventSuccess
    children: list["EventOutcome"]

    def collapse(self):
        match self.success:
            case EventSuccess.SUCCESS:
                assert len(self.children) == 0
                return CollapsedSuperposition(1,0)
            case EventSuccess.FAILURE:
                assert len(self.children) == 0
                return CollapsedSuperposition(1,0)


@dataclass
class Event:
    name: str
    outcome: EventOutcome

@dataclass
class Events:
    events: list[Event]

@dataclass
class PossibleEvents:
    posibilities: list[Events]

def superposition(outcomes: list[EventOutcome]) -> EventOutcome:
    return EventOutcome(EventSuccess.SUPERPOSITION, outcomes)

def success() -> EventOutcome:
    return EventOutcome(EventSuccess.SUCCESS, [])

def failure() -> EventOutcome:
    return EventOutcome(EventSuccess.FAILURE, [])
