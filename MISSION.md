# CeutIA + SERPIENTE — Persistent Mission Link

SERPIENTE is a component of the single continuous `CEUTIA_SERPIENTE_CONTINUOUS_SCIENTIFIC_ENGINEERING` mission.

The canonical machine-readable mission state is maintained in `DrRomanSalvador/Ceuta` at `mission/CEUTIA_SERPIENTE_MISSION_STATE.json`.

This repository must not treat SERPIENTE as an independent mission. Its role is the dynamic state/dynamics/interaction/prediction/uncertainty/risk/warning layer within the integrated architecture.

A new SERPIENTE agent instance must read this link, then load and reconcile the canonical mission state from CeutIA before continuing work.
