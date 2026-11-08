# Pre-registration — K-TH2 (Thailand Thai League 2 cards model)

Frozen: 2026-11-10, before any fitting. Branch `build/th-thaileague2`.
Design authority: `analysis/MODEL_DESIGN.md` (K-TH2); features X5;
evidence EDA (event yellows for 0.287 / against 0.099 — weak, recorded).
Reference: production `model_cards.py`; sibling analogue
`league/TH-ThaiLeague/prereg/PREREG_K_TH.md` — the architecture
(team yellow ratings + count distribution + naive ensemble structure)
is carried over in form, changing only league, windows, line and the
target-source decision below.
Phase rule (frozen): promotion play-off ties are excluded from every
fit and every scored window; only regular-phase rows are used.
Calibration = **actual − predicted** everywhere in this build.

- Target: total **event-unified yellows** = `ev_yellow_home +
  ev_yellow_away` (direct Yellow + YellowRed per team, event feed).
  Target-source decision (frozen here, before fitting, evidence in
  DATA_UNDERSTANDING Step 1): the stats feed is **null in all 681
  payloads**, so no stats-feed target exists in any window; the event
  feed publishes plain "Yellow" events in **every** era (1,204 in the
  dev season, 1,309 in the virgin) — the parent league's era-flipped
  artefact does **not** occur here. The event-unified target is
  therefore used in dev AND virgin for gate comparability. No
  stats-target sensitivity is possible; none is registered.
  Primary line **4.5** (scored-dev over-rate 0.437, closest to 0.5;
  the 3.5 over-rate is 0.596). Ladder 3.5/4.5/5.5 reported.
- Arms: **Gate Zero only** (reference unmodified; referee not used).
  X8 is NOT an arm: referee text coverage is 0/273 in the dev season
  and 0/306 in the virgin, so referee strictness is not even measurable
  (FEATURES). Recorded; not built.
- Walk-forward: per-match, chronological (date, match_id),
  predict-then-update, date-grouped (same-date matches never see each
  other). Warm-up: first 90 regular matches of 2024/2025 update state,
  never scored. Rows with `cards_source = none` (no event feed) are
  never scored and never update the target state.
- Dev: scored = remaining regular matches of 2024/2025 with an event
  feed, **n = 182** (one scored-block row has no event feed).
  Baselines: league base rate; naive trailing-10 through the same
  count distribution as the reference harness. NB size r per method
  estimated from the warm-up block's predictions, as in the sibling
  harness. The dev harness must not read 2025/2026 / 2026/2027 rows.
- Virgin: 2025/2026 regular (n = 306), read ONCE, only if Gate Zero
  passes the dev gate, continuing from the dev end state.
  Calibration at 4.5 = actual − mean predicted, SE = sd(y_i − p_i)/√n.
- Halves: 1H/2H presentation via the frozen yellow-cards constant
  0.3322 (card event times).

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@4.5 beats BOTH baselines (league base rate; naive trailing-10), else the candidate is dead, no virgin read. Virgin legs — (i) LL@4.5 ≤ best baseline's; (ii) calibration |actual − mean P(over 4.5)| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS. If Gate Zero passes all legs it ships; if any leg fails, K-TH2 verdict is FAIL and nothing ships.

Mechanical reading: Gate Zero passes iff it survives the dev gate
AND passes virgin legs (i)–(ii) (PROVISIONAL counts, recorded as
such). Gate Zero dev failure ⇒ FAIL, virgin NOT read.

## Outputs

Engine `engine/cards/`; `results_dev.json` (+ CSV);
`results_virgin.json`; `fitted_params_virgin.json`; on PASS,
`predictions/k_th2_virgin_predictions.csv` (FT ladder 3.5/4.5/5.5
+ 1H/2H presentation via frozen constant 0.3322). Verdict
`reports/K_TH2_VERDICT.md`.
