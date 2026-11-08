# Pre-registration — K-SA (SA-ProLeague cards model)

Frozen: 2026-11-09, before any fitting. Branch `build/sa-proleague`.
Design authority: `analysis/MODEL_DESIGN.md` (K-SA); features X5;
evidence F1/F2/F8 + DATA_UNDERSTANDING §3.1. Reference: production
`model_cards.py`; J1 analogue: `league/J1/prereg/PREREG_K_J1.md`
and its engine — the architecture (team yellow ratings + count
distribution + naive ensemble structure of the reference) is
carried over in form; read that prereg for the shared constants
and mirror them, changing only league, seasons, line — SA runs
Gate Zero only (see below). Engine port:
`league/SCO-Premiership/engine/cards/`.

- Target: unified yellows = `yellow_home + yellow_away` — the
  **event feed** (Yellow + YellowRed), `cards_source='events'` for
  every match. The stats feed was rejected as the target source on
  dev-era evidence measured before fitting (stats undercounts in
  every dev-era season; DATA_UNDERSTANDING §3.1), following the
  AR/BR/NO precedent. Primary line **3.5** (dev over-rate 0.606,
  closest to 0.5). Ladder 2.5/3.5/4.5 reported.
- Arms: **Gate Zero only** (reference unmodified; referee not
  used). The X8 referee arm is NOT built: its SA reliability check
  failed outright (EDA F8, split-half r = −0.279) and referee
  coverage collapses to 0.7% in the virgin season. Team yellow
  trait reliability is also weak here (F2: r = 0.264 post-era) —
  recorded, not patched; the gate decides.
- Warm-up 2021/2022 + 2022/2023 (never scored); dev scored
  **2023/2024 + 2024/2025 (n = 612)**; dev harness must not read
  2025/2026 / 2026/2027 rows.
- Baselines: league base rate; naive trailing-10 through the same
  count distribution as the reference harness.
- Virgin: 2025/2026 (n = 306), read ONCE, only if Gate Zero passes
  dev. Calibration at 3.5, SE = sd(p_i − y_i)/√n. 2026/2027 NOT
  read (reserved confirmatory).

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@3.5 beats BOTH baselines (league base rate; naive trailing-10), else arm dead, no virgin read. Virgin legs — (i) LL@3.5 ≤ Gate Zero's and ≤ best baseline's; (ii) calibration |mean P(over 3.5) − actual| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev per-season sign check for both-pass. Both-pass: both → lower pooled virgin LL ships; one → ships; none → FAIL.

Mechanical reading as in PREREG_S_SA (Gate Zero only, so (iii) is
vacuous; Gate Zero dev failure ⇒ FAIL, virgin NOT read).

## Outputs

Engine `engine/cards/`; `results_dev.json` (+ CSV);
`results_virgin.json`; `fitted_params_virgin.json`; on PASS,
`predictions/k_sa_virgin_predictions.csv` (FT ladder 2.5/3.5/4.5;
1H/2H presentation-only via frozen yellows constant 0.3509, lines
1H 0.5/1.5/2.5, 2H 1.5/2.5/3.5). Verdict `reports/K_SA_VERDICT.md`.
