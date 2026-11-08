# Pre-registration — K-SE-L1 (Lane 1 re-entry of SE-Allsvenskan cards)

Frozen: 2026-11-11, before any sealed-window access under this
registration. Branch `build/lane1-kse`. This preregistration is
committed before any sealed data is loaded, and that commit is the
first commit on the branch.

Authority: `league/IMPROVEMENT_PROGRAM.md` (Lane 1 — unread sealed
windows) and the cohort design in
`league/improvement_scratch/LANE1_WAVE1/cohort_report.md` §1.2,
§1.4 and §1.5 (cohort A — variants-moot). Original registration:
`league/SE-Allsvenskan/prereg/PREREG_K_SE.md` (frozen 2026-11-09,
commit 62320f5); original verdict:
`league/SE-Allsvenskan/reports/K_SE_VERDICT.md`.

## Why this candidate exists

K-SE is one of the ten variants-moot cases named in AUDIT.md §2
cause 4. The original verdict records, on dev (warm-up 2021,
scored 2022–2024, pooled n = 720):

- Gate Zero pooled LL@3.5 = 0.6917 — beats neither baseline
  (league base rate 0.6884; naive trailing-10 0.6871).
- Arm X8 (referee covariate) pooled LL@3.5 = 0.6770 — beats BOTH
  baselines (league base rate 0.6884; naive trailing-10 0.6871).

Under the original frozen gate order, Gate Zero's dev failure made
the variants moot ("Gate Zero dev failure ⇒ FAIL, virgin NOT
read"), and the sealed window was deliberately NOT read
(`results_virgin.json` records `virgin_read: false`). The referee
trait behind X8 is F8, split-half r = 0.616. This registration is
the future prereg the cohort report §1.5 designs for exactly this
shape.

## The one method difference (stated in advance)

**Arm X8 is the arm of record.** Gate Zero is retained as a
baseline only: its dev and sealed numbers are recomputed and
reported, but its dev pass is no longer a precondition for the arm
of record's sealed read. That precondition is the
gate-architecture defect this Lane 1 cohort exists to correct;
removing it is the stated method difference. Every other leg is
identical to the original prereg.

## Target and lines

- Target: unified yellows = `yellow_home + yellow_away` (stats
  feed, `cards_source='stats'` for every SE match), exactly as the
  original prereg.
- **Primary line 3.5** (dev over-rate 0.448, closest to 0.5).
  Ladder 2.5/3.5/4.5 reported. All gate legs use binary LL at 3.5.
- Baselines: league base rate; naive trailing-10 through the same
  count distribution as the reference harness.

## Arms

1. **Arm of record — X8 (referee covariate)**, constructed exactly
   as the original prereg's X8 arm and as implemented in
   `league/SE-Allsvenskan/engine/cards/` (the J1 K engine's
   referee arm, carried over in form): Gate Zero plus the referee
   covariate — the appointed referee's trailing in-league mean
   yellows/match (strictly pre-match), shrunk toward the league
   mean with prior weight K_REF = 8 matches; the multiplier is
   clamp(shrunk rate / league mean, 0.67, 1.50) and multiplies
   both expected home and expected away yellows. Referees with
   <8 prior in-league matches, and fixtures with unknown referee
   identity, fall back to the Gate Zero prediction for that match
   (the harness records fallbacks unknown_identity / thin_history
   per season; no imputation). Warehouse coverage is NOT complete:
   referee names are absent for all of 2021 (the warm-up season)
   and for 12–29% of matches from 2022 (84.6% named in the virgin
   season 2025). The arm is testable on the named majority.
2. **Gate Zero — baseline only** (reference unmodified; referee
   not used). Reported, never gated on as a precondition, never
   shipped under this registration.

## Dev protocol

Identical to the original: training seed / warm-up 2021 (updates
state, never scored); scored dev 2022–2024 (n = 720). The dev
harness must not read 2025 / 2026 rows. Dev evaluation runs
through `league/gate_lib/` (P5): the prereg tokens are parsed
mechanically (`parse_prereg`), dev loading asserts no sealed rows
(`assert_no_sealed_rows` against the sealed seasons 2025 and
2026), all leg arithmetic uses gate_lib functions (metrics,
calibration, sign check, worst-fold inputs), and the dev-pass
token for candidate `K-SE-L1` is recorded in the gate_lib
registry before any sealed load. The recomputed X8 dev legs must
reproduce the cohort report's documented dev pass (pooled
LL@3.5: X8 0.6770 vs league base rate 0.6884 and naive
trailing-10 0.6871; Gate Zero 0.6917, within artefact rounding);
if they do NOT, this candidate STOPs — no sealed read — and the
verdict file is written as a STOPPED report explaining the
discrepancy.

