# Pre-registration — K-EG (EG-PremierLeague cards model)

Frozen: 2026-11-09, before any fitting. Branch `build/eg-premier`.
Design authority: `analysis/MODEL_DESIGN.md` (K-EG); features X5
base (FEATURES.md); evidence EDA F1/F2/F5/F6. Reference: production
`model_cards.py`; SA analogue `league/SA-ProLeague/prereg/PREREG_K_SA.md`
and its engine — copy the architecture (team yellow ratings + count
distribution + naive ensemble structure) and constants, changing
only league, seasons, line and the target source below.
Phase rule (frozen, MODEL_DESIGN): all phases are ordinary rows in
every window; no phase feature anywhere.

- Target: total yellows = `yellow_home + yellow_away`, the STATS
  feed (`yellow_cards` columns; builder sets cards_source='stats'
  for every row). The event feed is NOT the target: Card events are
  largely absent before 2024/2025 (stats−events mean +2.03 / +3.18 /
  +3.77 per match over 2021/2022–2023/2024, exact agreement 45.9% /
  11.0% / 2.3%), while the stats feed is present in ~99–100% of
  matches in every season (EDA F6 / DATA_UNDERSTANDING F3). Event
  columns are audit only. Primary line **3.5** (scored-dev pooled
  2022/2023–2024/2025 over-rate 0.528, closest to 0.5). Ladder
  2.5 / 3.5 / 4.5 reported, gate at 3.5.
- Arms: **Gate Zero only.** X8 (referee covariate) is DROPPED, not
  an arm: referee strictness split-half r = 0.290 in the dev era
  (weak; TR adopted X8 at r = 0.505) and virgin-season referee
  coverage is only 26.7%, so the arm would run mostly on fallback
  in the virgin and could not ship honestly (FEATURES, coordinator
  decision 2026-11-09).
- Walk-forward: per-match, chronological (date, match_id),
  predict-then-update, date-grouped. Warm-up: 2021/2022 updates
  state, never scored (its stats-yellows level, 2.118/match, sits
  far below the scored era — warm-up only is the honest use).
- Dev: scored seasons 2022/2023–2024/2025 (rows with the target
  present; n = 824 of 837). The dev harness must not read
  2025/2026 or 2026/2027 rows at all.
- Baselines: league base rate (prior-seasons over-3.5 rate,
  constant within target season); naive trailing-10 through the
  same count distribution as the reference harness.
- Virgin: 2025/2026 (n = 322), read ONCE, only if Gate Zero passes
  the dev gate, continuing from the dev end state. Calibration =
  actual over-3.5 rate − mean P(over 3.5), SE = sd(y_i − p_i)/√n.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@3.5 beats BOTH baselines (league base rate; naive trailing-10), else arm dead, no virgin read. Virgin legs — (i) LL@3.5 ≤ best baseline's (single-arm candidate: the Gate Zero comparison is vacuous); (ii) calibration |actual − mean P(over 3.5)| ≤ 1.0pp is clean PASS; beyond 1 SE is FAIL, with SE reported, a breach within 1 SE of the 1.0pp boundary is PROVISIONAL PASS. Both-pass rule does not apply (one arm). If Gate Zero fails its dev gate, verdict FAIL, virgin NOT read.

Mechanical reading: Gate Zero passes iff it survives the dev gate
AND passes virgin legs (i)–(ii) (PROVISIONAL counts, recorded as
such); then it ships. Otherwise K-EG verdict is FAIL and nothing
ships.

## Outputs

Engine `engine/cards/`; `results_dev.json` (+ CSV);
`results_virgin.json`; `fitted_params_virgin.json`; on PASS,
`predictions/k_eg_virgin_predictions.csv` (FT ladder 2.5/3.5/4.5;
1H/2H presentation-only via frozen yellows constant 0.3609, lines
1H 0.5/1.5/2.5, 2H 1.5/2.5/3.5). Verdict `reports/K_EG_VERDICT.md`.
