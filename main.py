import os
from dataclasses import dataclass, field


from weapon import SimpleWeapon, AttackOptions, RollFunc
from weapon import (
    torrent,
    sustained_hits,
    lethal_hits,
    devastating_wounds,
    twin_linked,
    critical_hits,
    rapid_fire,
    precision,
    blast,
)
from outcomes import Dice
from model import SimpleModel
from table import Table, Heading, Cell, CellValue, Index
import roll as rl


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
        parts = [p.strip().lower() for p in line.split(",")]
        parts = [p for p in parts if len(p) > 0]
        assert len(parts) >= 8

        if "d" in parts[3]:
            attacks = Dice.from_str(parts[3])
        else:
            attacks = int(parts[3])

        if "d" in parts[7]:
            damage = Dice.from_str(parts[7])
        else:
            damage = int(parts[7])

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

    def create_weapon(self, modifier_map: dict[str, RollFunc]) -> SimpleWeapon:
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
            modifiers,
        )

    def create_weapon_and_table(
        self, options: AttackOptions, modifier_map: dict[str, RollFunc]
    ) -> tuple[SimpleWeapon, Table]:
        table = Table()

        table.set_rows([Heading(f"T {ii}", ii) for ii in range(2, 15)])
        table.set_columns([Heading(f"Sv{ii}+", ii) for ii in range(7, 1, -1)])

        weapon = self.create_weapon(modifier_map)

        for cell in table.get_full_cell_list():
            model = SimpleModel(
                f"{cell.row.name}, {cell.column.name}",
                cell.row.value,
                cell.column.value,
                1,
                0,
            )
            damage = rl.attackRoll(weapon, model, options, True)

            results = damage.outcomes().items()
            values = [0.0 for _ in range(table.damage_n)]
            for key, prob in results:
                damage = sum(k.value for k in key.outcomes)
                for ii in range(table.damage_n):
                    if damage >= (ii + 1):
                        values[ii] += prob
            new_cell = Cell(cell.row, cell.column, CellValue(True, [v * 100 for v in values]))

            table.set_cells([new_cell])

        return weapon, table


@dataclass
class DataFile:
    filename: str
    lines: list[DataLine] = field(default_factory=list)

    def read(self) -> None:
        with open(self.filename, "r") as fle:
            for ii, line in enumerate(fle):
                if ii == 0:
                    continue
                self.lines.append(DataLine.parse_line(line))


if __name__ == "__main__":
    modifier_funcs = [
        torrent,
        sustained_hits(1),
        sustained_hits(2),
        rapid_fire(1),
        rapid_fire(2),
        rapid_fire(3),
        lethal_hits,
        devastating_wounds,
        twin_linked,
        critical_hits(4),
        critical_hits(5),
        precision,
        blast,
    ]
    modifier_map = {func.__name__.lower().replace("_", " "): func for func in modifier_funcs}

    options = AttackOptions(12, False)
    input = "input"
    output = "docs"
    index = Index()
    for fle in os.listdir(input):
        if fle.endswith(".csv"):
            group_name = fle[0:-4]
            datafile = DataFile(os.path.join(input, fle))
            datafile.read()
            for line in datafile.lines:
                print(f"Process {group_name} {line.unit} {line.weapon_name}")
                weapon, table = line.create_weapon_and_table(options, modifier_map)
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
