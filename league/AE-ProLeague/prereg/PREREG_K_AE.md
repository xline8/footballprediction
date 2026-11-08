# Pre-registration — K-AE (AE-ProLeague cards model)

Frozen: 2026-11-10, before any fitting. Branch `build/ae-proleague`.
Design authority: `analysis/MODEL_DESIGN.md` (K-AE); features X5.
Reference: production `model_cards.py` pattern. Engine port pattern:
`league/CY-1Division/engine/cards/` adapted to the stats-feed target.

- **Target: stats-feed yellows** (`yellow_home + yellow_away` from the
  stats feed), frozen with reason: the event feed carries ~0 plain
  Yellow events in 2024/2025 and in the virgin 2025/2026 (0.01/match),
  so an event-unified target cannot exist in the virgin window; the
  stats feed is complete in every season (DATA_UNDERSTANDING §3).
- Primary line **3.5** (dev over-rate 0.523, n=545). Ladder 3.5/4.5/5.5
  reported, gate at 3.5.
- Arms: **Gate Zero only** (X8 referee arm DROPPED in FEATURES:
  referee named in 6/182 virgin matches).
- Warm-up 2021/2022 never scored; awarded matches excluded.
- Dev: scored seasons **2022/2023–2024/2025 (n=545)**. The dev harness
  must not read 2025/2026 or 2026/2027 rows at all.
- Baselines: league base rate (prior-seasons over-3.5 rate); naive
  trailing-10 through the same count distribution.
- Virgin: 2025/2026 (n=182), read ONCE, only if Gate Zero passes dev.
  Calibration = mean P(over 3.5) − actual rate, SE reported.
  2026/2027 NOT read. Halves presentation constant 0.3724.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@3.5 beats BOTH baselines (league base rate; naive trailing-10), else the arm is dead, no virgin read. Virgin legs — (i) LL@3.5 ≤ best baseline's; (ii) calibration |mean P(over 3.5) − actual| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS. Both-pass rule is vacuous (single arm): Gate Zero passes all legs → ships; any leg fails → FAIL, nothing ships.

## Outputs

Engine `engine/cards/`; `results_dev.json`; `results_virgin.json`;
`fitted_params_virgin.json`; on PASS,
`predictions/k_ae_virgin_predictions.csv` (FT ladder; 1H/2H
presentation via frozen cards constant 0.3724). Verdict
`reports/K_AE_VERDICT.md`.
