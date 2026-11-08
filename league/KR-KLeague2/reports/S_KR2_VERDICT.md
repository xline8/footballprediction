# S-KR2 verdict — FAIL (dev gate)

Dev pooled at OU 8.5, scored 2023–2024, n=461 (seed 2022):

| arm / baseline | pooled LL | 2023 LL | 2024 LL |
|---|---:|---:|---:|
| Gate Zero | 0.725091 | 0.687864 | 0.762806 |
| X7 box-touch | 0.758035 | 0.684529 | 0.832503 |
| league base rate | 0.698144 | 0.692528 | 0.703834 |
| naive trailing-10 | 0.716716 | 0.687218 | 0.746600 |

Gate Zero beats neither baseline pooled (0.725091 vs base 0.698144
and naive 0.716716), so the candidate FAILS the dev gate and the
virgin (2025) was deliberately NOT read for any arm. Nothing ships.

Pattern worth recording: Gate Zero beats the base rate in 2023
(0.687864 < 0.692528) and collapses in 2024 (0.762806 vs 0.703834).
X7 passes its 2023 sign check but is far worse in 2024, the season
where the box-touch guard actually activates (193/229 matches active
in 2024 vs 18/232 in 2023): in this league the box-touch multiplier
hurts exactly when it has data. The production SOT ratio
construction was already dropped at FEATURES (on-target ratio
split-half r = 0.006 in this league).

All headline LLs were recomputed independently from
`engine/sot/predictions_dev.csv` and match the engine output to
1e-6. No virgin outputs exist.
