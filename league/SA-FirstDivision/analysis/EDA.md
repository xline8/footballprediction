# Phase 3 — EDA: SA-FirstDivision

Source: `league/SA-FirstDivision/data/safd_matches.csv`, computed by
`analysis/eda_compute.py` → `analysis/eda_numbers.json`. Every number
below comes from that file.

**Virgin discipline.** Only DEV seasons are analysed here: goals in
2024/2025 regular played (n=306) and SOT/corners/total-shots/yellows
in 2025/2026 regular played (n=304). Goals levels for 2025/2026 and
all outcome levels for 2026/2027 are NOT in this document (goals
virgin / count-markets virgin). Regular played = phase `regular` AND
awarded `0` throughout (playoffs and the 2 awarded matches excluded).

Reference points in this document are the SA-ProLeague EDA
(post-break levels, same country) and the J1 checklist bars; no other
league's numbers are quoted.

## F1 — Levels (dev seasons only)

**Goals, 2024/2025 (n=306):** 2.595 goals/match (home 1.386, away
1.209), home edge +0.176, home win 40.5% / draw 26.8% / away win
32.7%, OU1.5 72.5%, **OU2.5 50.0%**, OU3.5 27.1%, BTTS 52.3%.
Team GD spread SD 0.615 — narrower than SA-ProLeague post-break
(0.896) and pre-break (0.663): the top team is an outlier, the rest
are compressed. Top: Neom SC +1.559 GD/match (next: Al Bukayriyah
+0.647, Al Najma +0.618). Bottom: Al Safa −1.059, Ohod −0.706.
Home edge +0.176 is nearly identical to SA-ProLeague post-break
(+0.175). One 9-goal match exists (Al Batin vs Neom SC, 2025-04-08).

**Count targets, 2025/2026 (n=304):**

| Target | Mean/match | Home | Away | vs SA-ProLeague post-break |
|---|---:|---:|---:|---:|
| SOT | 8.326 | 4.477 | 3.849 | 9.038 |
| Corners | 9.171 | 4.849 | 4.322 | 9.678 |
| Total shots | 23.546 | 12.513 | 11.033 | 24.645 |
| Event yellows | 4.418 | 2.151 | 2.266 | 4.074 |
| Stats yellows | 4.128 | 1.997 | 2.132 | — |
| Touches opp box | 39.115 | 20.809 | 18.306 | — |
| Big chances | 4.678 | 2.53 | 2.148 | — |
| Fouls | 23.451 | 11.99 | 11.461 | — |
| Red cards (stats) | 0.28 | — | — | — |

Every attacking level sits below the Pro League's post-break level —
a tier-2 league, as expected — except event yellows (4.418 vs 4.074),
which run slightly hotter. Per-match total distributions (dev
seasons) are tabulated in §F1b; the shapes are unimodal and
unremarkable (no bimodality, no truncation artefacts).

### F1b — Per-match total distributions (counts of matches)

- Goals 2024/25 (0–9): 0:23, 1:61, 2:69, 3:70, 4:46, 5:25, 6:10,
  7:1, 8:0, 9:1.
- SOT 2025/26 (1–18): 1:1, 2:5, 3:8, 4:16, 5:23, 6:34, 7:32, 8:37,
  9:53, 10:29, 11:20, 12:16, 13:17, 14:6, 15:5, 16:1, 17:0, 18:1.
- Corners 2025/26 (2–19): 2:2, 3:6, 4:12, 5:26, 6:21, 7:29, 8:35,
  9:41, 10:33, 11:32, 12:16, 13:17, 14:15, 15:9, 16:4, 17:3, 18:2,
  19:1.
- Total shots 2025/26 (9–41): 9:1, 10:0, 11:1, 12:2, 13:1, 14:3,
  15:10, 16:10, 17:13, 18:21, 19:14, 20:22, 21:20, 22:15, 23:23,
  24:21, 25:15, 26:18, 27:25, 28:16, 29:12, 30:4, 31:13, 32:7, 33:4,
  34:4, 35:1, 36:4, 37:2, 38:1, 39:0, 40:0, 41:1.
- Event yellows 2025/26 (0–10): 0:3, 1:13, 2:32, 3:55, 4:58, 5:55,
  6:47, 7:22, 8:14, 9:4, 10:1.

## F2 — Team-trait reliabilities (split-half, odd/even per team)

Method (SA/J1): per team, matches in chronological order split into
odd/even halves; Pearson r of the two half-means; minimum 10 matches
per team (all 18 teams qualify in both dev seasons: 17 vs 17 for
goals, 16–17 vs 16–17 for count targets — every team plays ~34
regular matches per season).

| Trait (dev season) | r | Verdict |
|---|---:|---|
| Goals for (2024/25) | 0.539 | SIGNAL (moderate) |
| Goals against (2024/25) | 0.595 | SIGNAL (moderate) |
| SOT for (2025/26) | 0.688 | SIGNAL |
| SOT against | 0.601 | SIGNAL |
| Corners for | 0.735 | SIGNAL |
| Corners against | 0.432 | SIGNAL (weak-moderate) |
| Total shots for | 0.808 | SIGNAL (strong) |
| Total shots against | 0.773 | SIGNAL (strong) |
| Touches opp box for | 0.790 | SIGNAL (strong) |
| Touches opp box against | 0.735 | SIGNAL |
| Big chances for | 0.624 | SIGNAL |
| Possession | 0.781 | SIGNAL |
| Fouls for | 0.494 | SIGNAL (moderate) |
| Event yellows for | 0.156 | **NOISE** |
| Stats yellows for | 0.190 | **NOISE** |

