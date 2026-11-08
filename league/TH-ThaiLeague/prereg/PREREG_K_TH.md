# Pre-registration — K-TH (Thailand Thai League 1 cards model)

Frozen: 2026-11-10, before any fitting. Branch `build/th-thaileague`.
Design authority: `analysis/MODEL_DESIGN.md` (K-TH); features X5;
evidence EDA (stats yellows for 0.522 / against 0.380). Reference:
production `model_cards.py`; sibling analogue
`league/RU-1Division/prereg/PREREG_K_RU1.md` — the architecture
(team yellow ratings + count distribution + naive ensemble structure)
is carried over in form, changing only league, seasons, line and the
target-source decision below.
Phase rule (frozen): all rows are phase `regular`; no phase feature.
Calibration = **actual − predicted** everywhere in this build.

- Target: total **stats-feed yellows** = `yellow_cards_home +
  yellow_cards_away`. Target-source decision (frozen here, before
  fitting, evidence in DATA_UNDERSTANDING Step 1): the
  stats-vs-events artefact IS present but era-flipped — in the dev
  seasons the event feed publishes NO plain-yellow events at all
  (event-unified mean 0.02–0.11/match vs stats 3.06–4.34), so an
  event-unified target does not exist in dev; in the virgin the
  classic direction appears (stats 4.088 vs unified 4.279/match).
  The stats target is therefore used in dev AND virgin for gate
  comparability. **Preregistered sensitivity (not a gate leg):** on
  the virgin read, the dev-passing arm's LL@4.5 and calibration are
  ALSO computed against the event-unified virgin target
  (`ev_yellow_home + ev_yellow_away`) and reported in the verdict.
  Primary line **4.5** (scored-dev over-rate 0.438, closest to 0.5;
  the 3.5 over-rate is 0.619). Ladder 3.5/4.5/5.5 reported.
- Arms: **Gate Zero only** (reference unmodified; referee not used).
  X8 is NOT an arm: referee strictness reliability r = 0.199 and
  virgin referee coverage is 9/240 (FEATURES). Recorded; not built.
- Training seed 2022/2023; dev 2023/2024–2024/2025 (stats rows
  n = 480); dev harness must not read 2025/2026 / 2026/2027 rows.
- Baselines: league base rate; naive trailing-10 through the same
  count distribution as the reference harness.
- Virgin: 2025/2026 (stats rows n = 240), read ONCE, only if Gate
  Zero passes the dev gate. Calibration at 4.5 = actual − mean
  predicted, SE = sd(y_i − p_i)/√n.
- Halves: 1H/2H presentation via the frozen yellow-cards constant
  0.3076 (period splits).

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@4.5 beats BOTH baselines (league base rate; naive trailing-10), else the candidate is dead, no virgin read. Virgin legs — (i) LL@4.5 ≤ best baseline's; (ii) calibration |actual − mean P(over 4.5)| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS. If Gate Zero passes all legs it ships; if any leg fails, K-TH verdict is FAIL and nothing ships.

Mechanical reading: Gate Zero passes iff it survives the dev gate
AND passes virgin legs (i)–(ii) (PROVISIONAL counts, recorded as
such). Gate Zero dev failure ⇒ FAIL, virgin NOT read.

## Outputs

Engine `engine/cards/`; `results_dev.json` (+ CSV);
`results_virgin.json`; `fitted_params_virgin.json`; on PASS,
`predictions/k_th_virgin_predictions.csv` (FT ladder 3.5/4.5/5.5
+ 1H/2H presentation via frozen constant 0.3076). Verdict
`reports/K_TH_VERDICT.md`.
