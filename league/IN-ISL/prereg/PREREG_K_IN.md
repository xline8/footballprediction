# Pre-registration — K-IN (India Indian Super League cards model)

Frozen: 2026-11-09, before any fitting. Branch `build/in-isl`.
Design authority: `analysis/MODEL_DESIGN.md` (K-IN); features X5;
evidence F1/F2/F8. Reference: production `model_cards.py`; J1
analogue: `league/J1/prereg/PREREG_K_J1.md` and its engine
(`league/J1/engine/cards/`) — the architecture (team yellow
ratings + count distribution + naive ensemble structure of the
reference) is carried over in form; read that prereg for the
shared constants and mirror them, changing only league,
seasons and line.

- Target: EVENT-UNIFIED yellows = `yellow_home + yellow_away`
  (event feed, `cards_source='events_unified'` for every IN
  match) — the Phase 1 §3 decision, taken on dev-era evidence
  (stats feed undercounts events in every dev season) before
  any fitting, following the NO-Eliteserien precedent. Primary
  line **4.5** (dev over-rate 0.439, closest to 0.5). Ladder
  3.5/4.5/5.5 reported.
- Arms: **Gate Zero ONLY** (reference unmodified; referee not
  used). The X8 referee arm is NOT built: FEATURES dropped X8
  on coverage alone — referee coverage is 13.5% in the dev
  seasons and 0% in the virgin season, and the most frequent
  named referee has 11 matches, so no strictness trait is even
  computable in IN (contrast J1 0.646, DK 0.561). There is no adopted variant to run; the
  candidate's gate is unchanged and Gate Zero must pass it
  alone. Recorded here, before fitting, so the single-arm form
  cannot be mistaken for a post-hoc simplification.
- Training seed 2021/2022; dev 2022/2023–2024/2025 (n = 419);
  dev harness must not read 2025/2026 / 2026/2027 rows.
- Baselines: league base rate; naive trailing-10 through the
  same count distribution as the reference harness.
- Virgin: 2025/2026 (n = 91), read ONCE, only if Gate Zero
  passes the dev gate. Calibration at 4.5,
  SE = sd(p_i − y_i)/√n.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@4.5 beats BOTH baselines (league base rate; naive trailing-10), else arm dead, no virgin read. Virgin legs — (i) LL@4.5 ≤ best baseline's; (ii) calibration |mean P(over 4.5) − actual| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS. Both-pass rule reduces to: Gate Zero passes ⇒ ships; fails ⇒ FAIL.

Mechanical reading as in PREREG_S_IN (no variant arms exist;
Gate Zero dev failure ⇒ FAIL, virgin NOT read).

## Outputs

Engine `engine/cards/`; `results_dev.json` (+ CSV);
`results_virgin.json`; `fitted_params_virgin.json`; on PASS,
`predictions/k_in_virgin_predictions.csv` (FT ladder 3.5/4.5/5.5;
1H/2H presentation-only via frozen yellows constant 0.366,
lines 1H 0.5/1.5/2.5, 2H 1.5/2.5/3.5). Verdict
`reports/K_IN_VERDICT.md`.
