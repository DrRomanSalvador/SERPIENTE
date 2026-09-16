# ESPÍA Runtime Denominator Evidence 001

## Scientific finding

Epidemiologic rates require an explicitly defined population at risk and time-at-risk denominator. Raw event counts are not directly comparable when the relevant population or observation period changes. CDC guidance distinguishes incidence proportion from incidence rate and defines the latter using person-time at risk; CDC surveillance guidance likewise notes that numerator-only surveillance counts do not account for population size and dynamics.

Primary references:
- CDC, Principles of Epidemiology, Lesson 3, Section 2: https://archive.cdc.gov/www_cdc_gov/csels/dsepd/ss1978/lesson3/section2.html
- CDC Field Epidemiology Manual, Describing Epidemiologic Data: https://www.cdc.gov/field-epi-manual/php/chapters/describing-epi-data.html
- CDC Principles and Practice of Public Health Surveillance: https://stacks.cdc.gov/view/cdc/92193/cdc_92193_DS1.pdf
- ECDC, Data quality monitoring and surveillance system evaluation: https://www.ecdc.europa.eu/sites/default/files/media/en/publications/Publications/Data-quality-monitoring-surveillance-system-evaluation-Sept-2014.pdf

## Consequence for SERPIENTE

A runtime `Observation` containing a count cannot authorize an incidence/risk interpretation by itself. The scientific work generated from an observation must retain denominator status as an unresolved object until the target population, population-at-risk definition, time interval/person-time, mobility/entry/exit, ascertainment and coverage are represented.

The current runtime observation contract therefore supports descriptive observation-level execution but does not establish real-world rate validity. This is an intentional capability boundary, not a software failure.

## Executable consequence

1. Preserve denominator requirements in the runtime scientific audit.
2. Prevent single-observation execution from promoting a count to an incidence/risk claim.
3. Require denominator evidence before rate-based predictive or causal interpretation.
4. Treat denominator change as a competing explanation for observed temporal change.
5. Persist the evidence provenance so future ESPÍA instances do not recreate the same scientific derivation.

## Epistemic status

FORMALIZED: yes.
IMPLEMENTED: yes in the runtime scientific bridge and execution boundary.
TEST-SPECIFIED: yes.
EMPIRICALLY_VALIDATED: no.
PROSPECTIVELY_VALIDATED: no.
OPERATIONALLY_EFFECTIVE: no.

## Negative knowledge

The available runtime `Observation` object alone cannot identify the true underlying population-at-risk denominator. Any component that would infer such a denominator from the observation count itself would exceed the evidence carried by the object.
