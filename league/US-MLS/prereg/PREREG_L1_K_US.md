# Pre-registration — L1-K-US (US-MLS cards, Lane 1 re-entry)

Frozen: 2026-11-11, before any sealed-window access under this
registration. Branch `build/lane1-kus`. This preregistration is
committed before any sealed data is loaded, and that commit is the
first commit on the branch.

Authority: `league/IMPROVEMENT_PROGRAM.md` (Lane 1 — unread sealed
windows) and the cohort design in
`league/improvement_scratch/LANE1_WAVE1/cohort_report.md` §1.2/§1.5
(cohort A — variants-moot; audit §2 cause 4). Original registration:
`league/US-MLS/prereg/PREREG_K_US.md` (frozen 2026-11-09, commit
d935f11); original verdict: `league/US-MLS/reports/K_US_VERDICT.md`.

## Why this candidate exists

The original candidate K-US failed at the DEV gate and its sealed
window was never read. The original verdict records, on dev
(scored 2022–2024, n=1529):

- Gate Zero pooled LL@4.5 = 0.678407 — beats naive trailing-10
  (0.682714) but loses to the league base rate (0.677134) by
  0.001273.
- Arm X8 (referee covariate) pooled LL@4.5 = 0.670898 — beats BOTH
  baselines (league base rate 0.677134; naive trailing-10
  0.682714).

