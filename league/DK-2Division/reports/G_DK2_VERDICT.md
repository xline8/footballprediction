# G-DK2 verdict — FAIL (virgin deliberately UNREAD)

Dev (season-blocked walk-forward, seed 2021/2022, scored 2022/2023–2024/2025,
pooled n=576), vs pooled-prior climatology:

| Arm | 1X2 LL | RPS | OU2.5 LL |
|---|---:|---:|---:|
| Gate Zero | 1.0532 | 0.2267 | 0.7406 |
| SHRINK | 1.0532 | 0.2267 | 0.7406 |
| X2 mover | 1.0314 | 0.2198 | 0.7120 |
| Climatology | 1.0781 | 0.2364 | 0.6984 |

Per-season 1X2 LL — Gate Zero: 2022/2023 1.0529, 2023/2024 1.0151,
2024/2025 1.0916. X2: 0.9720, 1.0176, 1.1046 (beats Gate Zero in 2 of 3
dev seasons — moot, see below).

Gate arithmetic: the dev gate requires Gate Zero to beat climatology on
1X2 LL, RPS and OU2.5 LL. It beats the first two (1.0532 < 1.0781;
0.2267 < 0.2364) but NOT OU2.5 LL (0.7406 > 0.6984). Gate Zero FAILS dev
⇒ variants are moot and the 2025/2026 virgin was NOT read
(results_virgin.json records this).

Notes: SHRINK is numerically identical to Gate Zero on the scored dev
seasons (0 of 576 predictions differ) — the model is fit once per season
start, so every team enters a scored season with either 0 or ≥32 training
matches and the shrink rule coincides with Gate Zero at both ends, exactly
as in G-DK1. X2 was genuinely implemented under the prereg-faithful DK-1
mechanism (blend dicts of 12/10/8 teams per scored season — the counter
includes all parent-season teams meeting the rule, most of them inert for
scoring; only the 2 entrants per season affect predictions; 156 of 576
predictions differ) and beats Gate Zero on 1X2 LL and RPS, but it too is
worse than climatology on OU2.5 LL (0.7120 > 0.6984) and is moot because
Gate Zero failed. The OU2.5 miss is a calibration story, not a near-miss:
Gate Zero's OU2.5 calibration is −9.09pp (SE 2.14pp) and X2's is −5.53pp
(SE 2.11pp) — both arms systematically under-predict over-2.5 in dev,
while home-win calibration is −2.82pp (SE 2.01pp). Nothing ships.

Review note: Codex's first dev run implemented X2 with an unregistered
twist (returning teams with old in-league history were reset to n=0, so
Næstved in 2024/2025 got a full parent-tier transplant; X2 pooled
1.0152/0.2145/0.7119, 186/576 differing). The coordinator caught it in the
line-by-line diff, restored the prereg-faithful DK-1 mechanism, and re-ran
dev. Gate Zero and SHRINK numbers are identical across both runs; only the
X2 numbers above are from the corrected implementation. The voided run's
numbers are recorded here so they are not mistaken for results.

All headline numbers independently recomputed by the coordinator from
dev_predictions.csv (pooled and per-season, all arms, plus climatology
recomputed from the raw match CSV) — all match results_dev.json to 1e-9.
The DC fit was verified bit-equivalent to DK-1's dc.py on identical
training data (max |diff| 0.0 over lambdas/probabilities).

S-DK2, C-DK2, K-DK2 and T-DK2 were never candidates: no stats feed, no
shotmap, and event cards reds-only — their targets do not exist in any
window, including the virgin window. League complete: the one buildable
candidate ran its full gate and failed it.
