# C-KR2 verdict — FAIL (dev gate)

Dev pooled at OU 8.5, scored 2023–2024, n=461 (seed 2022):

| arm / baseline | pooled LL | 2023 LL | 2024 LL |
|---|---:|---:|---:|
| Gate Zero | 0.716018 | 0.681691 | 0.750795 |
| X7 box-touch | 0.735672 | 0.682105 | 0.789940 |
| league base rate | 0.696015 | 0.693748 | 0.698312 |
| naive trailing-10 | 0.734307 | 0.701857 | 0.767183 |

Gate Zero beats the naive baseline (0.716018 < 0.734307) but not the
league base rate (0.696015); the dev gate requires both, so the
candidate FAILS and the virgin (2025) was deliberately NOT read for
any arm. Nothing ships.

Same shape as SOT: a clean 2023 (0.681691, better than both
baselines) reversed in 2024 (0.750795). X7 is worse than Gate Zero
in both seasons pooled and much worse in 2024 (0.789940), when the
min-8 guard activates for 193/229 matches (vs 18/232 in 2023).

All headline LLs were recomputed independently from
`engine/corners/predictions_dev.csv` and match to 1e-6. No virgin
outputs exist.
