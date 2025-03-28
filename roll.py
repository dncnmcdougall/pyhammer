from typing import Any
from events import EventSet, Probability, collapse_tree
from functools import lru_cache

import events as ev
import actions
from actions import AttackOptions, Modifier
from outcomes import Dice

from model import SimpleModel
from weapon import SimpleWeapon

LRU_CACHEMAX_MAX = 1_000


class ProbabilityTreeTooLargeError(Exception):
    pass


def return_res(results, name):
    # print(f'{name}{len(results)},', end='', flush=True)
    return ev.collapse_tree(results, name=name)


@lru_cache(maxsize=LRU_CACHEMAX_MAX)
def feel_no_pain_roll(fnp_char: int, options: AttackOptions, reroll: bool) -> ev.Together:
    # Like the save throw, a successful FNP means a failure to damage. i.e. negation
    results: list[EventSet] = [
        ev.Leaf("dmg", suc)
        for suc in [
            ev.failure() if fnp.success else ev.success(1)
            for fnp in actions.feel_no_pain(options.modifiers, fnp_char, options)
        ]
    ]
    return return_res(results, "F")


@lru_cache(maxsize=LRU_CACHEMAX_MAX)
def damage_roll(
    damage_char: int,
    spill: bool,
    fnp_char: int,
    options: AttackOptions,
    reroll: bool,
) -> ev.Together:
    results: list[EventSet] = []
    for damage in actions.damage(options.modifiers, damage_char, options):
        possible_damage = []
        for _ in range(damage.value):
            possible_damage.append(feel_no_pain_roll(fnp_char, options, True))

        all = ev.All(tuple(possible_damage))

        res = []
        for key, prob in all.outcomes().items():
            assert key.count <= 1
            if key.count > 0:
                res.append(ev.Leaf("a", ev.success(key.results[0]), probability=prob))
            else:
                res.append(ev.Leaf("a", ev.failure(), probability=prob))
        results.append(ev.Together(res))

    return return_res(results, "D")


@lru_cache(maxsize=LRU_CACHEMAX_MAX)
def save_roll(
    save_char: int,
    armour_penetration: int,
    damage_char: int,
    fnp_char: int,
    options: AttackOptions,
    reroll: bool,
) -> ev.Together:
    results: list[EventSet] = []
    for save in actions.save(options.modifiers, save_char, armour_penetration, options):
        if save.success:
            results.append(ev.Leaf("s-f", ev.failure()))
        elif save.reroll and reroll:
            results.append(save_roll(save_char, armour_penetration, damage_char, fnp_char, options, False))
        else:
            results.append(damage_roll(damage_char, False, fnp_char, options, True))
    return return_res(results, "S")


@lru_cache(maxsize=LRU_CACHEMAX_MAX)
def wound_roll(
    strength_char: int,
    target_toughness: int,
    save_char: int,
    armour_penetration: int,
    damage_char: int,
    fnp_char: int,
    options: AttackOptions,
    reroll: bool,
) -> ev.Together:
    results: list[EventSet] = []
    for wound in actions.wound(options.modifiers, strength_char, target_toughness, options):
        if wound.bypass_next:
            results.append(damage_roll(damage_char, False, fnp_char, options, True))
        elif wound.success:
            results.append(save_roll(save_char, armour_penetration, damage_char, fnp_char, options, True))
        elif wound.reroll and reroll:
            results.append(
                wound_roll(
                    strength_char,
                    target_toughness,
                    save_char,
                    armour_penetration,
                    damage_char,
                    fnp_char,
                    options,
                    False,
                )
            )
        else:
            results.append(ev.Leaf("w-f", ev.failure()))
    return return_res(results, "W")


@lru_cache(maxsize=LRU_CACHEMAX_MAX)
def hit_roll(
    weapon_skill: int,
    strength_char: int,
    target_toughness: int,
    save_char: int,
    armour_penetration: int,
    damage_char: int,
    fnp_char: int,
    options: AttackOptions,
    reroll: bool,
) -> ev.Together:
    results: list[EventSet] = []
    for hit in actions.hit(options.modifiers, weapon_skill, options):
        if hit.bypass_next:
            possible_hits: list[EventSet] = []
            save_results = save_roll(save_char, armour_penetration, damage_char, fnp_char, options, True)
            for _ in range(hit.value):
                possible_hits.append(save_results)
            results.append(ev.All(tuple(possible_hits), name="h-b"))
        elif hit.success:
            possible_hits: list[EventSet] = []
            wound_results = wound_roll(
                strength_char, target_toughness, save_char, armour_penetration, damage_char, fnp_char, options, True
            )
            for _ in range(hit.value):
                possible_hits.append(wound_results)
            results.append(ev.All(tuple(possible_hits), name="h-s"))
        elif hit.reroll and reroll:
            results.append(
                hit_roll(
                    weapon_skill,
                    strength_char,
                    target_toughness,
                    save_char,
                    armour_penetration,
                    damage_char,
                    fnp_char,
                    options,
                    False,
                )
            )
        else:
            results.append(ev.Leaf("h-f", ev.failure()))
    return return_res(results, "H")


@lru_cache(maxsize=LRU_CACHEMAX_MAX)
def attack_roll(
    attack_char: int | Dice,
    weapon_skill: int,
    strength_char: int,
    target_toughness: int,
    save_char: int,
    armour_penetration: int,
    damage_char: int | Dice,
    fnp_char: int,
    options: AttackOptions,
    reroll: bool,
) -> tuple[ev.Together, tuple[int, int]]:
    results: list[EventSet] = []
    all_possibilities = tuple()
    for attack in actions.attack(options.modifiers, attack_char, options):
        if attack.bypass_next:
            possible_attacks: list[EventSet] = []
            wound_results = wound_roll(
                strength_char, target_toughness, save_char, armour_penetration, damage_char, fnp_char, options, True
            )
            for _ in range(attack.value):
                possible_attacks.append(wound_results)
            all_possibilities = (attack.value, len(wound_results.events))
            results.append(ev.All(possible_attacks, name="byp"))
        elif attack.success:
            possible_attacks: list[EventSet] = []
            hit_results = hit_roll(
                weapon_skill,
                strength_char,
                target_toughness,
                save_char,
                armour_penetration,
                damage_char,
                fnp_char,
                options,
                True,
            )

            for _ in range(attack.value):
                possible_attacks.append(hit_results)
            all_possibilities = (attack.value, len(hit_results.events))
            results.append(ev.All(possible_attacks, name="suc"))
        elif attack.reroll and reroll:
            attack_result, all_possibilities = attack_roll(
                attack_char,
                weapon_skill,
                strength_char,
                target_toughness,
                save_char,
                armour_penetration,
                damage_char,
                fnp_char,
                options,
                False,
            )
            results.append(attack_result)
        else:
            results.append(ev.Leaf("attack", ev.failure()))
            all_possibilities = (1, 1)
    return return_res(results, "A"), all_possibilities
