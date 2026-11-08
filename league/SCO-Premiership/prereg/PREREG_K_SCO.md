# Pre-registration — K-SCO (SCO-Premiership cards model)

Frozen: 2026-11-09, before any fitting. Branch `build/sco-premiership`.
Design authority: `analysis/MODEL_DESIGN.md` (K-SCO); features X5;
evidence F1/F2/F8. Reference: production `model_cards.py`;
J1 analogue: `league/J1/prereg/PREREG_K_J1.md` and its engine
(`league/J1/engine/cards/`) — the architecture (team yellow ratings
+ count distribution + naive ensemble structure of the reference)
is carried over in form; read that prereg for the shared constants
and mirror them, changing only league, seasons, line — SCO runs Gate Zero only (see below).

- Target: unified yellows = `yellow_home + yellow_away` (stats feed,
  `cards_source='stats'` for every SCO match). Primary line **3.5**
  (dev over-rate 0.521, closest to 0.5). Ladder 2.5/3.5/4.5 reported.
- Arms: **Gate Zero only** (reference unmodified; referee not
  used). The X8 referee arm is NOT built: its SCO reliability check
  failed outright (EDA F8, split-half r = 0.158 vs J1 0.65 / DK 0.56).
  Referee coverage is also incomplete in 2021/2022 (47.4%).
- Training seed 2021/2022; dev 2022/2023–2024/2025 (n = 684);
  dev harness must not read 2025/2026 / 2026/2027 rows.
- Baselines: league base rate; naive trailing-10 through the same
  count distribution as the reference harness.
- Virgin: 2025/2026 (n = 228), read ONCE, only for dev-passing arms.
  Calibration at 3.5, SE = sd(p_i − y_i)/√n.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@3.5 beats BOTH baselines (league base rate; naive trailing-10), else arm dead, no virgin read. Virgin legs — (i) LL@3.5 ≤ Gate Zero's and ≤ best baseline's; (ii) calibration |mean P(over 3.5) − actual| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev per-season sign check for both-pass. Both-pass: both → lower pooled virgin LL ships; one → ships; none → FAIL.

Mechanical reading as in PREREG_S_SCO (variant sign check ≥2 of 3;
ties → Gate Zero; Gate Zero dev failure ⇒ FAIL, virgin NOT read).

## Outputs

Engine `engine/cards/`; `results_dev.json` (+ CSV);
`results_virgin.json`; `fitted_params_virgin.json`; on PASS,
`predictions/k_sco_virgin_predictions.csv` (FT ladder 2.5/3.5/4.5;
1H/2H presentation-only via frozen yellows constant 0.3120, lines
1H 0.5/1.5/2.5, 2H 1.5/2.5/3.5). Verdict `reports/K_SCO_VERDICT.md`.
