# Pre-registration — S-SE2 (SE-Superettan shots-on-target model)

Frozen: 2026-11-10, before any fitting. Branch `build/se-superettan`.
Design authority: `analysis/MODEL_DESIGN.md` (S-SE2); feature X5; evidence F1/F2.
Reference: production `model_sot.py` v5 with the SE/J1-frozen constants
(ridge lambda = 100, HL = 365, lazy refit 7 days, total-shots ratings prior
K = 8, Beta-Binomial prior P = 200, ensemble 50/50 with naive trailing-10,
NB size r = 79.94 frozen). NO X4 arm: the feed has no shotmap in any season
(FEATURES.md). NO X6 arm: no xGOT.

- Target: total SOT = `ShotsOnTarget_home + ShotsOnTarget_away` (stats feed).
  Primary line **9.5** (dev over-rate 0.511). Ladder 8.5 / 9.5 / 10.5, gate at 9.5.
- Arms: **Gate Zero** (v5 unmodified); **RS** (Gate Zero with BB prior P = 200 → 20,000).
- Walk-forward per-match chronological (date, match_id), predict-then-update,
  date-grouped. Warm-up: 2022 (first stats season) updates state, never scored.
- Dev: scored seasons 2023–2025 (n = 710 stats rows). The dev harness must not
  read 2026 rows at all.
- Baselines: league base rate (prior-seasons over-9.5 rate); naive trailing-10 through the same NB.
- Virgin: 2026 (n = 237 stats rows of 240), read ONCE, only for dev-passing arms.
  Calibration = mean P(over 9.5) − actual rate, SE = sd(p_i − y_i)/√n.
- Frozen note: the 2025 SOT regime spike and the low 2026 SOT level are recorded
  in EDA F1 before fitting; no arm or window changes follow from them.

## GATE LEGS (verbatim, frozen)
Dev gate — pooled dev LL at the primary line beats BOTH baselines (league base rate; naive trailing-10), else arm dead, no virgin read. Virgin legs — (i) LL ≤ Gate Zero's and ≤ best baseline's; (ii) calibration |mean P(over) − actual| ≤ 1.0pp clean PASS, breach within 1 SE = PROVISIONAL PASS, else FAIL; (iii) dev per-season sign check for both-pass (variant dev LL ≤ Gate Zero's in at least half the dev seasons). Both-pass: lower pooled virgin LL ships; one → ships; none → FAIL. Ties → simpler arm. If Gate Zero fails its dev gate, variants are moot, verdict FAIL, virgin NOT read.

## Outputs
Engine `engine/sot/`; `results_dev.json` (+ CSV); `results_virgin.json`;
`fitted_params_virgin.json`; on PASS, `predictions/s_se2_virgin_predictions.csv`
(FT ladder only — SOT is FT-only in this league, halves share null). Verdict `reports/S_SE2_VERDICT.md`.