Comparison to the J1 bars: SOT-for 0.688 (J1 0.76/0.80),
corners-for 0.735 (J1 0.65/0.64), shots-for 0.808 — the attacking
traits are as reliable here as in J1. The exception is yellows:
**r=0.156 (events) / 0.190 (stats)**, far below J1's 0.66/0.51 and
below SA-ProLeague's K-SA figure (r=0.264, whose candidate failed
its dev gate to the base rate). A cards model built on team traits
in this league has almost nothing to learn from — the K-SAFD dev
gate will be a hard test, and a FAIL there is the expected outcome
unless the ratings fit finds what the split-half cannot see. The
reliabilities are single-season (n=18 teams), so confidence
intervals are wide; the yellows verdict is nevertheless decisive in
direction (both feeds agree, and neither is near any plausible bar).

## F3 — Halves constants (frozen-constant question)

Measured on 2025/2026 regular played only (n=304; yellows n=301,
excluding 3 matches with 0 total yellows). Per-match 1H share
(FH total / FT total), with the SA variance decomposition (observed
SD vs binomial noise floor).

| Market | 1H share | Obs SD | Noise SD | True SD | Verdict |
|---|---:|---:|---:|---:|---|
| SOT | 0.4540 | 0.1770 | 0.1889 | 0.0 | frozen constant |
| Corners | 0.4678 | 0.1788 | 0.1785 | 0.0105 | frozen constant |
| Total shots | 0.4557 | 0.1033 | 0.1057 | 0.0 | frozen constant |
| Event yellows | 0.4010 | 0.2588 | 0.2621 | 0.0 | frozen constant |

True SD ≈ 0 for every market: per-match 1H share variance is
binomial noise around the league constant, exactly as in J1 and
SA-ProLeague. The halves book stays closed — FT + 1H/2H presentation
via these frozen constants only, no per-team or per-match shares.

**Goals: NO constant.** The goals dev season (2024/2025) has no
events and therefore no HT goals; a 1H share cannot be measured
without reading the goals virgin (2025/2026). G-SAFD presents FT
only. (For reference only, the count-market constants above sit in
the usual 0.40–0.47 band.)

## F4 — Movers / churn

6 teams change at each season boundary (6 in, 6 out; 12 ever-present
2024/25→2025/26). With only three seasons in the corpus and no
tier-3 or Pro-League data inside it, no mover transition effect is
estimable: X2 is dropped (FEATURES.md). The 6 newcomers per season
are exactly the thin-data population the sanctioned SHRINK arm
addresses in G-SAFD (and the within-season warm-up absorbs for the
count markets: a newcomer's first ~10 matches carry NaN trailing
features by the min-6/min-8 rules).

## F5 — Territory link (corners)

Per-match (team-match level, n=608) in 2025/2026: touches_opp_box
vs corners **r=0.537** (J1: 0.471); possession vs corners r=0.470
(J1: 0.286); big chances vs corners r=0.210. Shots vs SOT r=0.697.
The box-touch signal is, if anything, stronger here than in J1 —
X7 is adopted (FEATURES.md) and the C-SAFD X7 arm is a live
contender, not a formality.

## F6 — Referee: not measurable

0 referee names in both dev seasons (2024/2025 and 2025/2026). The
93/94 coverage in the in-progress 2026/2027 cannot rescue X8: a
trait that cannot be estimated on dev data cannot be an arm, and a
live pipeline could not have named referees for any dev or virgin
fixture. X8 dropped (FEATURES.md). Recorded for completeness: the
referee field exists in the payload format; it is simply unpopulated
before 2026/2027.

## F7 — Cards feed (dev-season recheck)

On 2025/2026 regular played (n=304): stats vs event-unified
yellows exact 257, stats-low 47, stats-high 0, mean(stats−events)
−0.289/match. Confirms the Phase A check on all 307 stats matches
(259/48/0, −0.296). The undercount is one-directional and stable;
the frozen target is event-unified yellows (Yellow + YellowRed) in
dev and virgin alike.

## F8 — Era / format notes

- No era break is testable: only one goals dev season and one count
  dev season exist. The design does not assume stationarity beyond
  the dev window; the virgin legs are the judge.
- No climate/altitude hypothesis is tested (no basis in this corpus;
  stadium cities are recorded in the CSV for any later check).
- Thin corpus, stated plainly: goals dev scored n=216, count dev
  scored n=214, count virgin n=94. No window was widened and no gate
  loosened for pool size (config.yaml).

## Primary lines (from the dev over-rate ladders)

| Market | Dev season | Mean | Primary line | Over-rate |
|---|---:|---:|---:|---:|
| Goals OU | 2024/25 | 2.595 | **2.5** | 0.500 |
| SOT | 2025/26 | 8.326 | **8.5** | 0.487 |
| Corners | 2025/26 | 9.171 | **9.5** | 0.434 |
| Total shots | 2025/26 | 23.546 | **23.5** | 0.487 |
| Event yellows | 2025/26 | 4.418 | **4.5** | 0.470 |

Goals OU2.5 sits at exactly 0.500 on dev. Corners 9.5 (0.434) beats
8.5 (0.569) by |0.434−0.5|=0.066 vs 0.069 — a mechanical pick, not
a judgement call; both lines are reported in MODEL_DESIGN.md.
