from typing import List
import logging

import exco.extraction_spec.extraction_task_spec
import yaml
from dataclasses import dataclass
from exco import setting
from exco import exception as exc

from exco.extraction_spec.spec_source import SpecSource
from exco.extraction_spec.extraction_task_spec import ExtractionTaskSpec


@dataclass
class ExcoBlock(SpecSource):
    start_line: int
    end_line: int
    raw: str

    def to_extractor_task_spec(self) -> ExtractionTaskSpec:
        # TODO: add special symbol to deref cell address at template
        d = yaml.load(self.raw, Loader=yaml.FullLoader)
        return ExtractionTaskSpec.from_dict(d, source=self)

    def describe(self) -> str:
        return self.raw

    @classmethod
    def from_string(cls, comment: str,
                    start_marker=setting.start_marker,
                    end_marker=setting.end_marker) -> List['ExcoBlock']:
        in_marker = False
        current_str = ''
        start_line = None
        ret = []
        for i, line in enumerate(comment.splitlines(keepends=True), start=1):
            if line.strip() == start_marker:
                logging.debug(f'start {i}')
                if in_marker:
                    raise exc.TooManyBeginException(f"Expect end marker before another begin marker at line {i}.")
                in_marker = True
                start_line = i
            elif line.strip() == end_marker:
                logging.debug(f'end {i}')
                if not in_marker:
                    raise exc.TooManyEndException(f"Expect another begin marker at line {i}.")
                in_marker = False
                end_line = i
                ret.append(ExcoBlock(
                    start_line=start_line,
                    end_line=end_line,
                    raw=current_str
                ))
                current_str = ''
            elif in_marker:
                logging.debug(f'in_marker: {i} {line!r}')
                current_str += line
        if in_marker:
            raise exc.ExpectEndException("Expect End marker before the end.")
        return ret
