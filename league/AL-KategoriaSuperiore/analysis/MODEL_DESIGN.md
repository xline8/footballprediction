# Phase 4 — Model Design: AL-KategoriaSuperiore Candidates

Rules of construction (program structure decision 2026-11-09):
the architecture is **not invented from zero**. The one candidate
names the existing proven model it references, states what stays
conceptually identical, and lists only the changes the AL EDA
justifies — each tied to a numbered finding in `EDA.md` with its
reliability verdict. Anything the audits closed stays forbidden
(FEATURES.md §3). Feature consumption rule (Phase 3.5): the
candidate may use only the features defined in `FEATURES.md` §1
and the architectural components delimited in its §2.

Shared validation frame (applies to the candidate; the build phase
turns this sketch into a real pre-registration before any fitting):

- **Dev period** (walk-forward, expanding window, season-blocked):
  seed season 2021/2022 (fit history, never scored); scored folds
  2022/2023, 2023/2024, 2024/2025, 2025/2026 (n=720 regular-season
  matches; the 14 playoff matches are excluded everywhere).
- **Virgin window, evaluated once, after the design is frozen**:
  season 2026/2027 (in progress, rounds 1–11, n=55 as of 2026-11-08).
  Marked **TRANSITIONAL** like J1's 2026: read ONCE for dev-passing
  arms only, with a confirmatory re-read reserved for season end.
- Design-level aggregates were inspected across all seasons during
  EDA (that is what EDA is); the virgin window is virgin for
  **fitting, feature selection among arms, and gate setting**. No
  parameter may be tuned on it.
- Baselines the candidate must beat on dev walk-forward: the league
  base rate (climatology) and the naive trailing-10 (X5).
- **Gate Zero**: the unmodified reference architecture, fitted per
  league, is itself an arm. A candidate whose justified changes do
  not beat (or at least match within the both-pass rule) its own
  reference arm does not ship its changes.
- Both-pass rule: if base arm and variant arm both pass the gate
  legs (log-loss leg + calibration leg at ±1.0pp pooled on the
  virgin window, per-season sign check), the arm with the lower
  pooled virgin log-loss ships.

## 1. Candidate G-AL — AL-KategoriaSuperiore goals model (1X2 / OU / BTTS / DC)

(a) **Reference**: the production goals model — Dixon-Coles fit as
used market-free in the experiments (per-fit rho from the
production grid, goals observation with the blend's goals-only
fallback, exponential time decay), and its walk-forward harness.
Production reference: `model_v2.py` (class `DC`, `probs`),
config `v2_config.json` (hl = 270). Engine port pattern:
`league/BA-PremierLeague/engine/goals/` (the closest sibling: also
scores-only, also Gate Zero + SHRINK).

(b) **Identical**: DC estimation pattern and rho; Poisson family
with DC low-score correction; time-decay fitting; the walk-forward
evaluation harness and its log-loss/RPS + calibration gate legs.
The blend degrades to goals-only for this league because no xG
exists anywhere in it (F13) — the reference's own documented
fallback, not a new design.

(c) **EDA-justified changes**:
  1. *Thin-history shrinkage* (feature **X2-SHRINK**). Clubs with
     fewer than 6 prior in-league matches in the training window
     have their fitted ratings shrunk toward the league mean
     (`a *= n/6`, `d *= n/6`). **F2 (WEAK)** — team traits are
     faint (split-half GF 0.27 / GA 0.14) and the tier gap is
     shallow, so the shrinkage matters less here than in J2, but
     the thin-data shape is the same (2 new clubs per season) —
     plus **F4** — no mover offset is estimable (no sibling tier),
     so shrinkage is the thin-data treatment. This is the
     sanctioned G-J2-lesson arm, already used in G-AE and G-BA.
     It is a variant arm to be gated against Gate Zero, not part
     of the base design. Expected degenerate under season-blocked
     expanding fits (prior counts 0 or ≥36) — if the two arms come
     out identical, that is a design note, not a defect.
  2. *Playoff matches excluded* from every fit and evaluation
     (14 matches; DATA_UNDERSTANDING §3 quirk 1). They are a
     knockout / top-4 mini-league, not the 36-round regular season.
  Nothing else changes. In particular the decay half-life (270
  days) is frozen — no search.

(d) **Forbidden here**: half-share anything (F3); finishing/form
features (no xG/shots exist); absence features (F6/R6);
standings/h2h snapshots as features (post-match leakage, R9);
any feature from FEATURES.md §3.

**NOT built if**: dev walk-forward fails to beat the climatology
baseline on LL/RPS/OU-LL, or the virgin readout breaches the
calibration leg — and the SHRINK arm is dropped (base may still
ship) if it does not beat Gate Zero on dev. Note the honest
pre-fit expectation from F2: team traits are weak, so a dev
failure is a live possibility and a FAIL verdict is a complete
outcome.

**Regular-phase scope (frozen)**: the model covers the 36-round
regular season only (rounds 1–36, 10 teams). The Final Four
playoff from 2023/2024 (semi-finals + bronze + final in 2023/24
and 2024/25; a 6-match round-robin in 2025/26, mislabelled rounds
1–3) is out of scope: different format, top-4 only, single-leg or
mini-league. The format has no split-group, championship, or
relegation round — the regular season is plain rounds 1–36 in
every season. Two-club churn per season is handled by the ratings
fit itself (teams enter/leave; unseen teams start at the league
mean, shrunk per X2-SHRINK where applicable).

## 2. Candidates S-AL / C-AL / K-AL / T-AL — NOT BUILDABLE

SOT, corners, cards, and total shots do not exist in this league's
data in any season (stats null 969/969; shotmap empty 969/969;
0 Yellow events; referee empty 969/969; lineups 0/969).
Per the template, a candidate requires (a) the target to exist in
the data AND (b) a valid virgin window containing the target.
Both fail for all four. They are recorded as not buildable in
`prereg/PREREG_SCKT_NOT_BUILDABLE.md` (written in Phase A, before
any fitting) and no engine, dev run, or virgin read exists for them.
