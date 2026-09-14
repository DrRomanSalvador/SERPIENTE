from datetime import datetime, timezone

from app.mapping import ObservationMapper
from app.polling import PollJob
from app.runtime import SerpienteRuntime


class FakeClient:
    def fetch(self, url, *, source_id, dataset_id):
        return b'{"observations":[{"value":21.5,"time":"2026-01-01T00:00:00+00:00"}]}', {"acquisition_time": datetime(2026,1,1,1,tzinfo=timezone.utc), "publication_time": datetime(2026,1,1,tzinfo=timezone.utc), "source_version":"v1", "provenance":("official:test",)}


def test_poll_once_inserts_mapped_observation():
    runtime = SerpienteRuntime()
    mapper = ObservationMapper(variable_id="temp", semantic_definition="air temperature", unit="degC", value_field="value", event_time_field="time", geography="Ceuta", source_id="test", dataset_id="obs", source_version="v1")
    count = runtime.poll_once(FakeClient(), PollJob("test", "obs", "https://example.org/data", 60), mapper)
    assert count == 1
    assert runtime.observations.at(datetime(2026,1,1,2,tzinfo=timezone.utc))[0].value == 21.5
