# Verdict — T-QASD (QA-SecondDivision total shots): **FAIL (dev gate)**

Frozen decision: PREREG_T_QASD.md (prereg commit
75aac0f17f333edbbb60e46a5fb8dbf3002f7577, before any fitting).
Virgin 2026/2027 was NOT read for total shots: no arm passed the dev
gate, so under the frozen mechanical reading the variants are moot and
the verdict is FAIL. This is a separate corpus from the top-5 prospective
total-shots trial (v2 vs E9).

Dev (within-season walk-forward over 2025/2026; warm-up rounds 1–7,
scored rounds 8–14, n = 28, date-grouped expanding fit; fit history
includes the 2024/2025 stats era, 38 matches; tuned on the 66 pre-scored
rows; λ = 300, r_A = 31.51, level cell [30.0, 0.5, 50.0], M_bar = 24.9):

| Arm | LL @ 22.5 | LL @ 23.5 | LL @ 24.5 | Dev gate |
|---|---|---|---|---|
| A (v1) | 0.6857 | 0.6644 | 0.6818 | FAIL |
| B (v2 + level layer) | 0.6845 | 0.6634 | 0.6798 | FAIL |
| C (E9 trailing-r) | 0.6847 | 0.6637 | 0.6818 | FAIL |
| League base rate | 0.6917 | 0.6923 | 0.7176 | — |
| Naive trailing-10 | 0.6674 | 0.6382 | 0.6647 | — |

All three arms beat the league base rate at the gate line 23.5 but lose
to the naive trailing-10 baseline (A by 0.0262, B by 0.0252, C by 0.0255
nats), so the dev gate fails for every arm. The fail is uniform across
the ladder: the naive baseline wins at 22.5 and 24.5 as well. The margin
is solid — this is a genuine fail, not a borderline one.

Diagnosis (recorded, not acted on): the naive baseline is unusually
strong here — its Poisson trailing-10 mean (LL 0.6382, MAE 3.906) beats
all three regression arms and the league base rate (MAE 4.129). The
arms' calibration is similar to the naive's (calibration −4.17pp for A/C,
−3.74pp for B, vs −4.23pp naive; SE ≈ 9.1pp), so the loss is per-match
sharpness, not level: on 28 scored matches the regression's team
ratings, fitted on 66 pre-scored rows across two thin seasons, add noise
rather than signal over a plain trailing mean. Arm B (level layer) is the
best arm but still 0.0252 nats behind naive.

Correction history: the first implementation pass replaced the frozen
220-line `model.py` (ShotsRegressionStore etc.) with a 25-line file, and
its naive baseline LL @ 23.5 was 3.00 — absurd for a trailing-10 mean,
indicating a broken naive computation that also contaminated the arms
via the shared ensemble. It was discarded and re-ported verbatim from
the SA seed (`model.py` is now byte-identical to the seed); the corrected
naive LL @ 23.5 is 0.6382. The corrected dev numbers above are the ones
that count; the first pass's numbers are void and are not reported.

Verification (coordinator, independent of the builder): headline LLs
recomputed from `engine/total_shots/predictions_dev.csv` by a second
path match `results_dev.json` to within 1 ulp (all fifteen numbers);
the 28 scored match ids are exactly 2025/2026 rounds 8–14; dates end
2026-04-30; no `results_virgin.json` exists; the run was re-executed
and reproduced all fitted params and LLs to full precision (only the
wall-clock `runtime_seconds` field differs). Latent defects found in the
(never-executed) virgin path — SA season count (94), the missing
2024/2025 history load, and virgin prediction fields naming the
superseded ladder (23.5/24.5/25.5 instead of 22.5/23.5/24.5) — were fixed
before this verdict (dev results unchanged). One labelling wart was also
fixed: the `baseline_league_p` column in `predictions_dev.csv` now
carries the seed's Poisson league-mean baseline probs, not the flat
over-rate. Documented adaptation (not a deviation): the level cell is
chosen on the 28-row warm-up block only, mirroring SA's "tune on the
warm-up block", while the regression/naive/base trackers evolve over the
full 66-row pre-scored history.

Nothing ships for T-QASD. The 2026/2027 virgin stays unread for total
shots; the confirmatory re-read at season end uses the corrected virgin
path.
