# Pre-registration — K-FR (FR-Ligue2 cards model)

Frozen: 2026-11-09, before any fitting. Branch `build/fr-ligue2`.
Design authority: `analysis/MODEL_DESIGN.md` (K-FR); features X5;
evidence EDA. Reference: production `model_cards.py`; J1 analogue:
`league/J1/prereg/PREREG_K_J1.md` and its engine
(`league/J1/engine/cards/`) — the architecture (team yellow ratings
+ count distribution + naive ensemble structure of the reference)
is carried over in form; read that prereg for the shared constants
and mirror them, changing only league, seasons, line — FR runs
Gate Zero only (see below).

- Target: unified yellows = `ev_yellow_home + ev_yellow_away`, the
  **event-feed** count (`cards_source='events'` for every FR match;
  EDA — the stats feed undercounts the event feed in every season:
  dev-period totals events 5,205 vs stats 4,857, worst in 2021/2022
  1,364 vs 1,138; exact per-match agreement only 86.1% pooled dev;
  AR/ES/IN precedent). Primary line **3.5** (dev over-rate 0.485,
  closest to 0.5). Ladder 2.5/3.5/4.5 reported. Team state keyed
  on team_id.
- Arms: **Gate Zero only** (reference unmodified; referee not
  used). The X8 referee arm is NOT built: its FR reliability check
  failed outright (EDA, split-half r = 0.028 on dev seasons, 0.156
  pooled — pure noise, the weakest in the program alongside ENGCH
  team traits). Referee coverage is also incomplete in 2021/2022
  (50.0%) and in the virgin (82.7%). The team yellows trait itself
  is real in this league (EDA, r = 0.445) — recorded here so the
  gate result is read against that base.
- Training seed 2021/2022; dev 2022/2023–2024/2025 (n = 1,065);
  dev harness must not read 2025/2026 / 2026/2027 rows.
- Baselines: league base rate; naive trailing-10 through the same
  count distribution as the reference harness.
- Virgin: 2025/2026 (n = 306), read ONCE, only for dev-passing arms.
  Calibration at 3.5 = actual rate − mean P(over 3.5), SE =
  sd(y_i − p_i)/√n.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@3.5 beats BOTH baselines (league base rate; naive trailing-10), else arm dead, no virgin read. Virgin legs — (i) LL@3.5 ≤ Gate Zero's and ≤ best baseline's; (ii) calibration |actual − mean P(over 3.5)| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev per-season sign check for both-pass. Both-pass: both → lower pooled virgin LL ships; one → ships; none → FAIL.

Mechanical reading as in PREREG_S_FR (variant sign check ≥2 of 3;
ties → Gate Zero; Gate Zero dev failure ⇒ FAIL, virgin NOT read).
With one arm, legs (i)/(iii) reduce to: virgin LL ≤ best baseline
and the calibration leg decides clean/provisional/fail.

## Outputs

Engine `engine/cards/`; `results_dev.json` (+ CSV);
`results_virgin.json`; `fitted_params_virgin.json`; on PASS,
`predictions/k_fr_virgin_predictions.csv` (FT ladder 2.5/3.5/4.5;
1H/2H presentation-only via frozen yellows constant 0.3736, lines
1H 0.5/1.5/2.5, 2H 1.5/2.5/3.5). Verdict `reports/K_FR_VERDICT.md`.
