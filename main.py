from enum import unique
import os
from dataclasses import dataclass, field
import icecream
import string
import datetime as dt


from weapon import SimpleWeapon
from outcomes import Dice
from model import SimpleModel
from table import Table, Heading, Cell, CellValue, Index
import roll as rl
from actions import AttackOptions
import actions

icecream.install()


@dataclass
class DataLine:
    unit: str
    weapon_name: str
    rng: int
    attacks: int | Dice
    weapon_skill: int
    strength: int
    armour_penetration: int
    damage: int | Dice
    modifiers: list[str]

    @staticmethod
    def parse_line(line: str) -> "DataLine":
        parts = []
        for ii, p in enumerate(line.split(",")):
            if ii < 2:
                parts.append(string.capwords(p))
            else:
                strip_p = p.strip().lower()
                if ii < 8 or len(p) > 0:
                    parts.append(strip_p.lower())

        assert len(parts) >= 8

        if "d" in parts[3]:
            attacks = Dice.from_str(parts[3])
        else:
            attacks = int(parts[3])

        if "d" in parts[7]:
            damage = Dice.from_str(parts[7])
        else:
            damage = int(parts[7])

        try:
            return DataLine(
                unit=parts[0],
                weapon_name=parts[1],
                rng=int(parts[2]),
                attacks=attacks,
                weapon_skill=int(parts[4]),
                strength=int(parts[5]),
                armour_penetration=int(parts[6]),
                damage=damage,
                modifiers=parts[8:],
            )
        except:
            ic(line)
            ic(parts)
            raise

    def create_weapon(self, modifier_map: dict[str, actions.Modifier]) -> SimpleWeapon:
        modifiers = []
        for modifier_name in self.modifiers:
            modifiers.append(modifier_map[modifier_name])

        return SimpleWeapon(
            self.weapon_name,
            self.rng,
            self.attacks,
            self.weapon_skill,
            self.strength,
            self.armour_penetration,
            self.damage,
            tuple(modifiers),
        )

    def create_table(self, options: AttackOptions, weapon: SimpleWeapon) -> Table:
        table = Table()

        table.set_rows([Heading(f"T {ii}", ii) for ii in range(2, 15)])
        table.set_columns([Heading(f"Sv{ii}+", ii) for ii in range(7, 1, -1)])

        these_options = AttackOptions(options.half_range, options.cover, options.anti_active, weapon.modifiers)

        full_cell_list = table.get_full_cell_list()

        next = 5
        total = len(full_cell_list)
        unique_possibilities = 0
        all_possibilities = 0
        first = True

        for jj, cell in enumerate(full_cell_list):
            target = SimpleModel(
                f"{cell.row.name}, {cell.column.name}",
                cell.row.value,
                cell.column.value,
                1,
                0,
            )
            start = dt.datetime.now()
            damage, all_possibilities = rl.attack_roll(
                weapon.A, weapon.WS, weapon.S, target.T, target.S, weapon.AP, weapon.D, target.FNP, these_options, True
            )

            results = damage.outcomes().items()
            unique_possibilities = len(results)
            end = dt.datetime.now()

            if first:
                diff = end - start
                total_outcomes = all_possibilities[1] ** all_possibilities[0]
                print(
                    f"unique outcomes: {unique_possibilities:,}, all outcomes {all_possibilities}: {total_outcomes:,}"
                )
                print(f"time per {diff} each of {total}, extimated {diff * total}")
                print("[", end="", flush=True)
                first = False
            values = [0.0 for _ in range(table.damage_n)]
            for key, prob in results:
                damage = key.total()
                for ii in range(table.damage_n):
                    if damage >= (ii + 1):
                        values[ii] += prob
            new_cell = Cell(cell.row, cell.column, CellValue(True, [v * 100 for v in values]))

            table.set_cells([new_cell])

            if (100 * jj) / total > next:
                print("=", end="", flush=True)
                next += 5
        print("]")

        return table


@dataclass
class DataFile:
    filename: str
    lines: list[DataLine] = field(default_factory=list)

    def read(self) -> None:
        with open(self.filename, "r") as fle:
            for ii, line in enumerate(fle):
                if ii == 0:
                    continue
                stripped_line = line.strip()
                if len(stripped_line) == 0:
                    continue
                self.lines.append(DataLine.parse_line(stripped_line))


if __name__ == "__main__":
    modifier_funcs = [
        actions.torrent,
        actions.reroll_hit_1,
        actions.all_hits_critical,
        actions.rapid_fire(1),
        actions.rapid_fire(2),
        actions.rapid_fire(3),
        actions.rapid_fire(5),
        actions.rapid_fire(6),
        actions.critical_hits(4),
        actions.critical_hits(5),
        actions.sustained_hits(1),
        actions.sustained_hits(2),
        actions.sustained_hits(Dice(1, 3, 0)),
        actions.lethal_hits,
        actions.twin_linked,
        actions.melta(4),
        actions.precision,
        actions.blast,
        actions.pistol,
        actions.hazardous,
        actions.ignores_cover,
        actions.indirect_fire,
        actions.anti("character", 4),
        actions.anti("fly", 4),
        actions.anti("vehicle", 2),
        actions.devastating_wounds,
        actions.bypass_wound,
        actions.bypass_save,
        actions.mortal_wounds,
        actions.all_wounds_critical,
        actions.one_shot,
        actions.assult,
        actions.heavy,
    ]
    modifier_map = {func.name.lower().replace("_", " "): func for func in modifier_funcs}

    key_errors = []

    options = AttackOptions(False, False, False, tuple())
    input = "input"
    output = "docs"
    index = Index()
    for fle in os.listdir(input):
        if fle.endswith(".csv"):
            group_name = fle[0:-4]
            datafile = DataFile(os.path.join(input, fle))
            datafile.read()
            for line in datafile.lines:
                start = dt.datetime.now()
                weapon = line.create_weapon(modifier_map)
                print(f"Process {group_name} {line.unit} {line.weapon_name}")
                print(weapon.stat_line())
                print(weapon.keywords())
                try:
                    table = line.create_table(options, weapon)
                except KeyError as e:
                    key_errors.append(e)
                    continue
                except rl.ProbabilityTreeTooLargeError as e:
                    print(f"Skipping due to huge probability tree: {e}")
                    continue

                finally:
                    end = dt.datetime.now()
                    print(f" {end - start}")
                output_folder = os.path.join(group_name, line.unit)
                if not os.path.exists(os.path.join(output, output_folder)):
                    os.makedirs(os.path.join(output, output_folder))
                output_filename = os.path.join(output_folder, f"{line.weapon_name}.html")
                table.write(
                    os.path.join(output, output_filename),
                    weapon.name,
                    weapon.stat_line(),
                    weapon.keywords(),
                )
                index.add_file(group_name, line.unit, weapon.name, filename=output_filename)
    index.write(os.path.join(output, "index.html"))

    for e in key_errors:
        print(e)
