# Phase 4 — Model Design: Argentina Liga Profesional Candidates

Status: built under the conveyor program mandate (2026-11-09).
Feature set: `FEATURES.md` (J1 X1–X9 template, verdicts measured in
this league). Evidence: `EDA.md` (F1–F12). Structure: this league's
own engine under `league/AR-LigaProfesional/engine/`, seeded from
the proven reference implementations and diverging only as written
here, through this league's own gates.

Shared validation frame (every candidate; each prereg turns this
into a frozen pre-registration before any fitting):

- **Blocks**: the corpus is eight chronological competition blocks
  (2021; 2022; 2023; 2024; 2025 - Apertura; 2025 - Clausura;
  2026 - Apertura; 2026 - Clausura), group phase only. The format
  changes across the window (single round-robin → split
  Apertura/Clausura with zones) are handled by the walk-forward
  itself: every fit uses only matches strictly before its target,
  whatever format they were played under. No block is dropped for
  its format.
- **Dev period**: blocks 2021 – 2026 - Apertura (n = 2,179). 2021
  is the initial training/warm-up block; scored dev blocks are
  2022, 2023, 2024, 2025 - Apertura, 2025 - Clausura,
  2026 - Apertura (n = 1,854).
- **Virgin window**: block **2026 - Clausura, group phase**
  (complete: 16/16 rounds, n = 240), evaluated **once**, only for
  arms that pass the dev gate. Its playoff bracket had not been
  played at pull time and is excluded by design everywhere; the
  confirmatory window for these candidates is the next block
  pulled into the warehouse (2027 - Apertura), reserved by rule
  and never touched in this build.
- Design-level aggregates were inspected across all blocks during
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
  AR constants (goals 0.444, SOT 0.459, corners 0.480, total shots
  0.462, yellows 0.373), presentation only, never fitted.

## 1. Candidate G-AR — Liga Profesional goals model (1X2 / OU / BTTS / DC)

(a) **Reference**: production goals model — Dixon-Coles fit
(per-division rho, blend observation 0.5·goals + 0.5·xG with
goals-only fallback, exponential time decay, hl = 270), as ported
in `league/J1/engine/goals/`.
(b) **Identical**: DC estimation pattern and rho grid; blend-with-
fallback scheme (here the fallback binds for all 2021–2022
training matches — xG exists only from 2023); time decay;
walk-forward harness; LL/RPS + calibration gate legs.
(c) **EDA-justified changes**:
  1. *Newcomer priors (X2)* as a variant arm: promoted clubs (2 per
     year boundary) get the F4 offset (attack −0.12, defence +0.18
     goals/match, as log-ratio shifts vs the decayed league team
     mean) instead of starting at the league mean. Production never
     needed this (no feeder tier in its fit). This is also the
     template's sanctioned response to the G-J2 lesson (extreme
     lambdas for 1–2-match teams in season openers) — with 16-round
     split blocks, thin-data exposure is structural here.
  2. *Variant arm: open-play / set-play decomposition tilt (X3)*
     on top of X2, exactly as G-J1's X3 arm — F5 (r = 0.353,
     modest; the arm is gated, Gate Zero is the fallback). The
     tilt's min-8-xG-matches rule means it is inactive for
     pre-2023 targets by construction.
(d) **Forbidden**: half-share anything (F3); finishing/conversion
features (F6/R2/R3); absence features (F10); standings/h2h
snapshots (leakage).
**NOT built if**: dev walk-forward fails to beat climatology on
RPS/LL, or the virgin readout breaches the calibration leg.

## 2. Candidate S-AR — Liga Profesional shots-on-target model

(a) **Reference**: `model_sot.py` **v5** — joint ridge Poisson team
ratings + NB (r = 79.94) + Beta-Binomial on-target ratio with prior
shrinkage, ensembled 50/50 with naive trailing-10, total-shots
signal included — as ported in `league/J1/engine/sot/`.
(b) **Identical**: joint estimation pattern, NB + BB family,
ensemble, harness, LL@line + calibration legs. Target = stats-feed
SOT (blocked shots excluded). Primary line **7.5** (dev mean 7.79,
over-rate 51.0% — the line nearest the dev median); ladder
6.5 / 7.5 / 8.5.
(c) **EDA-justified variant arms** (same trio as S-J1):
  1. *RS* — BB prior raised 200 → 20,000 pseudo-shots (ratio shrunk
     to near the league constant). Tests how much of F6's measured
     team ratio signal (r = 0.555) the gate believes vs v5's
     production shrinkage.
  2. *X4* — quality-adjusted ratio from trailing xG/shot
     (F6, r = 0.472), in addition to the raw total-shots signal.
     Active only from 2023 (shotmap era).
  3. *X6* — X4 plus the era-guarded attacking xGOT trait
     (F7, r = 0.422; **AR era guard: matches dated 2025-01-01
     onward only**), judged on its era folds for the dev gate.
