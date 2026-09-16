# ESPÍA Runtime Denominator Evidence 001

## Scientific finding

Epidemiologic rates require an explicitly defined population at risk and time-at-risk denominator. Raw event counts are not directly comparable when the relevant population or observation period changes. CDC guidance distinguishes incidence proportion from incidence rate and defines rates using a denominator appropriate to the population and period; CDC surveillance guidance notes that numerator-only surveillance counts do not account for population size and dynamics. CDC also identifies changes in reporting, completeness, timeliness and ascertainment as sources of misleading surveillance trends.

Primary references:
- CDC, Principles and Practice of Public Health Surveillance: https://stacks.cdc.gov/view/cdc/92193/cdc_92193_DS1.pdf
- CDC Field Epidemiology Manual, Describing Epidemiologic Data: https://www.cdc.gov/field-epi-manual/php/chapters/describing-epi-data.html
- CDC, Updated Guidelines for Evaluating Public Health Surveillance Systems: https://www.cdc.gov/mmwr/preview/mmwrhtml/rr5013a1.htm
- CDC, Framework for Evaluating Surveillance Systems for Early Detection of Outbreaks: https://www.cdc.gov/mmwr/PDF/RR/RR5305.pdf
- CDC, Behind the Model: Nowcasting, 30 January 2026: https://www.cdc.gov/cfa-behind-the-model/php/data-research/nowcasting.html
- ECDC, Data quality monitoring and surveillance system evaluation: https://www.ecdc.europa.eu/sites/default/files/media/en/publications/Publications/Data-quality-monitoring-surveillance-system-evaluation-Sept-2014.pdf

## Consequence for SERPIENTE

A runtime `Observation` containing a count cannot authorize an incidence/risk interpretation by itself. The scientific work generated from an observation must retain denominator status as an unresolved object until the target population, population-at-risk definition, time interval/person-time, mobility/entry/exit, ascertainment and coverage are represented.

Reporting delay is a separate temporal problem: a recent observed count may be incomplete because events occurring earlier have not yet been reported. CDC describes nowcasting as an explicit response to this observation-process problem and notes that reporting delays can vary over time, location and operational conditions.

The current runtime observation contract therefore supports descriptive observation-level execution but does not establish real-world rate validity or complete recent-event ascertainment. This is an intentional capability boundary, not a software failure.

## Executable consequence

1. Preserve denominator identity in the runtime `Observation` object and ingestion API.
2. Preserve missing-denominator state explicitly as `denominator:REQUIRED` in the scientific audit.
3. Prevent single-observation execution from promoting a count to an incidence/risk claim.
4. Treat denominator change, reporting delay, ascertainment and coverage change as competing explanations for observed temporal change.
5. Persist evidence provenance so future ESPÍA instances do not recreate the same scientific derivation.

## Epistemic status

FORMALIZED: yes.
IMPLEMENTED: yes in the runtime scientific bridge, observation contract, ingestion API and execution boundary.
TEST-SPECIFIED: yes.
EMPIRICALLY_VALIDATED: no.
PROSPECTIVELY_VALIDATED: no.
OPERATIONALLY_EFFECTIVE: no.

## Negative knowledge

The available runtime `Observation` object alone cannot identify the true underlying population-at-risk denominator or the final complete count for a recent reporting period. Any component that infers either from the observed count alone would exceed the evidence carried by the object.
