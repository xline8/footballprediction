# Pre-registration — K-VE (VE-PrimeraDivision cards)

Frozen: 2026-11-10, before any fitting. Branch `build/ve-primera`.
Design authority: `analysis/MODEL_DESIGN.md` (K-VE); features per
`analysis/FEATURES.md` (X5 adopted; **X8 DROPPED** — referees named
in only 87/233 matches in 2025 and 145/227 in 2026, and yellows exist
only in the stats era, so no multi-season referee reliability check
is runnable); evidence per `analysis/EDA.md` (yellows traits
for/against r=.156/.587 pooled — the for-trait is weak, the dev gate
decides).
Reference: production `model_cards.py` pattern, ported as in
`league/J1/engine/cards/` / `league/BO-PrimeraDivision/engine/cards/`.

## Target — stats yellows (frozen BEFORE fitting)

`y = yellow_cards_home + yellow_cards_away` (stats feed, player
cards). The event feed is NOT the target: the pre-fitting feed check
on dev-era evidence only (DATA_UNDERSTANDING.md / EDA.md) showed
event cards are ~absent before 2026 (2025 Clausura: 3 event-unified
vs 370 stats yellows; exact agreement 0/62) and overcount stats in
2026 (1,388 vs 1,276; exact 155/226), plausibly staff/bench cards.
This is the VE artefact precedent; the target decision was taken and
documented before any fitting and before any virgin read. The stats
feed has two tiers in 2025: yellows exist only in the 62 full-feed
Clausura matches (the 55 reduced-feed matches carry possession,
total shots, SOT and corners only) — the K target is missing (not
zero) outside the full-feed matches, and the min-6 trailing rule
absorbs that.

## Data and windows (measured before freezing)

Source: `league/VE-PrimeraDivision/data/ve_matches.csv`.
Dev-era (2026 Apertura regular) stats-yellows mean 6.1648 →
**primary line 6.5** (secondary 5.5/7.5 as in the reference harness).

- Seed (training only): 2025 Clausura regular (n = 91 matches, of
  which 62 carry yellows).
- Dev eval blocks: 2026 Apertura regular in two expanding blocks,
  rounds 1–7 (n = 49) and rounds 8–13 (n = 42); train on all prior
  stats-era regular matches; n = 91 scored.
- **Virgin: 2026 Clausura regular, TRANSITIONAL (n = 91, complete
  phase; season in progress)** — read ONCE, only if the (single) arm
  passes the dev gate, after dev results freeze. Season-end
  confirmatory read outstanding.
  NOTE (known before the read, descriptive only): the virgin mean is
  5.01 yellows/match vs 6.16 in dev (yellows fall through 2026 while
  shots rise); the calibration leg is expected to be hard, and the
  gate decides.
- The harness's dev mode must not read 2026 Clausura rows.

## Arms

1. **Gate Zero** — the unmodified production cards pattern (single
   arm by design; no variant exists for this candidate).

Baselines: league base rate at 6.5 (pooled stats-era rate strictly
prior to the scored block) and naive trailing-10.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@6.5 of Gate Zero must beat BOTH baselines, else the candidate is dead and the virgin is NOT read. Virgin legs — (i) LL leg: Gate Zero's virgin LL@6.5 ≤ both baselines'; (ii) calibration leg: |mean predicted P(over 6.5) − actual over-rate| ≤ 1.0pp clean PASS; a breach within 1 SE of the boundary is recorded PROVISIONAL PASS, beyond it FAIL (SE = sd(p_i − y_i)/√n). If both virgin legs pass, K-VE verdict is PASS (PROVISIONAL if leg (ii) is provisional, or by the transitional-virgin note) and Gate Zero ships; otherwise FAIL and nothing ships.

## Outputs

Engine `league/VE-PrimeraDivision/engine/cards/` (+ README);
`results_dev.json`, `results_virgin.json`, `fitted_params_virgin.json`;
on PASS, virgin predictions
`league/VE-PrimeraDivision/predictions/k_ve_virgin_predictions.csv`
(FT + halves via the frozen cards constant 0.3900, presentation only).
Verdict: `league/VE-PrimeraDivision/reports/K_VE_VERDICT.md`.
Production code untouched. No push. No merge.
