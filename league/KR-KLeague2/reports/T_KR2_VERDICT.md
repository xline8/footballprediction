# T-KR2 verdict — FAIL (dev gate)

Dev pooled at OU 24.5, scored 2023–2024, n=461 (seed 2022):

| arm / baseline | pooled LL | 2023 LL | 2024 LL |
|---|---:|---:|---:|
| Gate Zero | 0.723430 | 0.676469 | 0.771007 |
| X7 box-touch | 0.783080 | 0.679572 | 0.887943 |
| E9 trailing-200 r | 0.721798 | 0.676469 | 0.767720 |
| league base rate | 0.693141 | 0.692803 | 0.693483 |
| naive trailing-10 | 0.735176 | 0.695301 | 0.775572 |

Gate Zero beats the naive baseline but not the league base rate
(0.723430 vs 0.693141), so the candidate FAILS the dev gate and the
virgin (2025) was deliberately NOT read for any arm. Nothing ships.

E9 is the best model arm pooled (0.721798) but still loses to the
base rate; in 2023 it is numerically identical to Gate Zero (the
2022 seed window is 219 matches, so the trailing-200 r estimate
nearly coincides with the full-window one). X7 is the worst arm in
the build (0.887943 in 2024, when its guard activates for 193/229
matches).

Implementation disclosure (audit, fixed before these results): the
first count-engine implementation (i) ran the goals-scale IPF step
on count targets, which oscillates (train totals swung 234 → 3 →
174), and (ii) left the ratings uncentred, so teams with no history
— more than half of all 2023 fixtures involve an entering team —
were predicted at ~6.6 total shots against an actual 24.0. The
shipped engine uses a damped step (0.25 × 100) and league-centred
ratings; published mus average 24.4 against an actual 24.3. The
frozen model family, windows, lines and gates were not changed.
All headline LLs were recomputed independently from
`engine/total_shots/predictions_dev.csv` and match to 1e-6. No
virgin outputs exist.
