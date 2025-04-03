import os
import polars as pl

from table import Table, Heading, Cell, CellValue, Index

from icecream import ic


def to_nearest_in(value, edges):
    for v in edges:
        if v > value:
            return v
    return edges[-1]


if __name__ == "__main__":
    data_dir = "docs"
    output = "docs"

    index = Index()
    for root, _, files in os.walk(data_dir):
        for file in files:
            weapon_name, ext = os.path.splitext(file)
            if ext == ".csv":
                part, unit_name = os.path.split(root)
                _, group_name = os.path.split(part)

                ic(os.path.join(root, file))

                df = pl.read_csv(os.path.join(root, file))

                max_average_damage = max(df["damage_avg"]) * 1.1

                weapon_stats_line = ""
                weapon_keywords = ""
                with open(os.path.join(root, f"{weapon_name}.weapon.txt"), "r") as fle:
                    for ii, line in enumerate(fle):
                        match ii:
                            case 0:
                                weapon_stats_line = line.strip()
                            case 1:
                                weapon_keywords = line.strip()

                toughnesses = df["Toughness"].unique().sort()
                wounds = df["Wounds"].unique().sort()
                saves = df["Save"].unique().sort(descending=True)

                table = Table()
                table.level_max = max_average_damage
                table.set_rows([Heading(f"T {ii}", ii) for ii in toughnesses])
                table.set_columns([Heading(f"W {ii}", ii) for ii in wounds])
                table.set_inner_columns([Heading(f"Sv {ii}+", ii) for ii in saves])
                full_cell_list = table.get_full_cell_list()
                for cell in full_cell_list:
                    values = df.filter(
                        pl.col("Toughness") == cell.row.value, pl.col("Wounds") == cell.column.value
                    ).sort(by="Save", descending=True)
                    saves = values["Save"]
                    damage_avg = values["damage_avg"]
                    new_cell = Cell(cell.row, cell.column, CellValue(True, [v for v in damage_avg]))
                    table.set_cells([new_cell])

                output_folder = os.path.join(group_name, unit_name)
                if not os.path.exists(os.path.join(output, output_folder)):
                    os.makedirs(os.path.join(output, output_folder))
                output_filename = os.path.join(output_folder, f"{weapon_name}.html")
                table.write(
                    os.path.join(output, output_filename),
                    weapon_name,
                    weapon_stats_line,
                    weapon_keywords,
                )
                index.add_file(group_name, unit_name, weapon_name, filename=output_filename)
    index.write(os.path.join(output, "index.html"))