## Sealed (virgin) protocol

- Window: virgin_primary: 2025 (n = 240) — the original virgin
  season named in the original prereg and in `config.yaml`,
  unread by K-SE. The 2026 confirmatory season is NOT read
  anywhere in this entry.
- Read ONCE, only after the dev-pass token is recorded, loaded
  through gate_lib's fail-closed `load_sealed_rows` loader,
  online walk-forward continuing from the dev end state.
- Calibration sign convention (gate_lib, P5): **predicted − actual**
  — calibration = mean P(over 3.5) − actual over-rate, in
  percentage points, SE = sd(p_i − y_i)/√n reported.

## GATE LEGS (identical to the original prereg, with X8 as the arm of record)

Dev gate — pooled dev LL@3.5 beats BOTH baselines (league base rate; naive trailing-10), else arm dead, no virgin read. Virgin legs — (i) LL@3.5 ≤ Gate Zero's and ≤ best baseline's (best baseline = the lower of league base rate and naive trailing-10); (ii) calibration |mean P(over 3.5) − actual| ≤ 1.0 pp, SE reported, breach within 1 SE of the boundary = PROVISIONAL PASS, breach beyond 1 SE = FAIL; (iii) dev per-season sign check: X8 dev LL@3.5 ≤ Gate Zero's dev LL@3.5 in at least half the dev seasons (≥2 of 3, the original mechanical reading).

Both-pass semantics, adapted to the single arm of record as pinned
by cohort report §1.5: X8 is the only arm that can ship. If X8
passes legs (i) and (iii) and calibration is clean, the verdict is
CLEAN PASS and X8 ships. If X8 passes legs (i) and (iii) and
calibration is a within-1-SE breach, the verdict is PROVISIONAL
PASS and X8 ships as provisional. Otherwise FAIL, nothing ships.
One read, verdict final, no iteration against the window after
the read.

## Design seal (P2)

All EDA/design artefacts for this entry are under the P2 design
seal: EDA and reliability artefacts may only be computed on
dev-era seasons. This entry takes no new design decision from any
artefact: the design is inherited verbatim from the original
prereg (frozen 2026-11-09) and from cohort report §1.5. No
sealed-season aggregate was computed or consulted in writing this
preregistration. (The 84.6% sealed-season referee-coverage figure
quoted in the original prereg and the cohort report is a coverage
count published before this program; it is not used as a design
input here.)

## Worst-fold reporting (P6)

The verdict includes the P6 worst-fold block: the worst dev season
— defined by the reference arm (Gate Zero) at the primary metric —
with every arm's and baseline's legs on that fold reported beside
the pooled legs. Information only, no gate change.

## Operational condition (carried over verbatim from the original prereg)

If a fixture's appointment is not published pre-match in the live
pipeline, it falls back to Gate Zero — no imputation. Warehouse
records are post-match snapshots and cannot prove pre-match
publication. A PASS ships with this condition attached (the
K-BNAC precedent). A separate referee operational gate is run
before shipping: upcoming SE-Allsvenskan fixtures in the FotMob
data are counted for referee names (k/N); if 0/N, the verdict
stands but shipping is blocked, and that is stated plainly in the
verdict.

## Outputs

- Dev/sealed run script:
  `league/SE-Allsvenskan/engine/cards/run_lane1.py`, executed
  under `league/gate_lib/` guards.
- Artefacts:
  `league/SE-Allsvenskan/engine/cards/results_dev_lane1.json`,
  `league/SE-Allsvenskan/engine/cards/results_virgin_lane1.json`,
  dev-pass registry
  `league/SE-Allsvenskan/engine/cards/lane1_dev_pass_registry.json`.
- Sealed predictions (arm of record):
  `league/SE-Allsvenskan/predictions/k_se_lane1_virgin_predictions.csv`
  — match_id, date, teams, actual total yellows, exp_yellows_total,
  referee, FT ladder P(over 2.5/3.5/4.5), 1H/2H ladders
  presentation-only via the frozen yellows constant 0.370
  (1H lines 0.5/1.5/2.5; 2H lines 1.5/2.5/3.5).
- Verdict: `league/SE-Allsvenskan/reports/K_SE_LANE1_VERDICT.md`,
  recording all leg numbers (dev + sealed), the P6 worst-fold
  block, and this preregistration's commit hash.

## Forbidden

Any gate move after results are seen; any second sealed read; any
arm beyond Gate Zero/X8; any constant search on this corpus; any
use of 2026 rows. Production top-5 untouched. No push. No merge.
