# Pre-registration — K-ES (ES-LaLiga2 cards model)

Frozen: 2026-11-09, before any fitting. Branch `build/es-laliga2`.
Design authority: `analysis/MODEL_DESIGN.md` (K-ES); features X5;
evidence F1/F2/F8. Reference: production `model_cards.py`;
J1 analogue: `league/J1/prereg/PREREG_K_J1.md` and its engine
(`league/J1/engine/cards/`) — the architecture (team yellow ratings
+ count distribution + naive ensemble structure of the reference)
is carried over in form; read that prereg for the shared constants
and mirror them, changing only league, seasons, line — ES runs Gate Zero only (see below).

- Target: unified yellows = `yellow_home + yellow_away`, the
  **event-feed** count (`cards_source='events'` for every ES match;
  Phase 1 §3 — the stats feed undercounts in every dev season and
  is not one consistent quantity here; AR/IN precedent). Primary
  line **4.5** (dev over-rate 0.536, closest to 0.5). Ladder
  3.5/4.5/5.5 reported. Team state keyed on team_id.
- Arms: **Gate Zero only** (reference unmodified; referee not
  used). The X8 referee arm is NOT built: its ES reliability check
  failed outright (EDA F8, split-half r = 0.180 on dev seasons,
  0.269 pooled, vs J1 0.65 / DK 0.56). Referee coverage is also
  incomplete in 2021/2022 (48.5%) and in the virgin (82.1%). The
  team yellows trait itself is real in this league (EDA F2,
  r = 0.453 — the mirror image of ENGCH's −0.01) — recorded here
  so the gate result is read against that base.
- Training seed 2021/2022; dev 2022/2023–2024/2025 (n = 1,404);
  dev harness must not read 2025/2026 / 2026/2027 rows.
- Baselines: league base rate; naive trailing-10 through the same
  count distribution as the reference harness.
- Virgin: 2025/2026 (n = 468), read ONCE, only for dev-passing arms.
  Calibration at 4.5, SE = sd(p_i − y_i)/√n.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@4.5 beats BOTH baselines (league base rate; naive trailing-10), else arm dead, no virgin read. Virgin legs — (i) LL@4.5 ≤ Gate Zero's and ≤ best baseline's; (ii) calibration |mean P(over 4.5) − actual| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev per-season sign check for both-pass. Both-pass: both → lower pooled virgin LL ships; one → ships; none → FAIL.

Mechanical reading as in PREREG_S_ES (variant sign check ≥2 of 3;
ties → Gate Zero; Gate Zero dev failure ⇒ FAIL, virgin NOT read).
With one arm, legs (i)/(iii) reduce to: virgin LL ≤ best baseline
and the calibration leg decides clean/provisional/fail.

## Outputs

Engine `engine/cards/`; `results_dev.json` (+ CSV);
`results_virgin.json`; `fitted_params_virgin.json`; on PASS,
`predictions/k_es_virgin_predictions.csv` (FT ladder 3.5/4.5/5.5;
1H/2H presentation-only via frozen yellows constant 0.3455, lines
1H 0.5/1.5/2.5, 2H 1.5/2.5/3.5). Verdict `reports/K_ES_VERDICT.md`.
