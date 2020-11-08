import re

from excel_comment_orm import CellLocation, util
from excel_comment_orm.extractor.locator.locating_result import LocatingResult
from excel_comment_orm.extractor.locator.locator import Locator
from openpyxl import Workbook
from openpyxl.worksheet.worksheet import Worksheet


class RightOfLocator(Locator):  # TODO: Add search scope
    label: str

    def locate(self, anchor_cell_location: CellLocation, workbook: Workbook) -> LocatingResult:
        sheet: Worksheet = workbook[anchor_cell_location.sheet_name]
        compiled_regex = re.compile(self.regex)
        for row in sheet.iter_rows():
            for cell in row:
                if cell.value == self.label:
                    cell_loc = CellLocation(
                        sheet_name=anchor_cell_location.sheet_name,
                        coordinate=util.shift_coord(cell.coordinate, (0, 1))
                    )
                    return LocatingResult.good(cell_loc)
        return LocatingResult.bad(msg=f"Unable to find cell to the right of {self.label}")
