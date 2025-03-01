from dataclasses import dataclass

@dataclass(frozen=True)
class Heading:
    name: str
    value: int


@dataclass
class CellValue:
    is_set: bool = False

    value_1: float = -1
    value_2: float = -1
    value_3: float = -1


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

        self.n = 4
        self.step = 100/self.n

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
        for ii in range(self.n):
            if value < (ii+1)*self.step:
                cls_suffix = str(ii+1)
                break
        return f'<td class="{cls} {cls}_{cls_suffix}"> {value:.2g} </td>\n'


    def write(self, filename, name, sub_name, sub_name_2):

        with open(filename,'w') as fle:
            fle.write('<html>\n')
            fle.write('<head>\n')
            fle.write('<meta http-equiv="content-type" content="text/html; charset=UTF-8">\n')
            fle.write('<style>\n')

            hues = [135, 200, 0]
            step = 60/(self.n-1)
            for ii in range(3):
                fle.write(f'.val{ii+1} {{\n')
                if ii > 0:
                    fle.write('display: none;\n')
                fle.write('}\n')
                fle.write('\n')

                for jj in range(self.n):
                    fle.write(f'.val{ii+1}_{jj+1} {{\n')
                    fle.write(f'background: hsl({hues[ii]}, 100%, {100-(jj)*step}%);\n')
                    fle.write('}\n')
                    fle.write('\n')
            fle.write('</style>\n')
            fle.write('</head>\n')
            fle.write('<body>\n')

            # Heading and controls table
            fle.write(f'''<table>
            <tr>
                    <th>{name}</th>
                    <td>Show 1+ damage<input type="checkbox" id="val1" checked oninput='changeFunc(event)'/></td>
                </tr>
                <tr>
                    <td>{sub_name}</td>
                    <td>Show 2+ damage<input type="checkbox" id="val2" oninput='changeFunc(event)'/></td>
                </tr>
                <tr>
                    <td>{sub_name_2}</td>
                    <td>Show 3+ damage<input type="checkbox" id="val3" oninput='changeFunc(event)'/></td>
                </tr>
            </table>
            ''')

            # Heading Table
            fle.write('<table>\n')
            fle.write('<tr>\n')
            fle.write('<th></th>\n')
            for column in self.columns:
                fle.write(f'<th class="main_heading" colspan=1>{column.name}</th>\n')
            fle.write('</tr>\n')
            fle.write('<th></th>\n')
            for column in self.columns:
                for ii in range(3):
                    fle.write(f'<th class="val{ii+1}">{ii+1}+</th>\n')
            fle.write('</tr>\n')
            for row in self.rows:
                fle.write('<tr>\n')
                fle.write(f'<td>{row.name}</td>\n')
                for cell in self.cells[row].values():
                    if not cell.value.is_set:
                        for ii in range(3):
                            fle.write(f'<td class="val{ii+1}">-</td>\n')
                    else:
                        fle.write(self._cellItem(cell.value.value_1, 'val1'))
                        fle.write(self._cellItem(cell.value.value_2, 'val2'))
                        fle.write(self._cellItem(cell.value.value_3, 'val3'))
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
                        }
                    }
                }

                let cols = document.getElementById('val1').checked
                       + document.getElementById('val2').checked + 
                       + document.getElementById('val3').checked;

                let elements = document.querySelectorAll('.main_heading');
                for( let ii=0; ii < elements.length; ii++) {
                    elements[ii].setAttribute('colspan',cols);
                }
            }
            </script>
                      ''')

            fle.write('</body>\n')







