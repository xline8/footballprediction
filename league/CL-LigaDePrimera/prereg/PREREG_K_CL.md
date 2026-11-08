# Pre-registration — K-CL (Chile Liga de Primera cards model)

Frozen: 2026-11-10, before any fitting. Branch `build/cl-primera`.
Design authority: `analysis/MODEL_DESIGN.md` (K-CL); features X5;
evidence EDA (event yellows for r = 0.315, team-season split-half).
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
  stats-vs-events artefact check was run first (Step 1) and the
  stats feed's yellow_cards UNDERCOUNTS the event feed in every
  season (mean stats − events per match: −1.20 in 2021, −1.28 in
  2022, −0.49 in 2023, −0.44 in 2024, −0.16 in 2025). The event
  feed carries plain yellows in all seasons, so the target is
  frozen as EVENT-UNIFIED yellows; `cards_source` is "events" on
  every row and stats yellows are audit-only. Primary line **5.5**
  (dev-period over-rate 0.464, closest to 0.5; the 4.5 over-rate
  is 0.628). Ladder 4.5/5.5/6.5 reported, gate at 5.5.
- Arms: **Gate Zero only** (reference unmodified; referee not
  used). X8 is NOT an arm: referee strictness reliability is
  weak (split-half r = 0.357) and referee identity is missing
  for all of 2021 and 4–26% of later matches. Recorded in
  FEATURES; not built.
- Training seed 2021; dev 2022–2024 (n = 720);
  dev harness must not read 2025 / 2026 rows.
- Baselines: league base rate; naive trailing-10 through the same
  count distribution as the reference harness.
- Virgin: 2025 (n = 240), read ONCE, only if Gate Zero passes
  the dev gate. Calibration at 5.5 = actual − mean predicted,
  SE = sd(y_i − p_i)/√n.
- Halves: period splits exist from 2023; the frozen cards
  constant 0.3818 (EDA, stats splits) is used for 1H/2H
  presentation only.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@5.5 beats BOTH baselines (league base rate; naive trailing-10), else the candidate is dead, no virgin read. Virgin legs — (i) LL@5.5 ≤ best baseline's; (ii) calibration |actual − mean P(over 5.5)| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS. If Gate Zero passes all legs it ships; if any leg fails, K-CL verdict is FAIL and nothing ships.

Mechanical reading: Gate Zero passes iff it survives the dev gate
AND passes virgin legs (i)–(ii) (PROVISIONAL counts, recorded as
such). Gate Zero dev failure ⇒ FAIL, virgin NOT read.

## Outputs

Engine `engine/cards/`; `results_dev.json` (+ CSV);
`results_virgin.json`; `fitted_params_virgin.json`; on PASS,
`predictions/k_cl_virgin_predictions.csv` (FT ladder 3.5/4.5/5.5;
NO halves columns — FT only). Verdict `reports/K_CL_VERDICT.md`.
