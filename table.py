from typing import Any
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Heading:
    name: str
    value: int


@dataclass
class CellValue:
    is_set: bool = False

    values: list[float] = field(default_factory=list)


@dataclass
class Cell:
    row: Heading
    column: Heading

    value: CellValue


class Table:
    def __init__(self):
        self.cells: dict[Heading, dict[Heading, Cell]] = {}

        self.columns = []
        self.inner_columns = []
        self.rows = []

        self.level_n = 4
        self.level_max = 100

    def set_columns(self, columns: list[Heading]) -> None:
        self.columns = columns

    def set_inner_columns(self, inner_columns: list[Heading]) -> None:
        self.inner_columns = inner_columns

    def set_rows(self, rows: list[Heading]) -> None:
        self.rows = rows

    def get_full_cell_list(self) -> list[Cell]:
        results = []
        for row in self.rows:
            for col in self.columns:
                if row in self.cells and col in self.cells[row]:
                    results.append(self.cells[row][col])
                else:
                    results.append(Cell(row, col, CellValue(is_set=False)))
        return results

    def set_cells(self, cells: list[Cell]) -> None:
        for cell in cells:
            if not cell.value.is_set:
                continue
            if cell.row not in self.cells:
                self.cells[cell.row] = {}
            self.cells[cell.row][cell.column] = cell

    def _cell_item(self, value: float, cls: str) -> str:
        cls_suffix = ""
        step = self.level_max / self.level_n
        for ii in range(self.level_n):
            if value <= (ii + 1) * step:
                cls_suffix = str(ii + 1)
                break
        return f'<td class="{cls} {cls}_{cls_suffix}"> {value:.1f} </td>\n'

    def write(self, filename, *headings: str):
        with open(filename, "w") as fle:
            fle.write("""
            <html>
            <head>
            <meta http-equiv="content-type" content="text/html; charset=UTF-8">
            <style>
            """)
            fle.write("\n")

            hue_diff = int(360 / len(self.inner_columns))
            step = 60 / (self.level_n - 1)
            for ii, _ in enumerate(self.inner_columns):
                fle.write(f".val{ii + 1} {{\n")
                if ii > 0:
                    fle.write("display: none;\n")
                else:
                    fle.write("display: table-cell;\n")
                fle.write("}\n")
                fle.write("\n")

                for jj in range(self.level_n):
                    fle.write(f".val{ii + 1}_{jj + 1} {{\n")
                    fle.write(f"background: hsl({hue_diff * ii}, 100%, {100 - (jj) * step}%);\n")
                    fle.write("}\n")
                    fle.write("\n")
            fle.write("</style>\n")
            fle.write("</head>\n")
            fle.write("<body>\n")

            # Heading and controls table
            fle.write("<table>\n")
            cnt = max(len(headings), len(self.inner_columns))
            for ii in range(cnt):
                fle.write("<tr>\n")
                if ii < len(headings):
                    fle.write(f"<th>{headings[ii]}</th>\n")
                else:
                    fle.write("<th></th>\n")
                if ii < len(self.inner_columns):
                    state = "checked" if ii == 0 else ""
                    num = ii + 1
                    value = self.inner_columns[ii].name
                    fle.write(f'<td>Show {value}<input type="checkbox" id="val{num}"')
                    fle.write(f'{state} oninput="changeFunc(event)"/></td>\n')
                else:
                    fle.write("<td></td>\n")
                fle.write("</tr>\n")
            fle.write("</table>\n")

            # Heading Table
            fle.write("<table>\n")
            fle.write("<tr>\n")
            fle.write("<th></th>\n")
            for column in self.columns:
                fle.write(f'<th class="main_heading" colspan=1>{column.name}</th>\n')
            fle.write("</tr>\n")
            fle.write("<th></th>\n")
            for _ in self.columns:
                for ii, inner_column in enumerate(self.inner_columns):
                    fle.write(f'<th class="val{ii + 1}">{inner_column.name}</th>\n')
            fle.write("</tr>\n")
            for row in self.rows:
                fle.write("<tr>\n")
                fle.write(f"<td>{row.name}</td>\n")
                for cell in self.cells[row].values():
                    if not cell.value.is_set:
                        for ii, _ in enumerate(self.inner_columns):
                            fle.write(f'<td class="val{ii + 1}">-</td>\n')
                    else:
                        cell_value_count = len(cell.value.values)
                        for ii, _ in enumerate(self.inner_columns):
                            if ii < cell_value_count:
                                fle.write(self._cell_item(cell.value.values[ii], f"val{ii + 1}"))
                            else:
                                fle.write(f'<td class="val{ii + 1}">-</td>\n')
                fle.write("</tr>\n")
            fle.write("</table>\n")

            # Show script
            fle.write("""
            <script>
            function changeFunc(event) {

                for( let ii =0; ii < document.styleSheets.length; ii++){
                    let sheet = document.styleSheets[ii]
                    for( let jj = 0; jj <  sheet.cssRules.length; jj++) {
                        let rule = sheet.cssRules[jj]
                        if (rule.selectorText == '.'+event.srcElement.id) {
                            rule.style.setProperty('display', event.srcElement.checked ? 'table-cell' : 'none');
                            console.log(rule);
                        }
                    }
                }

                let cols = """)
            for ii, _ in enumerate(self.inner_columns):
                fle.write(f'+ document.getElementById("val{ii + 1}").checked\n')

            fle.write("""
                let elements = document.querySelectorAll('.main_heading');
                for( let ii=0; ii < elements.length; ii++) {
                    elements[ii].setAttribute('colspan',cols);
                }
            }
            </script>
                      """)

            fle.write("</body>\n")


class Index:
    def __init__(self):
        self.items = {}

    def add_file(self, *name_parts, filename):
        d = self.items
        total = len(name_parts)
        assert total > 0
        for ii, name in enumerate(name_parts):
            if ii == total - 1:
                d[name] = filename
            elif name not in d:
                d[name] = {}
            d = d[name]

    def write_list(self, fle, name: str, name_depth: int, values: dict[str, Any]) -> None:
        fle.write("<section>\n")
        fle.write(f"<h{name_depth}>{name}</h{name_depth}>\n")
        fle.write("<ul>\n")
        for key, value in values.items():
            if isinstance(value, dict):
                self.write_list(fle, key, name_depth + 1, value)
            else:
                fle.write(f'<li><a href="{value}">{key}</a></li>\n')
        fle.write("</ul>\n")
        fle.write("</section>\n")

    def write(self, filename):
        with open(filename, "w") as fle:
            fle.write("""
            <html>
            <head>
            <meta http-equiv="content-type" content="text/html; charset=UTF-8">
            <body>
            """)
            self.write_list(fle, "All", 1, self.items)
            fle.write("</body>\n")
