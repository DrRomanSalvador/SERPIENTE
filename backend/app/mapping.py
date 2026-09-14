from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .contracts import Observation


class ObservationMapper:
    """Map an official structured row into the canonical observation contract.

    No field is silently renamed or unit-converted. A source-unit mismatch is
    rejected unless an explicit transformation is represented by the mapping.
    """

    def __init__(self, *, variable_id: str, semantic_definition: str, unit: str, value_field: str, event_time_field: str, geography: str, source_id: str, dataset_id: str, source_version: str, source_unit: str | None = None, source_unit_field: str | None = None, transformation_lineage: tuple[str, ...] = ()) -> None:
        required = (variable_id, semantic_definition, unit, value_field, event_time_field, geography, source_id, dataset_id, source_version)
        if any(not item.strip() for item in required):
            raise ValueError("canonical source mapping requires complete semantic metadata")
        if source_unit_field and not source_unit:
            raise ValueError("source_unit is required when source_unit_field is configured")
        self.variable_id = variable_id
        self.semantic_definition = semantic_definition
        self.unit = unit
        self.value_field = value_field
        self.event_time_field = event_time_field
        self.geography = geography
        self.source_id = source_id
        self.dataset_id = dataset_id
        self.source_version = source_version
        self.source_unit = source_unit
        self.source_unit_field = source_unit_field
        self.transformation_lineage = transformation_lineage

    def map_row(self, row: dict[str, Any], *, acquisition_time: datetime, publication_time: datetime | None = None, revision: int = 0, provenance: tuple[str, ...], source_version: str | None = None) -> Observation:
        if self.value_field not in row or self.event_time_field not in row:
            raise ValueError("source row lacks a declared value or event-time field")
        if self.source_unit_field:
            actual_unit = row.get(self.source_unit_field)
            if actual_unit != self.source_unit:
                raise ValueError("source unit is incompatible with the declared mapping")
            if self.source_unit != self.unit and not self.transformation_lineage:
                raise ValueError("unit conversion requires explicit transformation lineage")
        version = source_version or self.source_version
        if not version.strip():
            raise ValueError("source version is required")
        value = row[self.value_field]
        if value is None:
            return Observation(self.source_id, self.dataset_id, self.variable_id, self.semantic_definition, self.unit, self.geography, self._time(row[self.event_time_field]), self._time(publication_time or acquisition_time), acquisition_time, version, revision, None, provenance, missing=True, transformation_lineage=self.transformation_lineage)
        try:
            numeric = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError("declared source value is not numeric") from exc
        return Observation(self.source_id, self.dataset_id, self.variable_id, self.semantic_definition, self.unit, self.geography, self._time(row[self.event_time_field]), self._time(publication_time or acquisition_time), acquisition_time, version, revision, numeric, provenance, transformation_lineage=self.transformation_lineage)

    @staticmethod
    def _time(value: Any) -> datetime:
        if isinstance(value, datetime):
            if value.tzinfo is None:
                raise ValueError("source timestamp must be timezone-aware")
            return value.astimezone(timezone.utc)
        if isinstance(value, str):
            parsed = datetime.fromisoformat(value)
            if parsed.tzinfo is None:
                raise ValueError("source timestamp must include timezone")
            return parsed.astimezone(timezone.utc)
        raise ValueError("source timestamp must be datetime or ISO-8601 string")
