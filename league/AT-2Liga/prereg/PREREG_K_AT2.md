# Pre-registration — K-AT2 (Austria 2. Liga cards model)

Frozen: 2026-11-10, before any fitting. Branch `build/at-2liga`.
Design authority: `analysis/MODEL_DESIGN.md` (K-AT2); features X5;
evidence EDA (event yellows for 0.445 / against 0.574).
Reference: production `model_cards.py`; sibling analogue
`league/RU-1Division/prereg/PREREG_K_RU1.md` — the architecture
(team yellow ratings + count distribution + naive ensemble
structure of the reference) is carried over in form; mirror the
shared constants, changing only league, seasons, line and target
source below.
Phase rule (frozen, MODEL_DESIGN): all rows are phase `regular`;
no phase feature anywhere.
Calibration = **actual − predicted** everywhere in this build.

- Target: EVENT yellows = `ev_yellow_home + ev_yellow_away`
  (event Yellow + YellowRed per team, from the match events feed).
  Target-source decision (frozen here, before fitting): the
  stats-vs-events artefact check is MOOT in this league — the
  stats feed carries NO yellow_cards key in any of the 1,266
  payloads (stats rows with a yellow count: 0), so no stats target
  exists to disagree with the events. The event count is the only
  possible target and is used by construction; `cards_source` is
  "events" on every row. Primary line **4.5** (dev-period
  over-rate 0.583, closest to 0.5; the 5.5 over-rate is 0.413).
  Ladder 3.5/4.5/5.5 reported.
- Arms: **Gate Zero only** (reference unmodified; referee not
  used). X8 is NOT an arm: referee text is empty in 100% of
  payloads in this league. Recorded in FEATURES; not built.
- Training seed 2021/2022; dev 2022/2023–2024/2025 (n = 720 — the
  events feed is complete, so unlike the stats markets the cards
  dev window has no missing rows); dev harness must not read
  2025/2026 / 2026/2027 rows.
- Baselines: league base rate; naive trailing-10 through the same
  count distribution as the reference harness.
- Virgin: 2025/2026 (n = 210), read ONCE, only if Gate Zero passes
  the dev gate. Calibration at 4.5 = actual − mean predicted,
  SE = sd(y_i − p_i)/√n.
- Halves: presentation only via the frozen event-derived yellows
  constant 0.3430 (EDA F3) — FT is fitted; 1H/2H splits in the
  predictions file are derived from the FT expectation, never
  fitted.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@4.5 beats BOTH baselines (league base rate; naive trailing-10), else the candidate is dead, no virgin read. Virgin legs — (i) LL@4.5 ≤ best baseline's; (ii) calibration |actual − mean P(over 4.5)| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS. If Gate Zero passes all legs it ships; if any leg fails, K-AT2 verdict is FAIL and nothing ships.

Mechanical reading: Gate Zero passes iff it survives the dev gate
AND passes virgin legs (i)–(ii) (PROVISIONAL counts, recorded as
such). Gate Zero dev failure ⇒ FAIL, virgin NOT read.

## Outputs

Engine `engine/cards/`; `results_dev.json` (+ CSV);
`results_virgin.json`; `fitted_params_virgin.json`; on PASS,
`predictions/k_at2_virgin_predictions.csv` (FT ladder 3.5/4.5/5.5
plus derived 1H/2H presentation via the frozen 0.3430 constant).
Verdict `reports/K_AT2_VERDICT.md`.
