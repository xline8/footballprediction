# Verdict — T-AE (AE-ProLeague total shots)

**PASS (PROVISIONAL, calibration) — arm C (E9 trailing-200 r) SHIPS.**

Dev LL@25.5 (n=545, recomputed exactly): A 0.682015, B 0.682259,
C 0.681906; baselines: league base rate 0.696534, naive 0.695637.
All three arms pass the dev gate. Sign checks vs A: B 2/3, C 2/3.

Virgin 2025/2026 (n=182, recomputed exactly from
`engine/total_shots/predictions_virgin.csv`):

| Arm | LL@25.5 | Mean P(over) | Actual | Breach (pred − actual) | 1 SE | Legs |
|---|---|---|---|---|---|---|
| A (v1) | 0.687007 | 0.4434 | 0.4121 | +3.13pp | 3.68pp | (i) PASS, (ii) PROVISIONAL |
| B (v2 level) | 0.687541 | 0.4317 | 0.4121 | +1.96pp | 3.68pp | (i) **FAIL** (> arm A), (ii) PROVISIONAL |
| C (E9) | **0.686302** | 0.4431 | 0.4121 | +3.10pp | 3.67pp | (i) PASS, (ii) PROVISIONAL, (iii) PASS |
| League base rate | 0.691060 | — | — | +6.87pp | — | — |
| Naive trailing-10 | 0.716627 | — | — | — | — | — |

Both-pass rule: A and C pass all legs; the lower pooled virgin LL
ships → **arm C**. Calibration is provisional, not clean: the virgin
season ran cold on shots (24.48/match vs 25.67–26.87 dev), so every
arm overstates the over-rate; C's +3.10pp breach sits inside 1 SE
(3.67pp) of the 1pp boundary.

Ships: `league/AE-ProLeague/predictions/t_ae_virgin_predictions.csv`
(arm C, 182 rows; FT columns are the engine's own virgin export;
1H/2H columns added presentation-only from the same per-match
predictions via the frozen constant 0.4608 and each row's trailing r).
Fitted params: `engine/total_shots/fitted_params_virgin.json`.
