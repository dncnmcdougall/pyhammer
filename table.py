from dataclasses import dataclass, field
from icecream import ic

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
        self.rows = []

        self.level_n = 4
        self.damage_n = 5

    def setColumns( self, columns: list[Heading] ) -> None:
        self.columns = columns

    def setRows( self, rows: list[Heading] ) -> None:
        self.rows = rows

    def getFullCellList(self) -> list[Cell]:
        results = []
        for row in self.rows:
            for col in self.columns:
                if row in self.cells and col in self.cells[row]:
                    results.append(self.cells[row][col])
                else:
                    results.append(Cell(row, col, CellValue(is_set=False)))
        return results

    def setCells(self, cells: list[Cell]) -> None:
        for cell in cells:
            if not cell.value.is_set:
                continue
            if cell.row not in self.cells:
                self.cells[cell.row] = {}
            self.cells[cell.row][cell.column] = cell

    def _cellItem(self, value: float, cls:str) -> str:
        cls_suffix = ''
        step = 100/self.level_n
        for ii in range(self.level_n):
            if value < (ii+1)*step:
                cls_suffix = str(ii+1)
                break
        return f'<td class="{cls} {cls}_{cls_suffix}"> {value:.0f} </td>\n'


    def write(self, filename, *headings:str):

        with open(filename,'w') as fle:
            fle.write('''
            <html>
            <head>
            <meta http-equiv="content-type" content="text/html; charset=UTF-8">
            <style>
            ''')
            fle.write('\n')

            hues = [135, 200, 320, 30, 0]
            step = 60/(self.level_n-1)
            for ii in range(self.damage_n):
                fle.write(f'.val{ii+1} {{\n')
                if ii > 0:
                    fle.write('display: none;\n')
                fle.write('}\n')
                fle.write('\n')

                for jj in range(self.level_n):
                    fle.write(f'.val{ii+1}_{jj+1} {{\n')
                    fle.write(f'background: hsl({hues[ii]}, 100%, {100-(jj)*step}%);\n')
                    fle.write('}\n')
                    fle.write('\n')
            fle.write('</style>\n')
            fle.write('</head>\n')
            fle.write('<body>\n')

            # Heading and controls table
            fle.write('<table>\n')
            cnt = max(len(headings), self.damage_n)
            for ii in range(cnt):
                fle.write('<tr>\n')
                if ii < len(headings):
                    fle.write(f'<th>{headings[ii]}</th>\n')
                else:
                    fle.write('<th></th>\n')
                if ii < self.damage_n:
                    fle.write(f'<td>Show {ii+1}+ damage<input type="checkbox" id="val{ii+1}" {"checked" if ii == 0 else ""} oninput="changeFunc(event)"/></td>\n')
                else:
                    fle.write('<td></td>\n')
                fle.write('</tr>\n')
            fle.write('</table>\n')

            # Heading Table
            fle.write('<table>\n')
            fle.write('<tr>\n')
            fle.write('<th></th>\n')
            for column in self.columns:
                fle.write(f'<th class="main_heading" colspan=1>{column.name}</th>\n')
            fle.write('</tr>\n')
            fle.write('<th></th>\n')
            for column in self.columns:
                for ii in range(self.damage_n):
                    fle.write(f'<th class="val{ii+1}">{ii+1}+</th>\n')
            fle.write('</tr>\n')
            for row in self.rows:
                fle.write('<tr>\n')
                fle.write(f'<td>{row.name}</td>\n')
                for cell in self.cells[row].values():
                    if not cell.value.is_set:
                        for ii in range(self.damage_n):
                            fle.write(f'<td class="val{ii+1}">-</td>\n')
                    else:
                        for ii in range(self.damage_n):
                            fle.write(self._cellItem(cell.value.values[ii], f'val{ii+1}'))
                fle.write('</tr>\n')
            fle.write('</table>\n')

            # Show script
            fle.write('''
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

                let cols = ''')
            for ii in range(self.damage_n):
                fle.write(f'+ document.getElementById("val{ii+1}").checked\n')

            fle.write('''
                let elements = document.querySelectorAll('.main_heading');
                for( let ii=0; ii < elements.length; ii++) {
                    elements[ii].setAttribute('colspan',cols);
                }
            }
            </script>
                      ''')

            fle.write('</body>\n')



class Index:

    def __init__(self):
        self.items = {}

    def addFile(self, name, filename):
        self.items[name] = filename

    def write(self, filename):
        with open(filename,'w') as fle:
            fle.write('''
            <html>
            <head>
            <meta http-equiv="content-type" content="text/html; charset=UTF-8">
            <body>
            ''')
            fle.write('<ul>\n')
            for name, filename in self.items.items():
                fle.write(f'<li><a href="{filename}">{name}</a></li>\n')
            fle.write('</ul>\n')
            fle.write('</body>\n')



