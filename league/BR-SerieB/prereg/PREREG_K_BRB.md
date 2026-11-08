# Pre-registration — K-BRB (BR-SerieB cards model)

Frozen: 2026-11-09, before any fitting. Branch `build/br-serieb`.
Design authority: `analysis/MODEL_DESIGN.md` (K-BRB); features X5,
X8; evidence: EDA cards investigation. Reference: production
`model_cards.py`; BR analogue `PREREG_K_BR.md` and the J1 K engine
(`league/J1/engine/cards/`) — the architecture (team yellow
ratings + count distribution + naive ensemble structure) is
carried over in form, changing only league, seasons, line, target
source, dev window (era-restricted, below) and the X8 shrinkage.

- Target: yellows = `yellow_unified_home + yellow_unified_away`,
  where unified = STATS-feed yellows from 2023 onward and NO valid
  value before 2023. The 2021–2022 cards data are unusable from
  both sources (EDA: stats mean 1.20/match vs 5.06 in 2023; events
  contain no ordinary Yellow records in 2021–2022, only Red /
  YellowRed — unlike Série A, events do NOT rescue those seasons).
  Primary line **4.5** (dev over-rate 0.566 on the scored dev
  season 2024, closest to 0.5). Ladder 3.5/4.5/5.5 reported.
- Arms: **Gate Zero** (reference unmodified; referee not used);
  **X8** — Gate Zero plus the referee covariate exactly as in
  PREREG_K_BR: appointed referee's trailing in-league mean
  yellows/match (strictly pre-match), shrunk toward the league
  mean with prior weight 8 matches; referees with <8 prior
  in-league matches take the shrunk league mean; operational
  fallback to Gate Zero when no appointment is published — no
  imputation. Warehouse referee coverage on the valid target era:
  ~94% 2023, ~77% 2024, ~87% virgin 2025; referee strictness
  split-half r = 0.397 (EDA).
- ERA-RESTRICTED WINDOW (frozen here, before fitting): training
  seed / warm-up = 2023 (state updates, never scored); dev scored
  = 2024 ONLY (n = 380; the one 2023 match with missing cards is
  excluded from cards state/scoring wherever it falls). Dev
  harness must not read 2025 / 2026 rows, and must not read
  2021–2022 rows for the cards target at all.
- Baselines: league base rate (prior-seasons over-4.5 rate —
  within this era, the 2023 rate applied to 2024); naive
  trailing-10 through the same count distribution as the
  reference harness.
- Virgin: 2025 (n = 380), read ONCE, only for dev-passing arms,
  continuing from the dev end state. Calibration at 4.5 =
  ACTUAL − PREDICTED (this build's stated convention),
  SE = sd(y_i − p_i)/√n. 2026 NOT read.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@4.5 beats BOTH baselines (league base rate; naive trailing-10), else arm dead, no virgin read. Virgin legs — (i) LL@4.5 ≤ Gate Zero's and ≤ best baseline's; (ii) calibration |actual − predicted| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev per-season sign check for both-pass. Both-pass: both → lower pooled virgin LL ships; one → ships; none → FAIL.

Mechanical reading: with ONE scored dev season (2024), the variant
sign check (iii) is that season itself (variant dev LL@4.5 ≤ Gate
Zero's in 2024). Ties → Gate Zero. Gate Zero dev failure ⇒ FAIL,
virgin NOT read.

## Outputs

Engine `engine/cards/`; `results_dev.json` (+ CSV);
`results_virgin.json`; `fitted_params_virgin.json` (on PASS); on
PASS, `predictions/k_brb_virgin_predictions.csv` (FT ladder
3.5/4.5/5.5; 1H/2H presentation-only via frozen yellows constant
0.352, lines 1H 0.5/1.5/2.5, 2H 1.5/2.5/3.5). Verdict
`reports/K_BRB_VERDICT.md`.
