# Pre-registration — K-MXE (Mexico Liga de Expansión MX cards model)

Frozen: 2026-11-10, before any fitting. Branch `build/mx-expansion`.
Design authority: `league/MX-ExpansionMX/analysis/MODEL_DESIGN.md`
(K-MXE); features per `analysis/FEATURES.md` (X8 referee DROPPED —
referee named on 0% of dev matches; no variant arm exists).
Reference: production cards model pattern (`model_cards.py`,
decayed venue-split team ratings shrunk to the league mean,
HL = 270, K = 8, NB total) as ported in `league/J1/engine/cards/`.
Target (frozen): **unified yellows from the event feed** —
`card='Yellow'` plus `card='YellowRed'` per side (a second yellow
is a yellow shown). Corpus restriction (frozen, DATA_UNDERSTANDING
F2): the cards corpus is the **clean era only** — blocks from
2023/2024 - Apertura onward. 2022/2023 - Clausura (partial capture:
45/153 zero-yellow matches) and all earlier blocks are excluded
from every cards fit and score. Phase rule: regular phase only.
Calibration is defined as **actual − predicted** everywhere.

## Reference architecture

- Online state per the J1 cards port: per-team decayed venue-split
  yellow for/against sums (HL = 270 days), shrunk toward the
  decayed league venue means with K_PRIOR = 8; league fallback
  means FB_MU_H = 2.15 / FB_MU_A = 1.95 (production constants) only
  before any observation.
- Prediction for a match = model expected total (venue-split
  multiplicative form), processed strictly chronologically
  (predict-then-update; kickoff order = (date, match_id)).
- Count distribution: Negative Binomial with r estimated on the
  warm-up block's records by the production moment estimator
  (per method: model / base / naive), frozen after warm-up.
- Methods scored alongside the model in every window: **base**
  (decayed league venue means total) and **naive** (trailing-10
  team means, venue-combined, per the reference implementation).
- Arms: **Gate Zero only** (the unmodified reference). No referee
  arm (X8 dropped on coverage), no other variant.

## Windows (frozen)

- Warm-up (unscored; also the r-estimation block): 2023/2024 -
  Apertura (n = 105).
- Dev (scored, online walk-forward continuing from warm-up):
  2023/2024 - Clausura, 2024/2025 - Apertura, 2024/2025 - Clausura,
  2025/2026 - Apertura (pooled n = 420).
- Virgin: 2025/2026 - Clausura (n = 105, complete), read ONCE,
  only if the dev gate passes, after dev results are frozen. The
  virgin is scored by continuing the same online state through the
  dev blocks (no refit, no reset — the production pattern).
- 2026/2027 is never read (in progress; stats-era season).

## Primary line (frozen from the dev distribution)

Dev distribution (clean era, scored blocks): mean 5.169 yellows;
over-rates 3.5 → 0.779, 4.5 → 0.598, 5.5 → 0.421. Primary line =
**5.5** (nearest the median). Ladder scored: 4.5 / 5.5 / 6.5;
gate legs apply at 5.5 only.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev model log-loss at the primary line 5.5 must beat BOTH the base-rate baseline's and the naive trailing-10 baseline's pooled dev log-loss at 5.5, else Gate Zero is dead, the verdict is FAIL, and the virgin is NOT read. Virgin legs — (i) LL leg: virgin model LL at 5.5 ≤ base LL at 5.5 AND ≤ naive LL at 5.5; (ii) calibration leg: |actual − mean predicted| ≤ 1.0pp for the over-5.5 rate, SE = sd(y_i − p_i)/√n reported; a breach within 1 SE of the boundary is recorded PROVISIONAL PASS, beyond it FAIL. Both legs pass (PROVISIONAL counts on leg ii, recorded as such) ⇒ K-MXE ships Gate Zero; any leg fails ⇒ FAIL and nothing ships.

## Outputs

Engine `league/MX-ExpansionMX/engine/cards/`; dev results
`results_dev.json`; virgin `results_virgin.json`; fitted params
`fitted_params_virgin.json`; on PASS, virgin predictions
`league/MX-ExpansionMX/predictions/k_mxe_virgin_predictions.csv`
(1H/2H presentation via frozen yellow constant 0.402). Verdict:
`league/MX-ExpansionMX/reports/K_MXE_VERDICT.md`. Production code
untouched. No push. No merge.
