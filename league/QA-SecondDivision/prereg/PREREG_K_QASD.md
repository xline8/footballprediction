# Pre-registration — K-QASD (QA-SecondDivision cards model)

Frozen: 2026-11-10, before any fitting. Branch `build/qa-seconddiv`.
Design authority: `analysis/MODEL_DESIGN.md` (K-QASD); features X5;
evidence F1/F2/F3/F5/F6/F7 + DATA_UNDERSTANDING §3.1. Reference:
production `model_cards.py`; SA analogue: `league/SA-ProLeague/
prereg/PREREG_K_SA.md` and its engine — the architecture (team
yellow ratings + count distribution + naive ensemble structure of
the reference) is carried over in form; read that prereg for the
shared constants and mirror them, changing only league, seasons,
line — QA-SecondDivision runs Gate Zero only (see below). Engine
port: `league/SCO-Premiership/engine/cards/` (and
`league/SA-ProLeague/engine/cards/`). Phase rule (frozen): single
phase `regular` throughout; only played rows are used. Calibration is
defined as **actual − predicted** everywhere.

- Target: unified yellows = `yellow_home + yellow_away` — the
  **event feed** (Yellow + YellowRed), `cards_source='events'` for
  every match. The stats feed was rejected as the target source on
  dev-era evidence measured before fitting (stats undercounts the
  event feed one-directionally: dev-season 2025/2026 recheck 37 exact
  / 19 low / 0 high, mean −0.52; pooled pre-virgin 71 / 23 / 0,
  mean −0.40), following the AR/BR/NO/SA precedent. Primary line
  **5.5** (dev over-rate 0.500, exactly — closest to 0.5). Ladder
  4.5/5.5/6.5 reported, gate at 5.5.
- Arms: **Gate Zero only** (reference unmodified; referee not
  used). The X8 referee arm is NOT built: referee coverage is 0%
  in both dev seasons (EDA F6). Team yellow trait reliability is
  also noise here (F2: r = −0.01 odd/even / −0.28 chrono) — recorded,
  not patched; the gate decides.
- Walk-forward: per-match, chronological (date, match_id),
  predict-then-update, date-grouped (same-date matches never see
  each other). Warm-up: first 28 matches of 2025/2026 (rounds 1–7,
  never scored); scored: the remaining **28 matches** (rounds 8–14).
  Fit history for scored matches is all matches strictly before each
  scored date — including the 2024/2025 stats-era rounds 6–14 (38
  matches) and the 2024/2025 event-yellows season (the event feed
  exists in all 56 matches of 2024/2025). The dev harness must not
  read 2026/2027 rows at all.
- Dev: scored block n = 28. Small-n note as in PREREG_S_QASD.
- Baselines: league base rate (over-5.5 rate of all matches strictly
  before each scored date, expanding); naive trailing-10 through the
  same count distribution as the reference harness.
- Virgin: 2026/2027 partial (n = 29, rounds 1–6, TRANSITIONAL),
  read ONCE, only if Gate Zero passes dev. Calibration at 5.5,
  SE = sd(y_i − p_i)/√n. Small-n note as in PREREG_S_QASD: at n = 29
  the calibration SE is ≈9pp; the gate is applied mechanically
  regardless, and the verdict records the virgin as TRANSITIONAL
  with a confirmatory read at season end.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@5.5 beats BOTH baselines (league base rate; naive trailing-10), else arm dead, no virgin read. Virgin legs — (i) LL@5.5 ≤ Gate Zero's and ≤ best baseline's; (ii) calibration |actual − mean P(over 5.5)| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev sign check for both-pass. Both-pass: both → lower pooled virgin LL ships; one → ships; none → FAIL.

Mechanical reading as in PREREG_S_QASD (Gate Zero only, so (iii) is
vacuous; Gate Zero dev failure ⇒ FAIL, virgin NOT read).

## Outputs

Engine `engine/cards/`; `results_dev.json` (+ CSV);
`results_virgin.json`; `fitted_params_virgin.json`; on PASS,
`predictions/k_qasd_virgin_predictions.csv` (FT ladder 4.5/5.5/6.5;
1H/2H presentation-only via frozen yellows constant 0.3151, event
times). Verdict `reports/K_QASD_VERDICT.md`.
