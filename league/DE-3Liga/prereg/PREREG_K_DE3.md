# Pre-registration — K-DE3 (DE-3Liga cards model)

Frozen: 2026-11-09, before any fitting. Branch `build/de-3liga`.
Design authority: `analysis/MODEL_DESIGN.md` (K-DE3); features X5,
X8; evidence EDA F2/F4/F6. Reference: production `model_cards.py`;
DE-2 analogue `PREREG_K_DE2.md` and the J1 K engine
(`league/J1/engine/cards/`) — the architecture (team yellow
ratings + count distribution + naive ensemble structure of the
reference) is carried over in form; mirror its shared constants,
changing only league, seasons, line, target source and the X8
shrinkage below.
Format rule (frozen, MODEL_DESIGN): all matches are ordinary rows
in every window; no phase feature anywhere.

- Target: EVENT-UNIFIED yellows = `yellow_home + yellow_away`
  (events; `cards_source='events'`). The stats-vs-events check
  (EDA F4) proves the stats block undercounts in this league
  (exact agreement 81.0%, mean −0.178/match), so unlike DE-2 the
  event-unified amendment IS the frozen target here. Primary line
  **4.5** (dev over-rate 0.499, closest to 0.5). Ladder
  3.5/4.5/5.5 reported.
- Arms: **Gate Zero** (reference unmodified; referee not used);
  **X8** — Gate Zero plus the referee covariate: appointed
  referee's trailing in-league mean yellows/match (strictly
  pre-match), shrunk toward the league mean with prior weight
  8 matches; referees with <8 prior in-league matches take the
  shrunk league mean; the covariate enters exactly as in the J1
  K engine's referee arm. Operational condition (inherited): if
  a fixture's appointment is not published pre-match in the live
  pipeline, it falls back to Gate Zero — no imputation.
  Warehouse coverage: 41.5% in the 2021/2022 seed, 88.2–98.9%
  from 2022/2023 (virgin 88.2%), and referee strictness is a real
  trait here (split-half r = 0.483, EDA F2), so the arm is
  testable on the scored dev seasons and the virgin.
- Training seed 2021/2022; dev evaluation 2022/2023–2024/2025
  (n = 1,140). Dev harness must not read 2025/2026 / 2026/2027
  rows.
- Baselines: league base rate; naive trailing-10.
- Virgin: 2025/2026 (n = 380), read ONCE, only for dev-passing
  arms. Calibration at 4.5 = actual rate − mean P(over)
  (actual − predicted), SE = sd(y_i − p_i)/√n.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@4.5 beats BOTH baselines (league base
rate; naive trailing-10), else arm dead, no virgin read. Virgin
legs — (i) LL@4.5 ≤ Gate Zero's and ≤ best baseline's;
(ii) calibration |actual − mean P(over 4.5)| ≤ 1.0pp, SE
reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev
per-season sign check for both-pass. Both-pass: both → lower
pooled virgin LL ships; one → ships; none → FAIL.

Mechanical reading as in PREREG_S_DE3 (variant sign check ≥2 of
3 dev seasons; ties → Gate Zero; Gate Zero dev failure ⇒ FAIL,
virgin NOT read).

## Outputs

Engine `engine/cards/`; `results_dev.json` (+ CSV);
`results_virgin.json`; `fitted_params_virgin.json`; on PASS,
`predictions/k_de3_virgin_predictions.csv` (FT ladder 3.5/4.5/5.5;
1H/2H presentation-only via frozen cards constant 0.361, lines
1H 1.5/2.5, 2H 2.5/3.5). Verdict `reports/K_DE3_VERDICT.md`.
