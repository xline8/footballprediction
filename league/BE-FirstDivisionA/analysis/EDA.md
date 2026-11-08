# Phase 3 — EDA: Belgium First Division A (2021/2022 – 2026/2027)

Computations on `data/be_matches.csv` (n=1,698; 24 team ids ever;
split-half checks are career-pooled per team, ≥20 team-matches, 60
random splits averaged, seed 42 — the CH/DK standard; scripts:
`analysis/eda_compute.py`, numbers: `analysis/eda_numbers.json`).
Virgin-window discipline: design-level aggregates only; no fitting
touched 2025/2026.

## Levels

| Season | Goals | SOT | Corners | Yellows | Shots | xG |
|---|---|---|---|---|---|---|
| 2021/2022 | 2.91 | 9.12 | 10.28 | 4.08 | 25.66 | 3.05 |
| 2022/2023 | 3.06 | 8.96 | 9.97 | 3.81 | 24.33 | 2.84 |
| 2023/2024 | 2.82 | 9.29 | 9.85 | 3.64 | 26.22 | 2.91 |
| 2024/2025 | 2.76 | 9.25 | 10.06 | 3.74 | 26.43 | 3.01 |
| 2025/2026 | 2.67 | 8.90 | 10.16 | 3.75 | 26.33 | 2.92 |
| 2026/2027 (partial) | 3.19 | 9.29 | 10.29 | 3.46 | 28.62 | 3.20 |
| **Pooled (complete)** | **2.85** | **9.11** | **10.10** | **3.81** | **25.81** | **2.94** |

Home/away goals 1.56/1.29 (home edge +0.27); HW/D/AW 42.8/24.9/32.3%;
Over 2.5 = 54.0%, BTTS = 54.3%. Dispersion (var/mean): goals 1.00,
SOT 1.09, corners 1.12, yellows 1.02, shots 1.36.

Context: BE sits mid-pack in the program — goals 2.85 vs top-5 2.84,
DK 2.90, CH 3.11, J1 2.55; SOT 9.11 vs J1 8.08; corners 10.10;
yellows 3.81, below the top-5's 4.04 and well below CH's 4.47.
Levels are league facts; the 1-league-1-model rule stands.

## Findings

**F1 — Levels drift down gently, then the partial season runs hot.**
Goals: 3.06 (2022/2023) → 2.67 in the virgin 2025/2026; yellows step
down at the 16-team format break (3.81 → 3.64) and stay down. The
reserved 2026/2027 partial is at 3.19 goals / 28.6 shots — the
hottest partial in the corpus. Verdict: **SIGNAL** (descriptive).
Time-decayed fitting and trailing baselines as in production; virgin
calibration legs will be read against a cooling season, the opposite
of CH's hot virgin.

**F2 — Core team traits are strongly reliable, yellows moderate.**
Career split-half r: shots-for 0.886, xG-for 0.879, SOT-for 0.866,
goals-for 0.800, goals-against 0.787, corners-for 0.721 — but
**yellows-for 0.404** (better than CH's 0.256, below DK's 0.599).
Verdict: **SIGNAL** for goals/SOT/corners/shots ratings; the cards
candidate has a real but moderate team component here.

**F3 — Half shares are noise, again.** True variance of the
per-match 1H share (observed − binomial floor), complete-splits era
(2023/2024–2025/2026): goals −0.002, SOT −0.0002, corners −0.0004,
shots +0.0002 — zero or below the floor. Yellows show the usual small
positive excess (+0.009) — a level fact about the league constant,
not a team tendency. **Frozen BE constants (complete era, ratio of
sums, n≈937): goals 0.458, SOT 0.452, corners 0.471, total shots
0.456, yellows 0.317.** Verdict: **NOISE — constants adopted.** BE
plays a larger share of its goals before half-time than CH (0.437)
and J1 (0.412), and a notably smaller share of its yellows (0.317 vs
CH 0.357, J1 0.383).

**F4 — Play-off phases: levels differ modestly, inclusion stands.**
Complete seasons, by phase — regular (n=1,332): goals 2.83, SOT
9.07, corners 10.17, yellows 3.87, shots 25.71; championship group
(n=114): 2.75 / 8.94 / **8.87 corners** / 3.93 / 25.37; Europe group
(n=114): 3.04 / 9.58 / 10.04 / **3.08 yellows** / 26.92; relegation
group (n=36): 3.14 / 9.28 / 9.92 / 3.36 / 24.78. The championship
corners dip and the Europe-group yellows dip are the only gaps
beyond ~0.3, on n=114 each; neither justifies discarding 7–23% of
every season or splitting rating windows in a thin league (the full
decision and its reasoning: DATA_UNDERSTANDING §1, frozen in
MODEL_DESIGN). Verdict: **DESCRIPTIVE — phases included, no phase
feature.**

