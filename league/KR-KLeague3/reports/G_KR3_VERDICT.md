# G-KR3 verdict — FAIL (dev gate, all three legs)

Frozen decision: PREREG_G_KR3.md (prereg commit 6d1a75fb, branch
build/kr-k-league3, before any fitting). Virgin 2025 was NOT read for
goals: Gate Zero failed the dev gate, so under the frozen mechanical
rule the variant is moot and the verdict is FAIL.

Dev (pooled 2022–2024, n=690, season-blocked expanding fit):

| leg | Gate Zero | climatology | pass |
|---|---:|---:|:--|
| 1X2 LL | 1.123054 | 1.090000 | **no** |
| RPS | 0.239301 | 0.229657 | **no** |
| OU 2.5 LL | 0.708503 | 0.692295 | **no** |

Per season (Gate Zero vs climatology):

| season | n | Gate Zero 1X2 LL / RPS / OU 2.5 LL | climatology 1X2 LL / RPS / OU 2.5 LL |
|---|---:|---:|---:|
| 2022 | 240 | 1.165646 / 0.248690 / 0.713119 | 1.090619 / 0.228479 / 0.687936 |
| 2023 | 210 | 1.141262 / 0.242958 / 0.715385 | 1.088804 / 0.226896 / 0.686651 |
| 2024 | 240 | 1.064529 / 0.226712 / 0.697865 | 1.090428 / 0.233252 / 0.701593 |

Gate Zero beats climatology only in 2024 (all three legs); in 2022 and
2023 it loses on every leg. The pooled failure is not marginal: 1X2 LL
is worse by 0.033, RPS by 0.010, OU LL by 0.016. The 2021 seed is a
single short season (202 regular matches, the weakest attack-trait
league in the programme's Korean set: split-half goals-for r=0.441),
and the fit built on it does not generalise to 2022–2023.

Other arm (dev only): SHRINK is numerically identical to Gate Zero
(1.123054 / 0.239301 / 0.708503 pooled; max per-match probability
difference 0.0) — in a season-blocked fit every returning team has
≥25 prior matches and every entering team sits at the zero rating,
which scaling by count/6 cannot move; the arm is inert by construction
here, exactly as in G-KR2. Its per-season sign check passes trivially
(3/3, equal not better), which is moot once Gate Zero fails.

Verification: every headline number above was recomputed independently
from `engine/goals/predictions_dev.csv` (per-match probabilities) and
from `data/kr3_matches.csv` (expanding climatology) and matches to
1e-6. The harness was code-reviewed: season-blocked fits (train = all
matches before the target season's first kickoff), rho selected on
training data only, no 2025 or 2026 rows loaded in dev mode
(`results_dev.json` protocol: `virgin_read: false`, seasons 2021–2024
only). No X2 arm exists in the code (zero K2→K3 movers; see prereg).

Nothing ships: no fitted params, no virgin predictions, no market
joins the daily runner. The 2025 virgin season (complete, 210 matches)
and the in-progress 2026 season (182 played) remain unread and are
reserved for a future prereg.
