# Pre-registration — G-J2 (J2 goals model)

Frozen: 2026-11-09, before any fitting. Branch `build/g-j2`.
Governed by `league/J1/analysis/MODEL_DESIGN.md` §2 (G-J2), the shared
validation frame in its preamble, and §7b. This document turns that
sketch into the binding gate for this candidate. Nothing in it may be
changed after fitting begins; amendments, if any, are appended as a
dated section, never edited into the frozen text.

## 1. Product scope

- J2 goals model, **full-time only**: 1X2, OU 2.5 (plus the other
  full-time derivatives the score matrix yields, reported but not
  gated). No halves presentation of any kind for J2.
- J2 has **no xG** (EDA F13). The production blend therefore degrades
  to goals-only — the reference implementation's own documented
  fallback, not a new design.

## 2. Reference architecture (both arms)

The production Dixon-Coles pattern as in `model_v2.py`, copied into
J2's own engine (`league/J2/engine/goals/`) per the per-league-engines
decision (MODEL_DESIGN §7b.5):

- Attack/defence log-ratings per team, home advantage `h`, low-score
  correction `tau` with `rho` chosen per fit on the production grid
  `(0.0, -0.05, -0.10, -0.15)` by weighted fit log-likelihood.
- Iterative fitting exactly as production: 14 sweeps, damping 0.7,
  +0.25 smoothing, exponential time decay with half-life **270 days**
  (the production `v2_config.json` value, frozen here — not tuned),
  training window capped at the most recent 4000 matches.
- Observation = goals only (no xG exists in J2).
- Score matrix 0–10 per side, normalised; 1X2 / OU2.5 read off it.

## 3. Data and evaluation frame

- Inputs: `league/J2/data/j2_matches.csv` (J2 matches), plus
  `league/J1/data/j1_matches.csv` and `league/J3/data/j3_matches.csv`
  used **only** for mover identification and movers' previous-tier
  scoring rates (Arm X2). Season `2026/2027` rows are excluded from
  everything (not dev, not virgin, not training).
- **Dev**: walk-forward, expanding window, monthly refit groups,
  seasons **2021–2024**, exactly the production `run_wf` semantics:
  for each calendar month, fit on all J2 matches with date strictly
  before the month start, then predict that month's matches.
  The first month (2021-02) has no prior data in the corpus and is
  **excluded from scored dev for all arms and baselines**.
- **Virgin**: season **2025** (n=383). Read **once**, after the dev
  results are frozen and the shipped-arm logic below is fixed.
  Evaluated with the same monthly walk-forward (fit on all matches
  strictly before each 2025 month start, expanding). No parameter,
  threshold, or design choice may be tuned on it.
- Team identity is FotMob `team_id` (names are display only).

## 4. Arms

### Gate Zero
The unmodified reference architecture above. A team with no J2
training matches starts at the league mean (attack = defence = 0).

### Arm X2 — cross-tier priors (feature X2, FEATURES.md §1)
Identical to Gate Zero except for the entry prior of **movers**: a
club whose previous completed season was in a different J.League tier
(J1 or J3, by `team_id` membership in that league's table for season
S−1) and which plays in J2 in season S.

- Prior, computed per fit from data strictly before the predicted
  month, using the mover's previous-tier season (S−1) per-match
  goals for (GF) and against (GA), adjusted by the measured tier gap
  from `league/J1/analysis/eda_summary.json` (`cross_tier`, EDA F4):
  - Promoted J3→J2 (`j3->j2.promoted`, n=9): GF −0.477, GA +0.560.
  - Relegated J1→J2 (`j2->j1.relegated` read in the J2 direction,
    n=10): GF +0.485, GA −0.550.
- With L = mean goals per team-match in the J2 training data,
  adjusted rates clamped to [0.3, 3.0]:
  `a_init = ln(adj_GF / L)`, `d_init = ln(adj_GA / L)`.
  These replace the 0/0 start for that team in the fit's sweeps; the
  sweeps then proceed exactly as Gate Zero, so the mover's own J2
  data takes over as it accumulates. A mover with no J2 training
  matches yet keeps exactly this prior — that is the intervention.
- Leakage guard (FEATURES.md X2): the offset and rates for season S
  use only transitions and matches completed before season S; a
  club's own current-season matches never inform its entry prior.
  Movers into J2 for 2021 have no 2020 data in the corpus, so they
  receive no prior (league mean, as Gate Zero) — recorded, not
  patched.

## 5. Baselines

- **Climatology** (for 1X2 LL / RPS): constant H/D/A probabilities
  equal to the outcome frequencies in all J2 matches strictly before
  the predicted month.
- **Base rate** (for OU2.5 LL): constant over-2.5 probability equal
  to the over rate in all J2 matches strictly before the predicted
  month.

## 6. Metrics

- 1X2 log-loss (mean −ln p of the actual outcome) and RPS (ordered
  H–D–A cumulative), pooled and per season.
- OU2.5 log-loss (binary, on the matrix's over probability).
- Calibration on the virgin window: mean predicted vs actual rate
  for home wins and for over 2.5, with standard errors
  `SE = sqrt(var(pred)/n + p_act(1−p_act)/n)`.

## 7. Gate legs (verbatim, binding)

Dev gate — pooled dev 1X2 LL and RPS beat climatology and OU2.5 LL beats base rate, else arm dead.

Virgin legs — (i) LL leg: virgin 1X2 LL ≤ Gate Zero's AND ≤ climatology's; (ii) calibration leg: |mean predicted − actual| ≤ 1.0pp pooled for home-win rate and OU2.5 over-rate, SEs reported; breach within 1 SE = PROVISIONAL PASS, beyond = FAIL; (iii) per-season sign check on dev for the both-pass rule.

Both-pass: if Gate Zero and X2 both pass, lower pooled virgin LL ships; one passes → it ships; none → FAIL, nothing ships.

Operationalisation of leg (iii), fixed here before fitting: an arm
is eligible for the both-pass rule only if its dev 1X2 LL beats
climatology in at least 3 of the 4 dev seasons (2021–2024, scored
months). An arm that passes legs (i)–(ii) but fails (iii) may still
ship if it is the *only* arm passing (i)–(ii); leg (iii) decides
eligibility only when both arms pass. For Gate Zero itself, leg (i)
reduces to virgin LL ≤ climatology's. A PROVISIONAL PASS on leg (ii)
counts as a pass for shipping and is flagged as provisional in the
verdict.

## 8. Outputs

- Dev results per arm per season (JSON + table in the verdict).
- Fitted parameters per arm from the final pre-virgin fit (trained
  through 2024-12-31): ratings, home advantage, rho.
- Virgin predictions: `league/J2/predictions/g_j2_virgin_predictions.csv`
  — one row per 2025 match, full-time probabilities only (1X2, OU2.5,
  lambdas, arm label; both arms' predictions retained in the file so
  the verdict is auditable, shipped arm marked).
- Verdict: `league/J2/reports/G_J2_VERDICT.md` with per-leg PASS/FAIL
  per arm and the shipped arm named.

## 9. Forbidden

Per MODEL_DESIGN §2(d) and §7: no half-share modelling, no
finishing/form or absence features, no post-match snapshot features,
no feature outside FEATURES.md §1, no tuning on the virgin window,
no production files touched, no push.
