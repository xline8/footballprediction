# Pre-registration — K-CN (China Super League cards model)

Frozen: 2026-11-10, before any fitting. Branch `build/cn-superleague`.
Design authority: `analysis/MODEL_DESIGN.md` (K-CN); features X5;
evidence EDA (stats yellows for 0.282 / against 0.347, dev block
2023–2025 — weak, recorded honestly). Reference: production
`model_cards.py`; sibling analogue
`league/TH-ThaiLeague/prereg/PREREG_K_TH.md` — the architecture
(team yellow ratings + count distribution + naive ensemble structure)
is carried over in form, changing only league, seasons, line and the
target-source decision below.
Era restriction (frozen, from EDA): fits use **2023+ only** (cards
level step in 2023; 2021/2022 excluded eras — see `analysis/EDA.md`).
Phase rule (frozen): all rows are ordinary rows; no phase feature.
Calibration = **actual − predicted** everywhere in this build.

- Target: total **stats-feed yellows** = `yellow_cards_home +
  yellow_cards_away`. Target-source decision (frozen here, before
  fitting, evidence in PREPROCESSING): the stats-vs-events artefact
  IS present but confined to the excluded era — in 2021/2022 the
  stats feed undercounts vs the event feed by −0.81/−0.57 per match
  (exact agreement 69.3%/73.5%); in the fit era 2023+ the two agree
  exactly in 82.5–90.4% of matches with mean stats-minus-events
  −0.15…−0.03 per match. An event-unified target is therefore not
  needed for era consistency, and the stats target (the reference
  architecture's own source) is used in dev AND virgin.
  **Preregistered sensitivity (not a gate leg):** on the virgin
  read, the dev-passing arm's LL@3.5 and calibration are ALSO
  computed against the event-feed virgin target (`ev_yellow_home +
  ev_yellow_away` from `cn_matches.csv`) and reported in the verdict.
  Primary line **3.5** (scored-dev over-rate 0.537, closest to 0.5;
  the 4.5 over-rate is 0.375). Ladder 3.5/4.5 reported, gate at 3.5.
- Arms: **Gate Zero only** (reference unmodified; referee not used).
  X8 is NOT an arm: referee strictness reliability ≈ 0 (blocks
  r = 0.133 / 0.014 / −0.703; dev block 0.218) and virgin referee
  coverage is 117/240 = 48.75% (FEATURES). Recorded; not built.
- Training seed 2023; dev 2024–2025 (stats rows n = 480); dev
  harness must not read 2026 rows.
- Baselines: league base rate; naive trailing-10 through the same
  count distribution as the reference harness.
- Virgin: 2026 (stats rows n = 240), read ONCE, only if Gate
  Zero passes the dev gate. Calibration at 3.5 = actual − mean
  predicted, SE = sd(y_i − p_i)/√n.
- Halves: 1H/2H presentation via the frozen yellow-cards constant
  0.3328 (period splits; event-time check 0.3398).

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@3.5 beats BOTH baselines (league base rate; naive trailing-10), else the candidate is dead, no virgin read. Virgin legs — (i) LL@3.5 ≤ best baseline's; (ii) calibration |actual − mean P(over 3.5)| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS. If Gate Zero passes all legs it ships; if any leg fails, K-CN verdict is FAIL and nothing ships.

Mechanical reading: Gate Zero passes iff it survives the dev gate
AND passes virgin legs (i)–(ii) (PROVISIONAL counts, recorded as
such). Gate Zero dev failure ⇒ FAIL, virgin NOT read.

## Outputs

Engine `engine/cards/`; `results_dev.json` (+ CSV);
`results_virgin.json`; `fitted_params_virgin.json`; on PASS,
`predictions/k_cn_virgin_predictions.csv` (FT ladder 3.5/4.5
+ 1H/2H presentation via frozen constant 0.3328). Verdict
`reports/K_CN_VERDICT.md`.
