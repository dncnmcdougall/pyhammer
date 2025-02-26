from typing import Type, TypeVar

from dataclasses import dataclass

T = TypeVar('T')

def collect(items: Type[T]) -> dict[T, int]:
        collection = {}
        for item in items:
            if item not in collection:
                collection[item] = 1
            else:
                collection[item] += 1
        return collection


@dataclass(frozen=True)
class Outcome:
    value: int
    success: bool
    bypass_next: bool

    def __lt__(self, other) -> bool:
        if self.value < other.value:
            return True
        if self.success < other.success:
            return True
        if self.bypass_next < other.bypass_next:
            return True
        return False

    def __repr__(self) -> str:
        return f"O({self.value}, {str(self.success)[0]}{str(self.bypass_next)[0]})"

@dataclass(frozen=True)
class OutcomeSequence:
    outcomes: tuple[Outcome]

    def __init__(self, outcomes):
        object.__setattr__(self, 'outcomes', tuple(outcomes))

    def success(self):
        result = len(self.outcomes) > 0 
        for outcome in self.outcomes:
            result = result and outcome.success
        return result

    def __repr__(self) -> str:
        return f"OS({','.join(repr(o) for o in self.outcomes)})"

    @staticmethod
    def append(original: "OutcomeSequence", addition: Outcome) -> "OutcomeSequence":
        return OutcomeSequence([*original.outcomes, addition])

    @staticmethod
    def prepend(addition: Outcome, original: "OutcomeSequence") -> "OutcomeSequence":
        return OutcomeSequence([addition, *original.outcomes])

    @staticmethod
    def join(*outcomes: Outcome) -> "OutcomeSequence":
        return OutcomeSequence(outcomes)


@dataclass
class OutcomeTree:
    count: float
    outcome: Outcome
    children: list["OutcomeTree"]

    def to_sequences(self) -> dict[OutcomeSequence, float]:
        results = {}
        if len(self.children) == 0 :
            results[OutcomeSequence([self.outcome])] = self.count
        else:
            total = sum([ c.count for c in self.children ])
            for child in self.children:
                child_sequences = child.to_sequences()
                for sequence, count in child_sequences.items():
                    this_oc = OutcomeSequence.prepend(self.outcome, sequence)
                    this_count = (self.count/total)*count
                    if this_oc not in results:
                        results[this_oc] = this_count
                    else:
                        results[this_oc] += this_count
        return results

