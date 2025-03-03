import os
from collections import defaultdict
from dataclasses import dataclass
from icecream import ic

from weapon import SimpleWeapon, AttackOptions
from weapon import (
    torrent,
    sustained_hits,
    rapid_fire,
    lethal_hits,
    devestating_wounds,
    melta,
    anti,
    twin_linked,
    dice,
)
from model import SimpleModel
from table import Table, Heading, Cell, CellValue, Index

from events import EventSet, EventSuccess
import events as ev


def feelNoPainRoll(
    weapon: SimpleWeapon, target: SimpleModel, options: AttackOptions, reroll: bool
) -> ev.Together:
    # Like the save throw, a successful FNP means a failure to damage. i.e. negation
    results: list[EventSet] = [
        ev.Leaf("dmg", suc)
        for suc in [
            ev.failure() if fnp.success else ev.success()
            for fnp in target.feel_no_pain()
        ]
    ]
    return ev.Together(results, name="fnp")


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

        all = ev.All(possible_damage)

        res = []
        for key, prob in all.outcomes().items():
            success = EventSuccess(sum(k.value for k in key.outcomes), spill=spill)
            res.append(ev.Leaf("a", success, probability=prob))
        results.append(ev.Together(res))

        # results.append(ev.All(possible_damage, name="d"))

    return ev.Together(results, name="dr")


def saveRoll(
    weapon: SimpleWeapon, target: SimpleModel, options: AttackOptions, reroll: bool
) -> ev.Together:
    results: list[EventSet] = []
    for save in target.save(weapon.AP):
        if save.success:
            results.append(ev.Leaf("s-f", ev.failure()))
        elif save.reroll and reroll:
            results.append(saveRoll(weapon, target, options, False))
        else:
            results.append(damageRoll(weapon, target, options, True, False))
    return ev.Together(results, name="sr")


def woundRoll(
    weapon: SimpleWeapon, target: SimpleModel, options: AttackOptions, reroll: bool
) -> ev.Together:
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
    return ev.Together(results, name="wr")


def hitRoll(
    weapon: SimpleWeapon, target: SimpleModel, options: AttackOptions, reroll: bool
) -> ev.Together:
    results: list[EventSet] = []
    for hit in weapon.hit(options):
        if hit.bypass_next:
            possible_hits: list[EventSet] = []
            for _ in range(hit.value):
                possible_hits.append(saveRoll(weapon, target, options, True))
            results.append(ev.All(possible_hits, name="h-b"))
        elif hit.success:
            possible_hits: list[EventSet] = []
            for _ in range(hit.value):
                possible_hits.append(woundRoll(weapon, target, options, True))
            results.append(ev.All(possible_hits, name="h-s"))
        elif hit.reroll and reroll:
            results.append(hitRoll(weapon, target, options, False))
        else:
            results.append(ev.Leaf("h-f", ev.failure()))
    return ev.Together(results, name="hr")


def attackRoll(
    weapon: SimpleWeapon, target: SimpleModel, options: AttackOptions, reroll: bool
) -> ev.EventSet:
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
    return ev.Together(results, name="ar")


