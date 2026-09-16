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
    AcquisitionSpec("aemet", "AEMET", "open_data_meteorology", "https://opendata.aemet.es/", AccessMode.HTTPS_API, AvailabilityStatus.CONTINUOUS, "resource-dependent; API supports scheduled/periodic retrieval", "resource-dependent; capture response metadata", "record source version and preserve prior observations", "meteorological observation/product time distinct from acquisition time", "Ceuta / Spanish meteorological network where the selected resource covers it", "API key required", ("weather exposure", "heat/cold stress", "precipitation", "environmental covariates", "seasonality"), ("specific station/resource coverage must be verified", "API key is an external provisioning dependency")),
    AcquisitionSpec("ine", "Instituto Nacional de Estadística", "ceuta_mortality_by_cause_sex_age_72146", "https://servicios.ine.es/wstempus/js/es/DATOS_TABLA/72146?tip=AM", AccessMode.HTTPS_DOWNLOAD, AvailabilityStatus.PERIODIC, "periodic statistical release; not real-time surveillance", "release-dependent; measure from publication metadata", "preserve source version/retrieval timestamp and prior releases", "death occurrence/reference period versus publication/acquisition time", "Ceuta", "none verified", ("mortality", "cause-specific mortality", "age/sex stratification", "denominator and severity context"), ("periodic release", "not a real-time outcome source", "cause-of-death coding and revisions must be tracked")),
    AcquisitionSpec("ine", "Instituto Nacional de Estadística", "ceuta_demographic_mortality_61267", "https://www.ine.es/jaxi/files/tpx/csv_bdsc/61267.csv", AccessMode.HTTPS_CSV, AvailabilityStatus.PERIODIC, "periodic statistical release", "release-dependent", "retain retrieved file/version fingerprint and acquisition timestamp", "demographic event/reference period versus acquisition time", "Ceuta", "none verified", ("population denominator", "demographic change", "mortality context"), ("periodic rather than continuous", "denominator changes must not be conflated with incidence changes")),
    AcquisitionSpec("ecdc", "European Centre for Disease Prevention and Control", "surveillance_atlas_infectious_diseases", "https://www.ecdc.europa.eu/en/surveillance-atlas-infectious-diseases", AccessMode.HTTPS_DOWNLOAD, AvailabilityStatus.PERIODIC, "latest available surveillance data; dataset-specific", "depends on national reporting and ECDC validation/release", "retain dataset release/retrieval metadata; do not infer point-in-time availability without release evidence", "surveillance reference period distinct from publication/availability time", "EU/EEA; Ceuta applicability depends on underlying Spanish reporting coverage", "none for published atlas data; non-atlas requests may require data request", ("infectious disease surveillance", "cross-jurisdiction corroboration", "case-count context", "surveillance trend comparison"), ("local Ceuta resolution may be unavailable", "national/EU aggregation limits local inference", "reporting process is part of the data-generating process")),
)


def get_ceuta_sources() -> tuple[AcquisitionSpec, ...]:
    return CEUTA_SOURCE_CATALOG


def sources_for_use(use: str) -> tuple[AcquisitionSpec, ...]:
    token = use.strip().lower()
    return tuple(source for source in CEUTA_SOURCE_CATALOG if token in {item.lower() for item in source.scientific_uses})


__all__ = ["AccessMode", "AcquisitionSpec", "AvailabilityStatus", "CEUTA_SOURCE_CATALOG", "get_ceuta_sources", "sources_for_use"]
