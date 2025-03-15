import functools
from typing import Concatenate, ParamSpec, TypeVar, reveal_type

from collections.abc import Callable

P = ParamSpec("P")


class Modifier[T]:
    def __init__(self, name: str, action_name: str, modify_func: Callable[Concatenate[list[T], P], list[T]]):
        self.name = name
        self.action_name = action_name
        self.modify_func = modify_func

    def __call__(self, outcomes: list[T], *args, **kwargs) -> list[T]:
        return self.modify_func(outcomes, *args, **kwargs)


type ActionFunc[T, **P] = Callable[P, list[T]]
type DecoratedActionFunc[T, **P] = Callable[Concatenate[list[Modifier[T]], P], list[T]]


def action[T, **P](action_name: str) -> Callable[[ActionFunc[T, P]], DecoratedActionFunc[T, P]]:
    def dec(func: ActionFunc[T, P]) -> DecoratedActionFunc[T, P]:
        @functools.wraps(func)
        def dec_impl(modifiers: list[Modifier[T]], *args: P.args, **kwargs: P.kwargs) -> list[T]:
            results = func(*args, **kwargs)
            for modifier in modifiers:
                if modifier.action_name == action_name:
                    results = modifier(results, *args, **kwargs)
            return results

        return dec_impl

    return dec


def modifier[T, **P](
    action: str, name: str | None = None
) -> Callable[[Callable[Concatenate[list[T], P], list[T]]], Modifier[T]]:
    def modify(func: Callable[Concatenate[list[T], P], list[T]]) -> Modifier:
        return Modifier(func.__name__ if name is None else name, action, func)

    return modify
