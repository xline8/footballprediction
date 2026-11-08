# Pre-registration — C-PY-L1 (Lane 1 re-entry of PY-DivisionProfesional corners)

Frozen: 2026-11-11, before any sealed-window access under this
registration. Branch `build/lane1-cpy`. This preregistration is
committed before any sealed data is loaded, and that commit is the
first commit on the branch.

Authority: `league/IMPROVEMENT_PROGRAM.md` (Lane 1 — unread sealed
windows) and the cohort design in
`league/improvement_scratch/LANE1_WAVE1/cohort_report.md` §1.2,
§1.4 and §1.5 (cohort A — variants-moot). Original registration:
`league/PY-DivisionProfesional/prereg/PREREG_C_PY.md` (frozen
2026-11-09, commit 06d6a41); original verdict:
`league/PY-DivisionProfesional/reports/C_PY_VERDICT.md`.

## Why this candidate exists

C-PY is one of the ten variants-moot cases named in AUDIT.md §2
cause 4 — the only corners case in that list. The original verdict
records, on dev (seed 2025 - Apertura training only; scored
2025 - Clausura + 2026 - Apertura, pooled n = 263):

- Gate Zero pooled LL@8.5 = 0.7211 — beats the league base rate
  (0.7313) but **loses to naive trailing-10 (0.7180)**.
- Arm X7 (opp-box touches multiplier) pooled LL@8.5 = 0.6918 —
  beats BOTH baselines (league base rate 0.7313; naive
  trailing-10 0.7180), and beats Gate Zero in both dev blocks
  (2025-Cl 0.6965 vs 0.7523; 2026-Ap 0.6870 vs 0.6896).

Under the original frozen gate order, Gate Zero's dev failure made
the variant moot ("If Gate Zero fails its own dev gate, variants
are moot, verdict FAIL, virgin NOT read"), and the sealed window
was deliberately NOT read (`results_virgin.json` records
`virgin_read: false`). The touches trait behind X7 is the opp-box
touches territorial trait, split-half r = 0.70 (FEATURES.md). This
registration is the future prereg the cohort report §1.5 designs
for exactly this shape. No referee input is used by any arm, so no
referee shipping caveat applies.

## The one method difference (stated in advance)

**Arm X7 is the arm of record.** Gate Zero is retained as a
baseline only: its dev and sealed numbers are recomputed and
reported, but its dev pass is no longer a precondition for the arm
of record's sealed read. That precondition is the
gate-architecture defect this Lane 1 cohort exists to correct;
removing it is the stated method difference. Every other leg is
identical to the original prereg.

## Target and lines

- Target: `y = corners_home + corners_away` (stats feed, 2025+
  only), exactly as the original prereg.
- **Primary line 8.5** (dev-era mean 8.75). Ladder 8.5/9.5/10.5
  reported. All gate legs use binary LL at 8.5.
- Baselines: league base rate; naive trailing-10, both computed
  exactly as the original harness computes them.

## Arms

1. **Arm of record — X7 (opp-box touches multiplier)**,
   constructed exactly as the original prereg's X7 arm and as
   implemented in `league/PY-DivisionProfesional/engine/corners/`
   (the production corners-v3 pattern ported from J1/KR): Gate
   Zero plus the opp-box touches multiplier component — the
   territorial multiplier gains the touches term
   `exp(beta · z_bt)` with beta fitted by grid search on the fit
   window only (grid BBT, exactly as frozen in `core.py`), the
   multiplier clamped to [0.70, 1.43]; beta = 0 collapses X7 to
   Gate Zero numerically. A fixture whose touches trait is
   inactive (fewer than 8 valid entries in the last 10, either
   side) takes multiplier 1.0 for that component, per the frozen
   core.
2. **Gate Zero — baseline only** (the unmodified production
   pattern: possession + big chances inside the territorial
   multiplier). Reported, never gated on as a precondition, never
   shipped under this registration.

Shared engine, per-block hyperparameter fitting, walk-forward
state rules and the min-10-prior-matches scoring rule are exactly
as in the original prereg.

## Dev protocol

Identical to the original: seed 2025 - Apertura (training only,
never scored); scored dev blocks 2025 - Clausura and
2026 - Apertura (n = 264 rows, 263 scored — the one target-missing
clásico row is unscored, PREPROCESSING §9). The dev evaluation
must not read 2026 - Clausura rows. Dev evaluation runs through
`league/gate_lib/` (P5): the prereg tokens are parsed mechanically
(`parse_prereg`), dev loading asserts no sealed rows
(`assert_no_sealed_rows` against the sealed season
2026 - Clausura), all leg arithmetic uses gate_lib functions
(log-loss, pooled LL, calibration, sign check), and the dev-pass
token for candidate `C-PY-L1` is recorded in the gate_lib registry
before any sealed load. The recomputed X7 dev legs must reproduce
the cohort report's documented dev pass (pooled LL@8.5: X7 0.6918
vs league base rate 0.7313 and naive trailing-10 0.7180; Gate Zero
0.7211, within artefact rounding); if they do NOT, this candidate
STOPs — no sealed read — and the verdict file is written as a
STOPPED report explaining the discrepancy.

