# Pre-registration — L1-T-CA (CA-PremierLeague total shots, Lane 1 re-entry)

**Lane 1 status.** This is a NEW candidate under the improvement
program charter (`league/IMPROVEMENT_PROGRAM.md`, Lane 1), entered
from `league/IMPROVEMENT_LANE1_INVENTORY.md` and the wave-1 cohort
report (`league/improvement_scratch/LANE1_WAVE1/cohort_report.md`
§2.2/§2.5, cohort B). The original candidate T-CA failed at the DEV
gate (`reports/T_CA_VERDICT.md`: FAIL, virgin NOT read). Its sealed
window was never read and remains genuinely sealed. This
preregistration is committed BEFORE any sealed access; one read,
verdict final, no iteration against the window after the read.

**Method difference, stated in advance (the sole difference).**
AUDIT.md §5.9: the shipped T-CA engine ran arms B/C with
`M_BAR = 24.15` in `engine/total_shots/model.py` — a constant copied
with the AR port — while the league's own derived mean sat unused in
its `results_dev.json` protocol block. Arm C's binding dev margin
was 0.0009 LL against the naive baseline, smaller than any plausible
prior effect. The corrected method derives M_BAR from this league's
own dev data and wires it into the model's LevelLayer/TrailingR.
Nothing else changes: same arms, same machinery, same baselines,
same gate legs as `PREREG_T_CA.md`.

## Derived constant (P5, gate_lib)

- Constant: `M_BAR` (level prior for arm B's level layer and arm
  C's trailing-r estimator).
- Derivation: `league/gate_lib/constants.py` `derive_level_prior`
  — the pooled mean of total shots per match (`total_shots_home +
  total_shots_away`) over ALL loaded dev-era rows: warm-up season
  2021 plus scored dev seasons 2022–2024, regular phase, included
  rows only (the harness's loaded set, n = 448). This is exactly
  the value the shipped harness already computes into its
  `results_dev.json` protocol block.
- **Derived value: M_BAR = 22.8326** (full precision
  22.832589285714285).
- The copied value 24.15 is FORBIDDEN in this candidate. Any other
  template constant is used exactly as the original prereg froze it.

## Arm of record and comparators

- **Arm of record: arm C** (E9 trailing-r mechanism, as frozen in
  `PREREG_T_CA.md`) with the corrected M_BAR = 22.8326. Only arm C
  can ship under this preregistration.
- Arm A (v1 pattern; this candidate's Gate-Zero-equivalent
  reference arm) never touches M_BAR, so its numbers reproduce the
  shipped run exactly; it is retained as a comparator/baseline only.
  The original prereg's clause "if Arm A fails its own dev gate,
  variants are moot" does NOT apply to this Lane 1 candidate — that
  veto is the gate-architecture feature this re-entry exists to
  correct (cohort report §2.5, point 3). Arm C's dev gate below is
  judged on arm C's own numbers.
- Arm B (v2 level layer) with the corrected M_BAR is computed and
  reported as a comparator only; it cannot ship under this
  preregistration.
- Baselines (harness, not models), unchanged from `PREREG_T_CA.md`:
  league base rate (for target season S, P(over 22.5) = the
  over-22.5 rate of all matches in seasons strictly before S) and
  naive trailing-10 (the trailing-10 total alone through the same
  NB machinery, arm A's MoM r). Neither baseline reads M_BAR; the
  recorded shipped baseline numbers stand.

## Target and data

- Target: total shots per match = `total_shots_home +
  total_shots_away` (stats feed).
- Scope: every included regular-season row, sorted by
  (date, match_id). One chronological walk-forward pass; every
  state updates only AFTER the match is predicted. Warm-up: season
  2021 updates state but is never scored; scored dev seasons 2022,
  2023, 2024 (n = 336).

## Frozen line and ladder

- **Primary line: 22.5**
- Ladder (reported): 21.5 / 22.5 / 23.5.
- All gate legs judged at 22.5 only (binary log-loss, natural log).

## Dev protocol

- Scored dev: seasons 2022–2024 (n = 336). The dev harness must
  not read 2025 or 2026 rows at all (enforced via
  `league/gate_lib/`'s sealed guard: dev loading asserts no sealed
  rows; P2 design seal applies to every artefact produced).
- Metric: mean binary log-loss at line 22.5, per season and
  pooled, per arm and per baseline, computed via `league/gate_lib/`
  metrics.
- The corrected dev evaluation reports the corrected arm B/C
  numbers beside the shipped (copied-constant) numbers.
- If arm C does NOT pass the dev gate, the candidate dies at dev:
  verdict FAIL (dev), the sealed window is NOT read.

## Virgin protocol

- Virgin window: season 2025 (n = 112) — the original candidate's
  virgin_primary per `config.yaml` and `PREREG_T_CA.md` — read
  **ONCE**, only if arm C passes the dev gate, after the dev-pass
  token is recorded via `league/gate_lib/` (`record_dev_pass`) and
  the window is loaded through the gate_lib sealed loader
  (`load_sealed_rows`). The walk-forward continues from the dev
  run's end state.
- Virgin metrics per arm: LL@22.5; calibration via gate_lib =
  predicted − actual (mean P(over 22.5) − actual over-22.5 rate),
  in percentage points, SE = sd(p_i − y_i)/√n reported.

## GATE LEGS (verbatim, frozen — identical to PREREG_T_CA)

Dev gate — pooled dev LL@22.5 beats BOTH baselines (league base rate; naive trailing-10), else arm dead, no virgin read. Virgin legs — (i) LL@22.5 ≤ Arm A's and ≤ best baseline's; (ii) calibration |mean P(over 22.5) − actual| ≤ 1.0 pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev per-season sign check for both-pass. Both-pass: both → lower pooled virgin LL ships; one → ships; none → FAIL.

Reading (as in the original, adapted only where the Lane 1 arm-of-
record designation requires it): leg (iii) = arm C's dev LL@22.5 ≤
Arm A's in at least half the dev seasons (≥ 2 of 3). Arm C passes
iff it survives the dev gate AND passes virgin (i)–(ii)
(PROVISIONAL counts on leg (ii), recorded as such) AND leg (iii).
Verdict labels: all legs clean → CLEAN PASS; leg (ii) provisional
with (i) and (iii) passed → PROVISIONAL PASS; otherwise FAIL. If
arm C passes, it ships (subject to the runner-join preparation on
this branch; no merge under this preregistration). Arms A and B
cannot ship under this preregistration regardless of their numbers.

## Reporting requirements

- P6 worst-fold: the verdict reports the worst dev season's legs
  (worst by the reference arm at the primary line) beside the pooled
  legs — information only, no gate change.
- P2 seal: all artefacts produced under this preregistration are
  computed on dev-era seasons only until the single sealed read;
  the verdict states the prereg commit hash and the dev-pass token
  record.
- Verdict: `reports/VERDICT_L1_T_CA.md`, with shipped vs corrected
  dev numbers and, if read, every sealed leg.

## Forbidden

The copied constant 24.15 anywhere in this candidate's runs; any
arm beyond A/B/C; any constant search on this corpus; any second
sealed read; half-share shot modelling (halves via the frozen
constant 0.447807 in presentation only).

Production code and data are untouched. No push. No merge.
