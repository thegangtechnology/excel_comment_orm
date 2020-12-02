import abc
from typing import Generic, TypeVar

from exco.cell_full_path import CellFullPath
from exco.extractor.actor import Actor

from exco.extractor.parser.parsing_result import ParsingResult

PARSER_CLASS_SUFFIX = 'Parser'
T = TypeVar('T')


class Parser(Actor, abc.ABC, Generic[T]):
    @abc.abstractmethod
    def parse(self, cfp: CellFullPath, fallback: T) -> ParsingResult[T]:
        raise NotImplementedError()
