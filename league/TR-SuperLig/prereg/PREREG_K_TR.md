# Pre-registration — K-TR (TR-SuperLig cards model)

Frozen: 2026-11-09, before any fitting. Branch `build/tr-superlig`.
Design authority: `analysis/MODEL_DESIGN.md` (K-TR); features X5,
X8; evidence F1/F2/F9. Reference: production `model_cards.py`;
J1 analogue: `league/J1/prereg/PREREG_K_J1.md` and its engine
(`league/J1/engine/cards/`) — the architecture (team yellow ratings
+ count distribution + naive ensemble structure of the reference)
is carried over in form; read that prereg for the shared constants
and mirror them, changing only league, seasons, line and the X8
shrinkage below.
Phase rule (frozen, MODEL_DESIGN): all phases are ordinary rows in
every window; no phase feature anywhere.

- Target: unified yellows = `yellow_home + yellow_away` (stats feed;
  `cards_source='stats'` for 1,771 of 1,818 played TR matches, with the
  frozen broken-stats event fallback on 47 rows — see
  DATA_UNDERSTANDING; the stats-vs-events check is there too).
  Primary line **4.5** (dev unified over-rate 0.436, closest to 0.5;
  the 3.5 over-rate is 0.608). Ladder 3.5/4.5/5.5 reported.
- Arms: **Gate Zero** (reference unmodified; referee not used);
  **X8** — Gate Zero plus the referee covariate: appointed
  referee's trailing in-league mean yellows/match (strictly
  pre-match), shrunk toward the league mean with prior weight
  8 matches; referees with <8 prior in-league matches take the
  shrunk league mean; the covariate enters exactly as in the J1
  K engine's referee arm. Operational condition (inherited): if a
  fixture's appointment is not published pre-match in the live
  pipeline, it falls back to Gate Zero — no imputation. Warehouse
  coverage is 50% in 2021/2022, 100% in 2022/2023–2024/2025, and
  91.5% in 2025/2026, so missing appointments fall back to Gate Zero.
  TR's referee strictness reliability is r = 0.505 pooled — the
  gate decides.
- Training seed 2021/2022; dev 2022/2023–2024/2025 (n = 1033);
  dev harness must not read 2025/2026 / 2026/2027 rows.
- Baselines: league base rate; naive trailing-10 through the same
  count distribution as the reference harness.
- Virgin: 2025/2026 (n = 306), read ONCE, only for dev-passing arms.
  Calibration at 4.5, SE = sd(p_i − y_i)/√n.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@4.5 beats BOTH baselines (league base rate; naive trailing-10), else arm dead, no virgin read. Virgin legs — (i) LL@4.5 ≤ Gate Zero's and ≤ best baseline's; (ii) calibration |mean P(over 4.5) − actual| ≤ 1.0pp is clean PASS; beyond 1 SE is FAIL, with SE reported, a breach within 1 SE of the 1.0pp boundary is PROVISIONAL PASS; (iii) dev per-season sign check for both-pass. Both-pass: both → lower pooled virgin LL ships; one → ships; none → FAIL.

Mechanical reading as in PREREG_S_TR (variant sign check ≥2 of 3;
ties → Gate Zero; Gate Zero dev failure ⇒ FAIL, virgin NOT read).

## Outputs

Engine `engine/cards/`; `results_dev.json` (+ CSV);
`results_virgin.json`; `fitted_params_virgin.json`; on PASS,
`predictions/k_tr_virgin_predictions.csv` (FT ladder 3.5/4.5/5.5;
1H/2H presentation-only via frozen yellows constant 0.3428, lines
1H 1.5/2.5/3.5, 2H 3.5/4.5/5.5). Verdict `reports/K_TR_VERDICT.md`.
