from dataclasses import dataclass, field
from typing import Generic, Dict, TypeVar, Any

from openpyxl import Workbook

from exco.cell_location import CellLocation
from exco.extractor.assumption.assumption import Assumption
from exco.extractor.assumption.assumption_result import AssumptionResult
from exco.extractor.locator.built_in.at_comment_cell_locator import AtCommentCellLocator
from exco.extractor.locator.locating_result import LocatingResult
from exco.extractor.locator.locator import Locator
from exco.extractor.parser.parser import Parser
from exco.extractor.parser.parsing_result import ParsingResult
from exco.extractor.validator.validation_result import ValidationResult
from exco.extractor.validator.validator import Validator
from exco.util import long_string

T = TypeVar('T')


@dataclass
class CellExtractionTaskResult(Generic[T]):
    key: str
    locating_result: LocatingResult
    parsing_result: ParsingResult[T]
    metadata: Dict[str, Any]
    validation_results: Dict[str, ValidationResult] = field(
        default_factory=dict)
    assumption_results: Dict[str, AssumptionResult] = field(
        default_factory=dict)

    def get_value(self) -> T:
        """Get Python equivalent value

        Returns:
            T. Python equivalent value.
        """
        return self.parsing_result.get_value()

    @property
    def is_ok(self):
        """
        Returns:
            True if it pass assumption, parsing, and validation.
        """
        return self.parsing_result.is_ok and \
               all(ar.is_ok for ar in self.assumption_results.values()) and \
               all(vr.is_ok for vr in self.validation_results.values())

    @classmethod
    def fail_locating(cls, key: str, locating_result: LocatingResult,
                      fallback: T, metadata: Dict[str, Any]) -> 'CellExtractionTaskResult[T]':
        msg = "Fail Locating"
        assert not locating_result.is_ok
        return CellExtractionTaskResult(
            key=key,
            locating_result=locating_result,
            parsing_result=ParsingResult[T].bad(msg=msg, fallback=fallback),
            metadata=metadata
        )

    @classmethod
    def fail_assumptions(cls, key: str,
                         locating_result: LocatingResult,
                         assumption_results: Dict[str, AssumptionResult],
                         fallback: T,
                         metadata: Dict[str, Any]) -> 'CellExtractionTaskResult[T]':
        msg = "Fail Assumption"
        assert any(not ar.is_ok for ar in assumption_results.values())
        return CellExtractionTaskResult(
            key=key,
            locating_result=locating_result,
            assumption_results=assumption_results,
            parsing_result=ParsingResult.bad(msg=msg, fallback=fallback),
            metadata=metadata
        )


@dataclass
class CellExtractionTask(Generic[T]):
    key: str
    locator: Locator
    parser: Parser[T]
    validators: Dict[str, Validator[T]]
    assumptions: Dict[str, Assumption]
    fallback: T
    metadata: Dict[str, Any]

    def __str__(self):
        s = long_string(f"""
        key: "{self.key}"
        locator: {self.locator}
        parser: {self.parser}
        validators: {[dict(key=key, v=v) for key, v in self.validators.items()]}
        assumptions: {[dict(key=key, a=a) for key, a in self.assumptions.items()]}
        metadata: {self.metadata}
        fallback: {self.fallback}""")
        return s

    def process(self, anchor_cell_location: CellLocation,
                workbook: Workbook) -> CellExtractionTaskResult[T]:
        locating_result = self.locator.locate(
            anchor_cell_location=anchor_cell_location,
            workbook=workbook
        )
        if not locating_result.is_ok:
            return CellExtractionTaskResult.fail_locating(
                key=self.key,
                locating_result=locating_result,
                fallback=self.fallback,
                metadata=self.metadata)
        cfp = locating_result.location.get_cell_full_path(workbook)

        assumption_results = {k: assumption.assume(
            cfp) for k, assumption in self.assumptions.items()}
        if any(not ar.is_ok for ar in assumption_results.values()):
            return CellExtractionTaskResult.fail_assumptions(
                key=self.key,
                locating_result=locating_result,
                assumption_results=assumption_results,
                fallback=self.fallback,
                metadata=self.metadata
            )

        parsing_result = self.parser.parse(cfp, self.fallback)
        if not parsing_result.is_ok:
            return CellExtractionTaskResult(
                key=self.key,
                locating_result=locating_result,
                assumption_results=assumption_results,
                parsing_result=parsing_result,
                metadata=self.metadata
            )

        validation_results = {k: vt.validate(
            parsing_result.value) for k, vt in self.validators.items()}
        return CellExtractionTaskResult(
            key=self.key,
            locating_result=locating_result,
            assumption_results=assumption_results,
            parsing_result=parsing_result,
            validation_results=validation_results,
            metadata=self.metadata
        )

    @classmethod
    def simple(cls, key: str, parser: Parser):
        return cls(
            key=key,
            locator=AtCommentCellLocator(),
            parser=parser,
            validators={},
            assumptions={},
            fallback=None,
            metadata={}
        )
