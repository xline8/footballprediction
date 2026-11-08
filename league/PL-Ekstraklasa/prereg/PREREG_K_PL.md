# Pre-registration — K-PL (PL-Ekstraklasa cards model)

Frozen: 2026-11-09, before any fitting. Branch `build/pl-ekstraklasa`.
Design authority: `analysis/MODEL_DESIGN.md` (K-PL); features X5,
X8; evidence EDA (yellows for 0.370 / against 0.227; referee
split-half r = 0.501 over the 20 referees meeting the sample
threshold, 42 distinct referees named). Reference: production
`model_cards.py`; BE analogue `PREREG_K_BE.md` and the J1 K engine
(`league/J1/engine/cards/`) — the architecture (team yellow ratings
+ count distribution + naive ensemble structure of the reference)
is carried over in form; mirror the shared constants, changing
only league, seasons, line and the X8 shrinkage below.
Phase rule (frozen, MODEL_DESIGN): all rows are phase `regular`;
no phase feature anywhere.
Calibration = **actual − predicted** everywhere in this build.

- Target: unified yellows = `yellow_home + yellow_away` (stats feed
  for 1,348 matches, `cards_source='events'` for the 306 matches of
  2021/2022 where the stats feed carries no yellow_cards key; the
  stats-vs-events check on the 1,348 dual-source matches: exact
  agreement 83.8%, stats lower in 12.9%, higher in 3.3%, mean
  stats − events = −0.158 — the artefact shape seen across the
  programme; the unified target stands as built). Primary line
  **3.5** (dev-period over-rate 0.567, closest to 0.5; the 4.5
  over-rate is 0.392). Ladder 2.5/3.5/4.5 reported.
- Arms: **Gate Zero** (reference unmodified; referee not used);
  **X8** — Gate Zero plus the referee covariate: appointed
  referee's trailing in-league mean yellows/match (strictly
  pre-match), shrunk toward the league mean with prior weight
  8 matches; referees with <8 prior in-league matches take the
  shrunk league mean; the covariate enters exactly as in the J1
  K engine's referee arm. Operational condition (inherited): if a
  fixture's appointment is not published pre-match in the live
  pipeline, it falls back to Gate Zero — no imputation. Warehouse
  referee coverage: 72.9% in 2021/2022, 100% in 2022/2023–2024/2025,
  86.6% in the virgin 2025/2026 — the arm is testable throughout
  dev; virgin matches without a named referee fall back to the
  shrunk league mean inside the arm, exactly as pre-registered
  here. PL's referee trait (r = 0.501) sits mid-programme (J1
  0.646, BE 0.378) — the gate decides.
- Training seed 2021/2022; dev 2022/2023–2024/2025 (n = 918);
  dev harness must not read 2025/2026 / 2026/2027 rows.
- Baselines: league base rate; naive trailing-10 through the same
  count distribution as the reference harness.
- Virgin: 2025/2026 (n = 306), read ONCE, only for dev-passing arms.
  Calibration at 3.5 = actual − mean predicted, SE = sd(y_i − p_i)/√n.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@3.5 beats BOTH baselines (league base rate; naive trailing-10), else arm dead, no virgin read. Virgin legs — (i) LL@3.5 ≤ Gate Zero's and ≤ best baseline's; (ii) calibration |actual − mean P(over 3.5)| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev per-season sign check for both-pass. Both-pass: both → lower pooled virgin LL ships; one → ships; none → FAIL.

Mechanical reading as in PREREG_S_PL (variant sign check ≥2 of 3;
ties → Gate Zero; Gate Zero dev failure ⇒ FAIL, virgin NOT read).

## Outputs

Engine `engine/cards/`; `results_dev.json` (+ CSV);
`results_virgin.json`; `fitted_params_virgin.json`; on PASS,
`predictions/k_pl_virgin_predictions.csv` (FT ladder 2.5/3.5/4.5;
1H/2H presentation-only via frozen yellows constant 0.3338, lines
1H 0.5/1.5/2.5, 2H 1.5/2.5/3.5). Verdict `reports/K_PL_VERDICT.md`.