## Sealed (virgin) protocol — frozen cohort

- Window: virgin_primary: 2026-Clausura — the season
  **2026 - Clausura**, named as the virgin in the original prereg,
  unread by C-PY. **Frozen cohort: n = 112** — the window was
  TRANSITIONAL at the original pull (112 of 132 fixtures played),
  and the original prereg froze the window at that cohort. The
  read under this registration uses exactly that frozen
  definition: the 2026 - Clausura rows present in the league's
  data snapshot (`py_matches.csv` as built for the original build;
  112 rows, played 2026-07-24 to 2026-11-08, all with corners
  recorded). If the league's data at read time contains MORE
  2026 - Clausura matches than the frozen n = 112, the read still
  uses only the frozen cohort and the verdict states that
  explicitly; the window is never silently widened. If it contains
  FEWER, the candidate STOPs and the discrepancy is reported.
- Read ONCE, only after the dev-pass token is recorded, loaded
  through gate_lib's fail-closed `load_sealed_rows` loader. The
  sealed fit is the original harness's virgin fit: parameters
  fitted on all non-virgin rows (seed + both dev blocks), then the
  frozen cohort is scored — exactly the construction
  `harness.virgin()` would have run for a dev-passing arm.
- Calibration sign convention (gate_lib, P5): **predicted − actual**
  — calibration = mean P(over 8.5) − actual over-rate, in
  percentage points, SE = sd(p_i − y_i)/√n reported.

## GATE LEGS (identical to the original prereg, with X7 as the arm of record)

Dev gate — pooled dev LL@8.5 beats BOTH baselines (league base rate; naive trailing-10), else arm dead, no virgin read. Virgin legs — (i) LL@8.5 ≤ Gate Zero's and ≤ both baselines'; (ii) calibration |mean P(over 8.5) − actual| ≤ 1.0 pp, SE reported, breach within 1 SE of the boundary = PROVISIONAL PASS, breach beyond 1 SE = FAIL; (iii) dev per-block sign check: X7 dev LL@8.5 ≤ Gate Zero's dev LL@8.5 in at least half the dev blocks (≥1 of 2, the original mechanical reading of "at least half the dev seasons" over this league's two scored blocks).

Both-pass semantics, adapted to the single arm of record as pinned
by cohort report §1.5: X7 is the only arm that can ship. If X7
passes legs (i) and (iii) and calibration is clean, the verdict is
CLEAN PASS and X7 ships. If X7 passes legs (i) and (iii) and
calibration is a within-1-SE breach, the verdict is PROVISIONAL
PASS and X7 ships as provisional. Otherwise FAIL, nothing ships.
One read, verdict final, no iteration against the window after
the read.

## Design seal (P2)

All EDA/design artefacts for this entry are under the P2 design
seal: EDA and reliability artefacts may only be computed on
dev-era seasons. This entry takes no new design decision from any
artefact: the design is inherited verbatim from the original
prereg (frozen 2026-11-09) and from cohort report §1.5. No
sealed-season aggregate was computed or consulted in writing this
preregistration. (The frozen n = 112 and the window's played-date
range quoted above are the cohort definition published in the
original prereg and the league config, not a fresh aggregate.)

## Worst-fold reporting (P6)

The verdict includes the P6 worst-fold block: the worst dev block
— defined by the reference arm (Gate Zero) at the primary metric —
with every arm's and baseline's legs on that fold reported beside
the pooled legs. Information only, no gate change.

## Outputs

- Dev/sealed run script:
  `league/PY-DivisionProfesional/engine/corners/run_lane1.py`,
  executed under `league/gate_lib/` guards.
- Artefacts:
  `league/PY-DivisionProfesional/engine/corners/results_dev_lane1.json`,
  `league/PY-DivisionProfesional/engine/corners/results_virgin_lane1.json`,
  dev-pass registry
  `league/PY-DivisionProfesional/engine/corners/lane1_dev_pass_registry.json`.
- Sealed predictions (arm of record):
  `league/PY-DivisionProfesional/predictions/c_py_lane1_virgin_predictions.csv`
  — match_id, date, teams, actual corners home/away/total, arm,
  mu, r, gamma, beta, FT ladder P(over 8.5/9.5/10.5), 1H/2H ladders
  presentation-only via the frozen corners constant 0.492
  (1H lines 4.5/5.5/6.5; 2H lines 5.5/6.5/7.5).
- Verdict: `league/PY-DivisionProfesional/reports/C_PY_LANE1_VERDICT.md`,
  recording all leg numbers (dev + sealed), the P6 worst-fold
  block, and this preregistration's commit hash.

## Forbidden

Any gate move after results are seen; any second sealed read; any
arm beyond Gate Zero/X7; any constant search on this corpus; any
widening of the frozen sealed cohort. Production top-5 untouched.
No push. No merge.
