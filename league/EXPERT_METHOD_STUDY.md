# Expert Method Study: How Professional Football Analytics Processes Data, and What It Says About Our EDA

Written 2026-11-11 at the user's request. Purpose: test the hypothesis
that our sealed-window failure rate is a method problem — how the
league program looks at data and judges correlations during EDA — and
not only a data-volume problem. The comparison benchmark is published
professional practice: the Soccermatics course (Uppsala, David
Sumpter, with club practitioners from Liverpool, Manchester City,
Barcelona and others), the Friends of Tracking material it grew out
of, StatsBomb's teaching material, a mixed-effects xG study on
StatsBomb open data, and two validation-methodology guides written
for football and sports models. Every claim about expert practice
below traces to one of those sources (listed at the end). Every claim
about our method was checked against `league/J1/analysis/`,
`league/BO-PrimeraDivision/analysis/`, `league/PA-LPF/analysis/` and
`league/AUDIT_BRIEF.md`.

## 1. How the experts process football data

### 1.1 The atomic unit is the event, not the match

Professional pipelines start from the event stream: every pass, carry
and shot as one row, with pitch coordinates, a timestamp, the player,
and the game state at that moment. The Soccermatics course opens its
modelling section by loading Wyscout event JSON files, filtering to
shots, and deriving geometry from raw coordinates — distance to goal
and the angle subtended by the goalposts — before any model is fit.
Possessions are kept as chains, so an action can be described by where
it sits in a sequence, not only by what it was.

Tracking data, where a club has it, is handled as a second stream
synchronised to the events. Laurie Shaw's Friends of Tracking
tutorials work from Metrica Sports sample data: event rows carry
start/end coordinates, tracking frames carry all 22 players' x/y
positions at 25 Hz, and the two are aligned frame by frame. William
Spearman's pitch control model, taught in the same series, defines
control at a location as the probability that a given player would
reach the ball first if it arrived there, computed from positions and
velocities through a temporal Voronoi construction. A later
peer-reviewed version of that idea validated the output against
behaviour: on 5,887 passes, the team the model said controlled the
receiving location was the team that actually received the pass 91%
of the time. The methodological point is the validation target — a
derived feature is checked against an observed outcome it was not
built from.

### 1.2 Model fitting is incremental, and each step is scored

The Soccermatics xG lesson fits a logistic regression by
maximum log-likelihood and grows it one term at a time on 8,451 shots:
angle alone (log-likelihood −2561.2), distance alone (−2524.4),
distance plus distance² (−2505.6), then a seven-term geometry model
(−2498.7). Each addition has to pay for itself in likelihood, and the
lesson plots the empirical scoring rate in bins before fitting
anything, so the functional form is chosen against a picture of the
raw relationship. Fit quality is reported as McFadden's R² and a ROC
curve. The course's framing is explicit and repeated: a statistical
model is there to "capture our understanding of football", and
flexible ML methods (gradient boosting, neural networks) are treated
as a later step whose cost is that the fitted relationship is no
longer directly readable. One of the lesson's own exercises is to fit
headers and non-headers as separate models — heterogeneity is handled
by splitting or by explicit terms, not by pooling and hoping.

### 1.3 Value models price positions and actions, not match totals

Expected Threat (xT), built in the course from Karun Singh's
formulation, discretises the pitch into a 16×12 grid and estimates,
per cell: the probability the next action is a shot, the probability
a shot from there scores (a binned xG), and a full transition matrix
of where the ball moves next, given that it moves. The cell values
are then solved by iterating the Markov chain — value = immediate
shooting payoff + move probability × expected value of the
destination — until the grid converges. Action-based variants
(VAEP is the standard reference) score each on-ball action by how it
changes the probability of scoring and conceding over the following
actions. Either way, the unit of analysis stays the action in
context. Nothing in this family is computed from match totals.

### 1.4 Heterogeneity is estimated as a variance component

