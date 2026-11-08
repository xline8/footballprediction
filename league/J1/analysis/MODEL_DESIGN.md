# Phase 4 — Model Design: J.League Candidates

Status: **BUILD APPROVED by the user, 2026-11-09 14:38 WIB.** This
document governs the J.League build program (league/J1|J2|J3, tracked in
league/PROGRAM_STATUS.md). The feature set was approved at 14:19 the
same day (§7b). Amendments after approval are recorded in §7b, never
edited silently into the frozen text.

Rules of construction, per the user's refinement (13:54):

- The architecture is **not invented from zero**. Every candidate names
  the existing proven model it references, states what stays
  conceptually identical, and lists only the changes the J.League EDA
  justifies — each tied to a numbered finding in `EDA.md` with its
  reliability verdict.
- **1 league = 1 model**, one CSV per league (Phase 2). Per the user's
  structure decision of 2026-11-09 14:33 (§7b.5, superseding the earlier
  shared-architecture lock): each league has **its own engine** under
  `league/<L>/engine/`, seeded from the proven reference implementation
  named in its candidate section and diverging only as that league's
  own design (this document) justifies in writing, through that
  league's gate. Differences between leagues come from their data,
  their coverage (EDA F13), and their documented design — never from
  undocumented drift.
- Anything the audits closed stays forbidden (§3), including where the
  J.League EDA re-tested it.
- **Feature consumption rule (Phase 3.5)**: candidates may use only
  the features defined in `FEATURES.md` §1 and the architectural
  components delimited in its §2. Features rejected in `FEATURES.md`
  §3 are forbidden even where §7 below does not repeat them, and a
  feature defined nowhere in `FEATURES.md` is not eligible.

Shared validation frame (applies to every candidate; the build phase
turns this sketch into a real pre-registration before any fitting):

- **Dev period** (walk-forward, expanding window, season-blocked):
  J1 = seasons 2021–2025, J2 = 2021–2024, J3 = 2021–2024.
- **Virgin windows, evaluated once, after the design is frozen**:
  J1 = transitional 2026 (complete, n=200; format caveat: shootout
  league — goals/SOT/corners/cards targets are regulation-play and
  unaffected; result markets treat a shootout draw as a draw, matching
  the 90-minute settlement convention) with 2026/27 reserved as the
  confirmatory virgin window, evaluated once when complete;
  J2 = season 2025 (n=383); J3 = season 2025 (n=383).
- Design-level aggregates were inspected across all seasons during
  EDA (that is what EDA is); the virgin windows are virgin for
  **fitting, feature selection among arms, and gate setting**. No
  parameter may be tuned on them.
- Baselines every candidate must beat on dev walk-forward: the league
  base rate and the naive trailing-10 (count markets) / market-free
  base rates (result markets), plus Gate Zero below.
- **Gate Zero**: the unmodified reference architecture, fitted per
  league, is itself an arm. A candidate whose justified changes do
  not beat (or at least match within the both-pass rule) its own
  reference arm does not ship its changes.
- Both-pass rule (copied from the total-shots pre-registrations): if
  base arm and variant arm both pass the gate legs (log-loss leg +
  calibration leg at ±1.0pp pooled on the virgin window, per-season
  sign check), the arm with the lower pooled log-loss ships.

## 1. Candidate G-J1 — J1 goals model (1X2 / OU / BTTS / DC)

(a) **Reference**: the production goals model — Dixon-Coles fit as
used market-free in the experiments (per-division rho, blend
observation 0.5·goals + 0.5·xG with goals-only fallback, exponential
time decay), and its walk-forward harness.

(b) **Identical**: DC estimation pattern and rho; Poisson family with
DC low-score correction; blend-with-fallback observation scheme;
time-decay fitting; the walk-forward evaluation harness and its
log-loss/RPS + calibration gate legs.

(c) **EDA-justified changes**:
  1. *Cross-tier priors for movers* (feature **X2**). When a club
     enters J1 from J2
     (or drops), its initial rating is offset by the measured tier
     gap instead of starting at the league mean — **F4 (SIGNAL)**:
     promoted sides lose ≈0.56 GF and concede ≈0.51 GA per match on
     arrival; the effect is symmetric for relegated sides. Production
     never needed this (no feeder tier inside its fit); J1 does,
     because 3–4 of its 18–20 clubs are movers every season.
  2. *Variant arm: open-play / set-play attack decomposition*
     (features **X3**). The
     xG observation may be split into open-play and set-play
     components with separate attack ratings — **F5
     (SIGNAL-CANDIDATE, split-half r=0.621)**. This is an arm to be
     gated against Gate Zero, not part of the base design.
  3. *2021 enters goals-only* (no xG exists for J1 2021 — coverage
     fact, Phase 1), which the reference blend already handles by
     its documented fallback. No new code concept.
  Nothing else changes. In particular the decay half-life and blend
  weight are fit/validated **per league** inside the harness — that
  is parameter estimation, not an architecture change.

