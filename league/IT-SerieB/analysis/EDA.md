# Step 3 — EDA: IT-SerieB

All numbers computed by `analysis/eda_compute.py` from the built
CSV (raw dump: `analysis/eda_numbers.json`). Complete seasons only
for pooled rates unless stated. J1/ES checklist replicated.
Calibration in this build is defined as **actual − predicted**
throughout (preregs and verdicts state it per candidate).

## Levels per season (per match, both teams; all phases)

| Season | Goals | SOT | Corners | Shots | Yellows (events) | Yellows (stats) | Reds |
|---|---|---|---|---|---|---|---|
| 2021/2022 | 2.485 | 8.326 | 10.128 | 25.933 | 5.169 | 5.005 | 0.251 |
| 2022/2023 | 2.328 | 7.885 | 9.846 | 25.126 | 5.008 | 4.813 | 0.297 |
| 2023/2024 | 2.526 | 8.197 | 9.536 | 25.672 | 5.064 | 4.964 | 0.249 |
| 2024/2025 | 2.460 | 8.077 | 9.000 | 25.640 | 4.907 | 4.840 | 0.252 |
| 2025/2026 (virgin) | 2.546 | 8.418 | 9.497 | 26.103 | 4.362 | 4.274 | 0.241 |
| 2026/2027 (partial, n=110) | 2.609 | 8.473 | 9.573 | 27.645 | 3.964 | 3.873 | 0.173 |

(2024/2025 corners = **9.000** — the lowest corner season of the
corpus.) F1 — Serie B is a **mid-scoring,
card-heavy** league: goals 2.33–2.53 in dev seasons, event yellows
≈ 4.9–5.2 per match (ES 4.7–5.0), corners drifting down
10.13 → 9.00 across the dev era, SOT ≈ 7.9–8.3, shots ≈ 25.1–25.9.
The virgin ran **hot on goals/SOT/shots** (2.546 / 8.418 / 26.103;
OU2.5 over-rate 48.2% vs dev-eval 45.0%) but **cold on cards**
(4.362, over-4.5 rate well below dev's 58.4%) and mid on corners —
the gates' calibration legs meet that mixed regime as it is. The
partial 2026/2027 runs hotter still on shots (27.6) and colder on
cards (3.96); it stays a reserved confirmatory window.

## Home advantage & base rates (complete seasons pooled, n=1,949)

Home goals 1.371 vs away 1.098 per match; pooled home/away ratio
**1.249** (Serie C 1.241, ES 1.337 implied). Home-win rate
~37–45% by season (36.9% in 2023/2024); dev-eval OU2.5 over-rate
45.0%.

## F2 — Team trait reliability (career-pooled split-half, teams ≥10 matches)

| Trait | r | n teams | Verdict |
|---|---|---|---|
| possession | 0.788 | 46 | SIGNAL |
| SOT-against | 0.631 | 46 | SIGNAL |
| SOT-for | 0.555 | 46 | SIGNAL |
| goals-for | 0.531 | 46 | SIGNAL |
| shots-against | 0.528 | 46 | SIGNAL |
| yellows-for (events) | 0.475 | 46 | SIGNAL (moderate) |
| goals-against | 0.457 | 46 | SIGNAL (moderate) |
| yellows-for (stats) | 0.431 | 44 | SIGNAL (moderate) |
| corners-against | 0.403 | 46 | SIGNAL (moderate) |
| shots-for | 0.367 | 46 | moderate |
| big-chance-for | 0.352 | 44 | moderate |
| box touches-for | 0.320 | 16 | weak, small n |
| corners-for | 0.296 | 46 | weak-moderate |
| box touches-against | −0.129 | 16 | NOISE |

Per-season goals split-half pairs are volatile (GF r from 0.11 to
0.58 across seasons) — pooled ratings with time decay are the
right structure, and thin-data shrinkage is a legitimate arm.
Box-touches reliability is measured on only 16 teams (the trait
needs valid values in both career halves; touches coverage is
74–77% in the first two seasons) and its against side is noise —
X7 fails the program's reliability standard here (ES adopted it
at 0.707/0.659).

## F3 — Half shares: frozen-constant question

Measured on the complete-splits **complete seasons**
2023/2024–2025/2026 (n=1,169; ratio of sums):

| Market | 1H share (frozen) |
|---|---|
| goals (events HT) | **0.4501** |
| SOT | **0.4598** |
| corners | **0.4734** |
| total shots | **0.4650** |
| yellows (events) | **0.3733** |

Per-match share variance is ≈ sampling noise around these
constants (true-SD estimates ≤0.08 under the binomial
approximation, in line with every other league in the program).
**Frozen constants only**, presentation only.

## F4 — Mover tier offsets (the Serie B churn question)

Entry-season performance of clubs whose previous season was in
the adjacent tier (warehouse team lists for Serie A id 55 /
Serie C id 147, accent-normalised name matching + the Reggiana
spelling alias; pooled over the four complete entry seasons
2022/2023–2025/2026; exactly 3 + 4 movers every season):

| Entry source | team-matches | GF/match | GA/match | GD/match | ΔGF vs mu 1.232 | ΔGA vs mu |
|---|---|---|---|---|---|---|
| from Serie A | 472 | 1.377 | 1.089 | **+0.288** | **+0.145** | **−0.143** |
| from Serie C | 623 | 1.162 | 1.350 | **−0.188** | **−0.070** | **+0.118** |

**SIGNAL, near-symmetric**: a relegated Serie A club enters about
a quarter-goal per match better than the average Serie B club,
split evenly between attack (+0.145) and defence (−0.143). A
promoted Serie C club's step is about two-thirds as large in the
other direction and is defence-led (GA +0.118, GF −0.070). These
magnitudes freeze the X2 arm's offsets in PREREG_G_ITB (ENGCH/ES
pattern: descriptive magnitudes, applied only at prediction time
in the mover's entry season). Note the first-pass classification
missed Reggiana 2023/2024 ( Serie C index spells it `Reggiana`,
Serie B `AC Reggiana 1919`); the alias fix above is included in
these pooled numbers — without it the Serie C pool understates
the step (623 vs 585 team-matches).

## F5 — Set-play xG share reliability: **NOT MEASURABLE** — the xG
   splits exist in 13 of 1,559 dev matches; the era starts inside
   the virgin. X3 dropped on availability (FEATURES). No number
   is quoted.
## F6 — xG per shot reliability: **NOT MEASURABLE** — shotmap in
   12 of 1,559 dev matches. X4 dropped on availability.
## F7 — xGOT per shot: **NOT MEASURABLE** in the dev window (same
   era break). X6 dropped on availability.
## F8 — Referee yellow rate reliability: r = **0.061** on dev
   seasons (54 referees with ≥10 matches) — **NOISE** by the
   program's standard (J1 0.65, DK 0.56; ES dropped X8 at 0.180).
   This is the weakest referee signal measured in the program.
   X8 is dropped in FEATURES; K-ITB runs Gate Zero only.
## F11 — xG calibration: not applicable to any arm (no xG arm).
   Descriptively, in the only era where xG exists, goals/xG is
   0.986 (2025/2026) and 0.966 (2026/2027 partial).

## Feasibility summary

Goals exist in 100% of matches; SOT / corners / total shots exist
in the stats feed in 100% of matches in every season; the unified
(event) yellows target exists in 100% of matches; the virgin
season contains all five targets → **five candidates**
(MODEL_DESIGN). The era break removes only the xG-consuming
*arms*, not any candidate — the exact ES-LaLiga2 shape, and the
opposite of IT-SerieC, where the stats feed itself was absent
from every complete season.
