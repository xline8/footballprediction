# Pre-registration — T-LV (Latvia Virsliga total shots model)

Frozen: 2026-11-10, before any fitting. Branch `build/lv-virsliga`.
Design authority: `league/LV-Virsliga/analysis/MODEL_DESIGN.md`
(T-LV); features per `analysis/FEATURES.md` (X5 adopted).
Reference: the shots family as frozen for T-J1 in
`league/J1/prereg/PREREG_T_J1.md` (v1 pattern / v2 level layer /
E9 trailing-r) — mirror the three arms' exact constructions,
changing only league, windows and line; sibling analogue
`league/RU-1Division/prereg/PREREG_T_RU1.md`.
Phase rule (frozen): all rows are phase `regular`; no phase
feature anywhere.
Calibration = **actual − predicted** everywhere in this build.

## Virgin-hygiene disclosure

As in PREREG_G_LV: step-1 inventory aggregates (including 2026)
are era facts; no per-match model output and no gate quantity was
computed from 2026 before this freeze. The virgin is NOT burned.

## Era rule (frozen)

Identical to PREREG_S_LV: the total-shots target exists ONLY in
the stats era (seasons 2025+); pre-era rows are never scored and
never update state.

- Target: total shots = `total_shots_home + total_shots_away`
  (stats feed, as published). Primary line **26.5** (2025 dev-era
  over-rate 0.517, closest to 0.5). Ladder 25.5/26.5/27.5
  reported, gate at 26.5.
- Arms: **A** v1 pattern (ratings + NB + naive ensemble);
  **B** v2 pattern (+ level layer); **C** E9 (NB r from a
  trailing window, league-level analogue).
- Walk-forward: per-match, chronological (date, match_id),
  predict-then-update, date-grouped. Warm-up, dev, virgin windows
  and state rules exactly as PREREG_S_LV (dev scored n = 133;
  virgin n = 179, continuing from dev end state).
- Baselines: league base rate; naive trailing-10.
- Virgin: 2026 (n = 179), read ONCE, only for dev-passing arms.
  Calibration at 26.5 = actual − mean predicted,
  SE = sd(y_i − p_i)/√n.
- Halves: FT + 1H/2H via frozen total-shots constant 0.4685 from
  2025 period splits (presentation only; true per-match share
  variance = 0).

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@26.5 beats BOTH baselines (league base rate; naive trailing-10), else arm dead, no virgin read. Virgin legs — (i) LL@26.5 ≤ the reference arm's (arm A if it passes dev; otherwise the dev-passing arm with the lowest pooled dev LL) and ≤ best baseline's; (ii) calibration |actual − mean P(over 26.5)| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev sign check for both-pass: with a single scored dev window in this league, a variant's pooled dev LL@26.5 must be ≤ the reference arm's. Both-pass: among passing arms, lower pooled virgin LL ships; one → ships; none → FAIL.

Mechanical reading as in PREREG_S_LV (ties → simpler arm A before
B before C). If arm A fails its dev gate AND no variant passes
dev, verdict FAIL, virgin NOT read. If arm A fails dev but a
variant passes, the variant alone is read on the virgin and must
pass legs (i)–(ii) against the baselines to ship.

## Outputs

Engine `league/LV-Virsliga/engine/total_shots/`;
`results_dev.json` (+ `predictions_dev.csv`);
`results_virgin.json`; `fitted_params_virgin.json`; on PASS,
`predictions/t_lv_virgin_predictions.csv` (FT ladder
25.5/26.5/27.5; 1H/2H presentation via frozen total-shots
constant 0.4685). Verdict `reports/T_LV_VERDICT.md`.
Production code untouched. No push. No merge.
