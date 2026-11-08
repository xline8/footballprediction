# G-AM Verdict — AM-PremierLeague goals model

Date: 2026-11-10. Branch `build/am-premier-league`. Prereg:
`league/AM-PremierLeague/prereg/PREREG_G_AM.md` (commit 98b8c9c1,
frozen before any fitting). Engine:
`league/AM-PremierLeague/engine/goals/`. Implementation by Codex
(gpt-5.6-luna) under the two-agent flow; all numbers below were
reproduced end-to-end by the coordinator's own rerun, and the engine's
lambdas were reproduced by a fresh DC implementation written from the
production pattern.

## Verdict: FAIL — Gate Zero fails the dev gate on the OU2.5 leg; nothing ships

Gate Zero beats climatology comfortably on pooled 1X2 LL and RPS,
but **loses the OU2.5 LL leg** (0.7142 vs 0.7019) — and loses it in
all four dev seasons individually. Per the frozen prereg the dev gate
requires all three legs, so Gate Zero **FAILS**. Per the frozen rule
— Gate Zero fails dev ⇒ variants moot — SHRINK is not virgin-read,
the virgin window (2026/2027, n=77) was **NOT read**, and no
predictions or fitted parameters exist for this league. This was not
the pre-fit expectation from EDA F2 (team traits strong: split-half
GF 0.78 / GA 0.76; tiers steep) — the 1X2/RPS legs confirm the team
signal is real, but the totals leg is systematically miscalibrated
(see "Why the OU leg fails" below). A FAIL is a complete outcome; no
gate was moved and no rescue arm was invented.

## Dev results (walk-forward expanding, season-blocked; n = 653)

Seed 2021/2022 (never scored); scored folds 2022/2023–2025/2026
(awarded-excluded; 7 awarded matches excluded everywhere).
Climatology per season uses pooled prior seasons only; the pooled
climatology row is the pooled score of those per-season predictions.

| Season | n | Arm | 1X2 LL | RPS | OU2.5 LL |
|---|---|---|---|---|---|
| 2022/2023 | 180 | Gate Zero | 1.0046 | 0.2133 | 0.7284 |
| 2022/2023 | 180 | SHRINK | 1.0046 | 0.2133 | 0.7284 |
| 2022/2023 | 180 | Climatology | 1.0631 | 0.2426 | 0.6993 |
| 2022/2023 | 180 | Naive trailing-10 | 0.9042 | 0.1852 | 0.7110 |
| 2023/2024 | 180 | Gate Zero | 1.0227 | 0.2243 | 0.7104 |
| 2023/2024 | 180 | SHRINK | 1.0227 | 0.2243 | 0.7104 |
| 2023/2024 | 180 | Climatology | 1.0480 | 0.2407 | 0.7022 |
| 2023/2024 | 180 | Naive trailing-10 | 0.9521 | 0.2040 | 0.7087 |
| 2024/2025 | 158 | Gate Zero | 1.0258 | 0.2354 | 0.7180 |
| 2024/2025 | 158 | SHRINK | 1.0258 | 0.2354 | 0.7180 |
| 2024/2025 | 158 | Climatology | 1.0265 | 0.2436 | 0.7123 |
| 2024/2025 | 158 | Naive trailing-10 | 0.8827 | 0.1905 | 0.6880 |
| 2025/2026 | 135 | Gate Zero | 0.9037 | 0.1805 | 0.6959 |
| 2025/2026 | 135 | SHRINK | 0.9037 | 0.1805 | 0.6959 |
| 2025/2026 | 135 | Climatology | 1.0741 | 0.2363 | 0.6928 |
| 2025/2026 | 135 | Naive trailing-10 | 0.9148 | 0.1787 | 0.7092 |
| Pooled | 653 | Gate Zero | **0.9939** | **0.2149** | **0.7142** |
| Pooled | 653 | SHRINK | **0.9939** | **0.2149** | **0.7142** |
| Pooled | 653 | Climatology | 1.0523 | 0.2410 | 0.7019 |
| Pooled | 653 | Naive trailing-10 | 0.9144 | 0.1903 | 0.7044 |

Dev gate (pooled LL and RPS must beat climatology, OU LL must beat
the base-rate baseline): Gate Zero **PASSES** LL (0.9939 < 1.0523)
and RPS (0.2149 < 0.2410) but **FAILS** OU LL (0.7142 > 0.7019, by
+0.0123). SHRINK **FAILS** identically. The model beats climatology
on 1X2 LL in all four seasons and on RPS in all four; on OU LL it
loses in all four (by +0.0292, +0.0082, +0.0058, +0.0032).

### Why the OU leg fails (diagnosis, not a rescue)

The season-blocked fit is stale on totals in a league whose goal
level rises steeply (2.42 → 2.48 → 2.79 → 3.15 across the dev
seasons). Mean predicted P(over 2.5) vs actual over-rate, from
`results_dev.csv`: 2022/23 0.372 vs 0.467 (−9.5pp), 2023/24 0.440
vs 0.506 (−6.5pp), 2024/25 0.474 vs 0.608 (−13.3pp) — the model
under-predicts totals in all three rising-level seasons, because
each season's fit is anchored on the lower levels of prior seasons
(the fitted mu climbs 1.19 → 1.24 → 1.32 → 1.49 but always one
season behind). In 2025/26, after fitting the hot 2024/25, it
over-predicts (+6.9pp) — the same staleness with the sign flipped.
The flat climatology base rate suffers the same level lag but is
less confidently wrong per match, so its OU LL wins. The 1X2 legs
survive because outcome shares move far less than totals when the
level rises.

