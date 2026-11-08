# Pre-registration — S-QASD (QA-SecondDivision shots-on-target model)

Frozen: 2026-11-10, before any fitting. Branch `build/qa-seconddiv`.
Design authority: `analysis/MODEL_DESIGN.md` (S-QASD); features X5 base
(FEATURES.md); evidence F1/F2/F3/F5/F7. Reference: production
`model_sot.py` v5; SA analogue `PREREG_S_SAFD.md` — the v5 architecture
constants there are carried over verbatim (ridge lambda = 100,
HL = 365, lazy refit 7 days, total-shots ratings prior K = 8,
Beta-Binomial prior P = 200, ensemble 50/50 with naive trailing-10,
NB size r = 79.94 frozen). Engine port:
`league/SCO-Premiership/engine/sot/` (and `league/SA-ProLeague/
engine/sot/`). X4/X6 are NOT arms: no shotmap and no xGOT exist in
any era (FEATURES.md). Phase rule (frozen): single phase `regular`
throughout; only played rows are used. Calibration is defined as
**actual − predicted** (mean P(over) − actual rate, SE reported)
everywhere in this build.

- Target: total SOT = `ShotsOnTarget_home + ShotsOnTarget_away`
  (stats feed). Primary line **8.5** (dev over-rate 0.482, closest
  to 0.5). Ladder 7.5 / 8.5 / 9.5 reported, gate at 8.5.
- Arms: **Gate Zero** (v5 unmodified); **RS** (Gate Zero with the
  BB prior raised P = 200 → 20,000).
- Walk-forward: per-match, chronological (date, match_id),
  predict-then-update, date-grouped (same-date matches never see
  each other). Warm-up: first 28 matches of 2025/2026 in (date,
  match_id) order (rounds 1–7, never scored); scored: the remaining
  **28 matches** (rounds 8–14). Fit history for scored matches is all
  stats matches strictly before each scored date — including the
  2024/2025 stats-era rounds 6–14 (38 matches). The dev harness must
  not read 2026/2027 rows at all.
- Dev: scored block n = 28. Small-n note, stated before fitting: at
  n = 28 the dev LL comparisons are noisy; the gate is applied
  mechanically regardless.
- Baselines: league base rate (over-8.5 rate of all matches strictly
  before each scored date, expanding); naive trailing-10 through the
  same NB.
- Virgin: 2026/2027 partial (n = 29, rounds 1–6, TRANSITIONAL),
  read ONCE, only for dev-passing arms, continuing from the dev end
  state. Calibration = actual − mean P(over 8.5),
  SE = sd(y_i − p_i)/√n. Small-n note, stated before reading: at
  n = 29 the calibration SE is ≈9pp, so the ≤1 SE provisional band
  is wide; the gate is applied mechanically regardless, and the
  verdict records the virgin as TRANSITIONAL with a confirmatory
  read at season end.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@8.5 beats BOTH baselines (league base rate; naive trailing-10), else arm dead, no virgin read. Virgin legs — (i) LL@8.5 ≤ Gate Zero's and ≤ best baseline's; (ii) calibration |actual − mean P(over 8.5)| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev sign check for both-pass. Both-pass: both → lower pooled virgin LL ships; one → ships; none → FAIL.

Mechanical reading: an arm passes iff it survives the dev gate AND
passes virgin legs (i)–(ii) (PROVISIONAL counts) AND, for variants,
leg (iii) — variant pooled dev LL@8.5 ≤ Gate Zero's pooled dev
LL@8.5. Ties → simpler arm (Gate Zero before RS). If Gate Zero fails
its dev gate, RS is moot, verdict FAIL, virgin NOT read.

## Outputs

Engine `engine/sot/`; `results_dev.json` (+ CSV);
`results_virgin.json`; `fitted_params_virgin.json`; on PASS,
`predictions/s_qasd_virgin_predictions.csv` (shipped arm; FT ladder
7.5/8.5/9.5 ensemble probabilities; 1H/2H presentation-only via
frozen SOT constant 0.4194). Verdict `reports/S_QASD_VERDICT.md`.
