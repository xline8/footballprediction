# Phase 4 — Model Design: Ireland First Division Candidates

Status: **Phase A complete; no fitting performed yet.** This document
governs the IE-FirstDivision build (league/IE-FirstDivision, tracked
by the coordinator in league/PROGRAM_STATUS.md — not edited here).
The feature set is defined in `FEATURES.md` (X1 goals-only, X2
relegated-mover offset; X3/X4/X6/X7/X8/X9 and X5-as-consumed are all
rejected or inapplicable — see FEATURES §3/§4); evidence per `EDA.md`
(F1–F6).

Rules of construction:

- The architecture is **not invented from zero**. The single candidate
  names the existing proven model it references, states what stays
  conceptually identical, and lists only the changes the EDA justifies
  — each tied to a numbered finding in `EDA.md` with its reliability
  verdict.
- **1 league = 1 model**, one CSV per league (Phase 2). This league's
  engine lives under `league/IE-FirstDivision/engine/`, seeded from
  the proven reference implementation named in its candidate section
  and diverging only as this design justifies in writing, through
  this league's gate.
- Anything the audits closed stays forbidden (§3 of this document and
  FEATURES §3), including where the EDA re-tested it.
- **Feature consumption rule (Phase 3.5)**: the candidate may use only
  the features defined in `FEATURES.md` §1 and the architectural
  components delimited in its §2.

Shared validation frame (applies to the candidate; the build phase
turns this sketch into a real pre-registration before any fitting):

- **Dev period** (walk-forward, expanding window, season-blocked):
  seasons 2021–2025, **regular-season matches only** (playoffs
  excluded from fitting and evaluation — Phase 1 §1). Season 2021
  is the initial training window; evaluation seasons are 2022, 2023,
  2024, 2025 (pooled dev n = 683 regular matches).
- **Virgin window, evaluated once, after the design is frozen**:
  season 2026, **regular-season matches only** (n = 180, complete,
  2026-02-13–2026-10-16). The 5 playoff matches of 2026 are not
  predicted and not scored.
- Design-level aggregates were inspected across all seasons during
  EDA (that is what EDA is); the virgin window is virgin for
  **fitting, feature selection among arms, and gate setting**. No
  parameter may be tuned on it. The only 2026 numbers used before
  the virgin read are the coverage inventory and the mover-arrival
  identity (Cork City, relegated from the Premier Division) listed
  in `eda_numbers.json` — the X2 offset magnitudes come from dev
  transitions only.
- Baselines the candidate must beat on dev walk-forward: the league
  base rate (climatology), plus Gate Zero below.
- **Gate Zero**: the unmodified reference architecture, fitted per
  league, is itself an arm. A candidate whose justified changes do
  not beat (or at least match within the both-pass rule) its own
  reference arm does not ship its changes.
- Both-pass rule (copied from the total-shots pre-registrations): if
  base arm and variant arm both pass the gate legs (log-loss leg +
  calibration leg at ±1.0pp pooled on the virgin window, per-season
  sign check), the arm with the lower pooled log-loss ships.

## 1. Candidate G-IEFD — First Division goals model (1X2 / OU / BTTS / DC)

(a) **Reference**: the production goals model — Dixon-Coles fit as
used market-free in the experiments (per-division rho, blend
observation 0.5·goals + 0.5·xG with goals-only fallback, exponential
time decay), and its walk-forward harness. Nearest working analogue:
the sibling `league/IE-PremierDivision/engine/goals/` (goals-only DC,
same warehouse format, same season-blocked frame).

(b) **Identical**: DC estimation pattern and rho; Poisson family with
DC low-score correction; time-decay fitting; the walk-forward
evaluation harness and its log-loss/RPS + calibration gate legs.
The blend degrades to goals-only for this league because no xG
exists anywhere in the corpus (F6) — the reference's own documented
fallback, not a new design.

