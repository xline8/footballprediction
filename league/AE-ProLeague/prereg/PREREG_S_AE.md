# Pre-registration — S-AE (AE-ProLeague shots-on-target model)

Frozen: 2026-11-10, before any fitting. Branch `build/ae-proleague`.
Design authority: `analysis/MODEL_DESIGN.md` (S-AE); features X5.
Reference: production `model_sot.py` v5 (ridge lambda=100, HL=365, lazy
refit 7 days, total-shots ratings prior K=8, Beta-Binomial prior P=200,
ensemble 50/50 with naive trailing-10, NB size r=79.94 frozen). Engine
port pattern: `league/CY-1Division/engine/sot/`. No X4/X6 arms exist
(no shotmap in this league).

- Target: total SOT = `ShotsOnTarget_home + ShotsOnTarget_away` (stats
  feed, 100% every season). Primary line **9.5** (dev over-rate 0.446,
  n=545, closest to 0.5). Ladder 8.5/9.5/10.5 reported, gate at 9.5.
- Arms: **Gate Zero** (v5 unmodified); **RS** (BB prior P=200 → 20,000).
- Walk-forward: per-match, chronological (date, match_id),
  predict-then-update, date-grouped. Warm-up: 2021/2022 updates state,
  never scored. Awarded matches excluded from state and scoring.
- Dev: scored seasons **2022/2023–2024/2025 (n=545)**. The dev harness
  must not read 2025/2026 or 2026/2027 rows at all.
- Baselines: league base rate (prior-seasons over-9.5 rate, constant
  within target season); naive trailing-10 through the same NB.
- Virgin: 2025/2026 (n=182), read ONCE, only for dev-passing arms,
  continuing from the dev end state. Calibration = mean P(over 9.5) −
  actual rate, SE = sd(p_i − y_i)/√n. 2026/2027 NOT read.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@9.5 beats BOTH baselines (league base rate; naive trailing-10), else arm dead, no virgin read. Virgin legs — (i) LL@9.5 ≤ Gate Zero's and ≤ best baseline's; (ii) calibration |mean P(over 9.5) − actual| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev per-season sign check for both-pass. Both-pass: both → lower pooled virgin LL ships; one → ships; none → FAIL.

Mechanical reading: an arm passes iff it survives the dev gate AND
passes virgin legs (i)–(ii) (PROVISIONAL counts) AND, for variants,
leg (iii) — variant dev LL@9.5 ≤ Gate Zero's in at least 2 of 3 dev
seasons. Ties → simpler arm (Gate Zero before RS). If Gate Zero fails
its dev gate, variants are moot, verdict FAIL, virgin NOT read.

## Outputs

Engine `engine/sot/`; `results_dev.json`; `results_virgin.json`;
`fitted_params_virgin.json`; on PASS,
`predictions/s_ae_virgin_predictions.csv` (FT ladder 8.5/9.5/10.5
ensemble probabilities; 1H/2H ladders presentation-only via frozen SOT
constant 0.4618, NB r=79.94, lines 1H 3.5/4.5/5.5, 2H 4.5/5.5/6.5).
Verdict `reports/S_AE_VERDICT.md`.
