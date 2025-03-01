from collections import defaultdict
import math
from dataclasses import dataclass
from icecream import ic

from weapon import SimpleWeapon, AttackOptions
from weapon import torrent, sustained_hits, rapid_fire, lethal_hits, devestating_wounds, melta, anti, twin_linked, dice
from model import SimpleModel

from events import EventSet 
import events as ev

def feelNoPainRoll(weapon:SimpleWeapon, target:SimpleModel, options:AttackOptions, reroll:bool) -> ev.Together:
    # Like the save throw, a successful FNP means a failure to damage. i.e. negation
    results:list[EventSet] =  [ ev.Leaf('dmg', suc) for suc in  [ ev.failure() if fnp.success else ev.success() for fnp in target.feel_no_pain() ]]
    return ev.Together(results, name='fnp')

def damageRoll(weapon:SimpleWeapon, target:SimpleModel, options:AttackOptions, reroll:bool, spill: bool) -> ev.Together:
    results:list[EventSet] = []
    for damage in weapon.damage(options):
        possible_damage = []
        for _ in range(damage.value):
            possible_damage.append(feelNoPainRoll(weapon, target, options, True))
        results.append(ev.All(possible_damage, name="d", meta=dict(spill=spill)))

    return ev.Together(results, name="dr")

def saveRoll(weapon:SimpleWeapon, target:SimpleModel, options:AttackOptions, reroll:bool) -> ev.Together:
    results:list[EventSet] = []
    for save in target.save(weapon.AP):
        if save.success:
            results.append(ev.Leaf('s-f', ev.failure()))
        elif save.reroll and reroll:
             results.append(saveRoll(weapon, target, options, False))
        else:
            results.append(damageRoll(weapon, target, options, True, False))
    return ev.Together(results, name='sr')

def woundRoll(weapon:SimpleWeapon, target:SimpleModel, options:AttackOptions, reroll:bool) -> ev.Together:
    results:list[EventSet] = []
    for wound in weapon.wound(target.T, options):
        if wound.bypass_next:
            results.append(damageRoll(weapon, target, options, True, False))
        elif wound.success:
            results.append(saveRoll(weapon, target, options, True))
        elif wound.reroll and reroll:
             results.append(woundRoll(weapon, target, options, False))
        else:
            results.append(ev.Leaf('w-f', ev.failure()))
    return ev.Together(results, name="wr")

def hitRoll(weapon:SimpleWeapon, target:SimpleModel, options:AttackOptions, reroll:bool) -> ev.Together:
    results:list[EventSet] = []
    for hit in weapon.hit(options):
        if hit.bypass_next:
            possible_hits:list[EventSet] = []
            for _ in range(hit.value):
                possible_hits.append(saveRoll(weapon, target, options, True))
            results.append(ev.All(possible_hits, name='h-b'))
        elif hit.success:
            possible_hits:list[EventSet] = []
            for _ in range(hit.value):
                possible_hits.append( woundRoll(weapon, target, options, True))
            results.append(ev.All(possible_hits, name='h-s'))
        elif hit.reroll and reroll:
             results.append(hitRoll(weapon, target, options, False))
        else:
            results.append(ev.Leaf('h-f', ev.failure()))
    return ev.Together(results, name="hr")

def attackRoll(weapon:SimpleWeapon, target:SimpleModel, options:AttackOptions, reroll:bool) -> ev.EventSet:
    results:list[EventSet] = []
    for attack in weapon.attack(options):
        if attack.bypass_next:
            possible_attacks:list[EventSet] = []
            for _ in range(attack.value):
                possible_attacks.append(woundRoll(weapon, target, options, True))
            results.append(ev.All(possible_attacks, name='byp'))
        elif attack.success:
            possible_attacks:list[EventSet] = []
            for _ in range(attack.value):
                possible_attacks.append(hitRoll(weapon, target, options, True))
            results.append(ev.All(possible_attacks, name='suc'))
        elif attack.reroll and reroll:
             results.append(attackRoll(weapon, target, options, False))
        else:
            results.append(ev.Leaf('attack', ev.failure()))
    return ev.Together(results, name="ar")




if __name__ == "__main__":

    weapons = [
        # SimpleWeapon("Deathwatch Bolt Rifle", 24, 2, 3, 5,-2,1),
        # SimpleWeapon("Bolt Sniper Rifle", 36, 1, 3, 5,-2,3),
        # SimpleWeapon("Bolt Rifle", 24, 2, 3, 4,-1,1),
        # SimpleWeapon("Bolt Rifle TW", 24, 2, 3, 4,-1,1, [twin_linked]),
        # SimpleWeapon("Bolt Rifle sus 2", 24, 2, 3, 4,-1,1, [sustained_hits(2)]),
        # SimpleWeapon("Gauss flayer", 24, 1, 4, 4,0,1, [rapid_fire(1)]),
        # SimpleWeapon("Flamer 3 3", 12, 3, 3, 3,0,1, ),
        # SimpleWeapon("Flamer 3", 12, 3, 0, 3,0,1, [torrent]),
        # SimpleWeapon("Flamer D3", 12, dice(3), 0, 3,0,1, [torrent]),
        # SimpleWeapon("Flamer D3+1", 12, dice(3, 1), 0, 3,0,1, [torrent]),
        SimpleWeapon("Gauss flayer", 24, 1, 4, 4,0,1 ),
        # SimpleWeapon("Gauss flayer LH", 24, 1, 4, 4,0,1, [lethal_hits]),
        # SimpleWeapon("Gauss flayer DW", 24, 1, 4, 4,0,1, [ devestating_wounds]),
        # SimpleWeapon("Gauss flayer LH DW", 24, 1, 4, 4,0,1, [lethal_hits, devestating_wounds]),
        ]
    models = [
        SimpleModel("Warrior", 4, 4, 1, 0),
        SimpleModel("Warrior FNP 5", 4, 4, 1, 5),
        # SimpleModel("Intercessor", 4, 3, 2, 0),
        ]

    for model in models:
        for weapon in weapons:
            for rng in [24]:
                options = AttackOptions(rng, False)
                print(f'{weapon.name} at {model.name} at {rng}"')
                damage = attackRoll(weapon, model, options, True)

                results = sorted([ (key, prob) for key, prob in damage.outcomes().items() ],key=lambda x: x[1], reverse=True)

                for key, prob in results:
                    print(f'{prob*100:.3g}%: {repr(key)}')







