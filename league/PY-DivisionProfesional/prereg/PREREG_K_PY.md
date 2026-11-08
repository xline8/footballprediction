# Pre-registration — K-PY (PY-DivisionProfesional cards)

Frozen: 2026-11-09, before any fitting. Branch `build/py-division`.
Design authority: `analysis/MODEL_DESIGN.md` (K-PY); features per
`analysis/FEATURES.md` (X5 adopted; **X8 DROPPED** — dev-era referee
appointment coverage is 11.1%: 11.4% / 20.5% / 1.5% by dev tournament,
so a referee arm is inactive on ~89% of dev rows and unvalidatable;
its strictness split-half r = 0.686 rests on 7 referees and is
concentrated in the virgin era, which may not rescue an arm — K-J2
precedent); evidence per `analysis/EDA.md` (F1/F2/F4).
Reference: production `model_cards.py` pattern, ported as in
`league/J1/engine/cards/` / `league/KR-KLeague1/engine/cards/`.

## Target — event-unified yellows (frozen BEFORE fitting)

`y = ev_yellow_inc2nd_home + ev_yellow_inc2nd_away` (each Yellow = 1,
each YellowRed = 1 additional yellow), from the CSV's event-derived
columns. The stats-feed `yellow_cards` columns are NOT the target:
the pre-fitting feed check on dev-era evidence only
(DATA_UNDERSTANDING.md) showed the stats feed undercounts in every
dev season (mean diff −0.356 / −0.386 / −0.344 vs unified events;
exact match only 79.8%). This is the AR/BR/NO/KR artefact; the
target decision was taken and documented before any fitting and
before any virgin read.

## Data and windows (measured before freezing)

Source: `league/PY-DivisionProfesional/data/py_matches.csv`.
Dev-era event-unified mean 4.89 → **primary line 4.5** (secondary
3.5/5.5 as in the reference harness).

- Seed (training only): 2025 - Apertura (n = 132).
- Dev eval blocks: 2025 - Clausura + 2026 - Apertura (n = 264;
  263 scored — the 2026-04-19 clásico has no events either, so its
  cards target is missing; PREPROCESSING §9).
- **Virgin: 2026 - Clausura, TRANSITIONAL (n = 112 played at pull)**
  — read ONCE, only if the (single) arm passes the dev gate, after
  dev results freeze. Season-end confirmatory read outstanding.
- The harness's dev mode must not read 2026 - Clausura rows.

## Arms

1. **Gate Zero** — the unmodified production cards pattern (single
   arm by design; no variant exists for this candidate).

Baselines: league base rate at 4.5 (pooled stats-era rate strictly
prior to the scored block) and naive trailing-10.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@4.5 of Gate Zero must beat BOTH baselines, else the candidate is dead and the virgin is NOT read. Virgin legs — (i) LL leg: Gate Zero's virgin LL@4.5 ≤ both baselines'; (ii) calibration leg: |mean predicted P(over 4.5) − actual over-rate| ≤ 1.0pp clean PASS; a breach within 1 SE of the boundary is recorded PROVISIONAL PASS, beyond it FAIL (SE = sd(p_i − y_i)/√n). If both virgin legs pass, K-PY verdict is PASS (PROVISIONAL if leg (ii) is provisional, or by the transitional-virgin note) and Gate Zero ships; otherwise FAIL and nothing ships.

## Outputs

Engine `league/PY-DivisionProfesional/engine/cards/` (+ README);
`results_dev.json`, `results_virgin.json`, `fitted_params_virgin.json`;
on PASS, virgin predictions
`league/PY-DivisionProfesional/predictions/k_py_virgin_predictions.csv`
(FT + halves via the frozen cards constant 0.327, presentation only).
Verdict: `league/PY-DivisionProfesional/reports/K_PY_VERDICT.md`.
Production code untouched. No push. No merge.
