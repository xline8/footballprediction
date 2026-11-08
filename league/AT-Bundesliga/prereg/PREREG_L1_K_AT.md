# Pre-registration — K-AT-L1 (Lane 1 re-entry of AT-Bundesliga cards, yellows)

Frozen: 2026-11-11, before any sealed-window access under this
registration. Branch `build/lane1-kat`. This preregistration is
committed before any sealed data is loaded, and that commit is the
first commit on the branch.

Authority: `league/IMPROVEMENT_PROGRAM.md` (Lane 1 — unread sealed
windows) and the cohort design in
`league/improvement_scratch/LANE1_WAVE1/cohort_report.md` §1.5 and
§4 item 2. Original registration:
`league/AT-Bundesliga/prereg/PREREG_K_AT.md` (frozen 2026-11-09);
original verdict: `league/AT-Bundesliga/reports/K_AT_VERDICT.md`.

## Why this candidate exists

K-AT is the 11th variants-moot case (not named in AUDIT.md §2's list
of 10; found during the cohort report's §5.6 screening and accepted
into Lane 1 wave 1, cohort A, by the coordinator on the strength of
its own verdict document). The original verdict records, on dev:

- Gate Zero pooled LL@4.5 = 0.6654 — beats the league base rate
  (0.6803) but loses to naive trailing-10 (0.6636).
- Arm X8 (referee covariate) pooled LL@4.5 = 0.6561 — beats BOTH
  baselines (league base rate 0.6803; naive trailing-10 0.6636).

Under the original frozen gate order, Gate Zero's dev failure made
the variants moot and the sealed window was not read. The original
verdict calls the X8 dev result "the standing diagnosis for any
future prereg". This registration is that future prereg.

## The one method difference (stated in advance)

**Arm X8 is the arm of record.** Gate Zero is retained as a baseline
only: its dev and sealed numbers are recomputed and reported, but
its dev pass is no longer a precondition for the arm of record's
sealed read. That precondition is the gate-architecture defect this
Lane 1 cohort exists to correct; removing it is the stated method
difference. Every other leg is identical to the original prereg.

## Target and lines

- Target: total yellows = `yellow_home + yellow_away` (stats feed,
  100% coverage), exactly as the original prereg.
- **Primary line 4.5** (dev over-rate 41.0%). Ladder 3.5 / 4.5 / 5.5.
  All gate legs use binary LL at 4.5.
- Baselines: league base rate (prior-seasons over-4.5 rate) and
  naive trailing-10 through the same NB, as the original harness
  computes them, at the 4.5 line.

## Arms

1. **Arm of record — X8 (referee covariate)**, constructed exactly
   as the original prereg's X8 arm: Gate Zero plus the referee
   strictness covariate (trailing referee mean of unified yellows
   within this league, shrunk toward the league mean with the
   engine's frozen shrinkage K_REF = 8, multiplier clamped to
   [0.67, 1.50]; referees with <8 prior in-league matches take the
   shrunk league mean). A fixture whose CSV referee is missing
   falls back to the Gate Zero prediction for that match (no
   imputation).
2. **Gate Zero — baseline only** (reference pattern, no referee).
   Reported, never gated on, never shipped under this registration.

## Dev protocol

Identical to the original: warm-up 2021/2022 (updates state, never
scored); scored dev 2022/2023–2024/2025 (n=585). The dev harness
must not read 2025/2026 or 2026/2027 rows. Dev evaluation runs
through `league/gate_lib/` (P5): the dev-pass token for candidate
`K-AT-L1` is recorded in the gate_lib registry before any sealed
load, and the sealed rows are loaded only through the fail-closed
`load_sealed_rows` loader. The recomputed X8 dev legs must
reproduce the documented dev pass (pooled LL@4.5 0.6561 vs league
base rate 0.6803 and naive trailing-10 0.6636, within artefact
rounding); if they do not, this candidate STOPs — no sealed read —
and the verdict file records the discrepancy.

## Sealed (virgin) protocol

- Window: virgin_primary: 2025/2026 (n=195) — the original virgin
  season named in the original prereg, unread by K-AT (no K-AT
  virgin predictions file exists; the original verdict states the
  season "remains unread by this candidate").
