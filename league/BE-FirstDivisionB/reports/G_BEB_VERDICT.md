# Verdict — G-BEB (BE-FirstDivisionB goals)

**FAIL at the dev gate. The virgin (2025/2026) was deliberately NOT
read. Nothing ships.**

Gate authority: `league/BE-FirstDivisionB/prereg/PREREG_G_BEB.md`
(committed 30b2d34, before any fitting). All numbers below were
recomputed by the coordinator from the engine's own artifacts
(`engine/goals/results_dev.json` + `engine/goals/predictions_dev.csv`,
n = 654 dev matches × 3 arms = 1,962 rows, dev seasons only) — the
two artifacts agree to 4 dp on every metric, and a clean re-run of
`run_g_beb.py dev` reproduces `results_dev.json` exactly.

## Dev results (season-blocked walk-forward; seed 2021/2022)

Pooled (n = 654):

| Arm | 1X2 LL | RPS | OU2.5 LL |
|---|---|---|---|
| Climatology / base rate | 1.0708 | 0.2381 | 0.6782 |
| Gate Zero | 1.0430 | 0.2270 | 0.7001 |
| SHRINK | 1.0430 | 0.2270 | 0.7001 |
| X2 (mover) | 1.0440 | 0.2271 | 0.7054 |

Per season, Gate Zero vs base rate (OU2.5 LL):

| Season | n | GZ LL | Clim LL | GZ OU | Base OU |
|---|---|---|---|---|---|
| 2022/2023 | 192 | 1.0351 | 1.0666 | 0.7213 | 0.6748 |
| 2023/2024 | 246 | 1.0687 | 1.0702 | 0.6923 | 0.6800 |
| 2024/2025 | 216 | 1.0209 | 1.0754 | 0.6902 | 0.6792 |

## Gate arithmetic (mechanical, prereg legs)

Dev gate: pooled 1X2 LL and RPS must beat climatology AND OU2.5 LL
must beat the base-rate baseline.

- Gate Zero: LL 1.0430 < 1.0708 ✓; RPS 0.2270 < 0.2381 ✓;
  OU 0.7001 > 0.6782 ✗ — **dev gate FAIL** (the OU leg fails pooled
  and in every individual dev season).
- Per the frozen rule ("If Gate Zero fails its own dev gate,
  variants are moot, verdict FAIL, virgin NOT read"), SHRINK and X2
  are moot. For the record: SHRINK is numerically identical to Gate
  Zero on all 654 matches — structural, not a bug: under
  season-blocked expanding fits every evaluated team has either 0
  prior in-league matches (unseen; ratings already 0) or ≥28, so
  the 1–5-match band the n/6 shrinkage bites on never occurs in
  this league (verified from the CSV: prior-count values are 0 or
  ≥28 in all three dev seasons). X2's mover sets matched the frozen
  sets exactly ({583877}; {149408, 8573, 10000}; {9992, 6351}); its
  pooled LL (1.0440) was slightly worse than Gate Zero's and its OU
  LL (0.7054) worse still; its dev sign check was 1/3 seasons.
- Virgin legs (i)–(iii): never reached. **Virgin 2025/2026 NOT
  read** (harness records `virgin_read: false`; the dev path
  asserts the forbidden seasons are absent). 2026/2027 likewise
  untouched. Both remain available to a future preregistration.

## Process note (corrected at merge time)

An interim segment of the Phase B Codex output stream (captured via
a truncated poll tail) showed pooled dev numbers (Gate Zero LL
0.9923, "ALL arms PASS the dev gate") that appear nowhere in the
run's artifacts. The COMPLETE final Phase B summary, delivered
afterwards, matches the artifacts exactly (Gate Zero pooled LL
1.043045 / RPS 0.227024 / OU 0.700108; climatology 1.070846 /
0.238064 / 0.678217; all arms dead on the OU leg) — the same reading
the builder reached independently. The discrepancy was an
interim-stream/delivery artefact, not a fabrication in the final
report. The artifacts (`results_dev.json`, `predictions_dev.csv`,
the `dev_gate` block reading `pass: false` for every arm) are
internally consistent, reproduce exactly on re-run, and match the
builder's independent recomputation — the build stands on them.
(Correction supplied by the builder post-report and applied by the
coordinator at merge, 2026-11-10.)

## What ships

Nothing. No fitted params, no virgin predictions. The goals halves
constant (0.434014, dev-era event times) remains a frozen EDA fact,
unused. G-BEB is closed as FAIL; a future attempt needs a new
preregistration (e.g. on the 2026/2027 virgin once complete, with
the stats era then available for xG-blend arms in dev).
