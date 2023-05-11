import re
from dataclasses import dataclass

from openpyxl import Workbook

from exco import CellLocation, util
from exco.extractor.locator.locating_result import LocatingResult
from exco.extractor.locator.locator import Locator
from openpyxl.worksheet.worksheet import Worksheet


@dataclass
class SearchBelowOfRegexLocator(Locator):
    regex: str
    max_empty_row_search: int

    def locate(self, anchor_cell_location: CellLocation,
               workbook: Workbook) -> LocatingResult:
        sheet: Worksheet = workbook[anchor_cell_location.sheet_name]
        compiled_regex = re.compile(self.regex)
        for row in sheet.iter_rows():
            for cell in row:
                if compiled_regex.fullmatch(str(cell.value)) is not None:
                    coord = util.get_bottommost_coordinate(sheet=sheet, cell=cell)
                    cell_cor = self._search_empty_row(coord.coordinate, sheet)
                    cell_loc = CellLocation(
                                sheet_name=anchor_cell_location.sheet_name,
                                coordinate=cell_cor
                            )
                    return LocatingResult.good(cell_loc)
        return LocatingResult.bad(
            msg=f"Unable to find cell below of {self.regex}")

    def _search_empty_row(self, cell_cor: str, sheet: Worksheet) -> str:
        for _ in range(0, self.max_empty_row_search):
            cell_cor = util.shift_coord(cell_cor, (1, 0))
            if sheet[cell_cor].value is not None:
                return cell_cor
        return cell_cor