The mixed-effects xG study (Appiah et al., 2026, on StatsBomb open
data) fits logistic models to 10,709 non-penalty shots from La Liga
2015/16 and the 2018 World Cup. Adding body part and competition to a
distance/angle baseline moves AIC from 6,167.8 to 5,980.0 (headers
score at roughly 31% of the odds of footed shots at the same
location). Adding a shooter-level random intercept improves AIC
again, to 5,967.7, and AUC from 0.78 to 0.79. The estimated shooter
variance is about 0.10 on the logit scale (SD 0.31): real, persistent
between-player differences in conversion *after shot location is
held constant*, with each player's estimate shrunk toward the
population mean in proportion to how many shots he has taken. The
paper's literature frame points the same way — Bayesian hierarchical
xG (Bayes-xG) with player and positional random effects is presented
as the current direction of the field. Shrinkage here is not a
constant someone picked; it is an estimated quantity with a standard
error.

### 1.5 Validation discipline is the part with actual rules

The two methodology guides agree on a concrete rule set:

- Folds are chronological. Training always precedes validation; the
  forecast origin rolls forward (GoalIQ guide; FundedPlays guide).
- The split follows the *information cut-off*, not the match date:
  anything that would not have been available at prediction time is
  excluded, and fixtures sharing a decision cut-off stay in the same
  block so simultaneous matches cannot leak into each other.
- Every learned transformation — imputation, scaling, encoding,
  **feature selection**, calibration — is fitted inside the training
  fold only. Full-sample preprocessing is named, in both guides, as
  the most common contamination route.
- Once cross-validation results have influenced feature selection,
  hyperparameters or window length, those folds are no longer an
  independent estimate; a later period must stay untouched until the
  specification is frozen, and if the final test then changes the
  model, it has become a development period and a new test is
  required (GoalIQ). The FundedPlays guide adds bookkeeping: document
  how many times the holdout was queried.
- Calibration, when fitted, is fitted on an inner slice of the
  training data (nested), never on the test fold.
- Report the spread across folds, recent-period performance and
  calibration by subgroup — not one pooled average. The GoalIQ worked
  example shows a candidate winning two of three folds and still
  being correctly rejected because it failed the latest, largest one.

## 2. Our method, as verified in the league tree

