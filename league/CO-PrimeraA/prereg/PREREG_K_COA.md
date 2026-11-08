# Pre-registration — K-COA (CO-PrimeraA cards)

Frozen: 2026-11-09, before any fitting. Branch `build/co-primeraa`.
Design authority: `league/CO-PrimeraA/analysis/MODEL_DESIGN.md`
(K-COA); features per `analysis/FEATURES.md` (X5 adopted; **X8
ADOPTED** — cards-era referee appointment coverage is 0.94 and
strictness split-half r = 0.487 on 36 referees, EDA F5; the PY
drop rationale — 11.1% coverage — does not apply here); evidence
per `analysis/EDA.md` (F1/F2/F5). Reference: production
`model_cards.py` pattern, ported as in
`league/PY-DivisionProfesional/prereg/PREREG_K_PY.md` (Gate Zero)
and `league/J1/engine/cards/` (the X8 referee mechanics).

## Target — event-unified yellows (frozen BEFORE fitting)

`y = ev_yellow_inc2nd_home + ev_yellow_inc2nd_away` (each Yellow = 1,
each YellowRed = 1 additional yellow), from the CSV's event-derived
columns. The stats-feed `yellow_cards` columns are NOT the target:
the pre-fitting feed check (DATA_UNDERSTANDING.md) showed card
events are absent in 2021–2022 while the stats feed's own level
breaks inside 2022 (4.22 → 2.67 → 5.14 per match across
2022-Ap/2022-Cl/2023-Ap) — the stats yellows of 2021–2022 are not
the same quantity as later ones. From 2023 - Apertura the event
feed is complete-looking and tracks the stats feed (stats ~0.1–0.2
below unified events, the familiar undercount direction). This is
the programme's cards artefact in its seventh league; the target
and era decisions were taken and documented before any fitting and
before any virgin read.

## Data and windows (measured before freezing)

Source: `league/CO-PrimeraA/data/co_primeraa_matches.csv`, era
2023 - Apertura onward only (the harness must not load earlier
rows for this candidate). Dev-era (2024–2025 blocks) event-unified
mean 5.60 → **primary line 5.5** (secondary 3.5/4.5/6.5 reported;
the reference harness's line set is shifted to this league's level).

- Seed (training only): 2023 - Apertura (n = 226).
- Dev eval blocks: 2023 - Clausura … 2025 - Clausura (5 tournaments,
  n = 1,110), chronological online walk-forward as in the reference
  harness (decayed state, HL = 270, K_PRIOR = 8).
- **Virgin: 2026 - Apertura (n = 204, complete)** — read ONCE, only
  for arms passing the dev gate, after dev results freeze.
  2026 - Clausura (in progress) is NOT read anywhere in this build.

## Arms

1. **Gate Zero** — the unmodified production cards pattern
   (decayed team attack/defence state + NB total; r estimated on
   the seed block per method, as in the reference harness).
2. **X8** — Gate Zero plus the referee multiplier, exactly as in
   the J1 cards engine: for the appointed referee, trailing mean
   of event-unified yellows within this league (matches strictly
   before kickoff), shrunk toward the running league mean with
   K_REF = 8; multiplier = clamp(rate / league_mean, 0.67, 1.50)
   applied to both teams' expectations. Referees with <8 prior
   era matches, or no named referee, fall back to Gate Zero for
   that fixture (multiplier 1.0, fallback recorded — no imputation).

Baselines: league base rate at 5.5 (the model's running league-mean
state — the reference harness's `base` method) and naive
trailing-10 (reference-harness definition).

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@5.5 of an arm must beat BOTH baselines, else the arm is dead. Virgin legs — (i) LL leg: arm's virgin LL@5.5 ≤ Gate Zero's AND ≤ both baselines'; (ii) calibration leg: |mean predicted P(over 5.5) − actual over-rate| ≤ 1.0pp clean PASS; a breach within 1 SE of the boundary is recorded PROVISIONAL PASS, beyond it FAIL (SE = sd(p_i − y_i)/√n); (iii) per-season sign check on dev (arm LL ≤ Gate Zero LL in at least half the dev seasons) for the both-pass rule. Both-pass rule: if Gate Zero and a variant both pass all legs, the lower virgin LL ships; if only one passes, it ships; if none passes, K-COA verdict is FAIL and nothing ships.

Variant arms require leg (iii); Gate Zero is exempt. Ties go to the
simpler arm (Gate Zero before X8). If Gate Zero fails its own dev
gate, variants are moot, verdict FAIL, virgin NOT read. Calibration
is reported as actual − predicted; the gate uses |breach|.

## Outputs

Engine `league/CO-PrimeraA/engine/cards/` (+ README);
`results_dev.json`, `results_virgin.json`, `fitted_params_virgin.json`;
on PASS, virgin predictions
`league/CO-PrimeraA/predictions/k_coa_virgin_predictions.csv`
(FT + halves via the frozen cards constant 0.3543, presentation only).
Verdict: `league/CO-PrimeraA/reports/K_COA_VERDICT.md`.
Production code untouched. No push. No merge.
