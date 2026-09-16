from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class AccessMode(StrEnum):
    HTTPS_CSV = "https_csv"
    HTTPS_API = "https_api"
    HTTPS_DOWNLOAD = "https_download"


class AvailabilityStatus(StrEnum):
    CONTINUOUS = "continuous"
    PERIODIC = "periodic"
    MANUAL_OR_REQUEST = "manual_or_request"


@dataclass(frozen=True, slots=True)
class AcquisitionSpec:
    source_id: str
    authority: str
    dataset_id: str
    url: str
    access_mode: AccessMode
    availability: AvailabilityStatus
    cadence: str
    publication_latency: str
    revision_policy: str
    temporal_semantics: str
    geographic_scope: str
    authentication: str
    scientific_uses: tuple[str, ...]
    limitations: tuple[str, ...]

    def __post_init__(self) -> None:
        if not all((self.source_id, self.authority, self.dataset_id, self.url, self.cadence, self.publication_latency, self.revision_policy, self.temporal_semantics, self.geographic_scope, self.authentication)):
            raise ValueError("acquisition specification is incomplete")
        if not self.scientific_uses or not self.limitations:
            raise ValueError("acquisition specification requires uses and limitations")


CEUTA_SOURCE_CATALOG: tuple[AcquisitionSpec, ...] = (
    AcquisitionSpec(
        source_id="aemet",
        authority="AEMET",
        dataset_id="open_data_meteorology",
        url="https://opendata.aemet.es/",
        access_mode=AccessMode.HTTPS_API,
        availability=AvailabilityStatus.CONTINUOUS,
        cadence="resource-dependent; API supports scheduled/periodic retrieval",
        publication_latency="resource-dependent; must be captured from response metadata",
        revision_policy="source version must be recorded from response metadata; do not overwrite prior observations",
        temporal_semantics="meteorological observation/product time distinct from acquisition time",
        geographic_scope="Ceuta / Spanish meteorological network where the selected resource covers it",
        authentication="API key required",
        scientific_uses=("weather exposure", "heat/cold stress", "precipitation", "environmental covariates", "seasonality"),
        limitations=("specific station/resource coverage must be verified before activation", "API key is an external provisioning dependency"),
    ),
    AcquisitionSpec(
        source_id="ine",
        authority="Instituto Nacional de Estadística",
        dataset_id="ceuta_mortality_by_cause_sex_age_72146",
        url="https://servicios.ine.es/wstempus/js/es/DATOS_TABLA/72146?tip=AM",
        access_mode=AccessMode.HTTPS_DOWNLOAD,
        availability=AvailabilityStatus.PERIODIC,
        cadence="periodic statistical release; not a real-time surveillance feed",
        publication_latency="release-dependent; must be measured from publication metadata",
        revision_policy="preserve source version/retrieval timestamp and never treat revised releases as historical real-time knowledge",
        temporal_semantics="death occurrence/reference period versus publication/acquisition time",
        geographic_scope="Ceuta",
        authentication="none verified",
        scientific_uses=("mortality", "cause-specific mortality", "age/sex stratification", "denominator and severity context"),
        limitations=("periodic release", "not suitable as a real-time outcome source", "cause-of-death coding and release revisions must be tracked"),
    ),
    AcquisitionSpec(
        source_id="ine",
        authority="Instituto Nacional de Estadística",
        dataset_id="ceuta_demographic_mortality_61267",
        url="https://www.ine.es/jaxi/files/tpx/csv_bdsc/61267.csv",
        access_mode=AccessMode.HTTPS_CSV,
        availability=AvailabilityStatus.PERIODIC,
        cadence="periodic statistical release",
        publication_latency="release-dependent",
        revision_policy="retain retrieved file/version fingerprint and acquisition timestamp",
        temporal_semantics="demographic event/reference period versus acquisition time",
        geographic_scope="Ceuta",
        authentication="none verified",
        scientific_uses=("population denominator", "demographic change", "mortality context"),
        limitations=("periodic rather than continuous", "denominator changes must not be conflated with incidence changes"),
    ),
    AcquisitionSpec(
        source_id="ecdc",
        authority="European Centre for Disease Prevention and Control",
        dataset_id="surveillance_atlas_infectious_diseases",
        url="https://www.ecdc.europa.eu/en/surveillance-atlas-infectious-diseases",
        access_mode=AccessMode.HTTPS_DOWNLOAD,
        availability=AvailabilityStatus.PERIODIC,
        cadence="latest available surveillance data; dataset-specific",
        publication_latency="depends on national reporting and ECDC validation/release",
        revision_policy="retain dataset release/retrieval metadata and do not infer point-in-time availability without release evidence",
        temporal_semantics="surveillance reference period distinct from ECDC publication/availability time",
        geographic_scope="EU/EEA; Ceuta applicability depends on the underlying Spanish reporting coverage",
        authentication="none for published atlas data; third-party non-atlas requests may require a data request",
        scientific_uses=("infectious disease surveillance", "cross-jurisdiction corroboration", "case-count context", "surveillance trend comparison"),
        limitations=("not all data are available at local Ceuta resolution", "national/EU aggregation can limit local inference", "underlying reporting processes must be treated as part of the data-generating process"),
    ),
)


def get_ceuta_sources() -> tuple[AcquisitionSpec, ...]:
    return CEUTA_SOURCE_CATALOG


def sources_for_use(use: str) -> tuple[AcquisitionSpec, ...]:
    token = use.strip().lower()
    return tuple(source for source in CEUTA_SOURCE_CATALOG if token in {item.lower() for item in source.scientific_uses})


__all__ = ["AccessMode", "AcquisitionSpec", "AvailabilityStatus", "CEUTA_SOURCE_CATALOG", "get_ceuta_sources", "sources_for_use"]
