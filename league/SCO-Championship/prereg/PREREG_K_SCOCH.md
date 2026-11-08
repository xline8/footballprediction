# Pre-registration — K-SCOCH (Scotland Championship cards model)

Frozen: 2026-11-10, before any fitting. Branch `build/sco-championship`.
Design authority: `analysis/MODEL_DESIGN.md` (K-SCOCH); features X5;
evidence EDA (event yellows for 0.301 / against 0.231).
Reference: production `model_cards.py`; sibling analogue
`league/RU-1Division/prereg/PREREG_K_RU1.md` — the architecture
(team yellow ratings + count distribution + naive ensemble
structure of the reference) is carried over in form; mirror the
shared constants, changing only league, seasons, line and the
target-source note below.
Phase rule (frozen): all rows are phase `regular`; no phase feature.
Calibration = **predicted − actual** everywhere in this build.

- Target: unified yellows = `yellow_home + yellow_away` in the
  league CSV. Target-source decision (frozen here, before
  fitting): the stats feed carries a `yellow_cards` key in ONLY
  19 of 969 payloads (the rich 2021/2022 subset); on exactly those
  19 the stats count agrees with the event-feed Yellow count
  EXACTLY (19/19 exact, mean difference 0.0 — EDA artefact check).
  No stats-vs-events conflict exists; the stats target simply does
  not exist for 950 matches, so the target is the event-feed
  Yellow count by construction for the whole corpus (the CSV's
  unified column uses the stats value on the 19 rich rows, where
  it is identical anyway). `YellowRed` events are NOT yellows
  under this definition (counted as reds), matching the stats
  agreement. Primary line **3.5** (dev-period over-rate 0.5407,
  closest to 0.5; the 4.5 over-rate is 0.3463). Ladder 2.5/3.5/4.5
  reported.
- Arms: **Gate Zero only** (reference unmodified; referee not
  used). The X8 referee arm is NOT built: referee strictness
  reliability in this league is r = 0.3318 (EDA), below the
  program adoption standard (SCO-Premiership dropped at 0.158;
  J1 adopted at 0.65). Recorded in FEATURES; not built.
- Training seed 2021/2022; dev 2022/2023–2024/2025 (n = 540 — the
  event target exists for every match, including the stats-outage
  rows); dev harness must not read 2025/2026 / 2026/2027 rows.
- Baselines: league base rate; naive trailing-10 through the same
  count distribution as the reference harness.
- Virgin: 2025/2026 (n = 180), read ONCE, only if Gate Zero passes
  the dev gate. Calibration at 3.5 = mean predicted − actual,
  SE = sd(p_i − y_i)/√n.
- Halves: presentation only via the frozen event-derived yellows
  constant 0.3121 (1H/2H ladders on PASS, exactly as SCO-Premiership
  K-SCO).

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@3.5 beats BOTH baselines (league base rate; naive trailing-10), else the candidate is dead, no virgin read. Virgin legs — (i) LL@3.5 ≤ best baseline's; (ii) calibration |mean P(over 3.5) − actual| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS. If Gate Zero passes all legs it ships; if any leg fails, K-SCOCH verdict is FAIL and nothing ships.

Mechanical reading: Gate Zero passes iff it survives the dev gate
AND passes virgin legs (i)–(ii) (PROVISIONAL counts, recorded as
such). Gate Zero dev failure ⇒ FAIL, virgin NOT read.

## Outputs

Engine `engine/cards/`; `results_dev.json` (+ CSV);
`results_virgin.json`; `fitted_params_virgin.json`; on PASS,
`predictions/k_scoch_virgin_predictions.csv` (FT ladder 2.5/3.5/4.5;
1H/2H presentation-only via frozen yellows constant 0.3121, lines
1H 0.5/1.5/2.5, 2H 1.5/2.5/3.5). Verdict
`reports/K_SCOCH_VERDICT.md`.
