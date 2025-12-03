"""Utilities for handling dataset payloads and synthetic generation."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, ValidationError

from backend.engines.schema_validator import DatasetSchema
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class DatasetPayload(BaseModel):
    """Expected payload for dataset submission."""

    dataset_schema: DatasetSchema = Field(..., alias="schema")
    records: list[dict[str, Any]]
    source: str = "synthetic"
    user: str = "system"
    transformation_steps: list[str] = Field(default_factory=list)

    class Config:
        allow_population_by_field_name = True


def load_dataset(payload: dict[str, Any]) -> tuple[DatasetSchema, list[dict[str, Any]]]:
    """Validate incoming payload and return schema and records."""
    try:
        parsed = DatasetPayload(**payload)
    except ValidationError as exc:
        logger.error("Dataset payload validation failed: %s", exc)
        raise

    if not parsed.records:
        raise ValueError("No records supplied")
    if not all(isinstance(item, dict) for item in parsed.records):
        raise ValueError("Records must be objects")

    logger.info("Dataset payload received with %d records", len(parsed.records))
    return parsed.dataset_schema, parsed.records
