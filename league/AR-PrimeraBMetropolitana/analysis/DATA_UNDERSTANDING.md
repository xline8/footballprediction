# Phase 1 — Data understanding

## Inventory

FotMob parent league `9213` contains 5,455 index rows. Filtering payload
`general.leagueName` to `Metropolitana` yields 2,236 PBM rows, spanning
2021–2026 and 2021-03-06 through 2026-11-02. Every PBM row is finished and
has a header score. The group-phase build contains 2,160 rows; 76 are
excluded.

| season | group | excluded | regular format |
|---|---:|---:|---|
| 2021 | 272 | 23 | Apertura + Clausura, 17 teams, 136 each |
| 2022 | 272 | 10 | Apertura + Clausura, 17 teams, 136 each |
| 2023 | 272 | 14 | Apertura + Clausura, 17 teams, 136 each |
| 2024 | 462 | 15 | Apertura + Clausura, 22 teams, 231 each |
| 2025 | 420 | 14 | Apertura + Clausura, 21 teams, 210 each |
| 2026 | 462 | 0 | virgin definition only: single table, 22 teams, rounds 1–42 |

The excluded rows are Promotion Playoff (9/10/12/12/14/0), Championship
Playoff (2/0/2/2/0/0), the 2021 Complemento Group A/B/C (3 each) and
Complemento Final Stage (3), and the 2024 `Fase Tercer Ascenso` final
Sarmiento de La Banda 0–1 Los Andes. The latter is a cross-competition
promotion final and is excluded from both league builds.

## Coverage and quirks

The payload carries no non-empty `content.stats` block and no shotmap shot
for any PBM row. Referee text is empty throughout. There are no period
splits. Event lists are present structurally on every payload; empty event
lists occur only on 0–0 rows. Header goals equal event-goal counts on every
PBM row. Goal events have integer times; for the half audit, 1H means
`time <= 45`, including time 45 and excluding time 46. Across the PBM
payloads, the boundary counts are 126 goals at 45 and 39 at 46.

Card events are only `Red` and `YellowRed`; there are zero `Yellow` events.
The `Red` event counts by season are 58, 73, 66, 124, 145, and 120.
Therefore cards are not a target candidate and yellow columns are not
created in the analysis CSV.

Team identity is FotMob team id. Canonical names use the spelling in the most
recent match, preserving one identity across accent-only variants.

The complete inventory and coverage record is in
`analysis/inventory_summary.json`.
