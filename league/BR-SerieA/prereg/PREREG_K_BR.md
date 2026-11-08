# Pre-registration — K-BR (BR-SerieA cards model)

Frozen: 2026-11-09, before any fitting. Branch `build/br-seriea`.
Design authority: `analysis/MODEL_DESIGN.md` (K-BR); features X5,
X8; evidence F1/F2/F8. Reference: production `model_cards.py`;
J1 analogue: `league/J1/prereg/PREREG_K_J1.md` and its engine
(`league/J1/engine/cards/`) — the architecture (team yellow
ratings + count distribution + naive ensemble structure of the
reference) is carried over in form; read that prereg for the
shared constants and mirror them, changing only league, seasons,
line, target source and the X8 shrinkage below.

- Target: **unified yellows** = `yellow_unified_home +
  yellow_unified_away` (events feed for 2021–2022, stats feed from
  2023 — PREPROCESSING; the stats feed undercounts in 2021–2022
  and must not be the target there). Primary line **4.5** (dev
  over-rate 0.573, closest to 0.5). Ladder 3.5/4.5/5.5 reported.
- Arms: **Gate Zero** (reference unmodified; referee not used);
  **X8** — Gate Zero plus the referee covariate: appointed
  referee's trailing in-league mean unified yellows/match
  (strictly pre-match), shrunk toward the league mean with prior
  weight 8 matches; referees with <8 prior in-league matches take
  the shrunk league mean; the covariate enters exactly as in the
  J1 K engine's referee arm. Operational condition (inherited):
  if a fixture's appointment is not published pre-match in the
  live pipeline, it falls back to Gate Zero — no imputation.
  Warehouse coverage: 0% in 2021 (warm-up season only — the arm
  is inactive there by the min-prior rule), 92.6% 2022, 96.6%
  2023, 97.9% 2024, 90.0% in the virgin 2025 — fully testable in
  dev and virgin (contrast K-J1's virgin collapse to 0.5%).
- Training seed 2021; dev 2022–2024 (n = 1,140 scored; the one
  match with missing cards is excluded from cards scoring only);
  dev harness must not read 2025 / 2026 rows.
- Baselines: league base rate; naive trailing-10 through the same
  count distribution as the reference harness.
- Virgin: 2025 (n = 380), read ONCE, only for dev-passing arms.
  Calibration at 4.5, SE = sd(p_i − y_i)/√n. 2026 NOT read.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@4.5 beats BOTH baselines (league base rate; naive trailing-10), else arm dead, no virgin read. Virgin legs — (i) LL@4.5 ≤ Gate Zero's and ≤ best baseline's; (ii) calibration |mean P(over 4.5) − actual| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev per-season sign check for both-pass. Both-pass: both → lower pooled virgin LL ships; one → ships; none → FAIL.

Mechanical reading as in PREREG_S_BR (variant sign check ≥2 of 3;
ties → Gate Zero; Gate Zero dev failure ⇒ FAIL, virgin NOT read).

## Outputs

Engine `engine/cards/`; `results_dev.json` (+ CSV);
`results_virgin.json`; `fitted_params_virgin.json` (cards arms
ship params on PASS as the other candidates do); on PASS,
`predictions/k_br_virgin_predictions.csv` (FT ladder 3.5/4.5/5.5;
1H/2H presentation-only via frozen yellows constant 0.366, lines
1H 0.5/1.5/2.5, 2H 1.5/2.5/3.5). Verdict `reports/K_BR_VERDICT.md`.
