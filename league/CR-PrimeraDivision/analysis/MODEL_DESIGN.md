# Phase 4 — Model Design: Costa Rica Primera Division Candidates

Rules of construction (program-wide):

- The architecture is **not invented from zero**. Every candidate names the existing proven model it
  references, states what stays conceptually identical, and lists only the changes this league's EDA
  justifies — each tied to a numbered finding in `EDA.md` with its reliability verdict.
- **1 league = 1 model**, one CSV per league. This league's engines live under
  `league/CR-PrimeraDivision/engine/`, seeded from the proven reference implementations named in its
  candidate section and diverging only as this design justifies in writing, through this league's gate.
- Anything the audits closed stays forbidden (§3 of FEATURES.md), including where this EDA re-tested it.
- **Feature consumption rule (Phase 3.5)**: candidates may use only the features defined in
  `FEATURES.md` §1 and the architectural components delimited in its §2.

Shared validation frame (applies to every candidate; the build phase turns this sketch into a real
pre-registration before any fitting):

- **Fitting scope: regular season only** (`stage == regular`). Playoffs (60 matches) are excluded —
  different format (two-legged ties) and, for cards, missing events in 2021–2024.
- **Dev period (goals)**: seasons 2021/2022–2023/2024, season-blocked walk-forward: 2021/2022 trains,
  2022/2023 and 2023/2024 scored (pooled dev n = 492 regular matches).
- **Dev period (cards)**: reliable era only — 2023/2024 Apertura is warm-up (processed, never scored),
  2023/2024 Clausura scored (n = 132 regular matches). 2022/2023 is excluded from cards entirely (F4).
- **Virgin window, evaluated once, after the design is frozen**: season **2024/2025**, regular only
  (n = 262). 2025/2026 (partial pull + format change to 10 teams) and 2026/2027 (in progress) are
  reserved as the confirmatory virgin windows, evaluated once when complete.
- Design-level aggregates were inspected across all seasons during EDA (that is what EDA is); the virgin
  window is virgin for **fitting, feature selection among arms, and gate setting**. No parameter may be
  tuned on it. (The frozen halves constants in F3 are design-level aggregates in the J1 precedent.)
- Baselines every candidate must beat on dev walk-forward: the league base rate and the naive
  trailing-10, plus Gate Zero below.
- **Gate Zero**: the unmodified reference architecture, fitted per league, is itself an arm. A candidate
  whose justified changes do not beat (or at least match within the both-pass rule) its own reference
  arm does not ship its changes. Both CR candidates are Gate Zero only (no variant arm exists — see below),
  so the gate reduces to Gate Zero vs the baselines on dev, and Gate Zero vs the best baseline + the
  calibration leg on virgin.
- Both-pass rule: if base arm and variant arm both pass the gate legs, the arm with the lower pooled
  log-loss ships. With a single arm per candidate, the rule is vacuous and recorded as such.

## 1. Candidate G-CR — Costa Rica goals model (1X2 / OU / BTTS / DC)

(a) **Reference**: the production goals model — Dixon-Coles fit as used market-free in the experiments
(per-division rho, blend observation 0.5·goals + 0.5·xG with goals-only fallback, exponential time
decay), and its walk-forward harness (J1 engine `league/J1/engine/goals/` is the closest in-program
copy of the pattern).

(b) **Identical**: DC estimation pattern and rho; Poisson family with DC low-score correction;
time-decay fitting (half-life 270 days, production value, frozen); the walk-forward evaluation harness
and its log-loss/RPS + calibration gate legs.

(c) **EDA-justified changes**: none beyond the reference's own fallback. The blend degrades to
goals-only for this league because no xG exists (F4/coverage) — the reference's documented fallback,
not a new design. No cross-tier prior (FEATURES X2 — no second tier in the warehouse); no thin-history
shrinkage variant (F5 — the G-J2 post-mortem band 1–9 prior matches is empty in-window; each target
season's only thin-history team has exactly 0 prior matches and already starts at the league mean).
Team traits are reliable (F2: goals-for r = 0.795, goals-against r = 0.793), so a scores-only ratings
fit has real signal — this is the entire justification for building a goals model where no other market
can exist.

(d) **Forbidden here**: half-share anything (F3); finishing/form features (unmeasurable — no xG);
absence features (FEATURES R6); standings/h2h snapshots as features (post-match leakage).

**NOT built if**: dev walk-forward fails to beat the base-rate baseline on RPS/LL, or the virgin readout
breaches the calibration leg.

## 2. Candidate K-CR — Costa Rica cards model (yellows)

(a) **Reference**: `model_cards.py` — yellow-card count model (team card ratings, count distribution;
referee not used in production). Its experiment recipe supplies the baseline definitions and the
NB-size estimation formula, unchanged. (J1 engine `league/J1/engine/cards/` is the closest in-program
copy, minus its referee arm.)

(b) **Identical**: target (yellows only — `Yellow` + `YellowRed` events per Phase 2, reds excluded,
design §5d of J1's design); estimation pattern (decayed team card rates, venue-split attack/defence,
shrinkage to the league mean, Negative Binomial count distribution); harness; LL@lines + calibration
gates. Primary line **4.5** (reliable-era mean 4.47; over-rate 48.9%), secondary lines **3.5**
(over-rate 63.7%) and **5.5** (over-rate 32.0%).

(c) **EDA-justified changes**: none beyond the reference. No referee arm is possible (F6 — identity
absent in 1,328/1,350 matches). The reliable-era restriction (2023/2024 onward, F4) is a data-scope
fact, not a model change: the dev window is 2023/2024 split Apertura-warm-up / Clausura-scored.

(d) **Forbidden**: red-card modelling as a target (0.22 per match — a rare-event count the production
design also excludes); any use of 2021/2022–2022/2023 card data (F4 — feed broken/patchy).

**NOT built if**: the dev gate fails (pooled dev LL@4.5 must beat both baselines) or the virgin
calibration leg fails.

## 3. NOT candidates — SOT / corners / total shots

Targets do not exist in the data: `content.stats` is null in every match, `shotmap.shots` is empty.
There is no SOT model, no corners model and no total-shots model for this league, and none can be built
until FotMob carries the underlying stats. Building any of them anyway would break the gate rule
(the virgin window contains no such targets at all — cf. J1's C-J2 ruling).

## 4. Halves presentation

Where a product ships, it presents FT + 1H/2H via the frozen CR constants (F3): goals 1H share **0.460**,
yellows 1H share **0.379**, presentation only, Poisson/NB plumbing mirroring production's halves
products. Per-match or per-team half modelling remains forbidden.

## 5. Global forbidden list (audits + this EDA; no candidate may use)

1. Half-share modelling or correction of any kind, for any stat (halves audit, top-5; replicated here
   as F3). Frozen league constants are the only permitted halves mechanism.
2. Lineup/absence features for SOT (V8/V10, top-5; no reopening evidence here).
3. Trailing finishing / conversion / on-target-rate "form" features (unmeasurable here — no xG/shots/SOT).
4. Two-stage generative SOT distributions (V11 failure stands; nothing here revives it).
5. Post-match snapshot features (`content.table`, `h2h`, teamForm) — leakage by construction.
6. Divergence from the reference architectures WITHOUT a written design justification in this document
   and a pass through this league's own gate.
7. Any feature whose only support is a within-sample pattern without a reliability check.
