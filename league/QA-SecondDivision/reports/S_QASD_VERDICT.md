# Verdict — S-QASD (QA-SecondDivision shots on target): **FAIL (dev gate)**

Frozen decision: PREREG_S_QASD.md (prereg commit
75aac0f17f333edbbb60e46a5fb8dbf3002f7577, before any fitting).
Virgin 2026/2027 was NOT read for SOT: no arm passed the dev gate,
so under the frozen mechanical reading the variants are moot and the
verdict is FAIL.

Dev (within-season walk-forward over 2025/2026; warm-up rounds 1–7,
scored rounds 8–14, n = 28, date-grouped expanding fit; fit history
includes the 2024/2025 stats era, 38 matches):

| Arm | LL @ 7.5 | LL @ 8.5 | LL @ 9.5 | Dev gate |
|---|---|---|---|---|
| Gate Zero (v5) | 0.6847 | 0.6649 | 0.6296 | FAIL |
| RS (BB prior 20,000) | 0.6819 | 0.6621 | 0.6263 | FAIL |
| League base rate | 0.7083 | 0.7010 | 0.6921 | — |
| Naive trailing-10 | 0.6818 | 0.6593 | 0.6202 | — |

Gate Zero beats the league base rate at the gate line 8.5 (0.6649 vs
0.7010) but loses to the naive trailing-10 baseline (0.6649 vs 0.6593,
by 0.0056 nats); RS likewise loses to naive (0.6621 vs 0.6593, by 0.0029
nats). The dev gate requires beating BOTH baselines, so both arms fail.
RS beats Gate Zero on all three lines (leg (iii) sign check would pass),
but that is moot: the dev gate itself fails, so the virgin is not read
for either arm.

Diagnosis (recorded, not acted on): this is a narrow fail, not a level
failure. Aggregate calibration is good — mean predicted over-8.5 rate
0.4438 (GZ) / 0.4434 (RS) vs actual 0.4286 (12/28) — so there is no
systematic SOT-level shortfall. The model loses on per-match sharpness
to a naive that is unusually strong here: the trailing-10 + Beta-Binomial
naive (0.6593) beats even the league base rate by 0.0417 nats. At n = 28
the dev gate is a weak discriminator (F7), and a 0.003–0.006 nat margin
is well inside sampling noise — but the gate is mechanical and was
pre-registered, so the verdict stands.

Correction history: the first implementation pass replaced the frozen v5
architecture with a simplified decayed team-mean model and neutered the
RS arm (the prior was computed but never used, so RS == GZ to full
precision). It was discarded and re-ported verbatim from the SA seed
(`Regression` + `Ratings`/Beta-Binomial ratio restored); RS now differs
from GZ on scored rows (max |Δp| = 0.0153 at 8.5). The corrected dev
numbers above are the ones that count; the first pass's numbers are
void and are not reported.

Verification (coordinator, independent of the builder): headline LLs
recomputed from `engine/sot/predictions_dev.csv` by a second path match
`results_dev.json` exactly (all twelve numbers, full precision); the 28
scored match ids are exactly 2025/2026 rounds 8–14; dates end 2026-04-30;
no `results_virgin.json` exists; the run was re-executed and reproduced
`results_dev.json` bit-identically. Latent defects found in the
(never-executed) virgin path — SA season counts (94) and the missing
2024/2025 history load — were fixed before this verdict (dev results
unchanged).

Nothing ships for S-QASD. The 2026/2027 virgin stays unread for SOT;
the confirmatory re-read at season end uses the corrected virgin path.
