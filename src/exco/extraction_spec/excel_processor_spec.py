from dataclasses import dataclass
from typing import Dict, List

from exco.cell_location import CellLocation
from exco import util
from exco.extraction_spec.extraction_task_spec import ExtractionTaskSpec


@dataclass
class ExcelProcessorSpec:
    task_specs: Dict[CellLocation, List[ExtractionTaskSpec]]  # comment cell -> specs

    def n_spec(self) -> int:
        return sum(len(v) for v in self.task_specs.values())

    def n_location(self) -> int:
        return len(self.task_specs)

    def is_keys_unique(self) -> bool:
        return util.is_unique(spec.key for specs in self.task_specs.values() for spec in specs)
