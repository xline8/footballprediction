# Pre-registration — S-HR (HR-HNL shots-on-target model)

Frozen: 2026-11-10, before any fitting. Branch `build/hr-hnl`.
Design authority: `analysis/MODEL_DESIGN.md` (S-HR); feature X5; evidence F1/F2.
Reference: production `model_sot.py` v5 with the programme-frozen constants
(ridge lambda = 100, HL = 365, lazy refit 7 days, total-shots ratings prior
K = 8, Beta-Binomial prior P = 200, ensemble 50/50 with naive trailing-10,
NB size r = 79.94 frozen). NO X4 arm: the feed has no shotmap in any season
(FEATURES.md). NO X6 arm: no xGOT.

- Target: total SOT = `ShotsOnTarget_home + ShotsOnTarget_away` (stats feed).
  Primary line **7.5** (dev over-rate 0.552). Ladder 6.5 / 7.5 / 8.5, gate at 7.5.
- Arms: **Gate Zero** (v5 unmodified); **RS** (Gate Zero with BB prior P = 200 → 20,000).
- Walk-forward per-match chronological (date, match_id), predict-then-update,
  date-grouped. Warm-up: 2021/2022 (180 stats rows) updates state, never scored.
- Dev: scored seasons 2022/2023–2024/2025 (n = 540 stats rows). The dev harness must not
  read 2025/2026 rows at all.
- Baselines: league base rate (prior-seasons over-7.5 rate); naive trailing-10 through the same NB.
- Virgin: 2025/2026 (n = 180 stats rows of 180), read ONCE, only for dev-passing arms.
  Calibration = mean P(over 7.5) − actual rate, SE = sd(p_i − y_i)/√n.
- Frozen note: the 2024/2025 dev season is a low-SOT outlier (7.478/match)
  and the 2025/2026 virgin level (8.156) sits above the dev mean — recorded
  in EDA F1 before fitting; no arm or window changes follow.

## GATE LEGS (verbatim, frozen)
Dev gate — pooled dev LL at the primary line beats BOTH baselines (league base rate; naive trailing-10), else arm dead, no virgin read. Virgin legs — (i) LL ≤ Gate Zero's and ≤ best baseline's; (ii) calibration |mean P(over) − actual| ≤ 1.0pp clean PASS, breach within 1 SE = PROVISIONAL PASS, else FAIL; (iii) dev per-season sign check for both-pass (variant dev LL ≤ Gate Zero's in at least half the dev seasons — ≥2 of 3). Both-pass: lower pooled virgin LL ships; one → ships; none → FAIL. Ties → simpler arm. If Gate Zero fails its dev gate, variants are moot, verdict FAIL, virgin NOT read.

## Outputs
Engine `engine/sot/`; `results_dev.json` (+ CSV); `results_virgin.json`;
`fitted_params_virgin.json`; on PASS, `predictions/s_hr_virgin_predictions.csv`
(FT ladder + 1H/2H presentation via frozen SOT constant 0.4729). Verdict `reports/S_HR_VERDICT.md`.
