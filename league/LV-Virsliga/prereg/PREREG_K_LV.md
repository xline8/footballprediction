# Pre-registration — K-LV (Latvia Virsliga cards model)

Frozen: 2026-11-10, before any fitting. Branch `build/lv-virsliga`.
Design authority: `league/LV-Virsliga/analysis/MODEL_DESIGN.md`
(K-LV); features per `analysis/FEATURES.md` (X5 adopted — split-half
yellows-for r = 0.598 in 2025, far stronger than MA's 0.010;
X8 DROPPED). Reference: production `model_cards.py`; sibling
analogue `league/RU-1Division/prereg/PREREG_K_RU1.md` — the
architecture (decayed team yellow ratings + NB count distribution
+ naive ensemble) is carried over in form, changing only league,
windows, line, target source and the era rule below.
Phase rule (frozen): all rows are phase `regular`; no phase
feature anywhere.
Calibration = **actual − predicted** everywhere in this build.

## Virgin-hygiene disclosure

As in PREREG_G_LV: step-1 inventory aggregates (including 2026)
are era facts; no per-match model output and no gate quantity was
computed from 2026 before this freeze. The virgin is NOT burned.

## Target-source decision (frozen here, before fitting)

The stats-vs-events artefact check is DECISIVE in this league —
unlike MA, a stats target exists AND disagrees with the events:
the stats `yellow_cards` key reads exactly 0/0 in 43/180 2025
matches while the event feed records 187 yellows in those same
matches (hole Mar–Aug 2025; other stats keys are sane there).
The stats key is therefore NOT the target. The event count is the
only complete target. Era restriction (payload-verified): plain
`Yellow` events are near-absent before 2025 (11/19/23/24 per
season 2021–2024), so pre-2025 rows are excluded from every
cards window.

- Target: EVENT-unified yellows = `yellow_home + yellow_away`
  where each side counts `Yellow` + `YellowRed` Card events
  (RU-1Division convention), stats era only. Primary line **4.5**
  (2025 dev-era over-rate 0.522, closest to 0.5). Ladder
  3.5/4.5/5.5 reported, gate at 4.5.
- Arms: **Gate Zero only** (reference unmodified; referee not
  used). X8 is NOT an arm: referee text is populated in only
  40/180 2025 matches (~12 referees, 1–5 matches each).
- Walk-forward: per-match, chronological (date, match_id),
  predict-then-update, date-grouped. Warm-up: stats-era matches
  2025-03-05 – 2025-04-30 (47 matches) update state, never
  scored. Dev: scored stats-era matches 2025-05-01 – 2025-11-09
  (n = 133). The dev harness must not read 2026 rows. Cards
  scores EVERY stats-era match (events exist for all).
- Baselines: league base rate; naive trailing-10 through the same
  count distribution as the reference harness.
- Virgin: 2026 (n = 179), read ONCE, only if Gate Zero passes
  the dev gate, continuing from the dev end state. Calibration at
  4.5 = actual − mean predicted, SE = sd(y_i − p_i)/√n.
- Halves: FT + 1H/2H via frozen yellows constant 0.3306 from 2025
  card-event times (presentation only; true per-match share
  variance = 0).

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@4.5 beats BOTH baselines (league base rate; naive trailing-10), else the candidate is dead, no virgin read. Virgin legs — (i) LL@4.5 ≤ best baseline's; (ii) calibration |actual − mean P(over 4.5)| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS. If Gate Zero passes all legs it ships; if any leg fails, K-LV verdict is FAIL and nothing ships.

Mechanical reading: Gate Zero passes iff it survives the dev gate
AND passes virgin legs (i)–(ii) (PROVISIONAL counts, recorded as
such). Gate Zero dev failure ⇒ FAIL, virgin NOT read.

## Outputs

Engine `league/LV-Virsliga/engine/cards/`; `results_dev.json`
(+ `predictions_dev.csv`); `results_virgin.json`;
`fitted_params_virgin.json`; on PASS,
`predictions/k_lv_virgin_predictions.csv` (FT ladder 3.5/4.5/5.5;
1H/2H presentation via frozen yellows constant 0.3306).
Verdict `reports/K_LV_VERDICT.md`. Production code untouched.
No push. No merge.
