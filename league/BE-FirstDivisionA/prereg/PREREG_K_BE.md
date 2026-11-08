# Pre-registration — K-BE (BE-FirstDivisionA cards model)

Frozen: 2026-11-09, before any fitting. Branch `build/be-firstdiva`.
Design authority: `analysis/MODEL_DESIGN.md` (K-BE); features X5,
X8; evidence F1/F2/F9. Reference: production `model_cards.py`;
J1 analogue: `league/J1/prereg/PREREG_K_J1.md` and its engine
(`league/J1/engine/cards/`) — the architecture (team yellow ratings
+ count distribution + naive ensemble structure of the reference)
is carried over in form; read that prereg for the shared constants
and mirror them, changing only league, seasons, line and the X8
shrinkage below.
Phase rule (frozen, MODEL_DESIGN): all phases are ordinary rows in
every window; no phase feature anywhere.

- Target: unified yellows = `yellow_home + yellow_away` (stats feed,
  `cards_source='stats'` for 1,695 BE matches, `'events'` for the
  three stats-less matches; the stats-vs-events check is in
  DATA_UNDERSTANDING §4). Primary line **3.5**
  (dev over-rate 0.543, closest to 0.5; the 4.5 over-rate is 0.331). Ladder 2.5/3.5/4.5 reported.
- Arms: **Gate Zero** (reference unmodified; referee not used);
  **X8** — Gate Zero plus the referee covariate: appointed
  referee's trailing in-league mean yellows/match (strictly
  pre-match), shrunk toward the league mean with prior weight
  8 matches; referees with <8 prior in-league matches take the
  shrunk league mean; the covariate enters exactly as in the J1
  K engine's referee arm. Operational condition (inherited): if a
  fixture's appointment is not published pre-match in the live
  pipeline, it falls back to Gate Zero — no imputation. Warehouse
  coverage is ≈86% overall (41.2% in 2021/2022, 93–100% from
  2022/2023), so the arm is testable on 2022/2023 onward and often
  shrunk to the league mean in the seed era. BE's referee trait is
  the weakest adopted in the program (EDA F9, r = 0.378) — the
  gate decides.
- Training seed 2021/2022; dev 2022/2023–2024/2025 (n = 956);
  dev harness must not read 2025/2026 / 2026/2027 rows.
- Baselines: league base rate; naive trailing-10 through the same
  count distribution as the reference harness.
- Virgin: 2025/2026 (n = 313), read ONCE, only for dev-passing arms.
  Calibration at 3.5, SE = sd(p_i − y_i)/√n.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@3.5 beats BOTH baselines (league base rate; naive trailing-10), else arm dead, no virgin read. Virgin legs — (i) LL@3.5 ≤ Gate Zero's and ≤ best baseline's; (ii) calibration |mean P(over 3.5) − actual| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev per-season sign check for both-pass. Both-pass: both → lower pooled virgin LL ships; one → ships; none → FAIL.

Mechanical reading as in PREREG_S_BE (variant sign check ≥2 of 3;
ties → Gate Zero; Gate Zero dev failure ⇒ FAIL, virgin NOT read).

## Outputs

Engine `engine/cards/`; `results_dev.json` (+ CSV);
`results_virgin.json`; `fitted_params_virgin.json`; on PASS,
`predictions/k_be_virgin_predictions.csv` (FT ladder 2.5/3.5/4.5;
1H/2H presentation-only via frozen yellows constant 0.317, lines
1H 0.5/1.5/2.5, 2H 1.5/2.5/3.5). Verdict `reports/K_BE_VERDICT.md`.
