"""Schema validation and contract enforcement."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, validator

from backend.utils.logger import get_logger

logger = get_logger(__name__)


class FieldSchema(BaseModel):
    name: str
    dtype: str
    required: bool = True
    allowed_values: list[Any] | None = None
    min_value: float | None = None
    max_value: float | None = None

    @validator("dtype")
    def validate_dtype(cls, value: str) -> str:  # noqa: N805
        allowed = {"int", "float", "str", "bool", "datetime"}
        if value not in allowed:
            raise ValueError(f"Unsupported dtype {value}")
        return value


class DatasetSchema(BaseModel):
    name: str
    version: str
    fields: list[FieldSchema]
    expected_records: int | None = None


class SchemaViolation(BaseModel):
    field: str
    message: str
    severity: str = "ERROR"


class SchemaValidator:
    """Validator to ensure records comply with declared contract."""

    def __init__(self, dataset_schema: DatasetSchema) -> None:
        self.schema = dataset_schema
        self.field_map = {field.name: field for field in dataset_schema.fields}

    def validate(self, records: list[dict[str, Any]]) -> list[SchemaViolation]:
        """Check each record against schema rules and report violations."""

        violations: list[SchemaViolation] = []
        for idx, record in enumerate(records):
            for field in self.schema.fields:
                if field.required and field.name not in record:
                    violations.append(
                        SchemaViolation(
                            field=field.name,
                            message=f"Record {idx} missing required field",
                        )
                    )
                    continue
                if field.name not in record:
                    continue
                value = record[field.name]
                if not self._matches_type(value, field.dtype):
                    violations.append(
                        SchemaViolation(
                            field=field.name,
                            message=f"Record {idx} type mismatch expected {field.dtype}",
                        )
                    )
                if field.allowed_values and value not in field.allowed_values:
                    violations.append(
                        SchemaViolation(
                            field=field.name,
                            message=f"Record {idx} value {value} not in allowed set",
                        )
                    )
                if field.min_value is not None and self._to_float(value) < field.min_value:
                    violations.append(
                        SchemaViolation(
                            field=field.name,
                            message=f"Record {idx} below min {field.min_value}",
                            severity="WARN",
                        )
                    )
                if field.max_value is not None and self._to_float(value) > field.max_value:
                    violations.append(
                        SchemaViolation(
                            field=field.name,
                            message=f"Record {idx} above max {field.max_value}",
                            severity="WARN",
                        )
                    )
        if self.schema.expected_records and len(records) != self.schema.expected_records:
            violations.append(
                SchemaViolation(
                    field="dataset",
                    message="Record count deviates from expected",
                    severity="WARN",
                )
            )
        logger.info("Schema validation produced %d violations", len(violations))
        return violations

    def _matches_type(self, value: Any, dtype: str) -> bool:
        """Return True if value conforms to declared dtype."""

        if dtype == "int":
            return isinstance(value, int) and not isinstance(value, bool)
        if dtype == "float":
            return isinstance(value, (int | float)) and not isinstance(value, bool)
        if dtype == "str":
            return isinstance(value, str)
        if dtype == "bool":
            return isinstance(value, bool)
        if dtype == "datetime":
            try:
                datetime.fromisoformat(str(value))
                return True
            except ValueError:
                return False
        return False

    def _to_float(self, value: Any) -> float:
        """Best-effort coercion to float to compare against numeric bounds."""

        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0