(d) **Forbidden here**: half-share anything (F3); finishing/form
features (F6); absence features (F10); standings/h2h snapshots as
features (post-match leakage).

**NOT built if**: dev walk-forward fails to beat the base-rate
baseline on RPS/LL, or the virgin readout breaches the calibration
leg — and the set-play arm is dropped (base may still ship) if it
does not beat Gate Zero on dev.

## 2. Candidates G-J2 / G-J3 — J2 and J3 goals models

(a) **Reference**: the same production Dixon-Coles pattern as G-J1 —
literally the same architecture, fitted per league (1 league = 1
model).

(b) **Identical**: everything in G-J1(b). The blend degrades to
goals-only for both leagues because neither has xG (F13) — again the
reference's own documented fallback, not a new design.

(c) **EDA-justified changes**: cross-tier priors (feature **X2**) in both directions
and at both steps — **F4 (SIGNAL)** measured at J2→J1 *and* J3→J2
with the same magnitudes, so a J2 fit uses the J3 step for its
promoted clubs and the J1 step for its relegated ones; J3 likewise.
Team traits are reliable in both tiers (**F2**: goals-for r=0.69 /
0.66, goals-against 0.62 / 0.68), so a scores-only ratings fit has
real signal — this is the entire justification for building goals
models where no other market can exist.

(d) **Forbidden**: as G-J1(d). Additionally for J3: no halves
anything (HT missing for 6.8% of matches *and* F3) — a J3 goals
model is a full-time model, full stop.

**NOT built if**: the dev walk-forward gate fails for that league —
each league's model stands or falls on its own gate, per the locked
rule; a J1 pass confers nothing on J2/J3.

## 3. Candidate S-J1 — J1 shots-on-target model

(a) **Reference**: `model_sot.py` **v5** — joint ridge Poisson team
ratings + Negative Binomial (r) + Beta-Binomial on-target ratio with
prior shrinkage, ensembled 50/50 with the naive trailing-10, total-
shots signal included.

(b) **Identical**: the joint estimation pattern, the NB + Beta-
Binomial distribution family, the ensemble, the walk-forward harness
and its LL@lines + calibration gate legs. Target definition = the
stats feed's SOT (blocked shots excluded), Phase 1 §4 — the same
definition family the production SOT model settles against.

(c) **EDA-justified changes**:
  1. *Variant arm: harder shrinkage of the on-target ratio*
     (architectural component, `FEATURES.md` §2 — not a covariate;
     the standalone trailing on-target rate is rejected there as R4).
     **F6** shows the team SOT-rate trait is **NOISE** in J1
     (split-half r=0.06) even though shot volume (0.85) and xG/shot
     (0.44) are real. v5's ratio component must therefore prove
     itself in J1: the prereg includes an arm with the ratio shrunk
     to (near) the league constant, gated against Gate Zero.
  2. *Variant arm: xG/shot as the quality input* (feature **X4**)
     in place of / in
     addition to the raw total-shots signal — **F6
     (SIGNAL-CANDIDATE, r=0.437)**.
  3. *Variant arm, recent era only: attacking xGOT-per-shot trait*
     (feature **X6**, with its era guard) —
     **F7 (SIGNAL-CANDIDATE, r=0.518, 2025+ era only)**. Evaluated
     as an arm on the era where the trait is measurable; the base
     design does not depend on it, and the defensive side is
     excluded (r=0.116, NOISE).

(d) **Forbidden here**: lineup/absence features — F10 re-tested the
question on this corpus and produced **no** new evidence (absence
residual +0.04 ≈ control +0.04, no dose pattern), so per the agreed
standard this is **not** a reopening candidate and is not flagged as
one; trailing conversion/finishing features (F6, NOISE); half-share
SOT modelling (F3) — a halves split, if a product is ever wanted,
uses the frozen J1 league constant 0.448 exactly as production's
SOT-halves plumbing does; the two-stage generative distribution
family (closed by V11 on top-5; nothing in this EDA revives it).

