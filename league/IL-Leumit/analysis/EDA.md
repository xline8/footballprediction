# Step 3 — EDA: IL-Leumit (goals-only corpus)

Computations: `league/IL-Leumit/analysis/eda.py` → `eda_summary.json`;
charts in `charts/` (`make_charts.py`). Sample: 1,480 matches in the
five complete seasons 2021/2022–2025/2026 + 101 in-progress 2026/2027.
Only goals exist in this corpus (Step 1: stats/shotmap 0%), so the
J1 checklist is replicated for the goals quantities and recorded as
NOT TESTABLE for SOT / corners / cards / total shots / halves /
referee — those markets are not buildable here, by coverage, not by
choice.

## Levels

| Season | n | Goals/match | Home | Away | Home adv | HW/D/AW % | BTTS % | Over 2.5 % | Dispersion |
|---|---|---|---|---|---|---|---|---|---|
| 2021/2022 | 296 | 2.348 | 1.294 | 1.054 | +0.240 | 38.5/35.1/26.4 | 51.7 | 43.2 | 1.084 |
| 2022/2023 | 296 | 2.595 | 1.392 | 1.203 | +0.189 | 43.2/25.0/31.8 | 46.3 | 44.9 | 0.991 |
| 2023/2024 | 296 | 2.791 | 1.466 | 1.324 | +0.142 | 39.5/26.7/33.8 | 54.7 | 50.3 | 1.156 |
| 2024/2025 | 296 | 2.649 | 1.439 | 1.209 | +0.230 | 43.9/22.3/33.8 | 48.3 | 48.3 | 0.958 |
| 2025/2026 | 296 | 2.716 | 1.361 | 1.355 | +0.007 | 35.1/31.4/33.4 | 57.8 | 49.7 | 1.025 |
| 2026/2027* | 101 | 3.069 | 1.535 | 1.535 | +0.000 | 40.6/16.8/42.6 | 53.5 | 60.4 | 1.008 |

*in progress (13 rounds), not comparable to full seasons.

**F1 — Levels drift and home advantage is fading.** Goals rise
2.35 → 2.72 across the complete seasons while home advantage falls
+0.24 → +0.01. Verdict: **SIGNAL** (descriptive). Consequence:
per-league fitting with time decay (production pattern), no borrowed
levels. Reference points: J1 scores 2.55/match; Leumit's complete-season
range 2.35–2.79 brackets it, but its draw rate is higher and more
volatile (22.3–35.1% vs J1 26.8%).

**Phase split (complete seasons):** regular rounds score 2.559/match
(n=1,200), split rounds 2.879/match (n=280) with home adv +0.25 vs
+0.14. Descriptive fact only — no phase feature is adopted (see
FEATURES §3); both phases stay in the fit, as they are real matches
against same-group opponents.

## Findings

**F2 — Goal traits are reliable.** Career split-half (60 random
splits, ≥24 matches/team, 28 teams): goals-for **r = 0.666**,
goals-against **r = 0.766**. Verdict: **SIGNAL** — a scores-only
Dixon-Coles ratings fit has real team signal to capture (compare
J1: GF 0.71 / GA 0.59).

**F3 — Half shares: NOT TESTABLE.** No period splits exist anywhere
in the corpus (0% coverage). No halves constant can be measured, so
there is nothing to freeze: any shipped product is **FT only**.
This is a coverage fact, not a noise verdict.

**F4 — Movers: relegated clubs arrive strong; promoted clubs arrive
roughly average.** Entry seasons 2022/2023–2025/2026, entry-season
performance in Leumit vs that season's league mean mu (per-team-match
goals), keyed by team ID; Ligat ha'Al membership from league_id 127
in the same warehouse; tier-3 (Liga Alef) is not in the warehouse, so
up-movers are entrants whose previous season was in neither league:

| Mover kind | n team-seasons | GF delta vs mu | GA delta vs mu |
|---|---|---|---|
| Down from Ligat ha'Al | 8 | **+0.291** | **−0.239** |
| Up from tier 3 | 8 | −0.080 | +0.109 |

Individual down-movers vary widely (GF delta −0.28…+0.78): the pooled
direction is consistent with a tier gap (a relegated top-tier club is
an above-average second-tier side — the mirror image of J1's F4),
but n=8 with wide spread makes the magnitudes **SIGNAL-CANDIDATE**,
to be tested as a gated arm, not assumed. Up-mover deltas are small
in both directions. Verdict: **SIGNAL-CANDIDATE** — justifies the X2
arm in the design with these frozen magnitudes.

**F5 — Everything else on the J1 checklist is NOT TESTABLE here:**
SOT / corners / cards / total-shots levels and trait reliabilities,
set-play share, xG per shot, xGOT, box touches, referee strictness —
all require stats or shotmap payloads that do not exist for this
league (0/1,581). Recorded as coverage absences, never estimated.
