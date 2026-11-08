# Pre-registration — S-TH (Thailand Thai League 1 shots-on-target model)

Frozen: 2026-11-10, before any fitting. Branch `build/th-thaileague`.
Design authority: `analysis/MODEL_DESIGN.md` (S-TH); features X5 base
(FEATURES.md); evidence EDA reliabilities (SOT for 0.694 / against
0.594). Reference: production `model_sot.py` v5; sibling analogue
`league/RU-1Division/prereg/PREREG_S_RU1.md` — the v5 architecture
constants there are carried over verbatim (ridge lambda = 100,
HL = 365, lazy refit 7 days, total-shots ratings prior K = 8,
Beta-Binomial prior P = 200, ensemble 50/50 with naive trailing-10,
NB size r = 79.94 frozen). X4/X6 are NOT arms: shotmap exists only
from the virgin season.
Phase rule (frozen): all rows are phase `regular`; no phase feature.
Calibration = **actual − predicted** everywhere in this build.

- Target: total SOT = `ShotsOnTarget_home + ShotsOnTarget_away`
  (stats feed). Primary line **9.5** (scored-dev over-rate 0.473,
  closest to 0.5; the 8.5 over-rate is 0.602). Ladder 8.5 / 9.5 /
  10.5 reported, gate at 9.5.
- Arms: **Gate Zero** (v5 unmodified); **RS** (Gate Zero with the
  BB prior raised P = 200 → 20,000).
- Walk-forward: per-match, chronological (date, match_id),
  predict-then-update, date-grouped (same-date matches never see
  each other). Warm-up: 2022/2023 (first stats season) updates state,
  never scored. Rows without stats are never scored and never update
  the target state.
- Dev: scored seasons 2023/2024–2024/2025 (stats rows n = 480).
  The dev harness must not read 2025/2026 or 2026/2027 rows at all.
- Baselines: league base rate (prior-seasons over-9.5 rate, constant
  within target season); naive trailing-10 through the same NB.
- Virgin: 2025/2026 (stats rows n = 240), read ONCE, only for
  dev-passing arms, continuing from the dev end state. Calibration
  = actual rate − mean P(over 9.5), SE = sd(y_i − p_i)/√n.
- Halves: 1H/2H presentation via the frozen SOT constant 0.4447
  (period splits exist from 2023/2024; FEATURES).

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@9.5 beats BOTH baselines (league base rate; naive trailing-10), else arm dead, no virgin read. Virgin legs — (i) LL@9.5 ≤ Gate Zero's and ≤ best baseline's; (ii) calibration |actual − mean P(over 9.5)| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev per-season sign check for both-pass. Both-pass: both → lower pooled virgin LL ships; one → ships; none → FAIL.

Mechanical reading: an arm passes iff it survives the dev gate AND
passes virgin legs (i)–(ii) (PROVISIONAL counts) AND, for variants,
leg (iii) — variant dev LL@9.5 ≤ Gate Zero's in at least half of the
dev seasons (≥1 of 2). Ties → simpler arm (Gate Zero before RS).
If Gate Zero fails its dev gate, variants are moot, verdict FAIL,
virgin NOT read.

## Outputs

Engine `engine/sot/`; `results_dev.json` (+ CSV);
`results_virgin.json`; `fitted_params_virgin.json`; on PASS,
`predictions/s_th_virgin_predictions.csv` (shipped arm; FT ladder
8.5/9.5/10.5 ensemble probabilities + 1H/2H presentation via the
frozen constant 0.4447). Verdict `reports/S_TH_VERDICT.md`.
