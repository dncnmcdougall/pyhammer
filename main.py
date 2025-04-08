from enum import unique
import os
from dataclasses import dataclass, field
import icecream
import string
import datetime as dt
import polars as pl

from weapon import SimpleWeapon
from outcomes import Dice
from model import SimpleModel
import roll as rl
from actions import AttackOptions
import actions
from events import cap_damage, average_damage, cumulative_damage_probabilities

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

    def compute_data(self, options: AttackOptions, weapon: SimpleWeapon) -> pl.DataFrame:
        saves = [ii for ii in range(7, 1, -1)]
        toughnesses = [ii for ii in range(2, 15)]
        wounds = [ii for ii in range(1, 15)]

        these_options = AttackOptions(options.half_range, options.cover, options.anti_active, weapon.modifiers)

        nxt = 5
        total = len(saves) * len(toughnesses)
        unique_possibilities = 0
        all_possibilities = 0

        damage_n = 9
        rows = {
            "Toughness": [],
            "Save": [],
            "Wounds": [],
        }
        rows["damage_avg"] = []
        for ii in range(damage_n):
            rows[f"damage_{ii + 1}+"] = []

        for ii, sv in enumerate(saves):
            for jj, tough in enumerate(toughnesses):
                number = ii * len(saves) + jj
                target = SimpleModel(
                    name=f"{sv}, {tough}",
                    T=tough,
                    S=sv,
                    W=1,
                    FNP=0,
                )
                start = dt.datetime.now()
                damage, all_possibilities = rl.attack_roll(
                    weapon.A,
                    weapon.WS,
                    weapon.S,
                    target.T,
                    target.S,
                    weapon.AP,
                    weapon.D,
                    target.FNP,
                    these_options,
                    True,
                )

                outcomes = damage.outcomes()
                unique_possibilities = len(outcomes)

                end = dt.datetime.now()

                if number == 0:
                    diff = end - start
                    total_outcomes = all_possibilities[1] ** all_possibilities[0]
                    print(
                        f"unique outcomes: {unique_possibilities:,}, "
                        + f"all outcomes {all_possibilities}: {total_outcomes:,}"
                    )
                    print(f"time per {diff} each of {total}, extimated {diff * total}")
                    print("[", end="", flush=True)

                for cap in wounds:
                    rows["Toughness"].append(tough)
                    rows["Save"].append(sv)
                    rows["Wounds"].append(cap)
                    capped_outcomes = cap_damage(outcomes, cap)
                    cumulative_damage_prob = cumulative_damage_probabilities(capped_outcomes, damage_n)
                    for ii, p in enumerate(cumulative_damage_prob):
                        rows[f"damage_{ii + 1}+"].append(p)

                    rows["damage_avg"].append(average_damage(capped_outcomes))

                if (100 * number) / total > nxt:
                    print("=", end="", flush=True)
                    nxt += 5
        print("]")

        return pl.DataFrame(rows)


@dataclass
class DataFile:
    filename: str
    lines: list[DataLine] = field(default_factory=list)

    def read(self) -> None:
        with open(self.filename, "r") as fle:
            ii = 0
            try:
                for ii, line in enumerate(fle):
                    if ii == 0:
                        continue
                    stripped_line = line.strip()
                    if len(stripped_line) == 0:
                        continue
                    self.lines.append(DataLine.parse_line(stripped_line))
            except Exception:
                print(f"Error in {self.filename}:{ii}")
                raise


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
        actions.rapid_fire(Dice(1, 3)),
        actions.critical_hits(4),
        actions.critical_hits(5),
        actions.sustained_hits(1),
        actions.sustained_hits(2),
        actions.sustained_hits(Dice(1, 3, 0)),
        actions.lethal_hits,
        actions.twin_linked,
        actions.melta(2),
        actions.melta(4),
        actions.precision,
        actions.blast,
        actions.pistol,
        actions.hazardous,
        actions.ignores_cover,
        actions.indirect_fire,
        actions.anti("character", 4),
        actions.anti("fly", 4),
        actions.anti("fly", 2),
        actions.anti("vehicle", 2),
        actions.anti("infantry", 4),
        actions.devastating_wounds,
        actions.bypass_wound,
        actions.bypass_save,
        actions.mortal_wounds,
        actions.all_wounds_critical,
        actions.one_shot,
        actions.assult,
        actions.heavy,
        actions.lance,
        actions.psychic,
    ]
    modifier_map = {func.name.lower().replace("_", " "): func for func in modifier_funcs}

    key_errors = []

    options = AttackOptions(False, False, False, tuple())
    input = "input"
    output = "docs"
    for fle in os.listdir(input):
        if fle.endswith(".csv"):
            group_name = fle[0:-4]
            datafile = DataFile(os.path.join(input, fle))
            datafile.read()
            for line in datafile.lines:
                weapon = line.create_weapon(modifier_map)
                print(f"Process {group_name} {line.unit} {line.weapon_name}")
                print(weapon.stat_line())
                print(weapon.keywords())

                output_folder = os.path.join(group_name, line.unit)
                if not os.path.exists(os.path.join(output, output_folder)):
                    os.makedirs(os.path.join(output, output_folder))
                output_filename = os.path.join(output_folder, line.weapon_name)

                if os.path.exists(os.path.join(output, f"{output_filename}.csv")):
                    df = pl.read_csv(
                        os.path.join(output, f"{output_filename}.csv"),
                    )
                    print("Not reprocessing")
                else:
                    start = dt.datetime.now()
                    try:
                        df = line.compute_data(options, weapon)
                        df.write_csv(
                            os.path.join(output, f"{output_filename}.csv"),
                            float_precision=4,
                        )
                        pass
                    except KeyError as e:
                        key_errors.append(e)
                        continue
                    except rl.ProbabilityTreeTooLargeError as e:
                        print(f"Skipping due to huge probability tree: {e}")
                        continue
                    finally:
                        end = dt.datetime.now()
                        print(f" {end - start}")

                with open(os.path.join(output, f"{output_filename}.weapon.txt"), "w") as fle:
                    fle.write(weapon.stat_line() + "\n")
                    fle.write(weapon.keywords() + "\n")

    for e in key_errors:
        print(e)
