from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional

from exco import setting as st
from exco.cell_location import CellOffset
from exco.dereferator import Dereferator
from exco.extractor_spec.apv_spec import APVSpec
from exco.extractor_spec.locator_spec import LocatorSpec
from exco.extractor_spec.spec_source import UnknownSource, SpecSource
from exco.extractor_spec.type import SpecParam
from exco.util import name_params


class TableItemDirection(Enum):
    DOWNWARD = 'downward'
    RIGHTWARD = 'rightward'

    @classmethod
    def default(cls) -> 'TableItemDirection':
        return TableItemDirection.DOWNWARD

    @classmethod
    def from_value(cls, v: Optional[str]) -> 'TableItemDirection':
        if v is None:
            return cls.default()
        else:
            return TableItemDirection(v)


@dataclass
class TableEndConditionSpec:
    name: str
    params: SpecParam = field(default_factory=dict)

    def deref(self, dereferator: Dereferator) -> 'TableEndConditionSpec':
        return TableEndConditionSpec(
            name=dereferator.deref_text(self.name),
            params={k: dereferator.deref_text(v) for k, v in self.params.items()}
        )

    @classmethod
    def default_conditions(cls) -> List['TableEndConditionSpec']:
        return [TableEndConditionSpec(name='all_blank', params={})]

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'TableEndConditionSpec':
        name, params = name_params(d)
        return TableEndConditionSpec(name=name, params=params)


@dataclass
class ColumnSpecDict:
    offset: CellOffset
    dict: Dict[str, Any]
    source: SpecSource


@dataclass
class TableExtractionSpec:
    key: str
    locator: LocatorSpec  # for corner
    columns: Dict[CellOffset, APVSpec]  # offset -> APVSpec
    end_conditions: List[TableEndConditionSpec] = field(
        default_factory=TableEndConditionSpec.default_conditions)
    item_direction: TableItemDirection = TableItemDirection.DOWNWARD
    source: SpecSource = field(default_factory=UnknownSource)

    def deref(self, dereferator: Dereferator) -> 'TableExtractionSpec':
        return TableExtractionSpec(
            key=dereferator.deref_text(self.key),
            locator=self.locator.deref(dereferator),
            columns={k: v.deref(dereferator) for k, v in self.columns.items()},
            end_conditions=[tec.deref(dereferator) for tec in self.end_conditions],
            item_direction=self.item_direction,
            source=self.source
        )

    @classmethod
    def from_dict(cls, d: Dict[str, Any], source: SpecSource = None) -> 'TableExtractionSpec':
        """Construct form dict

        Args:
            d ():
            source ():

        Returns:

        """
        source = source if source is not None else UnknownSource()
        col_dicts = [ColumnSpecDict(offset, col_spec, UnknownSource())
                     for offset, col_spec in d[st.k_columns].items()]
        return cls.from_table_and_column_dict(
            d, source, col_dicts
        )

    @classmethod
    def from_table_and_column_dict(cls,
                                   d: Dict[str,
                                           Any],
                                   source: SpecSource,
                                   column_dicts: List[ColumnSpecDict]) -> 'TableExtractionSpec':
        """
        Example:

        key: some_key
        locator: {LocatorSpec} # optional
        columns:
            - {offset: offset, spec: {AVPSpec}}
        end_conditions: # optional
            - {EndConditionSpec}
        item_direction: downward # optional

        Args:
            d (Dict[str, Any]):
            source (SpecSource):
            column_dicts (List[ColumnSpecDict])

        Returns:
            TableExtractionSpec
        """
        columns = {
            col.offset: APVSpec.from_dict(d=col.dict, source=col.source)
            for col in column_dicts
        }
        if st.k_end_conditions in d:
            end_conditions = [TableEndConditionSpec.from_dict(
                v) for v in d.get(st.k_end_conditions, [])]
        else:
            # should i have this default??
            end_conditions = TableEndConditionSpec.default_conditions()
        return TableExtractionSpec(
            key=d[st.k_key],
            locator=LocatorSpec.from_dict(d.get(st.k_locator, None)),
            columns=columns,
            end_conditions=end_conditions,
            item_direction=TableItemDirection.from_value(
                d.get(st.k_item_direction, None)),
            source=source
        )
