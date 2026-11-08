# G-RL2 verdict

Preregistration: `prereg/PREREG_G_RO-LigaII.md` (commit 4a8bb013, before
any fitting). Calibration is predicted − actual. Virgin 2025/2026 was
NOT read for G-RL2: both arms failed the dev gate, and the prereg states
that if Gate Zero fails its own dev gate, variants are moot, verdict
FAIL, virgin NOT read.

## Dev

| arm / baseline | LL 1X2 | RPS | OU2.5 LL |
|---|---:|---:|---:|
| Gate Zero pooled | 1.059351 | 0.221992 | 0.708297 |
| SHRINK pooled | 1.059351 | 0.221992 | 0.708297 |
| climatology pooled | 1.079497 | 0.229017 | 0.687443 |

Per-season Gate Zero model LL (2022/23, 2023/24, 2024/25) is 1.055880,
1.057519, 1.064656; climatology is 1.081607, 1.080084, 1.076802. The
model beats climatology on 1X2 LL in all three dev seasons, and on RPS
in all three (model 0.221464, 0.219013, 0.225499 vs climatology
0.228826, 0.226389, 0.231835). On OU2.5 LL the model loses in all three
(model 0.701592, 0.696867, 0.726432 vs base rate 0.691748, 0.682249,
0.688333). SHRINK is identical in every season: the shrinkage
adjustment changed 0 of 1,572 scored lambdas (no team ever has 1–5
prior in-league matches at a season start — prior counts are 0 or
≥25 — as pre-registered).

## Gate arithmetic

- Dev gate, Gate Zero: **FAIL** — pooled 1X2 LL 1.059351 beats
  climatology 1.079497 (by 0.020146); RPS 0.221992 beats 0.229017 (by
  0.007025); but OU2.5 LL 0.708297 is worse than the base-rate 0.687443
  (by 0.020854). The gate requires all three legs, so the arm is dead
  at dev.
- Dev gate, SHRINK: **FAIL** for the same numbers (identical results).

G-RL2 verdict: **FAIL (dev gate); nothing ships**. No virgin read, no
predictions CSV, no fitted virgin params, no `results_virgin.json`.

Diagnosis (not a rescue): the model's mean predicted over-2.5 rate sits
at ≈0.407 in every dev season (0.4071, 0.4084, 0.4066) while the actual
over-rate swings with the league's scoring level (0.4733, 0.3779,
0.4504) — the time-decayed DC anchors totals near the trailing level
and cannot follow the season-to-season swing (2.485, 2.271, 2.370
goals/match across the dev seasons). 1X2 and RPS still beat
climatology, so the failure is specific to the totals leg. No rescue
arm was invented.

Verification: coordinator re-ran the dev runner and reproduced
`results_dev.csv` byte-identically; recomputed the pooled climatology
numbers independently from raw counts (LL 1.079497, RPS 0.229017, OU
0.687443 — exact to 6 decimals); replayed production `model_v2.DC`
on 2022/2023 and 2024/2025 (LL/RPS/OU exact to 6 decimals);
`dc.py` is byte-identical to the RO-LigaI engine; SHRINK-vs-Gate-Zero
max per-match probability difference is 0.0 across all 786 dev
matches. Zero xG values were consumed (no xG columns exist).
