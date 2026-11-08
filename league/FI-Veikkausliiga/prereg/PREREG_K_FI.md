# Pre-registration — K-FI (FI-Veikkausliiga cards model)

Frozen: 2026-11-10, before any fitting. Branch `build/fi-veikkausliiga`.
Design authority: `analysis/MODEL_DESIGN.md` (K-FI); feature X5; evidence F1/F2/F6.
Reference: production `model_cards.py` pattern as frozen for K-SE2 (ratings +
naive ensemble through NB, per the cards harness family).
TARGET FREEZE (reason written, before fitting): the Veikkausliiga stats feed
publishes card keys (`yellow_cards`/`red_cards`) ONLY in the rich era
(2025–2026); the thin era (2021–2024) has no card keys at all, so a stats
target cannot cover the dev window. The stats-vs-events artefact check was
run first (EDA F6): on 2025 the two sources agree exactly in 81.9% of
matches with mean stats − events = −0.040 yellows/match; on 2026, 76.8%
and −0.096 — no era flip, no systematic artefact of the TH/ZA kind. The
target is therefore **event-derived unified yellows** (Yellow + YellowRed
per match, both teams) for dev AND virgin — the event-unified target by
coverage necessity, validated against the stats feed where both exist.
NO X8 arm: referee names are empty in all of 2021–2024 and in 141/177 of
2025, so the referee trait cannot be measured on the dev era.
Single-arm candidate.

- Target: total yellows (events). Primary line **3.5** (dev over-rate 0.587,
  closest to 0.5). Ladder 3.5 / 4.5 reported, gate at 3.5.
- Arm: **Gate Zero** only.
- Walk-forward per-match chronological, predict-then-update, date-grouped.
  Warm-up 2021; dev scored 2022–2025 (n = 678). Dev harness must not read 2026 rows.
- Baselines: league base rate (prior-seasons over-3.5 rate); naive trailing-10 through the same NB.
- Virgin: 2026 (n = 177), read ONCE, only if Gate Zero passes dev.
  Calibration = mean P(over 3.5) − actual, SE = sd(p_i − y_i)/√n.
- Frozen note: event yellows drop from 4.43/match (2024) to 3.50 (2025) and
  the virgin sits at 3.65 — recorded in EDA F1 before fitting; the level
  shift is the calibration leg's problem, not a reason to move windows.

## GATE LEGS (verbatim, frozen)
Dev gate — pooled dev LL at the primary line beats BOTH baselines (league base rate; naive trailing-10), else arm dead, no virgin read. Virgin legs — (i) LL ≤ Gate Zero's and ≤ best baseline's; (ii) calibration |mean P(over) − actual| ≤ 1.0pp clean PASS, breach within 1 SE = PROVISIONAL PASS, else FAIL; (iii) dev per-season sign check for both-pass (variant dev LL ≤ Gate Zero's in at least half the dev seasons). Both-pass: lower pooled virgin LL ships; one → ships; none → FAIL. Ties → simpler arm. If Gate Zero fails its dev gate, variants are moot, verdict FAIL, virgin NOT read.
(Single arm: leg (iii) and the both-pass rule are vacuous.)

## Outputs
Engine `engine/cards/`; `results_dev.json` (+ CSV); `results_virgin.json`;
on PASS, `predictions/k_fi_virgin_predictions.csv` (FT ladder; 1H/2H
presentation via frozen yellows constant 0.3109). Verdict `reports/K_FI_VERDICT.md`.
