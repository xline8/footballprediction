# Pre-registration — C-AE (AE-ProLeague corners model)

Frozen: 2026-11-10, before any fitting. Branch `build/ae-proleague`.
Design authority: `analysis/MODEL_DESIGN.md` (C-AE); features X5, X9
(Gate Zero), X7 (variant). Reference: production `model_corners_v3`
pattern (team corner ratings + NB total, territorial multiplier).
Engine port pattern: `league/CY-1Division/engine/corners/` extended
with the box-touch covariate set (X7 exists in this league; CY lacked
it).

- Target: total corners (stats feed, 100% every season). Primary line
  **10.5** (dev over-rate 0.439, n=545, closest to 0.5). Ladder
  9.5/10.5/11.5 reported, gate at 10.5.
- Arms: **Gate Zero** (multiplier on X9: possession + big-chance
  trailing rates, production form); **X7** (multiplier on X7:
  opp-box touches for/against trailing means, same multiplier form,
  min-8 window rule, else multiplier 1.0).
- Walk-forward: season-blocked expanding fit as in the reference port;
  warm-up 2021/2022 never scored; awarded matches excluded.
- Dev: scored seasons **2022/2023–2024/2025 (n=545)**. The dev harness
  must not read 2025/2026 or 2026/2027 rows at all.
- Baselines: league base rate (prior-seasons over-10.5 rate); naive
  trailing-10 through the same NB.
- Virgin: 2025/2026 (n=182), read ONCE, only for dev-passing arms.
  Calibration = mean P(over 10.5) − actual rate, SE reported.
  2026/2027 NOT read.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@10.5 beats BOTH baselines (league base rate; naive trailing-10), else the arm is dead, no virgin read. Virgin legs — (i) LL@10.5 ≤ Gate Zero's AND ≤ best baseline's (Gate Zero: ≤ best baseline's); (ii) calibration |mean P(over 10.5) − actual| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev per-season sign check for both-pass (variant dev LL@10.5 ≤ Gate Zero's in ≥2 of 3 dev seasons). Both-pass: both → lower pooled virgin LL ships; one → ships; none → FAIL.

Mechanical reading: an arm passes iff it survives the dev gate AND
passes virgin legs (i)–(ii) (PROVISIONAL counts, recorded as such) AND,
for the variant, leg (iii). Ties → simpler arm (Gate Zero before X7).
Gate Zero dev failure ⇒ variants moot, FAIL, virgin NOT read.

## Outputs

Engine `engine/corners/`; `results_dev.json`; `results_virgin.json`;
`fitted_params_virgin.json`; on PASS,
`predictions/c_ae_virgin_predictions.csv` (FT ladder; 1H/2H
presentation via frozen corners constant 0.4801). Verdict
`reports/C_AE_VERDICT.md`.
