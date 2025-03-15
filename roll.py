from events import EventSet, EventSuccess
from functools import cache

import events as ev
import actions
from actions import AttackOptions

from model import SimpleModel
from weapon import SimpleWeapon


@cache
def feelNoPainRoll(weapon: SimpleWeapon, target: SimpleModel, options: AttackOptions, reroll: bool) -> ev.Together:
    # Like the save throw, a successful FNP means a failure to damage. i.e. negation
    results: list[EventSet] = [
        ev.Leaf("dmg", suc)
        for suc in [
            ev.failure() if fnp.success else ev.success()
            for fnp in actions.feel_no_pain(weapon.modifiers, target.FNP, options)
        ]
    ]
    return ev.Together(tuple(results), name="fnp")


@cache
def damageRoll(
    weapon: SimpleWeapon,
    target: SimpleModel,
    options: AttackOptions,
    reroll: bool,
    spill: bool,
) -> ev.Together:
    results: list[EventSet] = []
    for damage in actions.damage(weapon.modifiers, weapon.D, options):
        possible_damage = []
        for _ in range(damage.value):
            possible_damage.append(feelNoPainRoll(weapon, target, options, True))

        all = ev.All(tuple(possible_damage))

        res = []
        for key, prob in all.outcomes().items():
            success = EventSuccess(sum(k.value for k in key.outcomes), spill=spill)
            res.append(ev.Leaf("a", success, probability=prob))
        results.append(ev.Together(tuple(res)))

        # results.append(ev.All(possible_damage, name="d"))

    return ev.Together(tuple(results), name="dr")


@cache
def saveRoll(weapon: SimpleWeapon, target: SimpleModel, options: AttackOptions, reroll: bool) -> ev.Together:
    results: list[EventSet] = []
    for save in actions.save(weapon.modifiers, target.S, weapon.AP, options):
        if save.success:
            results.append(ev.Leaf("s-f", ev.failure()))
        elif save.reroll and reroll:
            results.append(saveRoll(weapon, target, options, False))
        else:
            results.append(damageRoll(weapon, target, options, True, False))
    return ev.Together(tuple(results), name="sr")


@cache
def woundRoll(weapon: SimpleWeapon, target: SimpleModel, options: AttackOptions, reroll: bool) -> ev.Together:
    results: list[EventSet] = []
    for wound in actions.wound(weapon.modifiers, weapon.S, target.T, options):
        if wound.bypass_next:
            results.append(damageRoll(weapon, target, options, True, False))
        elif wound.success:
            results.append(saveRoll(weapon, target, options, True))
        elif wound.reroll and reroll:
            results.append(woundRoll(weapon, target, options, False))
        else:
            results.append(ev.Leaf("w-f", ev.failure()))
    return ev.Together(tuple(results), name="wr")


@cache
def hitRoll(weapon: SimpleWeapon, target: SimpleModel, options: AttackOptions, reroll: bool) -> ev.Together:
    results: list[EventSet] = []
    for hit in actions.hit(weapon.modifiers, weapon.WS, options):
        if hit.bypass_next:
            possible_hits: list[EventSet] = []
            save_results = saveRoll(weapon, target, options, True)
            for _ in range(hit.value):
                possible_hits.append(save_results)
            results.append(ev.All(tuple(possible_hits), name="h-b"))
        elif hit.success:
            possible_hits: list[EventSet] = []
            wound_results = woundRoll(weapon, target, options, True)
            for _ in range(hit.value):
                possible_hits.append(wound_results)
            results.append(ev.All(tuple(possible_hits), name="h-s"))
        elif hit.reroll and reroll:
            results.append(hitRoll(weapon, target, options, False))
        else:
            results.append(ev.Leaf("h-f", ev.failure()))
    return ev.Together(tuple(results), name="hr")


@cache
def attackRoll(weapon: SimpleWeapon, target: SimpleModel, options: AttackOptions, reroll: bool) -> ev.EventSet:
    results: list[EventSet] = []
    for attack in actions.attack(weapon.modifiers, weapon.A, options):
        if attack.bypass_next:
            possible_attacks: list[EventSet] = []
            wound_results = woundRoll(weapon, target, options, True)
            for _ in range(attack.value):
                possible_attacks.append(wound_results)
            results.append(ev.All(possible_attacks, name="byp"))
        elif attack.success:
            possible_attacks: list[EventSet] = []
            hit_results = hitRoll(weapon, target, options, True)
            for _ in range(attack.value):
                possible_attacks.append(hit_results)
            results.append(ev.All(possible_attacks, name="suc"))
        elif attack.reroll and reroll:
            results.append(attackRoll(weapon, target, options, False))
        else:
            results.append(ev.Leaf("attack", ev.failure()))
    return ev.Together(tuple(results), name="ar")
