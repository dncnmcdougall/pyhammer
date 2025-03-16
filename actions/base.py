import functools
from typing import Concatenate, ParamSpec, TypeVar, reveal_type

from collections.abc import Callable

type ModifierFunc[T, **P] = Callable[Concatenate[list[T], P], list[T]]


class Modifier[T, **P]:
    def __init__(self, name: str, action_name: str, modify_func: ModifierFunc[T, P]):
        self.name = name
        self.action_name = action_name
        self.modify_func = modify_func

    def __call__(self, outcomes: list[T], *args, **kwargs) -> list[T]:
        return self.modify_func(outcomes, *args, **kwargs)


type ActionFunc[T, **P] = Callable[P, list[T]]


class Action[T, **P]:
    def __init__(self, name: str, func: ActionFunc[T, P]):
        self.name = name
        self.func = func

    def __call__(self, modifiers: list[Modifier[T, P]], *args: P.args, **kwargs: P.kwargs) -> list[T]:
        results = self.func(*args, **kwargs)
        for modifier in modifiers:
            if modifier.action_name == self.name:
                results = modifier(results, *args, **kwargs)
        return results


def action[T, **P](action_name: str) -> Callable[[ActionFunc[T, P]], Action[T, P]]:
    def dec(func: ActionFunc[T, P]) -> Action[T, P]:
        return Action(action_name, func)

    return dec


def modifier[T, **P](action: Action[T, P], name: str | None = None) -> Callable[[ModifierFunc[T, P]], Modifier[T, P]]:
    def modify(func: ModifierFunc[T, P]) -> Modifier[T, P]:
        return Modifier(func.__name__ if name is None else name, action.name, func)

    return modify