(c) **EDA-justified changes**:
  1. *Relegated-mover priors* (feature **X2**). When a club enters
     the First Division from the Premier Division, its initial rating
     is offset by the measured tier gap instead of starting at the
     league mean — **F4 (SIGNAL-CANDIDATE, weak, n=6)**: relegated
     arrivals score ≈ +0.23 GF and concede ≈ −0.27 GA per match vs
     the league mean in their first First Division season. The arm
     applies the frozen magnitudes (+0.23 attack, −0.27 defence) at
     season entry. Production never needed this (no feeder tier
     inside its fit); this league does, because 1–2 of its 9–10
     clubs are relegated arrivals every season. Brand-new clubs
     (Kerry FC 2023, n=1) receive no offset — league mean.
  2. *No SHRINK arm.* G-IE proved the G-J2-lesson shrinkage arm a
     no-op under season-blocked fits (a mover has 0 prior in-league
     matches at fit time, so n/6 shrinkage never engages; Gate Zero
     and SHRINK were numerically identical in every dev season).
     Including it here would be theatre; the new-team failure mode
     is addressed, if at all, by the X2 prior offset.
  3. *Regular-season scope only.* Playoffs (5/season, two-legged
     semi-finals + final) are excluded from fitting and evaluation —
     a scope decision, not an architecture change. The 2024 final
     went to extra time and penalties; the regulation score is the
     target wherever a playoff match is ever scored, but no playoff
     match is scored in this build.
  Nothing else changes. In particular the decay half-life (270 days)
  and the DC pattern are fit/validated **per league** inside the
  harness — that is parameter estimation, not an architecture change.

(d) **Forbidden here**: half-share anything (F3); finishing/form
features (F6 — no data, and NOISE where measurable elsewhere);
absence features (F10/V10 — no lineups, and CLOSED); standings/h2h
snapshots as features (post-match leakage); red-card rates as a
target or covariate (R12).

**NOT built if**: dev walk-forward fails to beat the base-rate
baseline on RPS/LL, or the virgin readout breaches the calibration
leg — and the X2 arm is dropped (base may still ship) if it does
not beat Gate Zero on dev.

## 2. Candidates S-IEFD / C-IEFD / K-IEFD / T-IEFD — NOT buildable

- **S-IEFD (SOT)**: no SOT target exists in any season (no stats
  feed, no shotmap). The virgin window contains no SOT target, so
  the candidate could never be validated.
- **C-IEFD (corners)**: no corners target exists in any season.
- **T-IEFD (total shots)**: no total-shots target exists in any season.
- **K-IEFD (cards)**: no yellow-card target exists in any season —
  the event feed lists Red / YellowRed only (210 red-family events,
  0.20/match; zero plain Yellow events in 1,028 matches), and no
  referee is ever named. Reds alone are a rare-event count the
  production cards design excludes.
- These four are recorded as NOT buildable in
  `prereg/PREREG_NOT_BUILDABLE.md`, written in Phase A before any
  fitting, and no engine is built for them. Building any of them
  anyway would break the gate rule.

## 3. Global forbidden list (audits + this EDA; no candidate may use)

1. Half-share modelling or correction of any kind, for any stat
   (halves audit, top-5; **replicated here as F3**). Frozen league
   constants are the only permitted halves mechanism (goals 0.441).
2. Lineup/absence features for SOT (V8/V10, top-5; **no lineups exist
   here at all** — not a reopening candidate).
3. Trailing finishing / conversion / on-target-rate "form" features
   (F6 — NOISE on other corpora, NO DATA here).
4. Defensive xGOT traits (F7 — NOISE side elsewhere, NO DATA here).
5. Two-stage generative SOT distributions (V11 failure stands;
   nothing here revives it — and there is no SOT target anyway).
6. Post-match snapshot features (`content.table`, `h2h`,
   teamForm) — leakage by construction.
7. Divergence WITHOUT a written design justification in this
   document and a pass through this league's own gate.
8. Any feature whose only support is a within-sample pattern
   without a reliability check — the EDA labelled those NOISE or
   descriptive (F5), and they stay out.
9. **Playoff matches in fitting or evaluation.** Two-legged knockout
   ties are outside the regular-season scope frozen here; the
   playoff final's extra time / penalties never enter a goals target.

## 4. Build order

1. G-IEFD (the only buildable candidate).
2. Nothing else — S/C/K/T are not buildable by measurement, not by
   choice. The league is complete when G-IEFD has passed through its
   gate (pass or fail) and the not-buildable record is committed.