### The naive trailing-10 finding (not a gate leg, recorded)

The naive baseline (trailing-10 GF/GA means, refreshed match by
match including within the target season) beats Gate Zero pooled on
1X2 LL (0.9144 vs 0.9939) and RPS (0.1903 vs 0.2149), and wins the
1X2 LL leg in 3 of 4 seasons outright. On OU LL the naive loses
narrowly to climatology pooled (0.7044 vs 0.7019). The naive's edge is freshness: in a fast-moving league
(rising levels, 1–2 clubs churning every season, team counts
9→12), a rating frozen at the previous season's end is stale, and
the trailing-10's in-season updating is worth ~0.08 LL. This does
not rescue G-AM — the prereg gates Gate Zero against climatology,
not against the naive, and the naive is a baseline, not a shipped
model — but it is the sharpest pointer for any future re-test under
a fresh prereg: a within-season updating fit (or a shorter
half-life) is the arm that would have to beat climatology on all
three legs, including totals.

### Why SHRINK ≡ Gate Zero (verified, not a bug)

The SHRINK arm shrinks ratings only for teams with 1–5 prior
in-league matches in the training window. Under expanding
season-blocked fits no AM team ever has 1–5 prior matches:
recomputed independently per target season, prior-match counts are
0 (brand-new clubs: 2 in 2022/23, 1 in 2023/24, 1 in 2024/25) or
≥28 (every returning club; the minimum 28 is Gandzasar in 2025/26,
whose 30-match 2024/25 season loses 2 awarded matches). n=0 is
identical to Gate Zero's unseen rule, so the two arms produce
byte-identical predictions in every season. The arm is degenerate
in this league by construction — a design note, not an implementation
defect. (The G-J2 lesson it addresses bites only in mid-season /
partial-window fits, which this walk-forward never performs.)

## Virgin results: NOT READ

Per the frozen rule, Gate Zero's dev failure makes variants moot
and the virgin is not read. `engine/goals/results_virgin.json`
records `{"virgin_read": false, "reason": "gate_zero_failed_dev",
"shipped_arm": null}`. No virgin predictions file and no
`fitted_params_virgin.json` exist (verified: no `predictions/`
directory exists). The 2026/2027 window (in progress, n=77)
remains untouched for any future re-test under a fresh prereg;
its hot running level (2.95 goals/match) was observed only as a
design-level aggregate during EDA, never fitted on.

## Per-leg verdicts

| Leg | Gate Zero | SHRINK |
|---|---|---|
| Dev gate | **FAIL** (LL ✓ −0.0585, RPS ✓ −0.0261, OU LL ✗ +0.0123 vs climatology) | **FAIL** (identical) |
| Virgin LL | not read (moot) | not read (moot) |
| Calibration | not read (moot) | not read (moot) |
| Per-season sign check | n/a (comparator) | moot (identical) |
| **Overall** | **FAIL** | **FAIL** |

## Verification notes (coordinator, independent of Codex)

- Full harness rerun by the coordinator reproduces every model
  number above exactly (dev JSON identical to Codex's run).
- Dev isolation confirmed in code and in the outputs: dev loads
  only seasons 2021/2022–2025/2026; `results_dev.csv` contains no
  2026/2027 row and none of the 7 awarded match ids; scored n = 653
  asserted in code; 1,306 CSV rows = 653 unique matches × 2 arms.
- Pooled and per-season metrics recomputed from `results_dev.csv`
  with independent code match the JSON to 6 decimals; pooled
  climatology recomputed from the CSV's climatology columns matches
  too, and the 2022/23 climatology rates match a raw recomputation
  from the CSV (HW 0.4028 / D 0.2500 / AW 0.3472 / OU 0.4028).
- Spot check: a fresh DC implementation written from the production
  pattern (not importing engine code) reproduces the engine's
  lambdas exactly (max diff 0.0) on the first 40 matches of
  2022/2023 (fold h = 0.1350, rho = −0.10, mu = 1.1862).
  Per-fold fitted params are sane (h 0.0188–0.1710, rho ∈ {0.0,
  −0.10}, mu 1.1862–1.4850) — the fit is healthy; the totals leg
  fails on staleness, not on a broken fit.
- Engine diff vs the AL sibling: `dc.py`/`arms.py` identical except
  docstrings; `harness.py` differs only in the intended adaptations
  (CSV name, HALF_SPLIT 0.4335, scored-n 653, virgin-n 77,
  playoff_excluded False, league names, predictions filename).
  No silent divergence.
- SHRINK degeneracy verified independently (prior-count audit above);
  the identical arm numbers are correct, not a silent bug.
- The virgin gate branch was exercised: running the virgin command
  wrote only the not-read marker and created no predictions or
  fitted-params file — the virgin rows were never loaded.
- One coordinator correction during verification: the EDA halves
  section first used a match-total 1H-share definition that returned
  r ≈ 0.83 — a binomial-resampling null test showed r ≈ 0.82 for
  the same definition, i.e. it is confounded by team strength, not
  a timing trait. The own-goals definition (mean r ≈ +0.08) is the
  valid test and is what EDA F3 reports; the frozen constant
  0.4335 is unaffected.

## What ships

- Nothing. G-AM: FAIL (1X2 / OU / BTTS / DC — no arm ships).
- S-AM / C-AM / K-AM / T-AM: not buildable (prereg
  `PREREG_SCKT_NOT_BUILDABLE.md`); nothing ships for them.
- League completion state: the single buildable candidate (G-AM)
  is through its gates with a FAIL verdict, and the four other
  markets are recorded not buildable — **league complete: 0 pass /
  1 fail / 4 not buildable**.
