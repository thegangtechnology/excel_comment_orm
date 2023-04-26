from dataclasses import dataclass, field
from typing import Dict, Any

from exco.dereferator import Dereferator
from exco.extractor_spec.type import SpecParam
from exco.setting import k_key
from exco.util import name_params


@dataclass
class ValidatorSpec:
    """
    Validation is something to check after parsing
    Ex: if the parsed value is greater than 99
    """
    name: str
    params: SpecParam = field(default_factory=dict)

    def deref(self, dereferator: Dereferator) -> 'ValidatorSpec':
        return ValidatorSpec(
            name=dereferator.deref_text(self.name),
            params={k: dereferator.deref_text(v) for k, v in self.params.items()}
        )

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'ValidatorSpec':
        """Construct ValidationTaskSpec from dict
        {name: greater_than, threshold: 99}

        Args:
            d (Dict[str, Any]):

        Returns:
            ValidationTaskSpec
        """
        name, params = name_params(d, exclude={k_key})
        return ValidatorSpec(name=name, params=params)
