# Phase 4 — Model Design: AM-PremierLeague Candidates

Rules of construction (program structure decision 2026-11-09):
the architecture is **not invented from zero**. The one candidate
names the existing proven model it references, states what stays
conceptually identical, and lists only the changes the AM EDA
justifies — each tied to a numbered finding in `EDA.md` with its
reliability verdict. Anything the audits closed stays forbidden
(FEATURES.md §3). Feature consumption rule (Phase 3.5): the
candidate may use only the features defined in `FEATURES.md` §1
and the architectural components delimited in its §2.

Shared validation frame (applies to the candidate; the build phase
turns this sketch into a real pre-registration before any fitting):

- **Dev period** (walk-forward, expanding window, season-blocked):
  seed season 2021/2022 (fit history, never scored); scored folds
  2022/2023, 2023/2024, 2024/2025, 2025/2026 (n=653 awarded-excluded
  matches: 180 + 180 + 158 + 135; the 7 awarded matches are excluded
  everywhere).
- **Virgin window, evaluated once, after the design is frozen**:
  season 2026/2027 (in progress, rounds 1–13 + one early round-15
  fixture, n=77 as of 2026-11-08). Marked **TRANSITIONAL** like
  J1's 2026: read ONCE for dev-passing arms only, with a
  confirmatory re-read reserved for season end.
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

## 1. Candidate G-AM — AM-PremierLeague goals model (1X2 / OU / BTTS / DC)

(a) **Reference**: the production goals model — Dixon-Coles fit as
used market-free in the experiments (per-fit rho from the
production grid, goals observation with the blend's goals-only
fallback, exponential time decay), and its walk-forward harness.
Production reference: `model_v2.py` (class `DC`, `probs`),
config `v2_config.json` (hl = 270). Engine port pattern:
`league/AL-KategoriaSuperiore/engine/goals/` (the closest sibling:
also scores-only, also Gate Zero + SHRINK).

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
     (`a *= n/6`, `d *= n/6`). **F2 (STRONG)** — team traits are
     strong (split-half GF 0.78 / GA 0.76) and the tier gap is
     steep (top +1.17 to bottom −1.42 GD/match), so a new club
     fitted on a handful of matches can carry an extreme rating
     — the thin-data risk is live here, unlike in AL — plus
     **F4** — no mover offset is estimable (no sibling tier), so
     shrinkage is the thin-data treatment. This is the
     sanctioned G-J2-lesson arm, already used in G-AE, G-BA and
     G-AL. It is a variant arm to be gated against Gate Zero, not
     part of the base design. Expected degenerate under
     season-blocked expanding fits (prior counts 0 or ≥27) — if
     the two arms come out identical, that is a design note, not
     a defect.
  2. *Awarded matches excluded* from every fit and evaluation
     (7 matches, all 2024/2025, all involving West Armenia;
     DATA_UNDERSTANDING §4 quirk 1). They are administrative
     3-0/0-3 scorelines, six of them never played.
  Nothing else changes. In particular the decay half-life (270
  days) is frozen — no search. The changing team count (9 → 10 →
  10 → 11 → 10 → 12) and games-per-team (32/36/36/30/27) are
  format facts the ratings fit absorbs (teams enter/leave; unseen
  teams start at the league mean, shrunk per X2-SHRINK where
  applicable) — no format-specific adjustment is made.

(d) **Forbidden here**: half-share anything (F3); finishing/form
features (no xG/shots exist); absence features (F6/R6);
standings/h2h snapshots as features (post-match leakage, R9);
any feature from FEATURES.md §3.

**NOT built if**: dev walk-forward fails to beat the climatology
baseline on LL/RPS/OU-LL, or the virgin readout breaches the
calibration leg — and the SHRINK arm is dropped (base may still
ship) if it does not beat Gate Zero on dev. Note the honest
pre-fit expectation from F2: team traits are strong, so a dev
pass is a live possibility here — the opposite of AL, where the
pre-fit expectation was failure. A FAIL verdict would still be a
complete outcome.

**Regular-phase scope (frozen)**: the model covers the regular
season only — which in this league is the whole season in every
season (rounds 1–36, plain integers; no split-group,
championship/relegation round, or playoff exists). The format
changes are team-count/schedule changes only, documented in
DATA_UNDERSTANDING §3, and are in scope as format facts.

## 2. Candidates S-AM / C-AM / K-AM / T-AM — NOT BUILDABLE

SOT, corners, cards, and total shots do not exist in this league's
data in any season (stats null 881/881; shotmap empty 881/881;
0 Yellow events; referee empty 881/881; lineups 0/881 with real
content). Per the template, a candidate requires (a) the target to
exist in the data AND (b) a valid virgin window containing the
target. Both fail for all four. They are recorded as not buildable
in `prereg/PREREG_SCKT_NOT_BUILDABLE.md` (written in Phase A,
before any fitting) and no engine, dev run, or virgin read exists
for them.