- Read ONCE, only after the dev-pass token is recorded, online
  walk-forward continuing from the dev end state.
- Calibration sign convention (gate_lib, P5): **predicted − actual**
  — calibration = mean P(over 4.5) − actual over-rate, in percentage
  points, SE reported.

## GATE LEGS (identical to the original prereg, with X8 as the arm of record)

Dev gate — the arm of record's pooled dev LL at the primary line
beats BOTH baselines (league base rate; naive trailing-10 /
climatology), else the arm is dead and there is no sealed read.
Gate Zero's dev result is reported but is not a precondition.

Sealed legs — (i) X8 sealed LL ≤ Gate Zero's sealed LL and ≤ the
best baseline's sealed LL (best baseline = the lower of league base
rate and naive trailing-10); (ii) calibration
|mean P(over) − actual| ≤ 1.0 pp = CLEAN PASS; a breach beyond
1.0 pp but within 1 SE of the boundary = PROVISIONAL PASS; a breach
beyond 1 SE = FAIL; (iii) dev per-season sign check: X8 dev LL ≤
Gate Zero's dev LL in at least half the dev seasons (≥2 of 3).

Both-pass semantics, adapted to the single arm of record as pinned
by cohort report §1.5: X8 is the only arm that can ship. If X8
passes legs (i) and (iii) and calibration is clean, the verdict is
CLEAN PASS and X8 ships. If X8 passes legs (i) and (iii) and
calibration is a within-1-SE breach, the verdict is PROVISIONAL
PASS and X8 ships as provisional. Otherwise FAIL, nothing ships.
One read, verdict final, no iteration against the window after the
read.

## Design seal (P2)

All EDA/design artefacts for this entry are under the P2 design
seal: EDA and reliability artefacts may only be computed on dev-era
seasons. This entry takes no new design decision from any artefact:
the design is inherited verbatim from the original prereg (frozen
2026-11-09) and from cohort report §1.5. No sealed-season aggregate
was computed or consulted in writing this preregistration. (The
91.8% sealed-season referee-coverage figure quoted in the original
verdict and the cohort report is a coverage count published before
this program; it is not used as a design input here.)

## Worst-fold reporting (P6)

The verdict includes the P6 worst-fold block: the worst dev season
— defined by the reference arm (Gate Zero) at the primary metric —
with every arm's and baseline's legs on that fold reported beside
the pooled legs. Information only, no gate change.

## Operational condition (carried over verbatim from the original prereg)

Referee assignment must be known at prediction time in the live
pipeline; warehouse records are post-match snapshots and cannot
prove pre-match publication. The no-imputation fallback above is
the operating rule regardless of the verdict: an unpublished
appointment falls back to Gate Zero for that fixture, with no
imputation, and a PASS ships with that condition attached. A
separate referee operational gate is run before shipping: upcoming
AT-Bundesliga fixtures in the FotMob data are counted for referee
names (k/N); if 0/N, the verdict stands but shipping is blocked.

## Forbidden

Red-card target modelling; halves modelling (presentation via the
frozen constant 0.316 only); absence features; snapshot features —
all as in the original prereg.

## Outputs

- Dev/sealed run script:
  `league/AT-Bundesliga/engine/cards/run_lane1.py`, executed under
  `league/gate_lib/` guards.
- Artefacts: `league/AT-Bundesliga/engine/cards/results_dev_lane1.json`,
  `league/AT-Bundesliga/engine/cards/results_virgin_lane1.json`,
  dev-pass registry
  `league/AT-Bundesliga/engine/cards/lane1_dev_pass_registry.json`.
- Sealed predictions (arm of record):
  `league/AT-Bundesliga/predictions/k_at_lane1_virgin_predictions.csv`
  — match_id, date, teams, actual total yellows, exp_yellows_total,
  referee, FT ladder P(over 3.5/4.5/5.5), 1H/2H ladders
  presentation-only via frozen constant 0.316 with the arm's NB r
  (1H lines 0.5/1.5/2.5; 2H lines 1.5/2.5/3.5).
- Verdict: `league/AT-Bundesliga/reports/K_AT_LANE1_VERDICT.md`,
  recording all leg numbers (dev + sealed), the P6 worst-fold
  block, and this preregistration's commit hash.
