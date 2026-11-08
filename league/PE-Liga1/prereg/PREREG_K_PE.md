# Pre-registration — K-PE (PE-Liga1 cards)

Frozen: 2026-11-10, before any fitting. Branch `build/pe-liga1`.
Design authority: `league/PE-Liga1/analysis/MODEL_DESIGN.md` (K-PE);
features per `analysis/FEATURES.md` (X5 adopted; **X8 ADOPTED** —
cards-era referee coverage 97.9% (2023) / 84.6% (2024) / 80.5%
(virgin 2025) and strictness split-half r = 0.769 on 2023–2024,
EDA F8); evidence per `analysis/EDA.md` (F1/F2/F-feed-1/F8).
Reference: production `model_cards.py` pattern, ported as in
`league/CO-PrimeraA/prereg/PREREG_K_COA.md` (Gate Zero) and
`league/J1/engine/cards/` (the X8 referee mechanics).

## Target — event-unified yellows, era 2023+ (frozen BEFORE fitting)

`y = ev_yellow_inc2nd_home + ev_yellow_inc2nd_away` (each Yellow = 1,
each YellowRed = 1 additional yellow), from the CSV's event-derived
columns. The feed check (EDA F-feed-1, run before any fitting)
showed the programme's stats-vs-events artefact in an era-flipped
form: in 2021–2022 payloads the event feed carries **no plain-yellow
Card events at all** (events undercount stats by ~4.9/match), while
from 2023 events slightly exceed the stats feed (+0.23…+0.32/match,
the familiar stats-undercount direction). The stats feed cannot be
the target either: it exists only in rich matches, which number
**zero in every dev Clausura block**. The target is therefore the
event-unified count, and the candidate's era starts at
2023 - Apertura. The harness must not load earlier rows for this
candidate.

## Data and windows (measured before freezing)

Source: `league/PE-Liga1/data/pe_liga1_matches.csv`, modelling
corpus (regular, non-awarded), era 2023 onward only. Cards-era dev
mean (2023–2024) 4.909 → **primary line 4.5** (secondary
3.5/5.5/6.5 reported, as in the reference harness shifted to this
league's level).

- Seed (training only): 2023 - Apertura (n = 165).
- Dev eval blocks: 2023 - Clausura … 2024 - Clausura (3 blocks,
  n = 475), chronological online walk-forward as in the reference
  harness (decayed state, HL = 270, K_PRIOR = 8).
- **Virgin: calendar 2025 (n = 323)** — read ONCE, only for arms
  passing the dev gate, after dev results freeze. 2026 is NOT read
  anywhere in this build.

## Arms

1. **Gate Zero** — the unmodified production cards pattern
   (decayed team attack/defence state + NB total; r estimated on
   the seed block per method, as in the reference harness).
2. **X8** — Gate Zero plus the referee multiplier, exactly as in
   the J1/CO-A cards engines: for the appointed referee, trailing
   mean of event-unified yellows within this league (matches
   strictly before kickoff), shrunk toward the running league mean
   with K_REF = 8; multiplier = clamp(rate / league_mean, 0.67,
   1.50); referees with no prior in-league matches — and matches
   with no named referee — get factor 1.0. Operational condition:
   if the appointment is not published pre-match in the live
   pipeline, the fixture falls back to Gate Zero.

Baselines: league base rate at 4.5 (pooled rate strictly prior to
the scored block) and naive trailing-10 (reference-harness
definition).

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@4.5 of an arm must beat BOTH baselines, else the arm is dead. Virgin legs — (i) LL leg: arm's virgin LL@4.5 ≤ Gate Zero's AND ≤ both baselines'; (ii) calibration leg: |mean predicted P(over 4.5) − actual over-rate| ≤ 1.0pp clean PASS; a breach within 1 SE of the boundary is recorded PROVISIONAL PASS, beyond it FAIL (SE = sd(p_i − y_i)/√n); (iii) per-season sign check on dev (arm LL ≤ Gate Zero LL in at least half the dev seasons) for the both-pass rule. Both-pass rule: if Gate Zero and a variant both pass all legs, the lower virgin LL ships; if only one passes, it ships; if none passes, K-PE verdict is FAIL and nothing ships.

Variant arms require leg (iii); Gate Zero is exempt. Ties go to the
simpler arm (Gate Zero before X8). If Gate Zero fails its own dev
gate, variants are moot, verdict FAIL, virgin NOT read. Calibration
is reported as actual − predicted; the gate uses |breach|.

## Outputs

Engine `league/PE-Liga1/engine/cards/` (+ README);
`results_dev.json`, `results_virgin.json`, `fitted_params_virgin.json`;
on PASS, virgin predictions
`league/PE-Liga1/predictions/k_pe_virgin_predictions.csv`
(FT + halves via the frozen cards constant 0.3818, presentation only).
Verdict: `league/PE-Liga1/reports/K_PE_VERDICT.md`.
Production code untouched. No push. No merge.
