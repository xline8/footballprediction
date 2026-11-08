# Total Shots — Phase/Regime Diagnostic (history only)

Written 2026-11-08, after v2 failed its virgin 2026/27 window
(RESULTS.md: calibration −6.04pp pooled; top-5 −6.76pp). Purpose:
decide, from past data only, whether early 2026/27's shot heat is
(a) a recurring early-season phase pattern, (b) a persistent level
shift, or (c) a data artefact — and thereby which follow-up
protocol (if any) may be frozen. **No candidate model was tuned or
run for this diagnostic.** Script: `run_phase_diagnostic.py`.

Scope notes (read first):

- The brief asked for history 2015/16–2025/26, but
  `all_matches_clean.csv` contains **no rows before 2017/18 at all**
  (any division). History here is therefore **2017/18–2025/26
  (9 completed seasons)**; the case under study is 2026/27.
  Top-5 divisions only (E0, D1, I1, SP1, F1); total shots = HS+AS;
  16,560 matches used (3 dropped for missing HS/AS).
- v2's headline "actual Over 54.6%" was pooled across all spine
  divisions (n = 2,032). On the top-5 scope of this diagnostic,
  2026/27's actual Over-25.5 rate is **61.9%** (n = 451) — same
  window (through 2026-11-02), different scope, no contradiction.

## Q1 — Season phase: is there a consistent early-season elevation?

