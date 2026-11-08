# Pre-registration — K-ITB (IT-SerieB cards model)

Frozen: 2026-11-09, before any fitting. Branch `build/it-serieb`.
Design authority: `analysis/MODEL_DESIGN.md` (K-ITB); features
X5; evidence F1/F2/F8. Reference: production `model_cards.py`;
J1 analogue: `league/J1/prereg/PREREG_K_J1.md` and its engine
(`league/J1/engine/cards/`) — the architecture (team yellow
ratings + count distribution + naive ensemble structure of the
reference, including per-method NB-r estimation from causal
warm-up residuals, frozen for the scored window) is carried
over in form; read that prereg for the shared constants and
mirror them, changing only league, seasons, line — ITB runs
Gate Zero only (see below). **Calibration = actual −
predicted** throughout.

- Target: unified yellows = `yellow_home + yellow_away`, the
  **event-feed** count (`cards_source='events'` for every ITB
  match; Phase 1 — the stats feed undercounts in every dev
  season, −1.6% to −3.9%, exact agreement 79.7–89.7%; ES/AR
  precedent). Primary line **4.5** (dev-eval over-rate 0.584,
  closest to 0.5). Ladder 3.5/4.5/5.5 reported. Team state
  keyed on team_id.
- Arms: **Gate Zero only** (reference unmodified; referee not
  used). The X8 referee arm is NOT built: its ITB reliability
  check failed outright (EDA F8, split-half r = 0.061 on dev
  seasons — the weakest in the program; J1 0.65, DK 0.56, ES
  dropped at 0.180). Referee coverage is also 47.4% in the
  seed season. The team yellows trait itself is real in this
  league (EDA F2, events r = 0.475) — recorded here so the
  gate result is read against that base.
- Training seed 2021/2022; dev 2022/2023–2024/2025 (n = 1,169);
  dev harness must not read 2025/2026 / 2026/2027 rows.
- Baselines: league base rate; naive trailing-10 through the
  same count distribution as the reference harness.
- Virgin: 2025/2026 (n = 390), read ONCE, only if Gate Zero
  passes the dev gate. Calibration at 4.5 = actual over rate −
  mean P(over 4.5), SE = sd(y_i − p_i)/√n.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@4.5 beats BOTH baselines (league base rate; naive trailing-10), else arm dead, no virgin read. Virgin legs — (i) LL@4.5 ≤ best baseline's; (ii) calibration |actual − mean P(over 4.5)| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev per-season sign check for both-pass. Both-pass: both → lower pooled virgin LL ships; one → ships; none → FAIL.

Mechanical reading as in PREREG_S_ITB. With one arm, legs
(i)/(iii) reduce to: virgin LL ≤ best baseline and the
calibration leg decides clean/provisional/fail. Gate Zero dev
failure ⇒ FAIL, virgin NOT read.

## Outputs

Engine `engine/cards/`; `results_dev.json` (+ CSV);
`results_virgin.json`; `fitted_params_virgin.json`; on PASS,
`predictions/k_itb_virgin_predictions.csv` (FT ladder
3.5/4.5/5.5; 1H/2H presentation-only via frozen yellows
constant 0.3733, lines 1H 0.5/1.5/2.5, 2H 1.5/2.5/3.5).
Verdict `reports/K_ITB_VERDICT.md`.
