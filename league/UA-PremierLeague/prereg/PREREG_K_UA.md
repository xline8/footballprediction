# Pre-registration — K-UA (Ukraine Premier League cards model)

Frozen: 2026-11-10, before any fitting. Branch `build/ua-premier`.
Design authority: `analysis/MODEL_DESIGN.md` (K-UA); features X5.
Reference: production `model_cards.py`; sibling analogue
`league/RU-1Division/prereg/PREREG_K_RU1.md` (same event-target
position). Era restriction: 2022/2023+ only. Calibration =
actual − predicted.

- Target: total **event-unified yellows** = `ev_yellow_home +
  ev_yellow_away` (direct Yellow + YellowRed-once). Target-source
  decision (frozen here, before fitting): the stats feed carries
  NO yellow_cards key in any of the 1,191 payloads, so no stats
  target exists; the event feed is the only possible target in
  dev AND virgin (RU-1Division precedent; the TH/ZA era-flip
  artefact cannot arise — there is no second source to flip).
  Primary line **4.5** (dev over-rate 0.4262; 3.5 is 0.6076).
  Ladder 3.5 / 4.5, gate at 4.5.
- Arms: **Gate Zero only**. X8 is NOT an arm: referee text is
  empty in 1,191/1,191 payloads (FEATURES). EDA honesty note:
  dev-block team yellow traits are weak (for r=0.198, against
  r=0.095) — Gate Zero must prove itself at the gate regardless.
- Seed 2022/2023; dev 2023/2024 + 2024/2025 (n = 480, events
  exist for every row). Dev harness must not read 2025/2026 rows.
- Baselines: league base rate; naive trailing-10 through the same
  count distribution as the reference harness.
- Virgin: 2025/2026 (n = 240; one row lacks events-derived stats
  in the CSV sense — events exist for all 240; target n = 240,
  verified at read time and reported), read ONCE, only if Gate
  Zero passes the dev gate.
- Halves: 1H/2H presentation via frozen cards constant 0.3290
  (event times — a legitimate source exists for this market).

## GATE LEGS (verbatim, frozen)
Dev gate — pooled dev LL@4.5 beats BOTH baselines, else FAIL,
virgin NOT read. Virgin legs — (i) LL@4.5 ≤ best baseline's;
(ii) calibration |actual − mean P(over 4.5)| ≤ 1.0pp, SE
reported, breach within 1 SE = PROVISIONAL PASS. Gate Zero passes
iff it survives the dev gate AND passes virgin legs (i)–(ii).

## Outputs
Engine `engine/cards/`; `results_dev.json`;
`results_virgin.json`; `fitted_params_virgin.json`; on PASS,
`predictions/k_ua_virgin_predictions.csv` (FT ladder + 1H/2H
presentation via 0.3290). Verdict `reports/K_UA_VERDICT.md`.
