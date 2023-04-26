from dataclasses import dataclass, field
from typing import Dict, Any, ClassVar, Set, TypeVar, Generic

from exco import setting as st
from exco.dereferator import Dereferator
from exco.extractor_spec.assumption_spec import AssumptionSpec
from exco.extractor_spec.parser_spec import ParserSpec
from exco.extractor_spec.spec_source import SpecSource, UnknownSource
from exco.extractor_spec.validator_spec import ValidatorSpec

T = TypeVar('T')


@dataclass
class APVSpec(Generic[T]):  # Assume Parse Validate
    key: str
    parser: ParserSpec
    fallback: T
    validations: Dict[str, ValidatorSpec] = field(default_factory=dict)
    assumptions: Dict[str, AssumptionSpec] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    source: SpecSource = field(default_factory=UnknownSource)

    consumed_keys: ClassVar[Set[str]] = {
        st.k_key, st.k_validations, st.k_assumptions, st.k_metadata}
    allowed_keys: ClassVar[Set[str]] = consumed_keys | ParserSpec.allowed_keys

    def deref(self, dereferator: Dereferator) -> 'APVSpec[T]':
        return APVSpec(
            key=dereferator.deref_text(self.key),
            parser=self.parser.deref(dereferator),
            fallback=dereferator.deref_text(self.fallback),
            validations={k: v.deref(dereferator) for k, v in self.validations.items()},
            assumptions={k: v.deref(dereferator) for k, v in self.assumptions.items()},
            metadata=dereferator.deref(self.metadata),
            source=self.source
        )

    @classmethod
    def from_dict(cls, d: Dict[str, Any], source: source) -> 'APVSpec':
        return APVSpec(
            key=d[st.k_key],
            parser=ParserSpec.from_dict(d),
            fallback=d.get(st.k_fallback, st.default_fallback_value),
            validations={v[st.k_key]: ValidatorSpec.from_dict(
                v) for v in d.get(st.k_validations, [])},
            assumptions={v[st.k_key]: AssumptionSpec.from_dict(
                v) for v in d.get(st.k_assumptions, [])},
            metadata=d.get(st.k_metadata, {}),
            source=source if source is not None else UnknownSource()
        )