Under the original frozen gate order ("If Gate Zero fails its own
dev gate, the variants are moot — verdict FAIL regardless of
variant dev numbers, and the virgin window is not read"), Gate
Zero's dev failure made X8 moot and the sealed window was not
read. This registration is the Lane 1 re-entry of that candidate
as a NEW candidate, judged on that unread window: one read,
verdict final, no iteration against the window after the read.

## The one method difference (stated in advance)

**Arm X8 is the arm of record.** Gate Zero is retained as a
baseline/comparator only: its dev numbers are recomputed and
reported, and it is also run on the sealed window solely as the
leg-(i) reference, but its dev pass is no longer a precondition
for the arm of record's sealed read. That precondition is the
gate-architecture defect this cohort exists to correct (cohort
report §1.5); removing it is the stated method difference. Gate
Zero cannot ship under this preregistration regardless of its
numbers. Every other leg is identical to the original prereg:
same target, same machinery, same baselines, same gate legs.

## Target and lines

- Target: total unified yellows = `yellow_home + yellow_away`
  (stats feed), exactly as the original prereg. Matches whose
  stats feed lacks yellow_cards have no target and are excluded
  from this market entirely, never filled from event counts
  (the coordinator fix recorded in the original verdict: seven
  CF Montreal matches in 2021–2022; coverage 100% from 2023).
- **Primary line: 4.5** (dev over-rate 0.402). Ladder 3.5 / 4.5 / 5.5.
  All gate legs use binary LL at 4.5.
- Baselines: league base rate (prior-seasons over-4.5 rate) and
  naive trailing-10 through the same NB, as the original harness
  computes them, at the 4.5 line. The baselines named here are
  league base rate and naive trailing-10 (climatology in the
  generic gate text is the league base rate for this candidate).

## Arms

1. **Arm of record — X8 (referee covariate)**, constructed exactly
   as frozen in the original prereg and as implemented in
   `league/US-MLS/engine/cards/` (the J1 cards seed, `model.py` /
   `harness.py`): Gate Zero plus the referee strictness covariate
   (X8, F8 r=0.634). For the appointed referee, the trailing mean
   of unified yellows within this league (matches strictly before
   kickoff), shrunk toward the running league mean with the
   engine's frozen shrinkage K_REF = 8; multiplier =
   clamp(rate / league_mean, 0.67, 1.50), applied to both the
   home and away expected yellows. A fixture whose referee is
   missing, or whose referee has <8 prior in-league matches,
   falls back to the Gate Zero prediction for that match, with
   no imputation. Only X8 can ship under this preregistration.
2. **Gate Zero — baseline only** (reference pattern, no referee:
   per-match online walk-forward, team card ratings with the
   production decay/shrinkage pattern — HL = 270, K_PRIOR = 8 —
   NB count distribution with the engine's fitted r, and ensemble
   with the naive trailing-10 as in the J1 cards engine).
   Reported, never gated on as a precondition, never shipped
   under this registration.

## Dev protocol

Identical to the original: warm-up 2021 (referee coverage 0%,
never scored); scored dev 2022, 2023, 2024 (n=1529 scored of
1532 loaded-season rows before the missing-target exclusion;
dev rows loaded including warm-up = 1997). The dev harness must
not read 2025 rows at all or any 2026 rows.

Dev evaluation runs through `league/gate_lib/` (P5): the prereg
tokens are parsed mechanically (`parse_prereg`), dev loading
asserts no sealed rows (`assert_no_sealed_rows` against the
sealed season 2025, and 2026), all leg arithmetic uses
`league/gate_lib/` functions (pooled LL, calibration, sign
check, calibration band), and the dev-pass token for candidate
`L1-K-US` is recorded via `record_dev_pass` in the gate_lib
registry BEFORE any sealed load. The recomputed X8 dev legs must
reproduce the documented dev pass (pooled LL@4.5: X8 0.670898 vs
league base rate 0.677134 and naive trailing-10 0.682714; Gate
Zero 0.678407; dev n=1529) within artefact rounding; if they do
not, this candidate STOPs — no sealed read — and the verdict
file is written as a STOPPED report explaining the discrepancy.

Documented per-season dev LL@4.5 (Gate Zero / X8 / base rate /
naive trailing-10): 2022 (n=486) 0.706163 / 0.714217 / 0.684875 /
0.684033; 2023 (n=521) 0.676576 / 0.666706 / 0.683755 / 0.699059;
2024 (n=522) 0.654393 / 0.634751 / 0.663316 / 0.665172. X8 beats
Gate Zero in 2 of 3 dev seasons — the sign check is live, not a
formality.

## Sealed (virgin) protocol

- Window: virgin_primary: 2025 (n=540) — the original virgin
  season named in the original prereg and in `config.yaml`
  (`virgin_primary: "2025"`), unread by K-US (the original
  verdict states the virgin window was NOT read and no K-US
  virgin predictions file exists).
- Read ONCE, only after the dev-pass token is recorded, loaded
  through the gate_lib sealed loader (`load_sealed_rows`, which
  asserts the recorded dev-pass token before reading), online
  walk-forward continuing from the dev end state (r estimated
  on the warm-up block per method, as in the reference harness).
  2026 is NOT read anywhere in this build.
- Calibration sign convention (gate_lib, P5): **predicted − actual**
  — calibration = mean P(over 4.5) − actual over-rate, in
  percentage points, SE = sd(p_i − y_i)/√n reported. The gate
  uses |breach|, so the legs are identical under this convention.

## GATE LEGS (identical to the original prereg, with X8 as the arm of record)

Dev gate — pooled dev LL at the primary line beats BOTH baselines
(league base rate; naive trailing-10 / climatology), else arm
dead, no virgin read. This gate is judged on the arm of record,
X8. Gate Zero's dev result is reported but is not a precondition.

Virgin legs — (i) LL ≤ Gate Zero's and ≤ best baseline's;
(ii) calibration |mean P(over) − actual| ≤ 1.0pp, SE reported,
breach within 1 SE = PROVISIONAL PASS; (iii) dev per-season sign
check for both-pass (variant dev LL ≤ Gate Zero's in at least
half the dev seasons; Gate Zero exempt). Both-pass: both → lower
pooled virgin LL ships; one → ships; none → FAIL. Ties → simpler
arm (Gate Zero first).

Lane 1 reading (adapted only where the arm-of-record designation
requires it): leg (i) = X8 sealed LL@4.5 ≤ Gate Zero's sealed
LL@4.5 AND ≤ both baselines' sealed LL@4.5 (best baseline = the
lower of league base rate and naive trailing-10); leg (ii) =
calibration |breach| ≤ 1.0 pp clean PASS, a breach beyond 1.0 pp
but within 1 SE of the boundary (≤ 1.0pp + SE) PROVISIONAL PASS,
beyond it FAIL; leg (iii) = X8 dev LL@4.5 ≤ Gate Zero's dev
LL@4.5 in at least half the dev seasons (≥2 of 3). X8 is the
only arm that can ship. If X8 passes legs (i) and (iii) and
calibration is clean, the verdict is CLEAN PASS and X8 ships.
If X8 passes legs (i) and (iii) and calibration is a within-1-SE
breach, the verdict is PROVISIONAL PASS and X8 ships as
provisional. Otherwise FAIL, nothing ships. One read, verdict
final, no iteration against the window after the read.

