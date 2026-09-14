from datetime import datetime, timezone

import pytest

from app.mapping import ObservationMapper


def mapper():
    return ObservationMapper(variable_id="temp", semantic_definition="air temperature", unit="degC", value_field="value", event_time_field="time", geography="Ceuta", source_id="aemet", dataset_id="obs", source_version="v1")


def test_mapping_preserves_lineage_and_semantics():
    row = mapper().map_row({"value":"21.5", "time":"2026-01-01T00:00:00+00:00"}, acquisition_time=datetime(2026,1,1,1,tzinfo=timezone.utc), provenance=("official:aemet",))
    assert row.value == 21.5 and row.unit == "degC" and row.provenance == ("official:aemet",)


def test_mapping_rejects_naive_source_timestamp():
    with pytest.raises(ValueError):
        mapper().map_row({"value":1, "time":"2026-01-01T00:00:00"}, acquisition_time=datetime(2026,1,1,1,tzinfo=timezone.utc), provenance=("official",))


def test_mapping_rejects_incompatible_source_unit():
    with pytest.raises(ValueError, match="unit"):
        ObservationMapper(variable_id="temp", semantic_definition="air temperature", unit="degC", value_field="value", event_time_field="time", geography="Ceuta", source_id="aemet", dataset_id="obs", source_version="v1", source_unit="K", source_unit_field="unit")
