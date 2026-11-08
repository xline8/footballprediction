# Pre-registration — K-MA (Morocco Botola Pro cards model)

Frozen: 2026-11-10, before any fitting. Branch `build/ma-botola`.
Design authority: `league/MA-BotolaPro/analysis/MODEL_DESIGN.md`
(K-MA); features per `analysis/FEATURES.md` (X5 adopted with its
recorded weakness — rich-era split-half yellows-for r = 0.010;
X8 DROPPED). Reference: production `model_cards.py`; sibling
analogue `league/RU-1Division/prereg/PREREG_K_RU1.md` — the
architecture (decayed team yellow ratings + NB count distribution
+ naive ensemble) is carried over in form, changing only league,
windows, line, target source and the era rule below.
Phase rule (frozen): all rows are phase `regular`; no phase
feature anywhere.
Calibration = **actual − predicted** everywhere in this build.

## Target-source decision (frozen here, before fitting)

The stats-vs-events artefact check is MOOT in this league — the
stats feed carries NO yellow_cards key in any of the 1,255
payloads, so no stats target exists to disagree with the events.
The event count is the only possible target. Era restriction
(payload-verified): plain `Yellow` events exist ONLY in the rich
era (date >= 2024-11-01); the pre-era events feed carries only
`Red` / `YellowRed` cards (zero plain yellows in 2021/2022–
2023/2024), so pre-era rows are excluded from every cards window.

- Target: EVENT-unified yellows = `yellow_home + yellow_away`
  where each side counts `Yellow` + `YellowRed` Card events
  (RU-1Division convention), rich era only. Primary line **4.5**
  (rich dev-era over-rate 0.494, closest to 0.5). Ladder
  3.5/4.5/5.5 reported, gate at 4.5.
- Arms: **Gate Zero only** (reference unmodified; referee not
  used). X8 is NOT an arm: referee text is empty in 100% of
  payloads in this league. Recorded in FEATURES; not built.
- Walk-forward: per-match, chronological (date, match_id),
  predict-then-update, date-grouped. Warm-up: rich-era matches
  2024-11-01 – 2024-12-31 (64 matches) update state, never
  scored. Dev: scored rich-era matches 2025-01-01 – 2025-05-12
  (n = 112). The dev harness must not read 2025/2026 / 2026/2027
  rows. Cards scores EVERY rich-era match (events exist for all).
- Baselines: league base rate; naive trailing-10 through the same
  count distribution as the reference harness.
- Virgin: 2025/2026 (n = 240), read ONCE, only if Gate Zero passes
  the dev gate, continuing from the dev end state. Calibration at
  4.5 = actual − mean predicted, SE = sd(y_i − p_i)/√n.
- Halves: frozen constant 0.3465 from rich dev-era card-event
  times (presentation only).

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@4.5 beats BOTH baselines (league base rate; naive trailing-10), else the candidate is dead, no virgin read. Virgin legs — (i) LL@4.5 ≤ best baseline's; (ii) calibration |actual − mean P(over 4.5)| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS. If Gate Zero passes all legs it ships; if any leg fails, K-MA verdict is FAIL and nothing ships.

Mechanical reading: Gate Zero passes iff it survives the dev gate
AND passes virgin legs (i)–(ii) (PROVISIONAL counts, recorded as
such). Gate Zero dev failure ⇒ FAIL, virgin NOT read.

## Outputs

Engine `league/MA-BotolaPro/engine/cards/`; `results_dev.json`
(+ `predictions_dev.csv`); `results_virgin.json`;
`fitted_params_virgin.json`; on PASS,
`predictions/k_ma_virgin_predictions.csv` (FT ladder 3.5/4.5/5.5;
1H/2H presentation via frozen yellows constant 0.3465).
Verdict `reports/K_MA_VERDICT.md`. Production code untouched.
No push. No merge.
