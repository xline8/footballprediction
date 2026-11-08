# Phase 4 — Model Design: Netherlands Eredivisie Candidates

Status: built under the conveyor program mandate (2026-11-09).
Feature set: `FEATURES.md` (J1 X1–X9 template, verdicts measured in
this league). Evidence: `EDA.md` (F1–F12). Structure: this league's
own engine under `league/NL-Eredivisie/engine/`, seeded from the
proven reference implementations and diverging only as written
here, through this league's own gates.

Shared validation frame (every candidate; each prereg turns this
into a frozen pre-registration before any fitting):

- **Dev period** (expanding, season-blocked for goals; per-match
  walk-forward for count markets): seasons 2021/2022–2024/2025.
  2021/2022 is the initial training/warm-up season; scored dev
  seasons are 2022/2023, 2023/2024, 2024/2025 (n = 918).
- **Virgin window**: season **2025/2026** (complete, n = 306),
  evaluated **once**, only for arms that pass the dev gate.
  2026/2027 (partial, n = 108) is the reserved confirmatory window,
  evaluated once when complete — never touched in this build.
- Design-level aggregates were inspected across all seasons during
  EDA (that is what EDA is); the virgin window is virgin for
  fitting, arm selection and gate setting.
- Baselines every candidate must beat on dev: the league base rate
  and the naive trailing-10 (count markets) / climatology (goals).
- **Gate Zero**: the unmodified reference architecture, fitted per
  league, is itself an arm. Both-pass rule: if base and variant
  both pass (log-loss leg + calibration leg, |breach| ≤ 1.0pp clean
  PASS on the virgin; ≤ 1 SE = PROVISIONAL PASS; per-season sign
  check), the arm with the lower pooled virgin log-loss ships;
  ties go to the simpler arm.
- Halves presentation (all candidates): FT + 1H/2H via the frozen
  NL constants (goals 0.444, SOT 0.446, corners 0.462, total shots
  0.449, yellows 0.333), presentation only, never fitted.

## 1. Candidate G-NL — Eredivisie goals model (1X2 / OU / BTTS / DC)

(a) **Reference**: production goals model — Dixon-Coles fit
(per-division rho, blend observation 0.5·goals + 0.5·xG with
goals-only fallback, exponential time decay, hl = 270), as ported
in `league/J1/engine/goals/`.
(b) **Identical**: DC estimation pattern and rho grid; blend-with-
fallback scheme (here xG exists for every match, so the fallback
never binds); time decay; walk-forward harness; LL/RPS +
calibration gate legs.
(c) **EDA-justified changes**:
  1. *Newcomer priors (X2)* as a variant arm: promoted clubs (3 per
     season) get the F4 offset (attack −0.45, defence +0.26 goals/
     match, as log-ratio shifts vs the decayed league team mean)
     instead of starting at the league mean. Production never
     needed this (no feeder tier in its fit); the Eredivisie turns
     over 3 of 18 clubs yearly. This is also the template's
     sanctioned response to the G-J2 lesson (extreme lambdas for
     1–2-match teams in season openers).
  2. *Variant arm: open-play / set-play decomposition tilt (X3)*
     on top of X2, exactly as G-J1's X3 arm — F5 (r = 0.610).
(d) **Forbidden**: half-share anything (F3); finishing/conversion
features (F6/R2/R3); absence features (F10); standings/h2h
snapshots (leakage).
**NOT built if**: dev walk-forward fails to beat climatology on
RPS/LL, or the virgin readout breaches the calibration leg.

## 2. Candidate S-NL — Eredivisie shots-on-target model

(a) **Reference**: `model_sot.py` **v5** — joint ridge Poisson team
ratings + NB (r = 79.94) + Beta-Binomial on-target ratio with prior
shrinkage, ensembled 50/50 with naive trailing-10, total-shots
signal included — as ported in `league/J1/engine/sot/`.
(b) **Identical**: joint estimation pattern, NB + BB family,
ensemble, harness, LL@line + calibration legs. Target = stats-feed
SOT (blocked shots excluded). Primary line **9.5** (dev mean 9.61,
over-rate 49.3% — the line nearest the dev median); ladder
8.5 / 9.5 / 10.5.
(c) **EDA-justified variant arms** (same trio as S-J1):
  1. *RS* — BB prior raised 200 → 20,000 pseudo-shots (ratio shrunk
     to near the league constant). Tests how much of F6's measured
     team ratio signal (r = 0.581) the gate believes vs v5's
     production shrinkage.
  2. *X4* — quality-adjusted ratio from trailing xG/shot
     (F6, r = 0.759), in addition to the raw total-shots signal.
  3. *X6* — X4 plus the era-guarded attacking xGOT trait
     (F7, r = 0.522; **NL era guard: matches from 2024/2025
     onward only**), judged on its era folds for the dev gate.
