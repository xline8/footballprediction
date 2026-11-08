# Pre-registration — T-MA (Morocco Botola Pro total shots model)

Frozen: 2026-11-10, before any fitting. Branch `build/ma-botola`.
Design authority: `league/MA-BotolaPro/analysis/MODEL_DESIGN.md`
(T-MA); features per `analysis/FEATURES.md` (X5 adopted).
Reference: the shots family as frozen for T-J1 in
`league/J1/prereg/PREREG_T_J1.md` (v1 pattern / v2 level layer /
E9 trailing-r) — mirror the three arms' exact constructions,
changing only league, windows and line; sibling analogue
`league/RU-1Division/prereg/PREREG_T_RU1.md`.
Phase rule (frozen): all rows are phase `regular`; no phase
feature anywhere.
Calibration = **actual − predicted** everywhere in this build.

## Era rule (frozen)

Identical to PREREG_S_MA: the total-shots target exists ONLY in
the rich era (date >= 2024-11-01); pre-era rows and rich-era rows
without a stats block are never scored and never update state.

- Target: total shots = `total_shots_home + total_shots_away`
  (stats feed, as published). Primary line **16.5** (rich dev-era
  over-rate 0.518, closest to 0.5). Ladder 15.5/16.5/17.5
  reported, gate at 16.5.
- Arms: **A** v1 pattern (ratings + NB + naive ensemble);
  **B** v2 pattern (+ level layer); **C** E9 (NB r from a
  trailing window, league-level analogue).
- Walk-forward: per-match, chronological (date, match_id),
  predict-then-update, date-grouped. Warm-up, dev, virgin windows
  and state rules exactly as PREREG_S_MA (dev scored stats
  n = 109; virgin stats n = 226, continuing from dev end state).
- Baselines: league base rate; naive trailing-10.
- Virgin: 2025/2026 (stats rows n = 226), read ONCE, only for
  dev-passing arms. Calibration at 16.5 = actual − mean
  predicted, SE = sd(y_i − p_i)/√n.
- Halves: NONE — no period splits exist in this league; FT
  presentation only.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@16.5 beats BOTH baselines (league base rate; naive trailing-10), else arm dead, no virgin read. Virgin legs — (i) LL@16.5 ≤ the reference arm's (arm A if it passes dev; otherwise the dev-passing arm with the lowest pooled dev LL) and ≤ best baseline's; (ii) calibration |actual − mean P(over 16.5)| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev sign check for both-pass: with a single scored dev window in this league, a variant's pooled dev LL@16.5 must be ≤ the reference arm's. Both-pass: among passing arms, lower pooled virgin LL ships; one → ships; none → FAIL.

Mechanical reading as in PREREG_S_MA (ties → simpler arm A before
B before C). If arm A fails its dev gate AND no variant passes
dev, verdict FAIL, virgin NOT read. If arm A fails dev but a
variant passes, the variant alone is read on the virgin and must
pass legs (i)–(ii) against the baselines to ship.

## Outputs

Engine `league/MA-BotolaPro/engine/total_shots/`;
`results_dev.json` (+ `predictions_dev.csv`);
`results_virgin.json`; `fitted_params_virgin.json`; on PASS,
`predictions/t_ma_virgin_predictions.csv` (FT ladder
15.5/16.5/17.5; NO halves — FT only). Verdict
`reports/T_MA_VERDICT.md`. Production code untouched. No push.
No merge.