(d) **Forbidden**: as G-AR(d), plus defensive xGOT (R5) and the
two-stage generative family (V11, closed).
**NOT built if**: Gate Zero fails its own dev gate (variants moot),
or no arm passes the virgin calibration leg. Predictions-only
scope (no Liga Profesional SOT odds source in-system — expected).

## 3. Candidate C-AR — Liga Profesional corners model

(a) **Reference**: `model_corners_v3` — decay-weighted base rates +
rolling-5 shots relative factors + NB total + territorial
multiplier — as ported in `league/J1/engine/corners/`.
(b) **Identical**: ratings/base-rate pattern, multiplier structure,
harness, LL + calibration legs. Primary line **9.5** (dev mean
9.20, over-rate 43.9%; 8.5 is 56.3% — 9.5 is nearest the median);
ladder 8.5 / 9.5 / 10.5.
(c) **EDA-justified change** (one): the territorial covariate.
Gate Zero carries production's possession + big-chance covariates
(X9 — strong here too, F9). The variant arm replaces them with
opp-box touches (X7, F9: r = 0.749/0.802 where present), under the
min-8 trailing rule that absorbs the 2021–2023 gaps.
(d) **Forbidden**: half-share corner modelling (F3).
**NOT built if**: the box-touch arm does not beat Gate Zero on dev
(base may still ship), or the virgin calibration leg fails.

## 4. Candidate K-AR — Liga Profesional cards model

(a) **Reference**: `model_cards.py` — yellow-card count model
(decayed venue-split team ratings shrunk to the league mean,
HL = 270, K = 8, NB r = 112.39; referee not used in production) —
as ported in `league/J1/engine/cards/`.
(b) **Identical**: estimation pattern, harness, LL@line +
calibration legs — with ONE league-specific target change, forced
by measurement (Phase 1 §3.3): the target is **unified yellows
from the event feed** (`card='Yellow'`), because the stats-feed
`yellow_cards` key is not one consistent quantity in this league
(it undercounts throughout and breaks in 2026). The production
cards model's target definition (a unified yellow count) is
unchanged; only its provenance in this corpus differs, and the
reason is recorded in PREPROCESSING rule 5. Primary line **4.5**
(dev mean 4.92, over-rate 55.7%; 5.5 is 37.3% — 4.5 is nearest
the median); secondary 5.5.
(c) **EDA-justified change** (one): *variant arm with a referee
strictness covariate (X8)* — F8 (r = 0.724; warehouse referee
coverage ~100% from 2022 and 100% in the virgin block; 2021 has
no referee data and is warm-up only). Binding conditions, as in
K-J1: (i) it must beat Gate Zero on dev walk-forward; (ii) referee
assignment must be known at prediction time in the operational
pipeline — if not published pre-match for a fixture, that fixture
falls back to the base arm (no imputation).
(d) **Forbidden**: red-card modelling as a target (0.27/match rare
event; production excludes it too).
**NOT built if**: the virgin calibration leg fails, or (Gate Zero
included) the dev gate fails.

## 5. Candidate T-AR — Liga Profesional total shots model

Provenance (same as T-J1, stated plainly): the reference family is
under a frozen prospective trial on the top-5 (v2 + E9 challenger,
verdict due n ≥ 1,200 or season end — NOT reached). Per the user's
standing order for this program (J.League §6 override, applied
program-wide by the conveyor template), T-AR is built now, on this
corpus only; the top-5 trial is untouched and neither result
contaminates the other.
(a) **Reference**: the shots family in `experiments/shots_model/`
(v1 pattern) as ported in `league/J1/engine/total_shots/`.
(b) **Identical**: three frozen arms — **A** v1 pattern (joint
ridge Poisson ratings + NB + naive trailing-10 ensemble), **B**
v2 pattern (+ level layer), **C** E9 mechanism (NB r from a
trailing window; single-league analogue: league-level trailing r).
Primary line **23.5** (dev mean 24.15, over-rate 51.8%); ladder
22.5 / 23.5 / 24.5.
(c) **Changes**: none beyond per-league fitting — F2 (shots-for
r = 0.747) is the justification for building it here at all.
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