**Scope note**: there is no J.League SOT odds/settlement source in
our system; S-J1 would launch predictions-only, like the production
cards and 1H-corner products did.
**NOT built if**: Gate Zero (unmodified v5 pattern) fails its own
dev gate in J1 — the variants are then moot — or if no arm passes
the virgin calibration leg.

## 4. Candidate C-J1 — J1 corners model

(a) **Reference**: `model_corners_v3` — team corner ratings +
Negative Binomial total, with the adopted territorial multiplier.

(b) **Identical**: ratings + NB pattern, multiplier structure,
walk-forward harness, LL + calibration gates.

(c) **EDA-justified change** (one): the territorial covariate.
Production's multiplier uses possession and big-chance rates
(feature set **X9**, carried unchanged as the Gate Zero arm)
because the spine had nothing better. J1's stats feed carries
opp-box touches, whose team trait is the most stable measured in
this EDA (**F9: split-half r=0.857 for, 0.687 against; per-match
corr with corners
0.471 vs possession's 0.286**). The prereg therefore runs the
multiplier with box-touch rates (feature **X7**) as a variant arm against Gate Zero
(production covariates). No other change.

(d) **Forbidden**: half-share corner modelling (F3 — team 1H corner
share split-half r=0.05, true variance −0.0006; a 1H product, if
ever wanted, follows production's separate-1H-model-or-frozen-split
precedent and is NOT part of this candidate).

**NOT built if**: the box-touch arm does not beat Gate Zero on dev
(base may still ship), or the virgin calibration leg fails.
**J2 corners: NOT a candidate** — corner targets exist only inside
the Sep 2021–Sep 2024 stats window (F13); the J2 virgin window
(2025) contains no corner targets at all, so the candidate could
never be validated. Building it anyway would break the gate rule.
**J3 corners: NOT a candidate** — no data (F13).

## 5. Candidate K-J1 / K-J2 — cards models (J1, J2)

(a) **Reference**: `model_cards.py` — yellow-card count model
(team card ratings, count distribution; referee not used in
production).

(b) **Identical**: target (yellows only — unified `yellow_*` of
Phase 2, whose provenance per league is documented there),
estimation pattern, harness, LL@lines + calibration gates.

(c) **EDA-justified change** (one): *variant arm with a referee
strictness covariate* (feature **X8**) — **F8 (SIGNAL-CANDIDATE, split-half
r=0.646 pooled; r=0.649 on the J1+J2-only recheck in `FEATURES.md`)**, a trait this corpus can measure and the production
model never had. Two binding conditions on the arm: (i) it must
beat Gate Zero on dev walk-forward; (ii) referee assignment must
be known at prediction time in the operational pipeline — an
availability check to perform in the build phase; if referees are
not published pre-match for a fixture, that fixture falls back to
the base arm (the design does not impute referees).

(d) **Forbidden**: red-card modelling as a target (0.08–0.11 per
match — a rare-event count the production design also excludes);
any use of J3 (yellows do not exist there, F13 — **K-J3 is NOT a
candidate**); J1 2021 enters via the event feed per the documented
Phase 2 exception (its stats feed undercounts yellows — a data
provenance fact, not a model change).

**NOT built if**: for J2, the events-based target fails the dev
gate (its provenance differs from J1's stats-first target — the
gate, not optimism, decides); for either league, if the virgin
calibration leg fails.

## 6. Total shots (J1) — candidate T-J1 (deferral overridden by user)

Originally deferred: the reference family (v2 level layer / E9
per-division trailing-r) is under a frozen prospective trial on the
top-5, verdict due at n≥1,200 or season end, and this document
recommended not picking a J1 design before that verdict. **The user
overrode the deferral explicitly (2026-11-09 14:17, reaffirmed in the
14:38 build mandate)** — T-J1 is built now, ahead of the top-5 verdict,
on the J.League corpus only; the top-5 prospective trial is untouched
and neither result contaminates the other (different corpus, different
virgin window, no shared fitting). T-J1's prereg freezes three arms —
the v1 pattern (ratings + NB + naive ensemble), the v2 pattern
(+ level layer), and the E9 mechanism (NB r from a trailing window;
single-league analogue: league-level trailing r) — and records this
provenance in its first paragraph. J1 virgin windows as in the shared
frame (transitional 2026 primary).

## 7. Global forbidden list (audits + this EDA; no candidate may use)

1. Half-share modelling or correction of any kind, for any stat
   (halves audit, top-5; **replicated here as F3**). Frozen league
   constants are the only permitted halves mechanism.
2. Lineup/absence features for SOT (V8/V10, top-5; **replicated
   null here as F10** — the reopening condition agreed with the
   user, new reliability evidence surviving the split-half
   standard, was tested for and **not met**; no reopening is
   proposed).
3. Trailing finishing / conversion / on-target-rate "form"
   features (F6 — NOISE on this corpus as well).
4. Defensive xGOT traits (F7 — NOISE side of an otherwise
   interesting finding).
5. Two-stage generative SOT distributions (V11 failure stands;
   nothing here revives it).
6. Post-match snapshot features (`content.table`, `h2h`,
   teamForm) — leakage by construction.
7. ~~Bespoke per-league architectures~~ — SUPERSEDED 2026-11-09 14:33
   by the user's structure decision (§7b.5): per-league engines are
   now the rule. What remains forbidden under this item is divergence
   WITHOUT a written design justification in the league's own
   MODEL_DESIGN and a pass through that league's own gate.
8. Any feature whose only support is a within-sample pattern
   without a reliability check — the EDA labelled those NOISE or
   descriptive (F12), and they stay out.

## 7b. Amendment — user decisions, 2026-11-09 14:19 WIB (planning stage)

1. **J1 feature set approved.** The user approved all J1 features as
   consumed by the J1 candidates from `FEATURES.md` (X1–X9 as
   applicable per candidate, including the variant arms). Approval
   covers the feature/design level only — **nothing is built yet**;
   the project remains in the planning stage by the user's own
   statement, and building any candidate still needs his go.
2. **Halves products required for J1.** Each J1 product must present
   first-half, second-half, and full-time lines. The halves mechanism
   is the only permitted one (global forbidden list #1; EDA **F3**
   replicated the halves audit on this corpus): the full-time model
   is split by **frozen J1 league constants** measured in F3 —
   first-half share of goals **0.412**, SOT **0.448**, corners
   **0.447**, total shots **0.455** — with the remainder assigned to
   the second half, Poisson/NB plumbing mirroring production's
   halves products. Per-match or per-team half modelling remains
   forbidden: F3 measured the true variance of the per-match share
   at zero or below the noise floor for all four stats.
3. **Cards halves**: wanted (user, 2026-11-09) and measured the
   same day — EDA **F14** (`cards_halves.py`). Frozen J1 first-half
   yellow share = **0.383** (ratio of sums over the complete
   per-half-stats era, 2024+: n = 1,016 matches, 2,707 yellows;
   event-feed cross-check on the same matches 0.381). The
   variance-decomposition check passed the F3 standard: the two
   full normal seasons sit at or below the binomial noise floor
   (2024: −0.00094; 2025: −0.00028) and the team-level split-half
   is r = 0.097, so cards halves use the frozen constant exactly
   like the other four stats. (The all-rows pooled share, 0.357,
   was rejected as the constant: the partial 2023 splits understate
   the 1H share — 0.263 vs the event feed's 0.336 on the same
   matches.)
4. Because J1 carries real per-half stats (complete from 2024),
   halves presentations are gradeable against actual half outcomes
   once a product exists — the same grading treatment production
   gives its halves lines.
5. **Structure decision (user, 2026-11-09 14:33) — per-league
   engines.** The final project structure is `league/<L>/` per league
   (config, analysis, data, engine, predictions, prereg, reports),
   and **each league's engine is its own code**, seeded from the
   proven reference implementations and diverging only as that
   league's design justifies. This supersedes the earlier
   shared-architecture lock (forbidden item 7 amended accordingly).
   Rationale (user's): every league passes the same six-step process
   (understanding → preprocessing → EDA → visualization → feature
   engineering → design) but produces different features and models,
   so the engine is an output of the league's own process and lives
   in the league's own home.
6. **Build mandate (user, 2026-11-09 14:35–14:38).** All eight
   J.League candidates (G-J1, G-J2, G-J3, C-J1, K-J1, K-J2, S-J1,
   T-J1) are built now under this design. Every other warehouse
   league repeats the six-step process and its models are built
   immediately after its data work, using the J1 feature set (X1–X9)
   as the template where the league's data allows AND the feature's
   reliability check passes in that league. Program state is tracked
   in `league/PROGRAM_STATUS.md`.

## 8. Build order proposed (if approved)

1. G-J1 (richest data, xG era complete) → G-J2 → G-J3 (same
   architecture, descending data scope).
2. C-J1 and K-J1/K-J2 (single-change variants against proven
   references).
3. S-J1 last (most variant arms; predictions-only scope).
Each step ships only through its own league's virgin-window
verdict, exactly as the production models did.
