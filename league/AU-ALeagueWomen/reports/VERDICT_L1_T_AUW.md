# Verdict — L1-T-AUW (AU-ALeagueWomen total shots, Lane 1)

**FAIL (dev) — neither corrected arm passes the dev gate; the
sealed window was NOT read.**

Lane 1 re-entry of T-AUW under `prereg/PREREG_L1_T_AUW.md`
(prereg commit `8843187b`, first commit on branch
`build/lane1-tauw`, committed before any sealed access).
Cohort B (AUDIT.md §5.9): the shipped engine ran arms B/C with a
copied `M_BAR = 24.9` (J1's dev mean) while this league's own level
is ≥27.5. This candidate re-ran the dev evaluation with M_BAR
derived from the league's own dev rows via `league/gate_lib`
(`derive_level_prior` over all loaded dev-era rows, n = 439):
**M_BAR = 27.678815489749432** (27.6788). Arms of record: B
(level layer) and C (trailing-r). Arm A (the original prereg's
Gate Zero arm; never touches M_BAR) and both baselines retained
as comparators.

## Dev legs — shipped (M_BAR = 24.9) vs corrected (M_BAR = 27.6788)

Pooled dev LL@27.5, n = 369 (seasons 2022/2023–2024/2025):

| Entity | Shipped | Corrected | vs base 0.698602 | vs naive 0.696919 |
|---|---|---|---|---|
| A (Gate Zero ref; no M_BAR) | 0.698179 | 0.698179 | ✓ | ✗ |
| **B (arm of record, level layer)** | **0.698950** | **0.698867** | **✗** | **✗ by 0.0019** |
| **C (arm of record, trailing-r)** | **0.698417** | **0.698633** | **✗ by 0.00003** | **✗ by 0.0017** |
| League base rate | 0.698602 | 0.698602 | — | — |
| Naive trailing-10 | 0.696919 | 0.696919 | — | — |

Dev gate (identical to `PREREG_T_AUW`): pooled LL@27.5 must beat
BOTH baselines. The correction moved arm B by only −0.000083 LL
(0.698950 → 0.698867, the expected direction for an understated
level prior) and arm C by +0.000216 (0.698417 → 0.698633, the
wrong direction); neither comes close to closing the naive gap
(0.0019 / 0.0017), and both also lose to the league base rate
under corrected code. **Dev gate: FAIL for both arms of record.
The candidate dies at dev, per the Lane 1 protocol; the sealed
window (season 2025/2026, n = 110) was NOT read.**

Fidelity of the corrected run: arm A and both baselines reproduce
the shipped `results_dev.json` to ≤ 6e-16 on every per-season and
pooled cell (they do not read M_BAR), confirming the corrected
harness is the shipped walk-forward with only the M_BAR wiring
changed. The dev-pass registry
(`engine/total_shots/dev_pass_registry_l1.json`) records
`L1-T-AUW: dev_pass = false`; the gate_lib sealed loader was
verified to refuse any sealed load for this candidate
("dev pass is not exactly True"). P2 seal check on
`results_dev_l1.json`: CLEAN (no sealed-season references).

Sign check (leg iii, information at a dev death): corrected arms
vs arm A per season — B: 2022/2023 ✓ (0.719422 ≤ 0.722307),
2023/2024 ✗, 2024/2025 ✗ → 1 of 3; C: 2022/2023 ✗, 2023/2024 ✗,
2024/2025 ✓ (0.670502 ≤ 0.671558) → 1 of 3. Both would also have
failed leg (iii) had the window been read. Moot.

## P6 worst-fold block (information only, no gate change)

Worst dev season by the reference arm (A) at LL@27.5:
**2022/2023**.

| Entity | Pooled LL@27.5 (corrected) | Worst-season 2022/2023 LL@27.5 (n = 99) |
|---|---|---|
| A | 0.6982 | 0.7223 |
| B | 0.6989 | 0.7194 |
| C | 0.6986 | 0.7230 |
| baseline_league | 0.6986 | 0.7081 |
| baseline_naive | 0.6969 | 0.7024 |

On the worst fold both baselines beat every arm by a wide
margin — the pooled near-miss is not one easy season's doing,
and on this fold the corrected B is the only arm that improves
on A.

## Disposition

- Verdict: **FAIL (dev)** — final for this Lane 1 candidate.
- Sealed read: NO (deliberately unread; window stays sealed).
- Ships: nothing. No runner-join preparation.
- Artefacts: `engine/total_shots/model_l1.py`,
  `engine/total_shots/harness_l1.py`,
  `engine/total_shots/results_dev_l1.json`,
  `engine/total_shots/predictions_dev_l1.csv` (on disk),
  `engine/total_shots/dev_pass_registry_l1.json`.
- Prereg commit: `8843187b` (branch `build/lane1-tauw`, first
  commit, precedes any sealed access). No push, no merge.
