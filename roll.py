from events import EventSet, EventSuccess
from functools import cache

import events as ev

from model import SimpleModel
from weapon import SimpleWeapon, AttackOptions


@cache
def feelNoPainRoll(weapon: SimpleWeapon, target: SimpleModel, options: AttackOptions, reroll: bool) -> ev.Together:
    # Like the save throw, a successful FNP means a failure to damage. i.e. negation
    results: list[EventSet] = [
        ev.Leaf("dmg", suc) for suc in [ev.failure() if fnp.success else ev.success() for fnp in target.feel_no_pain()]
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
    for damage in weapon.damage(options):
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
    for save in target.save(weapon.AP):
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
    for wound in weapon.wound(target.T, options):
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
    for hit in weapon.hit(options):
        if hit.bypass_next:
            possible_hits: list[EventSet] = []
            for _ in range(hit.value):
                possible_hits.append(saveRoll(weapon, target, options, True))
            results.append(ev.All(tuple(possible_hits), name="h-b"))
        elif hit.success:
            possible_hits: list[EventSet] = []
            for _ in range(hit.value):
                possible_hits.append(woundRoll(weapon, target, options, True))
            results.append(ev.All(tuple(possible_hits), name="h-s"))
        elif hit.reroll and reroll:
            results.append(hitRoll(weapon, target, options, False))
        else:
            results.append(ev.Leaf("h-f", ev.failure()))
    return ev.Together(tuple(results), name="hr")


@cache
def attackRoll(weapon: SimpleWeapon, target: SimpleModel, options: AttackOptions, reroll: bool) -> ev.EventSet:
    results: list[EventSet] = []
    for attack in weapon.attack(options):
        if attack.bypass_next:
            possible_attacks: list[EventSet] = []
            for _ in range(attack.value):
                possible_attacks.append(woundRoll(weapon, target, options, True))
            results.append(ev.All(possible_attacks, name="byp"))
        elif attack.success:
            possible_attacks: list[EventSet] = []
            for _ in range(attack.value):
                possible_attacks.append(hitRoll(weapon, target, options, True))
            results.append(ev.All(possible_attacks, name="suc"))
        elif attack.reroll and reroll:
            results.append(attackRoll(weapon, target, options, False))
        else:
            results.append(ev.Leaf("attack", ev.failure()))
    return ev.Together(tuple(results), name="ar")
