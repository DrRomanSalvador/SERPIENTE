from app.source_catalog import AccessMode, AvailabilityStatus, get_ceuta_sources, sources_for_use


def test_verified_ceuta_sources_preserve_acquisition_semantics():
    sources = get_ceuta_sources()
    assert {source.source_id for source in sources} == {"aemet", "ine", "ecdc"}
    assert any(source.access_mode is AccessMode.HTTPS_API and source.authentication == "API key required" for source in sources)
    assert any(source.dataset_id == "ceuta_mortality_by_cause_sex_age_72146" and source.availability is AvailabilityStatus.PERIODIC for source in sources)
    assert all(source.temporal_semantics and source.revision_policy and source.limitations for source in sources)


def test_source_selection_is_scientific_use_not_url_selection():
    mortality = sources_for_use("mortality")
    assert mortality
    assert all("mortality" in {use.lower() for use in source.scientific_uses} for source in mortality)
    assert not sources_for_use("not-a-real-use")
