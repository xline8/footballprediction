# Pre-registration — K-SE2 (SE-Superettan cards model)

Frozen: 2026-11-10, before any fitting. Branch `build/se-superettan`.
Design authority: `analysis/MODEL_DESIGN.md` (K-SE2); feature X5; evidence F1/F2/F5.
Reference: production `model_cards.py` pattern as frozen for K-SE (ratings +
naive ensemble through NB, per the cards harness family).
TARGET FREEZE (reason written, before fitting): the Superettan stats feed
publishes NO card keys, so a stats target does not exist. The event feed DOES
carry plain Yellow events in every season (no era flip; levels 3.17–4.24/match).
The target is therefore **event-derived unified yellows** (Yellow + YellowRed
per match, both teams) for dev AND virgin — the event-unified target by
necessity, not by artefact repair. NO X8 arm: referee names are empty in
1,440/1,440 payloads, so the referee trait cannot be measured, let alone used.
Single-arm candidate.

- Target: total yellows (events). Primary line **3.5** (dev over-rate 0.519).
  Ladder 3.5 / 4.5 reported, gate at 3.5.
- Arm: **Gate Zero** only.
- Walk-forward per-match chronological, predict-then-update, date-grouped.
  Warm-up 2021; dev scored 2022–2025 (n = 960). Dev harness must not read 2026 rows.
- Baselines: league base rate (prior-seasons over-3.5 rate); naive trailing-10 through the same NB.
- Virgin: 2026 (n = 240), read ONCE, only if Gate Zero passes dev.
  Calibration = mean P(over 3.5) − actual, SE = sd(p_i − y_i)/√n.

## GATE LEGS (verbatim, frozen)
Dev gate — pooled dev LL at the primary line beats BOTH baselines (league base rate; naive trailing-10), else arm dead, no virgin read. Virgin legs — (i) LL ≤ Gate Zero's and ≤ best baseline's; (ii) calibration |mean P(over) − actual| ≤ 1.0pp clean PASS, breach within 1 SE = PROVISIONAL PASS, else FAIL; (iii) dev per-season sign check for both-pass (variant dev LL ≤ Gate Zero's in at least half the dev seasons). Both-pass: lower pooled virgin LL ships; one → ships; none → FAIL. Ties → simpler arm. If Gate Zero fails its dev gate, variants are moot, verdict FAIL, virgin NOT read.
(Single arm: leg (iii) and the both-pass rule are vacuous.)

## Outputs
Engine `engine/cards/`; `results_dev.json` (+ CSV); `results_virgin.json`;
on PASS, `predictions/k_se2_virgin_predictions.csv` (FT ladder; 1H/2H
presentation via frozen yellows constant 0.3344). Verdict `reports/K_SE2_VERDICT.md`.
