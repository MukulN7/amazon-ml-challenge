"""Schema contract definitions for Amazon ML Challenge 2026 datasets.

Defines expected structure, column types, identifier prefixes, and validation constraints
for train/test source files and ground truth.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set


class SchemaValidationError(Exception):
    """Raised when a dataset violates its expected schema contract."""
    pass


@dataclass
class ColumnSchema:
    name: str
    dtype: str
    allow_null: bool = False
    allow_empty_string: bool = False
    id_prefix: Optional[str] = None


@dataclass
class TableSchema:
    name: str
    columns: List[ColumnSchema]
    primary_key: Optional[str] = None
    expected_id_prefixes: Set[str] = field(default_factory=set)

    @property
    def column_names(self) -> List[str]:
        return [col.name for col in self.columns]


# Standard schema for source entity files (Source 1, Source 2, Source 3)
SOURCE1_SCHEMA = TableSchema(
    name="source1",
    primary_key="entity_id",
    expected_id_prefixes={"S1-"},
    columns=[
        ColumnSchema(name="entity_id", dtype="string", allow_null=False, allow_empty_string=False, id_prefix="S1-"),
        ColumnSchema(name="business_name", dtype="string", allow_null=True, allow_empty_string=True),
        ColumnSchema(name="business_address", dtype="string", allow_null=True, allow_empty_string=True),
        ColumnSchema(name="country", dtype="string", allow_null=True, allow_empty_string=True),
    ]
)

SOURCE2_SCHEMA = TableSchema(
    name="source2",
    primary_key="entity_id",
    expected_id_prefixes={"S2-"},
    columns=[
        ColumnSchema(name="entity_id", dtype="string", allow_null=False, allow_empty_string=False, id_prefix="S2-"),
        ColumnSchema(name="business_name", dtype="string", allow_null=True, allow_empty_string=True),
        ColumnSchema(name="business_address", dtype="string", allow_null=True, allow_empty_string=True),
        ColumnSchema(name="country", dtype="string", allow_null=True, allow_empty_string=True),
    ]
)

SOURCE3_SCHEMA = TableSchema(
    name="source3",
    primary_key="entity_id",
    expected_id_prefixes={"S3-"},
    columns=[
        ColumnSchema(name="entity_id", dtype="string", allow_null=False, allow_empty_string=False, id_prefix="S3-"),
        ColumnSchema(name="business_name", dtype="string", allow_null=True, allow_empty_string=True),
        ColumnSchema(name="business_address", dtype="string", allow_null=True, allow_empty_string=True),
        ColumnSchema(name="country", dtype="string", allow_null=True, allow_empty_string=True),
    ]
)

GROUND_TRUTH_SCHEMA = TableSchema(
    name="ground_truth",
    primary_key="source1_entity_id",
    expected_id_prefixes={"S1-"},
    columns=[
        ColumnSchema(name="source1_entity_id", dtype="string", allow_null=False, allow_empty_string=False, id_prefix="S1-"),
        ColumnSchema(name="matched_entity_ids", dtype="string", allow_null=True, allow_empty_string=True),
    ]
)

# Registry mapping filename pattern to schema definition
SCHEMA_REGISTRY: Dict[str, TableSchema] = {
    "train_source1.tsv": SOURCE1_SCHEMA,
    "train_source2.tsv": SOURCE2_SCHEMA,
    "train_source3.tsv": SOURCE3_SCHEMA,
    "test_source1.tsv": SOURCE1_SCHEMA,
    "test_source2.tsv": SOURCE2_SCHEMA,
    "test_source3.tsv": SOURCE3_SCHEMA,
    "train_ground_truth.tsv": GROUND_TRUTH_SCHEMA,
}
