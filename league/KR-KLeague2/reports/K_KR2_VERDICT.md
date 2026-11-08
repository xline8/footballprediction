# K-KR2 verdict — FAIL (dev gate)

Target: stats-feed yellows (frozen; the event feed contains zero
plain Yellow events in 2022–2025, so an event-unified target is
impossible in this league, and the artefact-low 2022 stats era is
excluded — population 2023–2025, see PREREG_K_KR2).

Dev at OU 2.5, scored 2024 (single scored season), n=229 (seed 2023):

| arm / baseline | LL |
|---|---:|
| Gate Zero | 0.714503 |
| league base rate | 0.666409 |
| naive trailing-10 | 0.697192 |

Gate Zero beats neither baseline, so the candidate FAILS the dev
gate and the virgin (2025) was deliberately NOT read. Nothing ships.
Cards had no variant arm by design: the X8 referee construction is
inestimable in this league (only 3 referees reach ≥20 matches
corpus-wide; identity coverage 29–52%).

The 2025 virgin season is the highest-yellows season in the corpus
(mean 3.71 vs 3.08 in 2024), but under gate discipline that is not
read once the dev gate fails. The headline LL was recomputed
independently from `engine/cards/predictions_dev.csv` and matches
to 1e-6. No virgin outputs exist.
