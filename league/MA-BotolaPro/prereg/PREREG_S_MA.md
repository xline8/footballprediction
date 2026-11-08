# Pre-registration — S-MA (Morocco Botola Pro SOT model)

Frozen: 2026-11-10, before any fitting. Branch `build/ma-botola`.
Design authority: `league/MA-BotolaPro/analysis/MODEL_DESIGN.md`
(S-MA); features per `analysis/FEATURES.md` (X5 adopted; X4/X6
DROPPED — no shotmap exists in this league). Reference: production
SOT v5 in `model_sot.py`; sibling analogue:
`league/RU-1Division/prereg/PREREG_S_RU1.md` — mirror its frozen
constants (joint Poisson ridge lambda = 100, HL = 365, lazy refit
7 days, total-shots ratings prior K = 8, Beta-Binomial prior
P = 200, ensemble 50/50 with naive trailing-10, NB size r = 79.94),
changing only league, windows, line and the era rule below.
Phase rule (frozen): all rows are phase `regular`; no phase
feature anywhere.
Calibration = **actual − predicted** everywhere in this build.

## Era rule (frozen, from the payload-verified era map)

The SOT target exists ONLY in the rich era (matches dated
>= 2024-11-01). Rows before that date do not exist for this market:
never scored, never update target state. Rows within the rich era
without a stats block (12 of 176 in 2024/2025; 14 of 240 in the
virgin) are likewise never scored and never update state.

- Target: total SOT = `ShotsOnTarget_home + ShotsOnTarget_away`
  (stats feed). Primary line **7.5** (rich dev-era over-rate 0.433;
  the 6.5 over-rate is 0.567 — 7.5 frozen as the higher line at
  equal distance). Ladder 6.5 / 7.5 / 8.5 reported, gate at 7.5.
- Arms: **Gate Zero** (v5 unmodified); **RS** (Gate Zero with the
  BB prior raised P = 200 → 20,000).
- Walk-forward: per-match, chronological (date, match_id),
  predict-then-update, date-grouped (same-date matches never see
  each other). Warm-up: rich-era matches 2024-11-01 – 2024-12-31
  update state, never scored (55 stats matches).
- Dev: scored rich-era matches 2025-01-01 – 2025-05-12 (stats
  n = 109). The dev harness must not read 2025/2026 or 2026/2027
  rows at all.
- Baselines: league base rate (rich warm-up era over-7.5 rate,
  constant within the scored window); naive trailing-10 through
  the same NB.
- Virgin: 2025/2026 (stats rows n = 226), read ONCE, only for
  dev-passing arms, continuing from the dev end state (per-match
  walk-forward through the virgin, rich-era rows only).
  Calibration = actual rate − mean P(over 7.5), SE =
  sd(y_i − p_i)/√n.
- Halves: NONE. This league's feed has no period splits for SOT
  and no event source exists — FT presentation only
  (halves_share_1h: null, RU-1Division precedent).

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@7.5 beats BOTH baselines (league base rate; naive trailing-10), else arm dead, no virgin read. Virgin legs — (i) LL@7.5 ≤ Gate Zero's and ≤ best baseline's; (ii) calibration |actual − mean P(over 7.5)| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev sign check for both-pass: with a single scored dev window in this league, the variant's pooled dev LL@7.5 must be ≤ Gate Zero's. Both-pass: both → lower pooled virgin LL ships; one → ships; none → FAIL.

Mechanical reading: an arm passes iff it survives the dev gate AND
passes virgin legs (i)–(ii) (PROVISIONAL counts) AND, for variant
arms, leg (iii). Ties → simpler arm (Gate Zero before RS). If Gate
Zero fails its dev gate, variants are moot, verdict FAIL, virgin
NOT read.

## Outputs

Engine `league/MA-BotolaPro/engine/sot/`; `results_dev.json`
(+ `predictions_dev.csv`); `results_virgin.json`;
`fitted_params_virgin.json`; on PASS,
`predictions/s_ma_virgin_predictions.csv` (shipped arm; FT ladder
6.5/7.5/8.5 ensemble probabilities; NO halves columns — FT only).
Verdict `reports/S_MA_VERDICT.md`. Production code untouched.
No push. No merge.
