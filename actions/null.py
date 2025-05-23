from .base import modifier, action
from .options import AttackOptions
from outcomes import Outcome


@action("null")
def null(options: AttackOptions) -> list[Outcome]:
    return []


@modifier(null)
def indirect_fire(outcomes: list[Outcome], options: AttackOptions) -> list[Outcome]:
    return outcomes


@modifier(null)
def ignores_cover(outcomes: list[Outcome], options: AttackOptions) -> list[Outcome]:
    return outcomes


@modifier(null)
def hazardous(outcomes: list[Outcome], options: AttackOptions) -> list[Outcome]:
    return outcomes


@modifier(null)
def pistol(outcomes: list[Outcome], options: AttackOptions) -> list[Outcome]:
    return outcomes


@modifier(null)
def precision(outcomes: list[Outcome], options: AttackOptions) -> list[Outcome]:
    return outcomes


@modifier(null)
def blast(outcomes: list[Outcome], options: AttackOptions) -> list[Outcome]:
    return outcomes


@modifier(null)
def mortal_wounds(outcomes: list[Outcome], options: AttackOptions) -> list[Outcome]:
    return outcomes


@modifier(null)
def one_shot(outcomes: list[Outcome], options: AttackOptions) -> list[Outcome]:
    return outcomes


@modifier(null)
def assult(outcomes: list[Outcome], options: AttackOptions) -> list[Outcome]:
    return outcomes


@modifier(null)
def heavy(outcomes: list[Outcome], options: AttackOptions) -> list[Outcome]:
    return outcomes


@modifier(null)
def lance(outcomes: list[Outcome], options: AttackOptions) -> list[Outcome]:
    return outcomes


@modifier(null)
def psychic(outcomes: list[Outcome], options: AttackOptions) -> list[Outcome]:
    return outcomes
