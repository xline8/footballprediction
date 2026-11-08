# Verdict — L1-T-HU-NBI (HU-NBI total shots, Lane 1)

**FAIL (dev) — neither corrected arm of record passes the dev
gate against the league base rate; sealed window NOT read.**

Lane 1 re-entry of T-HU-NBI under
`prereg/PREREG_L1_T_HUNBI.md` (prereg commit `c5dfe1ff`,
committed before any sealed access). Cohort B (AUDIT.md §5.9 +
§5.12): the shipped engine ran arms B/C with a copied
`M_BAR = 24.9` while the original prereg documents the league's
own level at 19.0425, and its "naive" baseline was wired equal
to arm B. This candidate re-ran the dev evaluation with BOTH
corrections together, via `league/gate_lib`:

- (a) M_BAR derived via `derive_level_prior` over the scored dev
  seasons 2022/2023–2024/2025 (n = 588, sum = 11197.0):
  **M_BAR = 19.0425** (19.042517006802722), wired into
  LevelLayer / TrailingR in `model_l1.py`.
- (b) True naive trailing-10 baseline:
  `nb_over(naive_total, 40.0, 19.5)` — the trailing-10 total
  alone through arm A's NB machinery, not arm B's blended
  probabilities.

Arms of record: C (E9 trailing-r) and corrected B (level layer),
both reported. Arm A retained as comparator only.

## Dev legs — shipped vs corrected

Pooled dev LL@19.5, n = 588 (seasons 2022/2023–2024/2025):

| Entity | Shipped | Corrected | vs base 0.695587 | vs naive (true) 0.716694 |
|---|---|---|---|---|
| A (comparator; no M_BAR) | 0.706730 | 0.706730 | ✗ | ✓ |
| B (level layer, arm of record) | 0.705784 | 0.705654 | ✗ by 0.010067 | ✓ |
| **C (trailing-r, arm of record)** | **0.703507** | **0.704224** | **✗ by 0.008637** | **✓** |
| league base rate | 0.695587 | 0.695587 | — | — |
| naive trailing-10 | 0.705784 (corrupt, = arm B) | **0.716694 (true)** | — | — |

Dev gate (identical to `PREREG.md`): pooled LL@19.5 must beat
BOTH baselines, plus the per-season sign check (improvement over
each baseline in EVERY scored season).

- Pooled leg: both arms of record beat the corrected true naive
  comfortably (B by 0.011040, C by 0.012470) — the §5.12 fix
  removes the vacuous/stronger comparator — but both still lose
  the pooled leg to the league base rate, the binding leg the
  cohort identified (C's shipped gap was 0.0079; corrected it
  widens slightly to 0.008637, because M_BAR = 19.0425 moved C
  by +0.000717 LL and B by only −0.000129 LL). The largest
  M_BAR distortion in the audit does not rescue either arm.
- Sign check: vs the true naive, B and C improve in all 3
  seasons. Vs the base rate, C is 0.696741 / 0.698677 / 0.717179
  against base 0.686255 / 0.704871 / 0.695871 — it wins only
  2023/2024 and loses 2022/2023 and 2024/2025; B (0.698367 /
  0.698268 / 0.720215) likewise wins only 2023/2024. The sign
  leg therefore also fails for both arms of record.

**Dev gate: FAIL for B and for C. The candidate dies at dev,
per the Lane 1 protocol; the sealed window (2025/2026,
n = 198) was NOT read.**

Fidelity of the corrected run: arm A (0.706730) and the league
base rate (0.695587) reproduce the shipped `results_dev.json`
to ≤ 1e-11 (they do not read M_BAR and the base definition is
unchanged), confirming the corrected harness is the shipped
walk-forward with only the two preregistered corrections
changed. The true naive is verified identical across all three
arm passes (tracker state is arm-independent). The dev-pass
registry (`engine/total_shots/dev_pass_registry_l1.json`)
records `L1-T-HU-NBI: dev_pass = false`; the gate_lib sealed
loader therefore refuses any sealed load for this candidate.
P2 seal check on `results_dev_l1.json`: CLEAN (no sealed-season
references).

## P6 worst-fold block (information only, no gate change)

Worst dev season by the reference arm (A) at LL@19.5:
**2024/2025**.

| Entity | Pooled LL@19.5 (corrected) | Worst-season 2024/2025 LL@19.5 (n = 197) |
|---|---|---|
| A | 0.706730 | 0.721510 |
| B | 0.705654 | 0.720215 |
| C | 0.704224 | 0.717179 |
| league base rate | 0.695587 | 0.695871 |
| naive trailing-10 (true) | 0.716694 | 0.722238 |

On the worst fold every arm degrades while the base rate holds
at 0.695871 — the pooled base-rate failure is not one easy
season's doing; the base rate beats every arm on this fold by
at least 0.0213 LL.

## Disposition

- Verdict: **FAIL (dev)** — final for this Lane 1 candidate.
- Sealed read: NO (deliberately unread; window stays sealed).
- Ships: nothing. No runner-join preparation.
- Artefacts: `engine/total_shots/model_l1.py`,
  `engine/total_shots/harness_l1.py`,
  `engine/total_shots/results_dev_l1.json`,
  `engine/total_shots/predictions_dev_l1.csv` (on disk),
  `engine/total_shots/dev_pass_registry_l1.json`.
- Prereg commit: `c5dfe1ff` (branch `build/lane1-thunbi`, first
  commit, precedes any sealed access). No push, no merge.
