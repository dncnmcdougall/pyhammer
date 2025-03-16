from typing import Any
from events import EventSet, EventSuccess
from functools import cache

import events as ev
import actions
from actions import AttackOptions, Modifier
from outcomes import Dice

from model import SimpleModel
from weapon import SimpleWeapon


@cache
def feel_no_pain_roll(fnp_char: int, options: AttackOptions, reroll: bool) -> ev.Together:
    # Like the save throw, a successful FNP means a failure to damage. i.e. negation
    results: list[EventSet] = [
        ev.Leaf("dmg", suc)
        for suc in [
            ev.failure() if fnp.success else ev.success()
            for fnp in actions.feel_no_pain(options.modifiers, fnp_char, options)
        ]
    ]
    return ev.Together(results, name="fnp")


@cache
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
            success = EventSuccess(sum(k.value for k in key.outcomes), spill=spill)
            res.append(ev.Leaf("a", success, probability=prob))
        results.append(ev.Together(tuple(res)))

        # results.append(ev.All(possible_damage, name="d"))

    return ev.Together(results, name="dr")


@cache
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
    return ev.Together(results, name="sr")


@cache
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
    return ev.Together(results, name="wr")


@cache
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
    return ev.Together(results, name="hr")


@cache
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
) -> ev.Together:
    results: list[EventSet] = []
    for attack in actions.attack(options.modifiers, attack_char, options):
        if attack.bypass_next:
            possible_attacks: list[EventSet] = []
            wound_results = wound_roll(
                strength_char, target_toughness, save_char, armour_penetration, damage_char, fnp_char, options, True
            )
            for _ in range(attack.value):
                possible_attacks.append(wound_results)
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
            results.append(ev.All(possible_attacks, name="suc"))
        elif attack.reroll and reroll:
            results.append(
                attack_roll(
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
            )
        else:
            results.append(ev.Leaf("attack", ev.failure()))
    return ev.Together(results, name="ar")