(d) **Forbidden**: as G-NL(d), plus defensive xGOT (R5) and the
two-stage generative family (V11, closed).
**NOT built if**: Gate Zero fails its own dev gate (variants moot),
or no arm passes the virgin calibration leg. Predictions-only
scope (no Eredivisie SOT odds source in-system — expected).

## 3. Candidate C-NL — Eredivisie corners model

(a) **Reference**: `model_corners_v3` — decay-weighted base rates +
rolling-5 shots relative factors + NB total + territorial
multiplier — as ported in `league/J1/engine/corners/`.
(b) **Identical**: ratings/base-rate pattern, multiplier structure,
harness, LL + calibration legs. Primary line **10.5** (dev mean
10.20, over-rate 44.5%; 9.5 is 55.8% — 10.5 is nearest the median);
ladder 9.5 / 10.5 / 11.5.
(c) **EDA-justified change** (one): the territorial covariate.
Gate Zero carries production's possession + big-chance covariates
(X9 — strong here too, F9). The variant arm replaces them with
opp-box touches (X7, F9: r = 0.959/0.876 where present), under the
min-8 trailing rule that absorbs the 2021–2023 gaps.
(d) **Forbidden**: half-share corner modelling (F3).
**NOT built if**: the box-touch arm does not beat Gate Zero on dev
(base may still ship), or the virgin calibration leg fails.

## 4. Candidate K-NL — Eredivisie cards model

(a) **Reference**: `model_cards.py` — yellow-card count model
(decayed venue-split team ratings shrunk to the league mean,
HL = 270, K = 8, NB r = 112.39; referee not used in production) —
as ported in `league/J1/engine/cards/`.
(b) **Identical**: target (unified yellows, stats-feed provenance
throughout this corpus), estimation pattern, harness, LL@line +
calibration legs. Primary line **2.5** (dev mean 2.89, over-rate
55.9%; secondary 3.5).
(c) **EDA-justified change** (one): *variant arm with a referee
strictness covariate (X8)* — F8 (r = 0.512; warehouse referee
coverage 100%). Binding conditions, as in K-J1: (i) it must beat
Gate Zero on dev walk-forward; (ii) referee assignment must be
known at prediction time in the operational pipeline — if not
published pre-match for a fixture, that fixture falls back to the
base arm (no imputation).
(d) **Forbidden**: red-card modelling as a target (0.15/match rare
event; production excludes it too).
**NOT built if**: the virgin calibration leg fails, or (Gate Zero
included) the dev gate fails.

## 5. Candidate T-NL — Eredivisie total shots model

Provenance (same as T-J1, stated plainly): the reference family is
under a frozen prospective trial on the top-5 (v2 + E9 challenger,
verdict due n ≥ 1,200 or season end — NOT reached). Per the user's
standing order for this program (J.League §6 override, applied
program-wide by the conveyor template), T-NL is built now, on this
corpus only; the top-5 trial is untouched and neither result
contaminates the other.
(a) **Reference**: the shots family in `experiments/shots_model/`
(v1 pattern) as ported in `league/J1/engine/total_shots/`.
(b) **Identical**: three frozen arms — **A** v1 pattern (joint
ridge Poisson ratings + NB + naive trailing-10 ensemble), **B**
v2 pattern (+ level layer), **C** E9 mechanism (NB r from a
trailing window; single-league analogue: league-level trailing r).
Primary line **26.5** (dev mean 27.01, over-rate 51.3%); ladder
25.5 / 26.5 / 27.5.
(c) **Changes**: none beyond per-league fitting — F2 (shots-for
r = 0.927) is the justification for building it here at all.
(d) **Forbidden**: half-share shot modelling (F3).
**NOT built if**: no arm passes the dev gate (virgin then unread),
or the virgin legs fail.

## 6. Global forbidden list

The program list (MODEL_DESIGN §7 of J.League) applies verbatim:
no half-share modelling; no lineup/absence features for SOT; no
trailing finishing/conversion/on-target-rate covariates (R2–R4 —
with this league's measurements recorded in FEATURES §3, including
the two that measured real here and are still not consumed, for
the stated double-counting reasons); no defensive xGOT; no
two-stage generative SOT distributions; no post-match snapshot
features; no feature without a reliability check in this league's
EDA; no divergence from a reference pattern without a written
justification above and a pass through this league's own gate.
