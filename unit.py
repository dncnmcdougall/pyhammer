from collections import defaultdict
import math
from dataclasses import dataclass
from icecream import ic

from rules import SimpleModel, SimpleWeapon

from outcomes import Outcome, OutcomeSequence, OutcomeTree
import outcomes as oc



def to_trees(outcomes: list[Outcome]) -> list[OutcomeTree]:
    return [ OutcomeTree(count=c, outcome=o, children=[]) for o, c  in oc.collect(outcomes).items() ]

def damageTree(weapon:SimpleWeapon, target:SimpleModel) -> list[OutcomeTree]:
    # TODO feel no pain
    results = []
    for damage in weapon.damage():
        if damage.bypass_next:
            results.append(OutcomeTree(1, damage, []))
        if damage.success:
            # TODO: damage modifiers
            # results.append(OutcomeTree(1, Outcome(target.damage_modifier(damage.value), True, False), []))
            results.append(OutcomeTree(1, damage, []))
        else:
            results.append(OutcomeTree(1, Outcome(0, False, False), []))
    return results

def saveTree(weapon:SimpleWeapon, target:SimpleModel) -> list[OutcomeTree]:
    results = []
    for save in target.save(weapon.AP):
        if save.success:
            results.append(OutcomeTree(1, Outcome(0, False, False), []))
        else:
            results.append(OutcomeTree(1, Outcome(1, True, False), damageTree(weapon, target)))
    return results

def woundTree(weapon:SimpleWeapon, target:SimpleModel) -> list[OutcomeTree]:
    results = []
    for wound in weapon.wound(target.T):
        if wound.bypass_next:
            results.append(OutcomeTree(1, Outcome(1, True, True), damageTree(weapon, target)))
        elif wound.success:
            results.append(OutcomeTree(1, Outcome(1, True, False), saveTree(weapon, target)))
        else:
            results.append(OutcomeTree(1, Outcome(0, False, False), []))
    return results

def hitTree(weapon:SimpleWeapon, target:SimpleModel) -> list[OutcomeTree]:
    results = []
    for hit in weapon.hit():
        if hit.bypass_next:
            results.append(OutcomeTree(hit.value, Outcome(1, True, True), saveTree(weapon, target)))
        elif hit.success:
            results.append(OutcomeTree(hit.value, Outcome(1, True, False), woundTree(weapon, target)))
        else:
            results.append(OutcomeTree(1, Outcome(0, False, False), []))
    return results

def computeDamage(weapon:SimpleWeapon, target:SimpleModel, rng) -> dict[OutcomeSequence, float]:
    # Not yet correct: A tree represents a sequence of modifiers.
    # Attackes do not modify each other, rather they combine combinatorally
    attack_trees = []
    for attack in weapon.attack(rng):
        if attack.bypass_next:
            for _ in range(attack.value):
                attack_trees.append(OutcomeTree(1, Outcome(1, True, True), woundTree(weapon, target)))
        elif attack.success:
            for _ in range(attack.value):
                attack_trees.append(OutcomeTree(1, Outcome(1, True, False), hitTree(weapon, target)))
        else:
            attack_trees.append(OutcomeTree(1, Outcome(1, False, False), []))

    final_outcomes: dict[OutcomeSequence, float] = {}
    for ii,tree in enumerate(attack_trees):
        summaries = defaultdict(lambda: 0)
        for key, value in tree.to_sequences().items():
            summaries[key.outcomes[-1]] += value

        if len(final_outcomes) == 0 :
            final_outcomes = { OutcomeSequence([out]):value for out, value in summaries.items() }
        else:
            new_final_outcomes = {}
            for f_seq, f_value in final_outcomes.items():
                for out, value in summaries.items():
                    key = OutcomeSequence.append(f_seq, out)
                    new_final_outcomes[key] = f_value*value
            final_outcomes = new_final_outcomes

    assert abs(sum(final_outcomes.values()) -1) <1e-5

    return final_outcomes


if __name__ == "__main__":

    # tree = OutcomeTree(1, Outcome(1, True, True), [
    #                     OutcomeTree(2, Outcome(1, True, True), [
    #                         OutcomeTree(2, Outcome(1, True, True), []),
    #                         OutcomeTree(3, Outcome(1, False, False), []),
    #                         ]),
    #                     OutcomeTree(1, Outcome(1, False, False), []),
    #                     OutcomeTree(1, Outcome(1, False, False), []),
    #                     ])
    # ic(tree)
    # ic(tree.to_sequences())
    # exit()


    weapons = [
        SimpleWeapon("Deathwatch Bolt Rifle", 2, 3, 4,-1,1),
        SimpleWeapon("Bolt Rifle2 ", 2, 3, 4,0,1),
        SimpleWeapon("Gauss flayer", 1, 4, 4,0,1),
        ]
    models = [
        SimpleModel("Warrior", 4, 4, 1),
        SimpleModel("Intercessor", 4, 3, 2),
        ]

    for weapon in weapons:
        for model in models:
            print(f'{weapon.name} at {model.name}')
            damage = computeDamage(weapon, model, 12)

            sorted_sequences = { tuple(sorted(list(d.outcomes))): v for d,v in damage.items() }
            summary = defaultdict(lambda:0)
            for k,v in sorted_sequences.items():
                summary[k] += v
            for k, v in summary.items():
                print(f'{v*100:.2g}%: {k}')









