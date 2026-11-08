# K-BNAC Verdict — X8 ships provisionally

Date: 2026-11-10. Cards use event-feed Yellow counts only. The virgin pass loaded 2023–2026 chronologically, scored only 2026 (`n = 648`), and reproduced the frozen dev pooled LLs exactly.

## Dev results

| Block | n | Gate Zero LL@4.5 | X8 LL@4.5 | League base LL@4.5 | Naive t-10 LL@4.5 |
|---|---:|---:|---:|---:|---:|
| 2024 | 722 | 0.680672 | 0.658960 | 0.696946 | 0.691228 |
| 2025 | 612 | 0.679757 | 0.660366 | 0.693055 | 0.690273 |
| **Pooled** | **1,334** | **0.680252** | **0.659605** | **0.695161** | **0.690790** |

Both arms pass the dev gate: Gate Zero `0.680252195145 < 0.695160684104` and `< 0.690789712910`; X8 `0.659605115216 < 0.695160684104` and `< 0.690789712910`. X8 wins the dev sign check in 2/2 blocks.

Secondary dev LL@5.5 (same `n`): 2024 — Gate Zero `0.620287`, X8 `0.601837`, league base `0.635232`, naive `0.630194`; 2025 — Gate Zero `0.636477`, X8 `0.621372`, league base `0.640046`, naive `0.640765`; pooled — Gate Zero `0.627714`, X8 `0.610799`, league base `0.637440`, naive `0.635044`.

## Virgin results (`n = 648`)

| Arm / baseline | LL@4.5 | LL@5.5 | Mean P(over 4.5) | Actual over-rate | Calibration diff | SE | Status |
|---|---:|---:|---:|---:|---:|---:|---|
| Gate Zero | 0.676939 | 0.629402 | 0.508952 | 0.521605 | -1.2653pp | 1.9334pp | Provisional |
| X8 | **0.669291** | **0.624247** | 0.510994 | 0.521605 | -1.0611pp | 1.9191pp | **Provisional** |
| League base rate (`n prior = 1,982`) | 0.692222 | — | 0.523713 | 0.521605 | — | — | Baseline |
| Naive trailing-10 | 0.687911 | — | — | — | — | — | Baseline |

The league base-rate virgin constant is the pooled 2023–2025 over-4.5 rate `0.523713420787`. Naive trailing-10 continues from the dev state with frozen NB `r = 112.39`.

## Per-leg verdict

| Leg | Gate Zero | X8 |
|---|---|---|
| Dev gate | PASS | PASS |
| Virgin (i), LL ≤ Gate Zero and ≤ best baseline | PASS (reference equality; `0.676939 ≤ 0.687911`) | PASS (`0.669291 ≤ 0.676939` and `≤ 0.687911`) |
| Virgin (ii), calibration | PROVISIONAL PASS: 1.2653pp breach, excess over 1pp = 0.2653pp ≤ 1 SE (1.9334pp) | PROVISIONAL PASS: 1.0611pp breach, excess over 1pp = 0.0611pp ≤ 1 SE (1.9191pp) |
| Virgin (iii), dev sign | n/a | PASS, 2/2 blocks |
| **Overall** | **PROVISIONAL PASS** | **PROVISIONAL PASS** |

Under the both-pass rule, the lowest pooled virgin LL@4.5 ships: **X8** (`0.669290808029`). Ties would go to Gate Zero. The operational referee condition is unchanged: if appointments are not published pre-match, fall back to Gate Zero for that fixture; no referee identity is imputed. Presentation halves use the frozen first-half constant **0.390091** (second half `0.609909`).

## Verification

- The virgin runner asserted exact dev reproduction: Gate Zero `0.6802521951453993`; X8 `0.6596051152161717`.
- The prediction file has 648 chronological rows; actual yellows reconcile to the 2026 source totals, half means sum to expected total, and all probabilities are in `[0,1]`.
- Independent hand checks covered one X8 fixture with at least 8 referee priors and one with fewer than 8: the former's total was recomputed from the snapshot state and referee multiplier; the latter used factor `1.0`; NB P(over 4.5) matched the CSV.
- No goals virgin file was written and `engine/goals/results_dev.json` was not changed. No commit was made.
