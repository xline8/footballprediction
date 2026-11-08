# Pre-registration — K-RU1 (Russia 1. Division cards model)

Frozen: 2026-11-10, before any fitting. Branch `build/ru-1division`.
Design authority: `analysis/MODEL_DESIGN.md` (K-RU1); features X5;
evidence EDA (event yellows for 0.722 / against 0.724 — the
strongest reliability pair among the count traits here).
Reference: production `model_cards.py`; sibling analogue
`league/RU-PremierLeague/prereg/PREREG_K_RU.md` — the architecture
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
  stats feed carries NO yellow_cards key in any of the 1,756
  payloads (stats rows with a yellow count: 0), so no stats target
  exists to disagree with the events. The event count is the only
  possible target and is used by construction; `cards_source` is
  "events" on every row. Primary line **4.5** (dev-period
  over-rate 0.461, closest to 0.5; the 3.5 over-rate is 0.639).
  Ladder 3.5/4.5/5.5 reported.
- Arms: **Gate Zero only** (reference unmodified; referee not
  used). X8 is NOT an arm: referee text is empty in 100% of
  payloads in this league. Recorded in FEATURES; not built.
- Training seed 2021/2022; dev 2022/2023–2024/2025 (n = 918);
  dev harness must not read 2025/2026 / 2026/2027 rows.
- Baselines: league base rate; naive trailing-10 through the same
  count distribution as the reference harness.
- Virgin: 2025/2026 (n = 305), read ONCE, only if Gate Zero passes
  the dev gate. Calibration at 4.5 = actual − mean predicted,
  SE = sd(y_i − p_i)/√n.
- Halves: NONE — no period splits exist in this league; FT
  presentation only.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@4.5 beats BOTH baselines (league base rate; naive trailing-10), else the candidate is dead, no virgin read. Virgin legs — (i) LL@4.5 ≤ best baseline's; (ii) calibration |actual − mean P(over 4.5)| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS. If Gate Zero passes all legs it ships; if any leg fails, K-RU1 verdict is FAIL and nothing ships.

Mechanical reading: Gate Zero passes iff it survives the dev gate
AND passes virgin legs (i)–(ii) (PROVISIONAL counts, recorded as
such). Gate Zero dev failure ⇒ FAIL, virgin NOT read.

## Outputs

Engine `engine/cards/`; `results_dev.json` (+ CSV);
`results_virgin.json`; `fitted_params_virgin.json`; on PASS,
`predictions/k_ru1_virgin_predictions.csv` (FT ladder 3.5/4.5/5.5;
NO halves columns — FT only). Verdict `reports/K_RU1_VERDICT.md`.