For this candidate the "primary line" in the gate text is 4.5
and LL means binary log-loss at 4.5.

## Design seal (P2)

All EDA/design artefacts for this entry are under the P2 design
seal (`league/design_seal/`): EDA and reliability artefacts may
only be computed on dev-era seasons. This entry takes no new
design decision from any artefact: the design is inherited
verbatim from the original prereg (frozen 2026-11-09) and from
cohort report §1.5. No sealed-season aggregate was computed or
consulted in writing this preregistration. (The 96.1% sealed-
season referee-coverage figure quoted in the original prereg
and verdict is a coverage count published before this program;
it is not used as a design input here.)

## Worst-fold reporting (P6)

The verdict includes the P6 worst-fold block
(`league/worst_fold/`): the worst dev season — defined by the
reference arm (Gate Zero) at the primary metric — with every
arm's and baseline's legs on that fold reported beside the
pooled legs. Information only, no gate change.

## Operational condition (carried over verbatim from the original prereg)

Referee assignment must be known at prediction time in the live
pipeline; warehouse records are post-match snapshots and cannot
prove pre-match publication. The no-imputation fallback above is
the operating rule regardless of the verdict.

A separate referee operational gate is run before shipping (only
if the verdict is a PASS): upcoming US-MLS fixtures in the FotMob
data are counted for referee names (k/N); if 0/N, the verdict
stands but shipping is blocked, and the verdict/report says so
plainly. Historical referee coverage (original prereg): 0% in
2021 (warm-up only), 97.3%/99.0%/96.2% in dev 2022–2024, and
96.1% in virgin 2025.

## Forbidden

Red-card target modelling (R12); halves modelling (presentation
via frozen constant 0.341 only); absence features; snapshot
features — all as in the original prereg. Any gate move after
results are seen; any second sealed read; any arm beyond Gate
Zero/X8; any constant search on this corpus; any use of 2026
rows. Production code untouched. No push. No merge.

## Outputs

- Lane 1 run script: `league/US-MLS/engine/cards/run_l1_k_us.py`,
  executed under `league/gate_lib/` guards; it does ALL leg
  arithmetic with gate_lib functions (the original harness's own
  virgin verdict writer is not used — the known §5.6-class trap).
- Artefacts: `league/US-MLS/engine/cards/results_dev_l1.json`,
  `league/US-MLS/engine/cards/results_virgin_l1.json`,
  dev-pass registry
  `league/US-MLS/engine/cards/dev_pass_registry_l1.json`.
- Virgin predictions: `league/US-MLS/predictions/k_us_virgin_predictions.csv`
  (shipped arm; evidence of the read) — match_id, date, teams,
  actual total unified yellows, exp_yellows_total, referee, FT
  ladder P(over 3.5/4.5/5.5), 1H/2H ladders presentation-only via
  frozen constant 0.341 with the arm's NB r (1H lines 0.5/1.5/2.5;
  2H lines 1.5/2.5/3.5), as in the original prereg outputs.
- Verdict: `league/US-MLS/reports/VERDICT_L1_K_US.md`, recording
  all leg numbers (dev + sealed), the P6 worst-fold block, and
  this preregistration's commit hash.