if __name__ == "__main__":
    weapons = [
        SimpleWeapon(
            "Necron Combat Patrol", "Tachyon arrow", 72, 1, 2, 16, -5, dice(6, 2)
        ),
        SimpleWeapon(
            "Necron Combat Patrol",
            "Overlord's blade",
            1,
            4,
            2,
            8,
            -3,
            2,
            [devestating_wounds],
        ),
        SimpleWeapon(
            "Necron Combat Patrol", "Gauss flayer", 24, 1, 4, 4, 0, 1, [lethal_hits]
        ),
        SimpleWeapon(
            "Necron Combat Patrol", "Gauss reaper", 12, 2, 4, 5, -1, 1, [lethal_hits]
        ),
        SimpleWeapon("Necron Combat Patrol", "Warrior CCW", 1, 1, 4, 4, 0, 1),
        SimpleWeapon(
            "Necron Combat Patrol", "Skorpekh hyperphase weapons", 1, 4, 3, 7, -2, 2
        ),
        SimpleWeapon("Necron Combat Patrol", "Feeder mandibles", 1, 6, 5, 2, 0, 1),
        SimpleWeapon(
            "Necron Combat Patrol", "Doomsday blaster", 48, dice(6, 1), 4, 14, -3, 3
        ),
        SimpleWeapon(
            "Necron Combat Patrol",
            "Twin gauss flayer",
            24,
            1,
            4,
            4,
            0,
            1,
            [lethal_hits, twin_linked],
        ),
        SimpleWeapon("Necron Combat Patrol", "Doom stalker limbs", 1, 3, 4, 6, 0, 1),
        SimpleWeapon(
            "Deathwatch Combat Patrol", "Lietenant Bolt pistol", 12, 1, 2, 4, 0, 1
        ),
        SimpleWeapon(
            "Deathwatch Combat Patrol", "Master crafted power weapon", 1, 5, 2, 5, -2, 2
        ),
        SimpleWeapon(
            "Deathwatch Combat Patrol", "Absolvor bolt pistol", 18, 1, 3, 5, -1, 2
        ),
        SimpleWeapon("Deathwatch Combat Patrol", "Reductor pistol", 3, 1, 3, 4, -4, 2),
        SimpleWeapon("Deathwatch Combat Patrol", "Appotheecary CCW", 1, 4, 3, 4, 0, 1),
        SimpleWeapon(
            "Deathwatch Combat Patrol",
            "Astartes grenade launcher - frag",
            24,
            dice(3),
            3,
            4,
            0,
            1,
        ),
        SimpleWeapon(
            "Deathwatch Combat Patrol",
            "Astartes grenade launcher - krak",
            24,
            1,
            3,
            9,
            -2,
            dice(3),
        ),
        SimpleWeapon("Deathwatch Combat Patrol", "Bolt pistol", 12, 1, 3, 4, 0, 1),
        SimpleWeapon("Deathwatch Combat Patrol", "Bolt rifle", 24, 2, 3, 4, -1, 1),
        SimpleWeapon("Deathwatch Combat Patrol", "Intercessor CCW", 1, 3, 3, 4, 0, 1),
        SimpleWeapon(
            "Deathwatch Combat Patrol",
            "Flamestorm gauntlets",
            12,
            dice(6, 1),
            0,
            4,
            0,
            1,
            [torrent, twin_linked],
        ),
        SimpleWeapon(
            "Deathwatch Combat Patrol",
            "Twin power fists",
            1,
            3,
            4,
            8,
            -2,
            2,
            [twin_linked],
        ),
        SimpleWeapon("Necron", "Gauss blaster", 24, 2, 3, 5, -1, 1, [lethal_hits]),
        SimpleWeapon("Necron", "Tesla carbine", 24, 2, 3, 5, 0, 1, [sustained_hits(2)]),
    ]

    options = AttackOptions(12, False)
    index = Index()
    for weapon in weapons:
        table = Table()
        t_suffix = {4: "W,S", 6: "D,A"}
        s_suffix = {4: "W", 3: "D,S,A"}
        table.setRows(
            [
                Heading(f"T {ii} {t_suffix[ii] if ii in t_suffix else ''}", ii)
                for ii in range(2, 15)
            ]
        )
        table.setColumns(
            [
                Heading(f"Sv{ii}+ {s_suffix[ii] if ii in s_suffix else ''}", ii)
                for ii in range(7, 1, -1)
            ]
        )
        print(weapon.name)

        for cell in table.getFullCellList():
            model = SimpleModel(
                f"{cell.row.name}, {cell.column.name}",
                cell.row.value,
                cell.column.value,
                1,
                0,
            )
            damage = attackRoll(weapon, model, options, True)

            results = damage.outcomes().items()
            values = [0.0 for _ in range(table.damage_n)]
            for key, prob in results:
                damage = sum(k.value for k in key.outcomes)
                for ii in range(table.damage_n):
                    if damage >= (ii + 1):
                        values[ii] += prob
            new_cell = Cell(
                cell.row, cell.column, CellValue(True, [v * 100 for v in values])
            )

            table.setCells([new_cell])
        if not os.path.exists(os.path.join("docs", weapon.folder)):
            os.mkdir(os.path.join("docs", weapon.folder))

        filename = os.path.join(weapon.folder, f"{weapon.name}.html")
        table.write(
            os.path.join("docs", filename),
            weapon.name,
            weapon.statLine(),
            weapon.keywords(),
        )
        index.addFile(weapon.folder, weapon.name, filename=filename)
    index.write(os.path.join("docs", "index.html"))
