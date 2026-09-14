import pytest

from app.source_registry import OfficialSourceRegistry


def test_official_registry_is_https_and_credentialed_where_required(monkeypatch):
    registry = OfficialSourceRegistry("config/official_sources.yaml")
    assert "opendata.aemet.es" in registry.hosts()
    assert "servicios.ine.es" in registry.hosts()
    monkeypatch.delenv("AEMET_API_KEY", raising=False)
    with pytest.raises(RuntimeError):
        registry.require_credentials("aemet_opendata")
