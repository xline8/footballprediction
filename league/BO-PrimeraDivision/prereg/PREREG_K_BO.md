# Pre-registration — K-BO (BO-PrimeraDivision cards)

Frozen: 2026-11-10, before any fitting. Branch `build/bo-primera`.
Design authority: `analysis/MODEL_DESIGN.md` (K-BO); features per
`analysis/FEATURES.md` (X5 adopted; **X8 DROPPED** — referee text is
empty 2021–2024 and named on only 40/240 in 2025, 79/199 in 2026, so
no dev-era referee signal exists); evidence per `analysis/EDA.md`
(yellows traits for/against r=.116/.231 — weak, the dev gate decides).
Reference: production `model_cards.py` pattern, ported as in
`league/J1/engine/cards/` / `league/PY-DivisionProfesional/engine/cards/`.

## Target — event-unified yellows (frozen BEFORE fitting)

`y = event_yellow_unified_home + event_yellow_unified_away` (each
Yellow = 1, each YellowRed = 1 additional yellow), from the CSV's
event-derived columns. The stats-feed `yellow_cards` columns are NOT
the target: the pre-fitting feed check on dev-era evidence only
(DATA_UNDERSTANDING.md) showed the stats feed undercounts (1,324 vs
1,495 event-unified in 2025; exact match only 151/240 matches; the
stats-period 1H share 0.3980 also disagrees with the event-unified
0.3739). Event-feed plain Yellow cards exist only in 2025–2026, so
the cards target exists only in the stats era. This is the PY
artefact precedent; the target decision was taken and documented
before any fitting and before any virgin read.

## Data and windows (measured before freezing)

Source: `league/BO-PrimeraDivision/data/bo_matches.csv`.
Dev-era event-unified mean 6.15 → **primary line 6.5** (secondary
5.5/7.5 as in the reference harness).

- Seed (training only): 2025 rounds 1–10 (n = 80).
- Dev eval blocks: 2025 rounds 11–30 in four expanding 5-round blocks
  (train on all prior 2025 rounds; n = 160 scored).
- **Virgin: 2026 regular, TRANSITIONAL (n = 199 played at pull;
  season in progress, rounds 1–25)** — read ONCE, only if the
  (single) arm passes the dev gate, after dev results freeze.
  Season-end confirmatory read outstanding.
- The harness's dev mode must not read 2026 rows.

## Arms

1. **Gate Zero** — the unmodified production cards pattern (single
   arm by design; no variant exists for this candidate).

Baselines: league base rate at 6.5 (pooled stats-era rate strictly
prior to the scored block) and naive trailing-10.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@6.5 of Gate Zero must beat BOTH baselines, else the candidate is dead and the virgin is NOT read. Virgin legs — (i) LL leg: Gate Zero's virgin LL@6.5 ≤ both baselines'; (ii) calibration leg: |mean predicted P(over 6.5) − actual over-rate| ≤ 1.0pp clean PASS; a breach within 1 SE of the boundary is recorded PROVISIONAL PASS, beyond it FAIL (SE = sd(p_i − y_i)/√n). If both virgin legs pass, K-BO verdict is PASS (PROVISIONAL if leg (ii) is provisional, or by the transitional-virgin note) and Gate Zero ships; otherwise FAIL and nothing ships.

## Outputs

Engine `league/BO-PrimeraDivision/engine/cards/` (+ README);
`results_dev.json`, `results_virgin.json`, `fitted_params_virgin.json`;
on PASS, virgin predictions
`league/BO-PrimeraDivision/predictions/k_bo_virgin_predictions.csv`
(FT + halves via the frozen cards constant 0.3739, presentation only).
Verdict: `league/BO-PrimeraDivision/reports/K_BO_VERDICT.md`.
Production code untouched. No push. No merge.
