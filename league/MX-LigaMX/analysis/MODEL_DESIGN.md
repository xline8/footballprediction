# Phase 4 — Model Design: Mexico Liga MX Candidates

Status: built under the conveyor program mandate (2026-11-09).
Feature set: `FEATURES.md` (J1 X1–X9 template, verdicts measured in
this league — X2 and X6 dropped on this league's evidence).
Evidence: `EDA.md` (F1–F13). Structure: this league's own engine
under `league/MX-LigaMX/engine/`, seeded from the proven reference
implementations (AR/J1 ports) and diverging only as written here,
through this league's own gates.

Shared validation frame (every candidate; each prereg turns this
into a frozen pre-registration before any fitting):

- **Blocks**: 10 chronological tournament blocks (2021/2022 -
  Apertura … 2025/2026 - Clausura), regular phase only (153 matches
  each). The 2026/2027 - Apertura tournament is in progress at pull
  time (143 regular matches, no playoffs yet) and is excluded from
  the corpus wholesale; it is the reserved confirmatory window.
  Format is constant across the window (18 teams, 17 rounds,
  Liguilla excluded) — the walk-forward's expanding window handles
  the level drift (F1) the same way production does.
- **Dev period**: tournaments 1–9 (n = 1,377). Tournament 1
  (2021/2022 - Apertura) is the initial training/warm-up block;
  scored dev blocks are tournaments 2–9 (n = 1,224).
- **Virgin window**: **2025/2026 - Clausura regular phase**
  (complete: 17/17 rounds, n = 153), evaluated **once**, only for
  arms that pass the dev gate. The in-progress 2025 Apertura
  question does not arise here: the most recent *complete*
  tournament is the virgin, and the in-progress 2026/2027 -
  Apertura is reserved as confirmatory, never touched in this
  build. (Design-level aggregates were inspected across all blocks
  during EDA, as in every conveyor league; the virgin is virgin for
  fitting, arm selection and gate setting.)
- Baselines every candidate must beat on dev: the league base rate
  and the naive trailing-10 (count markets) / climatology (goals).
- **Gate Zero**: the unmodified reference architecture, fitted per
  league, is itself an arm. Both-pass rule: if base and variant
  both pass (log-loss leg + calibration leg, |breach| ≤ 1.0pp clean
  PASS on the virgin; ≤ 1 SE = PROVISIONAL PASS; per-block sign
  check), the arm with the lower pooled virgin log-loss ships;
  ties go to the simpler arm.
- Halves presentation (all candidates): FT + 1H/2H via the frozen
  MX constants (goals 0.456, SOT 0.455, corners 0.465, total shots
  0.458, yellows 0.385), presentation only, never fitted.

## 1. Candidate G-MX — Liga MX goals model (1X2 / OU / BTTS / DC)

(a) **Reference**: production goals model — Dixon-Coles fit
(per-division rho, blend observation 0.5·goals + 0.5·xG with
goals-only fallback, exponential time decay, hl = 270), as ported
in `league/J1/engine/goals/` and `league/AR-LigaProfesional/`.
(b) **Identical**: DC estimation pattern and rho grid; blend scheme
(here xG is 100% in every tournament, so the fallback never binds
— F13); time decay; walk-forward harness; LL/RPS + calibration
gate legs.
(c) **EDA-justified changes**: ONE variant arm —
*open-play / set-play decomposition tilt (X3)*, exactly as G-J1's /
G-AR's X3 arm — F5 (r = 0.558, measured ratio-of-sums). There is **no X2 arm**:
no movers exist in this league (F4), and no shrinkage/prior arm is
needed — every club enters every block after warm-up with deep
expanding-window history (the G-J2 failure mode, 1–2-match teams
in season openers, cannot occur with a constant 18-team set and
tournament-blocked expanding fits).
(d) **Forbidden**: half-share anything (F3); finishing/conversion
features (F6/R2/R3); absence features (F10); altitude (F12/R7);
standings/h2h snapshots (leakage).
**NOT built if**: dev walk-forward fails to beat climatology on
RPS/LL, or the virgin readout breaches the calibration leg.

## 2. Candidate S-MX — Liga MX shots-on-target model

(a) **Reference**: `model_sot.py` **v5** — joint ridge Poisson team
ratings + NB (r = 79.94) + Beta-Binomial on-target ratio with prior
shrinkage, ensembled 50/50 with naive trailing-10, total-shots
signal included — as ported in `league/J1/engine/sot/`.
(b) **Identical**: joint estimation pattern, NB + BB family,
ensemble, harness, LL@line + calibration legs. Target = stats-feed
SOT (blocked shots excluded). Primary line **8.5** (dev mean 8.92,
over-rate 51.2% — nearest the dev median); ladder 7.5 / 8.5 / 9.5.
(c) **EDA-justified variant arms** (two — the S-J1/S-AR trio minus
X6, dropped on this league's evidence, F7/R5):
  1. *RS* — BB prior raised 200 → 20,000 pseudo-shots (ratio shrunk
     to near the league constant). Tests how much of F6's measured
     team ratio signal (r = 0.488) the gate believes vs v5's
     production shrinkage.
  2. *X4* — quality-adjusted ratio from trailing xG/shot
     (F6, r = 0.626), in addition to the raw total-shots signal.
     Active in all tournaments (shotmap 100%).
(d) **Forbidden**: as G-MX(d), plus defensive xGOT (R6), attacking
xGOT (R5 — dropped on measurement, not merely unused), and the
two-stage generative family (V11, closed).
**NOT built if**: Gate Zero fails its own dev gate (variants moot),
or no arm passes the virgin calibration leg. Predictions-only
scope (no Liga MX SOT odds source in-system — expected).

## 3. Candidate C-MX — Liga MX corners model

(a) **Reference**: `model_corners_v3` — decay-weighted base rates +
rolling-5 shots relative factors + NB total + territorial
multiplier — as ported in `league/J1/engine/corners/`.
(b) **Identical**: ratings/base-rate pattern, multiplier structure,
harness, LL + calibration legs. Primary line **9.5** (dev mean
9.79, over-rate 50.8%); ladder 8.5 / 9.5 / 10.5.
(c) **EDA-justified change** (one): the territorial covariate.
Gate Zero carries production's possession + big-chance covariates
(X9 — strong here too, F9). The variant arm replaces them with
opp-box touches (X7, F9: r = 0.863/0.890 where present), under the
min-8 trailing rule that absorbs the early-tournament gaps.
(d) **Forbidden**: half-share corner modelling (F3).
**NOT built if**: the box-touch arm does not beat Gate Zero on dev
(base may still ship), or the virgin calibration leg fails.

## 4. Candidate K-MX — Liga MX cards model

(a) **Reference**: `model_cards.py` — yellow-card count model
(decayed venue-split team ratings shrunk to the league mean,
HL = 270, K = 8, NB r = 112.39; referee not used in production) —
as ported in `league/J1/engine/cards/`.
(b) **Identical**: estimation pattern, harness, LL@line +
calibration legs — with ONE league-specific target change, forced
by measurement (DATA_UNDERSTANDING F10): the target is **unified
yellows from the event feed** (`card='Yellow'`), because the
stats-feed `yellow_cards` key undercounts the event feed in every
dev tournament (regular-phase dev totals: stats 6,090 vs events
6,235; per-match agreement only 120–135 of 153 per tournament).
The production cards model's target definition (a unified yellow
count) is unchanged; only its provenance in this corpus differs.
Primary line **4.5** (dev mean 4.53, over-rate 47.5%); ladder
3.5 / 4.5 / 5.5.
(c) **EDA-justified change** (one): *variant arm with a referee
strictness covariate (X8)* — F8 (r = 0.331, weak-moderate; coverage
0% in warm-up, 95–100% in scored dev blocks through 2024/2025
Clausura, 24.8% in 2025/2026 Apertura, 58.2% in the virgin block).
Binding conditions, as in K-J1: (i) it must beat Gate Zero on dev
walk-forward; (ii) referee assignment must be known at prediction
time in the operational pipeline — if not published pre-match for
a fixture, that fixture falls back to the base arm (no
imputation); unnamed referees in the backtest take the shrunk
league mean by the preregistered fallback.
(d) **Forbidden**: red-card modelling as a target (rare event;
production excludes it too).
**NOT built if**: the virgin calibration leg fails, or (Gate Zero
included) the dev gate fails.

## 5. Candidate T-MX — Liga MX total shots model

Provenance (same as T-J1/T-AR, stated plainly): the reference
family is under a frozen prospective trial on the top-5 (v2 + E9
challenger, verdict due n ≥ 1,200 or season end — NOT reached).
Per the user's standing order for this program (J.League §6
override, applied program-wide by the conveyor template), T-MX is
built now, on this corpus only; the top-5 trial is untouched and
neither result contaminates the other.
(a) **Reference**: the shots family in `experiments/shots_model/`
(v1 pattern) as ported in `league/J1/engine/total_shots/`.
(b) **Identical**: three frozen arms — **A** v1 pattern (joint
ridge Poisson ratings + NB + naive trailing-10 ensemble), **B**
v2 pattern (+ level layer), **C** E9 mechanism (NB r from a
trailing window; single-league analogue: league-level trailing r).
Primary line **26.5** (dev mean 26.65, over-rate 47.9% — the line
nearest the dev median rate); ladder 25.5 / 26.5 / 27.5.
(c) **Changes**: none beyond per-league fitting — F2 (shots-for
r = 0.845) is the justification for building it here at all.
(d) **Forbidden**: half-share shot modelling (F3).
**NOT built if**: no arm passes the dev gate (virgin then unread),
or the virgin legs fail.

## 6. Global forbidden list

The program list (MODEL_DESIGN §7 of J.League) applies verbatim:
no half-share modelling; no lineup/absence features for SOT; no
trailing finishing/conversion covariates (R2/R3); no standalone
on-target-rate covariate (R4); no xGOT traits in this league (R5/
R6 — measured NOISE here); no altitude feature (R7); no two-stage
generative SOT distributions; no post-match snapshot features; no
feature without a reliability check in this league's EDA; no
divergence from a reference pattern without a written
justification above and a pass through this league's own gate.