Ratios are within division-season (match total ÷ that
division-season's mean), pooled over 2017/18–2025/26, so the phase
shape is separated from season levels.

By days since division-season start:

| Days | n | Pooled ratio | Season median | IQR | Range | Seasons > 1.0 |
|---|---|---|---|---|---|---|
| 0–30 | 1,816 | 1.005 | 1.007 | [0.990, 1.018] | [0.972, 1.028] | 5/9 |
| 31–60 | 1,592 | 1.001 | 1.000 | [0.980, 1.013] | [0.975, 1.039] | 4/9 |
| 61–90 | 1,676 | 0.997 | 0.997 | [0.983, 1.011] | [0.958, 1.027] | 4/9 |
| 91–120 | 1,792 | 1.007 | 0.993 | [0.990, 1.033] | [0.963, 1.046] | 4/9 |
| 121–150 | 1,468 | 1.002 | 0.989 | [0.985, 1.016] | [0.970, 1.035] | 4/9 |
| 151–180 | 1,726 | 0.987 | 0.976 | [0.970, 1.002] | [0.965, 1.017] | 3/9 |
| 181–210 | 1,741 | 0.984 | 0.985 | [0.973, 1.003] | [0.932, 1.025] | 3/9 |
| 211–240 | 1,554 | 1.004 | 0.998 | [0.988, 1.010] | [0.970, 1.055] | 3/8 |
| 241–270 | 1,604 | 1.005 | 1.004 | [0.990, 1.010] | [0.980, 1.078] | 5/8 |
| 271+ | 1,140 | 1.015 | 1.050 | [1.042, 1.052] | [0.963, 1.075] | 7/8 |

By calendar month the picture is the same: Aug 1.001, Sep 1.011,
Oct 1.001, Nov 1.001, Dec 0.998, **Jan 0.991, Feb 0.986, Mar 0.984**
(a mild mid-winter dip), Apr 1.004, **May 1.032** (the only strong
phase feature — the late-season rise, mirrored in days 271+).

First-60-days factor per season (vs own season mean): median 1.010,
IQR [0.983, 1.012], range [0.975 (2020/21), 1.030 (2017/18)]; only
5 of 9 seasons above 1.0. 2026/27's own factor is 1.008 — ordinary.

**Answer Q1: NO consistent early-season elevation.** The first 90
days sit at ratio ≈ 1.00 (pooled 1.005 / 1.001 / 0.997). The
largest phase effect anywhere near the early window is worth
roughly +0.25 shots — an order of magnitude below the 2026/27
deviation measured in Q2 (+3.35). A phase curve cannot explain
2026/27, and fitting one would be fitting noise (cf. the halves
audit: phase-shape corrections are this project's recurring
mirage).

## Q2 — How unusual is 2026/27's start?

Early window E1 = matches on/before Nov 2 of the start year (the
v2 verdict window: n = 451 top-5, per division E0 90 / D1 72 /
I1 99 / SP1 109 / F1 81 — the script reproduces these exactly).
E2 (first 100 matches per division) gives the same picture and is
in the script output.

| Season | Early n | Early mean | Early Over% | Full mean | Full Over% | Early − full (shots) | Early − full (pp) |
|---|---|---|---|---|---|---|---|
| 2017/18 | 508 | 25.34 | 45.3 | 24.79 | 42.2 | +0.55 | +3.1 |
| 2018/19 | 494 | 24.46 | 39.1 | 24.20 | 39.4 | +0.26 | −0.4 |
| 2019/20 | 527 | 24.17 | 42.3 | 23.73 | 37.4 | +0.45 | +4.9 |
| 2020/21 | 341 | 22.61 | 31.1 | 23.04 | 32.6 | −0.42 | −1.6 |
| 2021/22 | 535 | 24.49 | 39.8 | 24.91 | 44.1 | −0.43 | −4.3 |
| 2022/23 | 604 | 25.37 | 47.0 | 25.00 | 44.1 | +0.36 | +2.9 |
| 2023/24 | 478 | 25.85 | 52.5 | 26.04 | 51.9 | −0.19 | +0.6 |
| 2024/25 | 477 | 25.23 | 43.8 | 24.80 | 43.1 | +0.44 | +0.7 |
| 2025/26 | 486 | 24.90 | 45.1 | 25.16 | 45.6 | −0.26 | −0.5 |
| **2026/27** | **451** | **27.98** | **61.9** | (partial) | | — | — |

For a partial season the within-season elevation is mechanically
zero, so the correct yardstick is the **level deviation** from the
historical norm (mean of full-season means 2017/18–2025/26 =
**24.63**):

- 2026/27 early deviation: **+3.35 shots** (phase-adjusted, using
  the typical early factor φ = 1.011: **+3.09**).
- Historical early deviations: range **[−2.02, +1.22]**, i.e. the
  largest previous hot start (2023/24, +1.22) is barely a third of
  2026/27's. Phase-adjusted historical range: [−2.28, +0.96] —
  2026/27's +3.09 is **3.2× the largest** value in 9 seasons.
- By early-window level, 2026/27 ranks **1st of 10 seasons**
  (27.98; next hottest early window: 2023/24 at 25.85). Its
  Over-25.5 rate of 61.9% stands against a historical early range
  of 31.1–52.5% and a historical full-season range of 32.6–51.9%.
- All five divisions are elevated (early means: D1 30.36, I1 28.87,
  E0 27.38, SP1 26.96, F1 26.81) — a broad level shift, not one
  league's quirk.

**Answer Q2: the most extreme start in the sample, by level, by a
wide margin — and not attributable to phase (Q1) or to one
division.**

## Q3 — Persistence: does early heat stay, or revert?

Per completed season, early deviation (E1 mean − 24.63) vs
rest-of-season deviation (post-Nov-2 mean − 24.63):

| Season | Early dev | Rest dev |
|---|---|---|
| 2017/18 | +0.72 | −0.05 |
| 2018/19 | −0.17 | −0.52 |
| 2019/20 | −0.45 | −1.10 |
| 2020/21 | −2.02 | −1.49 |
| 2021/22 | −0.14 | +0.46 |
| 2022/23 | +0.74 | +0.19 |
| 2023/24 | +1.22 | +1.48 |
| 2024/25 | +0.60 | +0.00 |
| 2025/26 | +0.27 | +0.63 |

- OLS rest_dev ~ early_dev: **slope 0.78, Pearson r = 0.82**
  (n = 9 seasons; phase-adjusted version identical up to the
  constant shift: slope 0.78, r = 0.82).
- Two-group: seasons starting above the median early deviation
  averaged rest_dev **+0.41**; below-median starters averaged
  **−0.41**.
- Among the 5 hot starts (early_dev > 0), the rest of the season
  kept on average **76%** of the early deviation
  (mean rest_dev / early_dev = 0.76). 2023/24 is the archetype:
  hot start, hot rest — a whole-season level shift.

**Answer Q3: early deviations mostly PERSIST.** They behave as
season-level shifts, not as phase blips: roughly three quarters of
an early deviation survives into the rest of the season. Applied
to 2026/27, the historical regression implies a rest-of-season
level around **27.1 shots** (norm 24.63) — stated with its
caveats: n = 9 seasons, and 2026/27's early deviation (+3.35) lies
far outside the historical regressor range (max +1.22), so this is
directional evidence, not a precise forecast. But the sign and the
mechanism are clear: nothing in 9 seasons of history shows an
early level deviation of even half this size snapping back to the
norm mid-season.

## Q4 — Artefact check: spine vs FotMob warehouse

Join on (div, season, date, home, away) against
`data_enrichment/shot_lineup_features.csv` (FotMob totals);
**every** features row matched in all three seasons (0 unmatched).

| Season | n | Exact | \|diff\| ≤ 1 | \|diff\| ≤ 2 | Mean diff (FotMob − spine) | Mean \|diff\| |
|---|---|---|---|---|---|---|
| 2024/25 | 1,751 | 83.2% | 95.6% | 97.3% | +0.22 | 0.30 |
| 2025/26 | 1,752 | 89.0% | 99.4% | 99.9% | +0.06 | 0.12 |
| 2026/27 | 451 | 88.9% | 99.6% | 100.0% | +0.10 | 0.12 |

On the identical matched matches, FotMob's own mean for 2026/27
is **28.08** vs the spine's 27.98 — the independent provider sees
the same heat, marginally hotter. FotMob counts alone reproduce
the Q2 picture: early-window means 25.42 (2022/23), 26.00
(2023/24), 25.82 (2024/25), 24.95 (2025/26), **28.08 (2026/27)**.

**Answer Q4: artefact RULED OUT.** 2026/27's spine-vs-FotMob
agreement is in line with (slightly cleaner than) the two prior
seasons; there is no counting/source change inflating this
season's spine numbers. The heat is in both providers
independently.

## Branch decision

The evidence is one-directional on all four questions:

- Q1 kills the phase explanation (early phase ≈ ×1.00; Branch B's
  premise — a *stable early-season elevation* — does not exist at
  any usable size).
- Q2 + Q4 establish a real, broad, record-size level shift.
- Q3 establishes that early level deviations of this kind
  historically **persist** into the rest of the season
  (slope 0.78, ~76% retention).

→ **Branch A.** The follow-up frozen in
`PREREG_PROSPECTIVE.md` is the prospective test of the v2 design,
byte-identical (commit 92fe654), on top-5 matches from
2026-11-09 onward. Branch B is not frozen: building a phase curve
on a pattern the data does not contain would repeat the halves
mistake. The evidence is not ambiguous, so a prereg is written.

One honest limit: this diagnostic shows the shift persists
*within* a season historically; whether 2026/27's level marks a
multi-season regime change is unknowable from data through
2026-11-02 and is not claimed. The prospective test judges only
the frozen design on the rest of 2026/27 (plus its pre-committed
confirmation rule) — not the regime question.
