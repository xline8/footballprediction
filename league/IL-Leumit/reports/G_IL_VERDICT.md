# G-IL Verdict — Israel Leumit League goals model

Date: 2026-11-09. Branch `build/il-leumit`. Prereg:
`league/IL-Leumit/prereg/PREREG_G_IL.md` (commit 0f8f4e4, frozen
before any fitting). Engine: `league/IL-Leumit/engine/goals/`.
Implementation by Codex (gpt-5.6-luna) under the two-agent flow;
every dev number below was reproduced **exactly** by the
coordinator's independent second implementation (own DC code written
from the prereg text; per-season and pooled LL/RPS/OU identical to
4 decimal places for all three arms and climatology).

## Verdict: FAIL — no arm passes the dev gate; virgin NOT read

Gate Zero fails the pooled dev gate on all three legs (LL, RPS and
OU2.5 LL all worse than climatology). X2 beats climatology on pooled
LL only and fails RPS (by 0.0002) and OU2.5 LL. SHRINK is identical
to Gate Zero by construction (see below). Per the prereg's frozen
mechanical reading — Gate Zero fails its own dev gate ⇒ variant arms
are moot, verdict FAIL, **virgin NOT read** — season 2025/2026 was
never touched by any fit or evaluation. Nothing ships; no virgin
predictions CSV and no fitted virgin parameters exist, by design.

## Dev results (walk-forward expanding, season-blocked; n = 888)

Climatology per season uses pooled prior seasons only; the pooled
climatology row is the pooled score of those per-season predictions.

| Season | n | Arm | 1X2 LL | RPS | OU2.5 LL |
|---|---|---|---|---|---|
| 2022/2023 | 296 | Gate Zero | 1.1049 | 0.2388 | 0.7124 |
| 2022/2023 | 296 | SHRINK | 1.1049 | 0.2388 | 0.7124 |
| 2022/2023 | 296 | X2 | 1.1128 | 0.2414 | 0.7090 |
| 2022/2023 | 296 | Climatology | 1.0976 | 0.2337 | 0.6886 |
| 2023/2024 | 296 | Gate Zero | 1.1058 | 0.2381 | 0.7052 |
| 2023/2024 | 296 | SHRINK | 1.1058 | 0.2381 | 0.7052 |
| 2023/2024 | 296 | X2 | 1.1106 | 0.2389 | 0.7025 |
| 2023/2024 | 296 | Climatology | 1.0919 | 0.2326 | 0.7010 |
| 2024/2025 | 296 | Gate Zero | 1.0588 | 0.2311 | 0.6970 |
| 2024/2025 | 296 | SHRINK | 1.0588 | 0.2311 | 0.6970 |
| 2024/2025 | 296 | X2 | 1.0325 | 0.2225 | 0.6971 |
| 2024/2025 | 296 | Climatology | 1.0739 | 0.2361 | 0.6935 |
| Pooled | 888 | Gate Zero | 1.0898 | 0.2360 | 0.7049 |
| Pooled | 888 | SHRINK | 1.0898 | 0.2360 | 0.7049 |
| Pooled | 888 | X2 | 1.0853 | 0.2343 | 0.7029 |
| Pooled | 888 | Climatology | 1.0878 | 0.2341 | 0.6944 |

## Gate arithmetic (pooled dev; arm must beat climatology on all three)

| Arm | LL leg | RPS leg | OU2.5 leg | Dev gate |
|---|---|---|---|---|
| Gate Zero | 1.0898 > 1.0878 FAIL | 0.2360 > 0.2341 FAIL | 0.7049 > 0.6944 FAIL | **FAIL** |
| SHRINK | identical to Gate Zero | identical | identical | **FAIL** |
| X2 | 1.0853 < 1.0878 PASS | 0.2343 > 0.2341 FAIL | 0.7029 > 0.6944 FAIL | **FAIL** |

Virgin legs: not reached for any arm. Virgin window 2025/2026
(n = 296) **deliberately unread**; 2026/2027 remains the reserved
confirmatory window, also untouched.

## Why

- **The DC model is worse than climatology in the first two dev
  seasons and better only in 2024/2025.** The pattern tracks EDA F1:
  levels drift upward (2.35 → 2.72 goals/match) and home advantage
  collapses (+0.24 → +0.01) across the corpus, so a decay-weighted
  ratings fit anchored on older, lower-scoring, stronger-home-edge
  seasons systematically lags the simple prior-season base rates.
  The OU2.5 leg fails for every arm in every dev season.
- **SHRINK ≡ Gate Zero is mathematically forced here, not a bug:**
  in a season-blocked expanding window a team's prior in-league
  match count is only ever 0 or ≥ 37 (verified directly: counts per
  target season are {0, 37, 74, 111}), so the n<6 shrinkage bites
  only at n = 0, where it sets ratings to the league mean — exactly
  Gate Zero's unseen-team rule. The arm was registered from the
  G-J2 lesson (a match-by-match failure mode); under this league's
  season-blocked frame it is vacuous.
- **X2 helps exactly where it should and nowhere else:** in
  2024/2025 — the dev season whose mover deltas the frozen
  magnitudes best match — X2 improves LL by 0.026 over Gate Zero;
  in 2022/2023 and 2023/2024 it hurts. Pooled, that is not enough:
  it passes only the LL leg. Re-estimating the magnitudes would be
  a new prereg, not a fix to this one.

## Verification notes (coordinator, independent of Codex)

- Full dev harness reproduced by an independent second
  implementation: every number in the table matches to 4 dp.
  (First pass of the verifier disagreed; the fault was traced to
  the verifier's own crossed defence ratings, fixed, and the rerun
  matches exactly. The fits themselves were also compared directly:
  identical a/d/h/rho per window, max diff 0.0.)
- Dev isolation confirmed in code: the dev path loads only seasons
  2021/2022–2024/2025 with an assert; 2025/2026 is touched only by
  the separate virgin entry point, which was never run.
- SHRINK equivalence verified from the data (prior-count sets
  above), not assumed from the identical outputs.
- Mover classification per season recomputed in the verifier from
  the Ligat ha'Al warehouse JSONs (team IDs) — same movers, same
  numbers.

## League completion state

IL-Leumit is **complete**: its only buildable candidate (G-IL,
goals) has been through its full gate and FAILs; SOT / corners /
cards / total shots are not buildable (0% stats / 0% shotmap
coverage, documented at Step 1). Nothing ships, so the league does
not join the daily pipeline. No production code, cron, or
`league/PROGRAM_STATUS.md` was touched.
