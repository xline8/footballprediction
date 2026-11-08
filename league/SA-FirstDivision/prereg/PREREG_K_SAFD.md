# Pre-registration — K-SAFD (SA-FirstDivision cards model)

Frozen: 2026-11-10, before any fitting. Branch `build/sa-firstdiv`.
Design authority: `analysis/MODEL_DESIGN.md` (K-SAFD); features X5;
evidence F1/F2/F6/F7 + DATA_UNDERSTANDING §3.1. Reference:
production `model_cards.py`; SA analogue: `league/SA-ProLeague/
prereg/PREREG_K_SA.md` and its engine — the architecture (team
yellow ratings + count distribution + naive ensemble structure of
the reference) is carried over in form; read that prereg for the
shared constants and mirror them, changing only league, seasons,
line — SA-FirstDivision runs Gate Zero only (see below). Engine
port: `league/SCO-Premiership/engine/cards/` (and
`league/SA-ProLeague/engine/cards/`). Phase rule (frozen):
promotion playoffs and awarded matches are **excluded from every
fit and every scored window**; only regular played rows are used.
Calibration is defined as **actual − predicted** everywhere.

- Target: unified yellows = `yellow_home + yellow_away` — the
  **event feed** (Yellow + YellowRed), `cards_source='events'` for
  every match. The stats feed was rejected as the target source on
  dev-era evidence measured before fitting (stats undercounts the
  event feed one-directionally: dev-season recheck 257 exact / 47
  low / 0 high, mean −0.289 on 2025/2026 regular played; Phase A
  check 259/48/0, −0.296 on all 307 stats matches), following the
  AR/BR/NO/SA precedent. Primary line **4.5** (dev over-rate 0.470,
  closest to 0.5). Ladder 3.5/4.5/5.5 reported, gate at 4.5.
- Arms: **Gate Zero only** (reference unmodified; referee not
  used). The X8 referee arm is NOT built: referee coverage is 0%
  in both dev seasons (EDA F6). Team yellow trait reliability is
  also noise here (F2: r = 0.156 events / 0.190 stats) — recorded,
  not patched; the gate decides.
- Walk-forward: per-match, chronological (date, match_id),
  predict-then-update, date-grouped. Warm-up: first 90 regular
  played matches of 2025/2026 (never scored); scored: the remaining
  **214 matches**. The 2024/2025 season contributes no cards
  history (score-only, no events) and is not read by this harness
  at all.
- Dev: scored block n = 214. The dev harness must not read
  2026/2027 rows at all.
- Baselines: league base rate (over-4.5 rate of all regular played
  matches strictly before each scored date, expanding); naive
  trailing-10 through the same count distribution as the reference
  harness.
- Virgin: 2026/2027 partial (n = 94, rounds 1–11, TRANSITIONAL),
  read ONCE, only if Gate Zero passes dev. Calibration at 4.5,
  SE = sd(p_i − y_i)/√n. Small-n note as in PREREG_S_SAFD: at n = 94
  the calibration SE is ≈5pp; the gate is applied mechanically
  regardless, and the verdict records the virgin as TRANSITIONAL
  with a confirmatory read at season end.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@4.5 beats BOTH baselines (league base rate; naive trailing-10), else arm dead, no virgin read. Virgin legs — (i) LL@4.5 ≤ Gate Zero's and ≤ best baseline's; (ii) calibration |mean P(over 4.5) − actual| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev sign check for both-pass. Both-pass: both → lower pooled virgin LL ships; one → ships; none → FAIL.

Mechanical reading as in PREREG_S_SAFD (Gate Zero only, so (iii) is
vacuous; Gate Zero dev failure ⇒ FAIL, virgin NOT read).

## Outputs

Engine `engine/cards/`; `results_dev.json` (+ CSV);
`results_virgin.json`; `fitted_params_virgin.json`; on PASS,
`predictions/k_safd_virgin_predictions.csv` (FT ladder 3.5/4.5/5.5;
1H/2H presentation-only via frozen yellows constant 0.4010, lines
1H 1.5/2.5/3.5, 2H 2.5/3.5/4.5). Verdict `reports/K_SAFD_VERDICT.md`.