**F5 — No in-corpus tier bridge.** Promoted sides arrive from First
Division B, which this corpus does not contain, so no cross-tier
offset is estimable (contrast J1 F4). The thin-data problem is real:
each season 1–3 sides open with 0–2 in-league matches, exactly the
G-J2 failure mode. The sanctioned response is a pre-registered
shrinkage arm in the goals candidate — nothing else.

**F6 — Set-play xG share is a real team identity here.**
Split-half r = **0.599** (ratio of sums, all seasons) — close to
J1 (0.621), above DK (0.567) and CH (0.369). Verdict:
**SIGNAL-CANDIDATE (arm)** — justifies the X3 decomposition arm in
G-BE, gated against Gate Zero.

**F7 — Shot quality is reliable; on-target rate is too (recorded,
not used).** xG/shot split-half r = **0.435** — above the arm
standard DK applied at 0.348. Verdict: **SIGNAL-CANDIDATE (arm)** —
X4 analogue **ADOPTED** for S-BE (contrast CH, where 0.247 failed).
Shotmap on-target rate r = 0.534 is also reliable in BE, unlike CH;
per the J1 template it still stays out as a standalone covariate —
v5's internal Beta-Binomial ratio component is architectural, and
the RS arm tests its shrinkage. No finishing/conversion covariates.

**F8 — xGOT attacking trait FAILS its reliability check here.**
Era-guarded (2024/2025 onward, where xGOT is populated for ~99.7% of
shots): split-half r = **0.075** — pure noise, the weakest xGOT
reading in the program (J1 0.518; DK/CH dropped at 0.212). Verdict:
**NOISE — X6 analogue DROPPED.** No xGOT arm is built.

**F9 — Referee strictness is a weak-moderate trait.** Referee
yellow-rate split-half r = **0.378** (19 referees with ≥20 matches;
coverage ≈86% overall, 41.2% in 2021/2022 → 93–100% from 2022/2023).
Verdict: **SIGNAL-CANDIDATE (arm only)** — justifies the X8 referee
arm in K-BE (J1: 0.646; DK: 0.561; CH: 0.549 — BE's is the weakest
adopted reading, and the gate, not optimism, decides), with the
inherited operational caveat: warehouse records are post-match
snapshots; fixtures without a published appointment fall back to
the base arm, no imputation. The thin 2021/2022 coverage means
early dev-season X8 values are often the shrunk league mean.

**F10 — Territorial pressure: box touches are elite here too.**
Opp-box-touches-for split-half r = **0.916**, against r = **0.824**.
Possession-for r = 0.933, big-chances-for r = 0.841 — the production
Gate Zero covariates (X9) are themselves strong in BE. Verdict:
**SIGNAL-CANDIDATE** — X7 box-touch multiplier arm vs a genuinely
strong Gate Zero, as in J1/DK/CH (where β fitted to 0 in all three;
the gate, not optimism, decides). Coverage 70–81% before 2024/2025,
100% from 2024/2025 — the min-8 rule absorbs the early gaps.

**F11 — Star absence: not re-tested.** The question is CLOSED by
V10 (top-5) and its J1 replication; no new reliability evidence
exists in this corpus and none was sought. Lineup/absence features
remain forbidden.

**F12 — FotMob xG runs high for BE in the recent era.** Goals/xG
per season: 0.955, 1.080, 0.975, 0.917, 0.916, 0.998 (partial);
pooled ≈ 0.97. Verdict: **SIGNAL** (input-quality fact) — the
production blend has a usable input from the first season, but
fitted ratings will absorb a consistent ~−8% finishing-under-xG
level in 2024/2025–2025/2026 (the opposite sign of CH's +4%).

**F13 — Feasibility.** Every target (goals, SOT, corners, yellows,
total shots) exists for 1,696 of 1,698 matches (absent for the two
score-only matches, DATA_UNDERSTANDING §2) **including every match
of the virgin season 2025/2026** — all five candidates are
buildable: G-BE, S-BE, C-BE, K-BE, T-BE. Windows: dev =
2021/2022–2024/2025 (n=1,286; scored walk-forward seasons
2022/2023–2024/2025, n=956 for goals, n=955 for the count markets —
one scored-season match is score-only), virgin = 2025/2026 (n=313,
complete), confirmatory 2026/2027 reserved un-read.
