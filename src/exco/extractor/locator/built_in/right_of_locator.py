from dataclasses import dataclass

from openpyxl import Workbook
from openpyxl.worksheet.worksheet import Worksheet

from exco import CellLocation, util
from exco.extractor.locator.locating_result import LocatingResult
from exco.extractor.locator.locator import Locator


@dataclass
class RightOfLocator(Locator):  # TODO: Add search scope
    label: str

    def locate(self, anchor_cell_location: CellLocation,
               workbook: Workbook) -> LocatingResult:
        sheet: Worksheet = workbook[anchor_cell_location.sheet_name]
        for row in sheet.iter_rows():
            for cell in row:
                if cell.value == self.label:
                    coord = cell.coordinate
                    if util.is_merged_cell(sheet, cell.coordinate):
                        coord = util.get_rightmost_coordinate(sheet=sheet, cell=cell)
                    cell_loc = CellLocation(
                        sheet_name=anchor_cell_location.sheet_name,
                        coordinate=util.shift_coord(util.tuple_to_coordinate(coord[0], coord[1]),
                                                    (0, 1))
                    )
                    return LocatingResult.good(cell_loc)
        return LocatingResult.bad(
            msg=f"Unable to find cell to the right of {self.label}")
