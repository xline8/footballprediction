# Pre-registration — K-ZA (South Africa Premier Soccer League cards model)

Frozen: 2026-11-10, before any fitting. Branch `build/za-psl`.
Design authority: `analysis/MODEL_DESIGN.md` (K-ZA); features X5;
evidence EDA (stats yellows for 0.578 / against 0.608). Reference:
production `model_cards.py`; sibling analogue
`league/TH-ThaiLeague/prereg/PREREG_K_TH.md` — the architecture
(team yellow ratings + count distribution + naive ensemble structure)
is carried over in form, changing only league, seasons, line and the
target-source decision below.
Phase rule (frozen): all modelled rows are phase `regular`; no phase
feature. Team identity is the FotMob team id.
Calibration = **actual − predicted** everywhere in this build.

- Target: total **stats-feed yellows** = `yellow_cards_home +
  yellow_cards_away`. Target-source decision (frozen here, before
  fitting, evidence in DATA_UNDERSTANDING Step 1): the
  stats-vs-events artefact IS present and era-flipped in BOTH
  windows — in the dev seasons and in the virgin the event feed
  publishes NO plain-yellow events at all (event-unified mean
  ≈0.05/match vs stats 3.30–3.75), so an event-unified target does
  not exist in dev OR virgin. The stats target is therefore used in
  dev AND virgin for gate comparability. **No virgin event-unified
  sensitivity is registered** (unlike TH): the unified virgin count
  does not exist; the first season carrying both feeds is the
  confirmatory 2026/2027, which this build never reads. Primary line
  **3.5** (scored-dev over-rate 0.526, closest to 0.5; the 4.5
  over-rate is 0.320). Ladder 2.5/3.5/4.5 reported.
- Arms: **Gate Zero only** (reference unmodified; referee not used).
  X8 is NOT an arm: referee strictness reliability r = 0.080 and
  virgin referee coverage is 13/240 (FEATURES). Recorded; not built.
- Training seed 2022/2023; dev 2023/2024–2024/2025 (rows with the
  target n = 447); dev harness must not read 2025/2026 / 2026/2027
  rows.
- Baselines: league base rate; naive trailing-10 through the same
  count distribution as the reference harness.
- Virgin: 2025/2026 (stats rows n = 240), read ONCE, only if Gate
  Zero passes the dev gate. Calibration at 3.5 = actual − mean
  predicted, SE = sd(y_i − p_i)/√n.
- Halves: 1H/2H presentation via the frozen yellow-cards constant
  0.3253 (period splits).

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@3.5 beats BOTH baselines (league base rate; naive trailing-10), else the candidate is dead, no virgin read. Virgin legs — (i) LL@3.5 ≤ best baseline's; (ii) calibration |actual − mean P(over 3.5)| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS. If Gate Zero passes all legs it ships; if any leg fails, K-ZA verdict is FAIL and nothing ships.

Mechanical reading: Gate Zero passes iff it survives the dev gate
AND passes virgin legs (i)–(ii) (PROVISIONAL counts, recorded as
such). Gate Zero dev failure ⇒ FAIL, virgin NOT read.

## Outputs

Engine `engine/cards/`; `results_dev.json` (+ CSV);
`results_virgin.json`; `fitted_params_virgin.json`; on PASS,
`predictions/k_za_virgin_predictions.csv` (FT ladder 2.5/3.5/4.5
+ 1H/2H presentation via frozen constant 0.3253). Verdict
`reports/K_ZA_VERDICT.md`.
