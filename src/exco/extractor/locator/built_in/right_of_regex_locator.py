import re
from dataclasses import dataclass

from exco import CellLocation, util
from exco.extractor.locator.locating_result import LocatingResult
from exco.extractor.locator.locator import Locator
from openpyxl import Workbook
from openpyxl.worksheet.worksheet import Worksheet


@dataclass(frozen=True)
class RightOfRegexLocator(Locator):
    regex: str
    n: int = 1

    def locate(self, anchor_cell_location: CellLocation,
               workbook: Workbook) -> LocatingResult:
        sheet: Worksheet = workbook[anchor_cell_location.sheet_name]
        compiled_regex = re.compile(self.regex)
        for row in sheet.iter_rows():
            for cell in row:
                if compiled_regex.fullmatch(str(cell.value)) is not None:
                    coord = util.get_rightmost_coordinate(sheet=sheet, cell=cell)
                    cell_loc = CellLocation(
                        sheet_name=anchor_cell_location.sheet_name,
                        coordinate=util.shift_coord(coord.coordinate, (0, self.n))
                    )
                    return LocatingResult.good(cell_loc)
        return LocatingResult.bad(
            msg=f"Unable to find cell to the right of {self.regex}")
