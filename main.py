from collections import defaultdict
import math
from dataclasses import dataclass
from icecream import ic

from weapon import SimpleWeapon, AttackOptions
from weapon import torrent, sustained_hits, rapid_fire, lethal_hits, devestating_wounds, melta, anti, twin_linked
from model import SimpleModel

from events import Event, EventSet, EventOutcome
import events as ev


def saveRoll(weapon:SimpleWeapon, target:SimpleModel, options:AttackOptions, reroll:bool) -> EventOutcome:
    results = []
    for save in target.save(weapon.AP):
        if save.success:
            results.append(ev.failure())
        elif save.reroll and reroll:
             results.append(saveRoll(weapon, target, options, False))
        else:
            results.append(ev.success())
    return ev.superposition(results)

def woundRoll(weapon:SimpleWeapon, target:SimpleModel, options:AttackOptions, reroll:bool) -> EventOutcome:
    results = []
    for wound in weapon.wound(target.T, options):
        if wound.bypass_next:
            results.append(ev.success())
        elif wound.success:
            results.append(saveRoll(weapon, target, options, True))
        else:
            results.append(ev.failure())
    return ev.superposition(results)

def hitRoll(weapon:SimpleWeapon, target:SimpleModel, options:AttackOptions, reroll:bool) -> EventSet:
    results:list[EventSet] = []
    for hit in weapon.hit(options):
        if hit.bypass_next:
            possible_hits:list[EventSet] = []
            for _ in range(hit.value):
                possible_hits.append(ev.One(Event('hit', saveRoll(weapon, target, options, True))))
            results.append(ev.All(possible_hits, name='byp'))
        elif hit.success:
            possible_hits:list[EventSet] = []
            for _ in range(hit.value):
                possible_hits.append(ev.One(Event('hit', woundRoll(weapon, target, options, True))))
            results.append(ev.All(possible_hits, name='suc'))
        elif hit.reroll and reroll:
             results.append(hitRoll(weapon, target, options, False))
        else:
            results.append(ev.One(Event('hit', ev.failure())))
    return ev.Together(results, name="hr")

def attackRoll(weapon:SimpleWeapon, target:SimpleModel, options:AttackOptions, reroll:bool) -> EventSet:
    results:list[EventSet] = []
    for attack in weapon.attack(options):
        if attack.bypass_next:
            possible_attacks:list[EventSet] = []
            for _ in range(attack.value):
                possible_attacks.append(ev.One(Event('wound',woundRoll(weapon, target, options, True))))
            results.append(ev.All(possible_attacks, name='byp'))
        elif attack.success:
            possible_attacks:list[EventSet] = []
            for _ in range(attack.value):
                possible_attacks.append(hitRoll(weapon, target, options, True))
            results.append(ev.All(possible_attacks, name='suc'))
        elif attack.reroll and reroll:
             results.append(attackRoll(weapon, target, options, False))
        else:
            results.append(ev.One(Event('attack', ev.failure())))
    return ev.Together(results, name="ar")




if __name__ == "__main__":

    weapons = [
        # SimpleWeapon("Deathwatch Bolt Rifle", 24, 2, 3, 5,-2,1),
        # SimpleWeapon("Bolt Sniper Rifle", 36, 1, 3, 5,-2,3),
        SimpleWeapon("Bolt Rifle", 24, 2, 3, 4,-1,1),
        SimpleWeapon("Bolt Rifle TW", 24, 2, 3, 4,-1,1, [twin_linked]),
        # SimpleWeapon("Bolt Rifle sus 2", 24, 2, 3, 4,-1,1, [sustained_hits(2)]),
        # SimpleWeapon("Gauss flayer", 24, 1, 4, 4,0,1, [rapid_fire(1)]),
        # SimpleWeapon("Flamer WS 0", 12, 3, 0, 3,0,1, [torrent]),
        # SimpleWeapon("Gauss flayer ", 24, 1, 4, 4,0,1, ),
        # SimpleWeapon("Gauss flayer sus 2", 24, 1, 4, 4,0,1, [sustained_hits(2)]),
        # SimpleWeapon("Gauss flayer LH", 24, 1, 4, 4,0,1, [lethal_hits]),
        # SimpleWeapon("Gauss flayer DW", 24, 1, 4, 4,0,1, [ devestating_wounds]),
        # SimpleWeapon("Gauss flayer LH DW", 24, 1, 4, 4,0,1, [lethal_hits, devestating_wounds]),
        ]
    models = [
        SimpleModel("Warrior", 4, 4, 1),
        # SimpleModel("Intercessor", 4, 3, 2),
        ]

    for model in models:
        for weapon in weapons:
            for rng in [24]:
                options = AttackOptions(rng, False)
                print(f'{weapon.name} at {model.name} at {rng}"')
                wounds = attackRoll(weapon, model, options, True)

                results = sorted([ (key, prob) for key, prob in wounds.outcomes().items() ],key=lambda x: x[1], reverse=True)

                for key, prob in results:
                    print(f'{prob*100:.3g}%: {repr(key)}')