Per league, six stages produce `DATA_UNDERSTANDING.md`,
`PREPROCESSING.md`, `EDA.md`, charts, `FEATURES.md` and
`MODEL_DESIGN.md`, then a pre-registration, then an engine under
`league/<L>/engine/`. Features follow the J1 template and are admitted
per league only if split-half reliability passes there: split-half
figures are career-pooled per team (random disjoint halves of each
team's matches, ≥24 matches per team in J1). Models are count models
— Dixon-Coles for goals, the v5 pattern (joint ridge Poisson ratings
+ Negative Binomial + Beta-Binomial on-target ratio) for SOT, and
relatives for corners, cards and total shots. Every candidate runs
against Gate Zero, the unmodified reference architecture fitted to
that league, plus any justified variant arms. The dev gate is a
season-blocked expanding walk-forward against base-rate and
trailing-10 baselines; the sealed window (final season, or a
transitional season plus a reserved confirmatory season in several
leagues) is read once, with log-loss and calibration legs at
±1.0pp pooled and a per-season sign check. The J1 design document
states the hygiene rule precisely: the sealed windows are sealed
"for fitting, feature selection among arms, and gate setting" — and
states, in the same paragraph, that "design-level aggregates were
inspected across all seasons during EDA (that is what EDA is)".

Three further verified facts matter below. First, shrinkage in our
engines is hand-set: ridge penalties and Beta-Binomial priors are
fixed constants, cross-tier movers get a measured fixed offset (J1
finding F4: promoted sides lose ≈0.56 GF and concede ≈0.51 GA per
match), and several leagues carry a SHRINK arm that scales a new
team's rating by n/6 for its first six matches — a patch written
after J2's thin-team extreme lambdas were diagnosed. In PA-LPF the
SHRINK arm is expected to be degenerate, identical to Gate Zero,
because the only thin teams are n=0 newcomers. Second, later design
docs show the hygiene improving where someone thought about it: in
BO-PrimeraDivision the gate lines are "computed only from the dev
distribution… No 2026 value sets a line." Third, the data itself:
FotMob gives match-level team aggregates for ~240k matches across
~160 leagues; shotmap event data exists only for the top-5 and
J.League pulls; there is no tracking data anywhere in the warehouse.

## 3. Point-by-point comparison

| Dimension | Expert practice | Our method | Gap |
|---|---|---|---|
| Unit of analysis | Event (shot/pass) with coordinates and game state | Match-level team aggregates | Real, but data-bound (§3.1) |
| Feature admission | Inside the training fold, re-derived per fold | Split-half reliability, career-pooled, computed once per league | Forward stability never tested (§3.2) |
| Sealed test | Untouched by any selection step; queries logged | Sealed for fitting, arm selection, gate setting — but EDA design aggregates inspected across all seasons | Partial, documented in our own design doc (§3.2) |
| Shrinkage | Estimated variance components (random effects / empirical Bayes) | Fixed ridge/prior constants; hand-written n/6 SHRINK patches; fixed tier offsets | Pooling strength never estimated (§3.3) |
| Calibration | Fitted on inner slices, then tested | Detected at the gate; no recalibration component exists | Failures are terminal that an inner-fitted calibrator might have prevented |
| Reporting | Fold spread, per-period and per-subgroup calibration | Pooled dev LL, pooled ±1.0pp calibration leg, per-season sign check | Worst-era behaviour hidden inside pooled dev numbers |
| Baselines | Simple benchmark in every comparison | Base rate + trailing-10 + Gate Zero | Aligned — this part of our method matches the guides |

### 3.1 Gap (a): event level vs match aggregates

The mechanism is confounding by mix. A match-level on-target rate
blends two different things: where a team's shots come from and how
well it converts from a given location. The mixed-effects study holds
location constant and still finds a shooter effect (variance 0.10,
SD 0.31 logits). Our J1 EDA, working on the unconditioned aggregate,
measured the team on-target trait at split-half r = 0.06 and rejected
it as noise (finding F6), while BO-PrimeraDivision measured the same
aggregate trait at r = 0.613 and admitted it. Both measurements can be
honest; an unconditional correlation and a location-conditional effect
are different quantities, and either can be the one that vanishes.
The same applies to game state: event data records score and minute
for every action, so "shots while trailing" — more numerous, from
worse locations, against a set defence — can be separated from shots
while level. A match aggregate cannot, so any correlation involving
shot volume partly prices in game-state mix. A third asymmetry runs
the other way: match totals for corners and cards have no event-level
counterpart in the expert literature at all, because club analytics
barely models them. Our corners/cards machinery has no professional
template to be behind.

The honest bound on this gap: it is reachable only where shotmaps
exist — the top-5 production system and the J.League pulls. For the
~155 world leagues whose FotMob coverage is aggregates only, no EDA
method, ours or anyone's, recovers event-level information that was
never recorded. Gap (a) can explain at most the rich-data failures
(the user's suspicion covers those too: J.League lost markets at the
sealed window), and even there, our one location-aware aggregate —
attacking xGOT per shot, F7, r = 0.518 — was measurable only from
2025 onward, which is an era-coverage fact, not an EDA error.

### 3.2 Gap (b): leakage hygiene — where our seal actually leaks

Our seal is strong where the design doc says it is: no fitting, no
arm selection, no gate setting on sealed seasons, and in later
leagues (BO) not even gate lines. It leaks at exactly the layer the
validation guides warn about first — design-level selection:

- **EDA inspected all seasons.** The J1 EDA is titled "2021 – 2026/27"
  and the design doc confirms design-level aggregates were inspected
  across all seasons, sealed ones included. Era guards ("this trait
  exists only from 2025"), the decision that a trait exists at all,
  and the frozen half-share constants all encode information from
  seasons that later served as the sealed test. Per the GoalIQ rule,
  a period that influenced *any* selection is a development period.
  Our sealed windows are therefore honestly described as
  fit-sealed, not design-sealed.
- **Split-half reliability is a random split.** Career-pooled
  split-half correlation asks whether a trait persists across a random
  interleaving of a team's whole history. Both validation guides
  reject random splits for time-ordered data for the same reason they
  reject random k-fold: the halves share eras, squads and conditions.
  Worse for our failure pattern, split-half r is nearly blind to
  level shift — if a stat's league mean jumps in the final era, both
  halves contain pre- and post-jump matches, team rankings survive,
  and r stays high while forward calibration breaks. The 2026/27
  total-shots regime shift (league mean ≈27.98 per match against a
  ≈24.63 norm in the top-5 study) is precisely the failure shape a
  random split cannot see and a time-ordered split cannot miss.
- **No query bookkeeping.** Nothing records how many design decisions
  a given sealed season influenced across ~160 leagues built from one
  template. Each decision is small; the template multiplies it.

None of this says EDA "cheated". It says our admission test measures
the wrong kind of stability (persistence under random mixing) for the
question the gate later asks (transportability forward in time), and
that design knowledge flowed across a boundary we otherwise guard
carefully. That combination predicts exactly the observed signature:
candidates that look solid through dev and then fail the sealed
calibration leg, in rich leagues as well as thin ones.

### 3.3 Gap (c): independent fits vs partial pooling

Our unit of independence is the league: own data, own engine, own
fit. Thin data inside that unit is handled by constants — a ridge
penalty, a Beta-Binomial prior strength, a fixed tier offset, an n/6
rating scale for a team's first six matches. The hierarchical
alternative estimates the same quantities as variance components:
how much true team-to-team spread exists, how much match-to-match
noise exists, and therefore how far each thin estimate should be
pulled toward its group mean. Three of our recurring failure shapes
are textbook symptoms of un-estimated pooling:

- **Season-opener extremes.** J2's diagnosis — thin-data teams
  getting extreme lambdas in early rounds — is what an unshrunk (or
  uniformly shrunk) rating does when a promoted team has three
  matches of history. The n/6 SHRINK arms patch the first six matches
  with a linear rule; a variance component produces the same shape
  from the data, with the strength fitted rather than asserted, and
  applies it to *every* team in proportion to its evidence, not only
  to newcomers.
- **Tier movement.** Our cross-tier prior is one measured constant
  (≈0.56/0.51 goals) applied to every mover. In a three-tier hierarchy
  (J1/J2/J3 fitted jointly at the prior level), the tier gap is a
  parameter with uncertainty, and a mover's initial rating is a
  posterior, not a constant minus a constant.
- **Calibration, again.** A model that cannot express "this rating is
  uncertain" predicts at full confidence from match one. Pooled
  calibration at ±1.0pp is where overconfidence in a minority of
  fixtures (openers, movers, thin teams) shows up, even when the
  average team is rated fine. That goals — the market with the most
  promoted/relegated churn — fails calibration nearly everywhere
  while SOT and corners (traits with higher measured stability) pass
  more often is consistent with this reading, and the audit's
  classification can confirm or refute it by checking whether sealed
  calibration breaches concentrate in opener/mover fixtures.

## 4. Ranked candidate findings

Ranking is by (failure patterns plausibly explained) × (data we
actually have) ÷ (implementation cost). Every test below is
pre-registerable under existing discipline: arms against Gate Zero,
both-pass rule unchanged, sealed and reserved confirmatory windows
read once, no gate threshold moved.

**1. Time-ordered admission: replace split-half-only reliability with
a forward-stability leg.**
The change: a trait is admitted only if, in addition to split-half r,
its first-era measurement predicts its second-era measurement in time
order (era-blocked correlation across at least two era boundaries),
and league levels are reported per era so a level shift is a visible
EDA output rather than a sealed-window surprise. Explains:
dev-pass/sealed-fail calibration breaches driven by era drift,
including the total-shots regime shape. Data: match aggregates we
already hold — no new feed. Test: freeze the rule in a
pre-registration; apply it prospectively to the reserved
confirmatory windows that remain unspent (J1 2026/27 confirmatory;
BO's outstanding season-end confirmatory read) and to any future
league, comparing admission sets and sealed outcomes against the
split-half-only rule recorded in parallel. The retrospective version
(re-running admission on completed leagues) is diagnostic only and
must be labelled as such, since those windows are spent.

**2. Design-seal the EDA stage.**
The change: EDA workbooks load dev seasons only; sealed-season files
are not present in the EDA environment, so design aggregates,
constants and era guards cannot encode them. Feature sets are frozen
and hashed before any sealed file is pulled. Explains: part of the
dev-pass/sealed-fail gap in every league built since J1, rich ones
included — the one mechanism in this study that operates at full
program scale. Data: none; this is procedure, and BO's
dev-only line-setting shows it is already feasible inside our own
conventions. Test: procedural adoption for future builds, with the
audit's Scope 2 item 5 classification ("EDA missed it" vs "could not
have seen it") as the baseline measurement; the success metric for
the next program is the dev-pass/sealed-fail rate against this
program's.

**3. Estimate the shrinkage: variance-component ratings.**
The change: replace fixed ridge strengths and the n/6 SHRINK rule
with empirical-Bayes / mixed-effects team ratings — per-market
between-team and within-team variance components, tier as a hierarchy
level where a tier system exists. Per-league engines stay; what
changes is that the prior layer's strength is fitted per league (or
per tier system) instead of asserted. Explains: opener extreme
lambdas, mover misfit, and goals calibration failures in
high-churn leagues. Data: scores and counts we already hold for every
league — this is the only candidate that reaches the scores-only
leagues where most zero-market outcomes sit. Test: pre-registered arm
against Gate Zero on a named set of leagues with unspent
confirmatory windows, both-pass rule as written; report the fitted
variance components per league as part of the verdict, so the field
can see whether thin leagues actually wanted more pooling.

**4. A sanctioned recalibration layer, fitted on inner slices.**
The change: candidates gain one optional component — an
isotonic/Platt calibrator fitted on a trailing inner slice inside
each walk-forward fold, never on dev-scored or sealed data — gated as
an arm like any other. Explains: calibration-leg failures where the
log-loss leg passed, i.e. the model ranked fine and was wrong about
its own level. Data: existing predictions. Test: arm vs Gate Zero
under the existing legs unchanged; the arm ships only if the *same*
sealed calibration leg passes with the calibrator active. This is
the guides' nested-calibration rule applied literally, and it is the
only candidate that converts a class of terminal failures into a
design question instead of a verdict.

**5. Worst-fold reporting in the dev gate.**
The change: dev verdicts must report per-fold and per-era calibration
spread alongside pooled numbers, and a candidate whose worst era
breaches the calibration band is flagged in the pre-registration as
calibration-fragile (not failed — flagged, with the sealed sign check
already in place as the decider). Explains: pooled dev passes that
hid one bad era which then became the sealed window. Data: existing
harness output. Test: retrospective classification on verdict files
(diagnostic), then prospective adoption; cost is near zero.

**6. Event-level features where shotmaps exist (top-5, J.League
only).**
The change: add location-conditioned aggregates — big-chance share,
set-play share (J1 F5, r = 0.621, already an arm), and a shrunken
location-adjusted finishing component in the style of the paper's
random intercept, aggregated to team level. Explains: part of the
goals/SOT signal our aggregates structurally cannot see (§3.1). Data:
FotMob shotmaps — available for exactly these two corpora and
nowhere else in the warehouse. Test: arms on the reserved J1
2026/27 confirmatory window under existing prereg rules; no
extrapolation of the result to aggregate-only leagues.

## 5. What not to adopt

- **Tracking-data methods (pitch control, off-ball value, VAEP with
  freeze-frame context).** Sound methods, absent data: FotMob
  supplies no tracking for any league we cover, and the Metrica
  sample corpus is two matches. Provider xG models that use
  freeze-frame defensive context sit behind the same wall — StatsBomb
  open data covers a fixed competition list that does not intersect
  our ~160-league warehouse. Adopting the vocabulary without the
  data would change nothing except the slide deck.
- **High-capacity ML (gradient boosting, neural networks) on match
  aggregates.** Our failures concentrate in the calibration leg while
  log-loss legs against baselines often pass; that is a level and
  uncertainty problem, not a ranking-capacity problem. Per-league
  samples are hundreds of matches, where added capacity buys variance,
  and the Soccermatics course itself treats these methods as the step
  you take after the interpretable model, with understanding as the
  stated cost. If a future candidate tests one, it belongs behind the
  same Gate Zero arm structure — but nothing in the expert sources
  suggests it addresses our observed failure signature.
- **Random cross-validation anywhere — admission, tuning, or
  screening.** Both guides are unambiguous, and §3.2 argues our
  split-half test is already closer to this error than to the
  forward-chaining standard.
- **Reopening closed topics with expert citations.** The literature
  does not revive them. The paper's shooter random effect is a
  shrunken, location-conditional conversion term — it is not evidence
  for the aggregate finishing/form features (F6) or star-absence
  features (F10/V8/V10) we tested and rejected, and nothing in the
  sources touches the two-stage generative SOT family (failed as V11)
  or half-share modelling, where our own measurement put the true
  per-match variance at ≈0. Those stay closed.
- **One joint world model replacing per-league engines.** The
  hierarchy in candidate 3 lives in the prior layer; the engines,
  gates and verdicts stay per league, per the user's structure
  decision. A single global fit would also reintroduce, at program
  scale, the pooled-average reporting problem of §3.2.
- **Recalibrating to the sealed window after reading it.** Both
  guides name this as the move that converts a test into a
  development set. Any calibrator is fitted inside folds (candidate
  4) or not at all.

## 6. Bottom line for the audit

The user's suspicion is partly right, and the part that is right is
specific. Our EDA's core instrument — career-pooled split-half
reliability — certifies persistence under random mixing, and our
sealed windows are fit-sealed but not design-sealed; professional
practice tests forward stability and seals the design layer too.
That is a method flaw, it operates in rich leagues as well as thin
ones, and candidates 1, 2 and 5 address it with data already in the
warehouse. Separately, our shrinkage is asserted where expert
practice estimates it; candidate 3 is the fix and the only one that
reaches the scores-only leagues. What the method critique does not
explain away is data absence: markets that were never buildable
because the stats feed starts in 2025, and event-level signal that
FotMob never recorded outside two corpora. The audit's classification
should keep those ledgers separate — causes ranked by markets killed,
with "EDA method" as one named cause among them, sized by evidence
rather than by how satisfying the explanation is.

## Sources

- Sumpter, D. *Soccermatics* course notes, Uppsala University —
  course front page and contents; "Statistical models"; "Fitting the
  xG model"; "Expected Threat — Position-based"; "Calculating xT
  (position-based)". https://soccermatics.readthedocs.io/en/latest/
- Shaw, L. *Friends of Tracking* tutorials (Metrica Sports sample
  data; event/tracking processing in Python), GitHub tutorial code;
  Spearman, W. pitch control masterclass, Friends of Tracking (2020).
- Wu, L. & Swartz, T. B. "A new metric for pitch control based on an
  intuitive motion model." *Computational Statistics* 40 (2025) —
  pitch-control definition and 5,887-pass validation.
  https://link.springer.com/article/10.1007/s00180-024-01512-2
- Appiah, K. N. et al. "Building reproducible expected-goals models
  from public football event data: Logistic and mixed-effects
  analysis using StatsBomb open data." Research Square (2026).
  https://www.researchsquare.com/article/rs-9022775/v1
- GoalIQ. "Time-Series Cross-Validation for Football Models."
  https://www.goaliqai.com/time-series-cross-validation-football-models/
- FundedPlays. "How to Avoid Overfitting a Sports Model: time-aware
  validation and pipelines."
  https://www.fundedplays.com/blogs/how-to-avoid-overfitting-a-sports-model-time-aware-validation
- StatsBomb Academy. "Introduction to Football Analytics" (course
  contents: xG, types of attack, set pieces, defensive choices,
  team/opposition analysis). https://courses.statsbomb.com/courses/introduction-to-football-analytics
- Internal: `league/J1/analysis/MODEL_DESIGN.md`, `EDA.md`,
  `FEATURES.md`; `league/BO-PrimeraDivision/analysis/MODEL_DESIGN.md`;
  `league/PA-LPF/analysis/MODEL_DESIGN.md`; `league/AUDIT_BRIEF.md`.
