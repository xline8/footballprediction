# Phase 3 — EDA: Denmark Superligaen (2021/2022 – 2026/2027)

Computations on `data/dk_matches.csv` (n=1,049; 16 teams ever; split-half
checks are career-pooled per team, ≥24 matches/team, 60 random splits
averaged — with only 12–16 teams, |r| under ~0.3 has a wide interval and
is treated as weak at best, the same standard as J1). Virgin-window
discipline: design-level aggregates only; no fitting touched 2025/2026.

## Levels

| Season | Goals | SOT | Corners | Yellows | Shots | xG |
|---|---|---|---|---|---|---|
| 2021/2022 | 2.65 | 9.15 | 9.97 | 3.69 | 26.15 | 2.92 |
| 2022/2023 | 2.74 | 9.21 | 10.02 | 3.67 | 25.64 | 2.79 |
| 2023/2024 | 2.82 | 8.94 | 10.06 | 3.61 | 24.67 | 2.81 |
| 2024/2025 | 3.14 | 9.23 | 10.10 | 3.32 | 26.25 | 2.92 |
| 2025/2026 | 3.10 | 9.70 | 9.75 | 3.24 | 26.67 | 3.07 |
| 2026/2027 (partial) | 3.06 | 9.00 | 9.93 | 3.54 | 27.70 | 3.05 |
| **Pooled** | **2.90** | **9.22** | **9.98** | **3.51** | **26.02** | **2.91** |

Home/away goals 1.54/1.36 (home edge +0.18); HW/D/AW 41.7/27.1/31.3%;
Over 2.5 = 55.2%, BTTS = 59.1%. Dispersion (var/mean): goals 0.93
(mildly *under*-dispersed), SOT 1.08, corners 1.17, yellows 1.02,
shots 1.27.

Context: DK scores like the top-5 (2.90 vs 2.84) and well above J1
(2.55); SOT 9.22 vs J1 8.08; corners 9.98 vs J1 9.47; yellows 3.51 —
between J1's 2.34 and the top-5's 4.04. Levels are league facts; the
1-league-1-model rule stands.

## Findings

**F1 — Levels drift by season.** Goals step up in 2024/2025 (2.82 →
3.14) and stay up in 2025/2026 (3.10); yellows step down steadily
(3.69 → 3.24). Verdict: **SIGNAL** (descriptive). Per-league,
time-decayed fitting as in production; trailing baselines will adapt
faster than ratings to level steps — the K-J2 lesson applies here.

**F2 — Core team traits are strongly reliable.** Career split-half r:
shots-for 0.824, xG-for 0.826, SOT-for 0.801, goals-for 0.747,
goals-against 0.719, corners-for 0.605, yellows-for 0.599.
Verdict: **SIGNAL** — a ratings architecture has real signal in every
market. (12–16 teams → intervals are wide, but every core trait is
far above the noise floor.)

**F3 — Half shares are noise, again.** True variance of the per-match
1H share (observed − binomial floor), complete era: goals −0.001
(all-era events), SOT +0.001, corners +0.002, shots −0.001 — zero or
below the floor. Team 1H goal-share split-half r = 0.278 (weak,
contradicted by the variance decomposition, the sharper instrument).
Yellows show a small positive excess (+0.007…+0.011 in complete
seasons) but the same frozen-constant treatment applies — it is a
level fact about the league constant, not a team tendency.
**Frozen DK constants (complete-splits era 2023/2024–2025/2026,
ratio of sums, n=579): goals 0.463, SOT 0.462, corners 0.488,
total shots 0.470, yellows 0.319.** Verdict: **NOISE — constants
adopted.** Note DK's corners 1H share (0.488) is far above J1's
0.447 and the goals share (0.463) above J1's 0.412: Denmark plays
much more of its game before half-time than Japan does.

**F4 — No in-corpus tier bridge.** Promoted sides arrive from the
1st Division, which this corpus does not contain, so no cross-tier
offset is estimable (contrast J1 F4). What remains is the thin-data
problem itself: 2 new sides per season open with 0–2 in-league
matches, exactly the G-J2 failure mode (extreme lambdas for 1–2-match
teams in season openers). The sanctioned response is a
pre-registered shrinkage arm in the goals candidate — nothing else.

**F5 — Set-play xG share is a stable team identity.** Split-half
r = **0.567** (ratio of sums, stats-feed splits, all seasons).
Verdict: **SIGNAL-CANDIDATE** — justifies the X3 decomposition arm
in G-DK, gated against Gate Zero (J1 F5: 0.621).

**F6 — Shot quality mildly real; outcomes weak.** xG/shot split-half
r = **0.348** (J1: 0.437); on-target rate r = 0.310 (weak — in J1 it
was 0.06, pure noise; here it is weak-positive but still far below
shot volume 0.824); finishing (goals − xG) r = 0.246 → **NOISE**
(weak, wide interval at 16 teams). Design consequence: S-DK keys on
volume + xG/shot (X4 arm); the ratio-shrink arm (RS) still tests
whether v5's ratio component earns its place; no finishing /
conversion / standalone on-target-rate covariates.

**F7 — xGOT attacking trait FAILS its reliability check here.**
Era-guarded (2024/2025 onward, where xGOT is populated for ~100% of
shots): split-half r = **0.212** (13 teams ≥20 era matches).
Verdict: **NOISE/weak — X6 analogue DROPPED** (J1 measured 0.518;
Denmark does not replicate it). No xGOT arm is built.

**F8 — Referee strictness is a real trait.** Referee yellow-rate
split-half r = **0.561** (15 referees with ≥20 matches; coverage
100%). Verdict: **SIGNAL-CANDIDATE** — justifies the X8 referee arm
in K-DK (J1 F8: 0.646), subject to the same pre-match-availability
operational caveat as J1: warehouse records are post-match
snapshots; fixtures without a published appointment fall back to
the base arm, no imputation.

**F9 — Territorial pressure: box touches are elite here too.**
Opp-box-touches-for split-half r = **0.830**, against r = **0.871**
(the against side is the single most stable trait measured in this
EDA). Possession-for r = 0.906 and big-chances-for r = 0.723 — the
production Gate Zero covariates (X9) are themselves strong in DK.
Verdict: **SIGNAL-CANDIDATE** — X7 box-touch multiplier arm vs a
genuinely strong Gate Zero, as in J1 (where β fitted to 0; the gate,
not optimism, decides).

**F10 — Star absence: not re-tested.** The question is CLOSED by
V10 (top-5) and its J1 replication (F10 there); no new reliability
evidence exists in this corpus and none was sought. Lineup/absence
features remain forbidden.

**F11 — FotMob xG is calibrated for DK.** Goals/xG pooled 0.997;
per season 0.908 (2021/2022) then 0.981–1.076. Verdict: **SIGNAL**
(input quality) — the production blend has a sound input here from
the first season (no goals-only era, unlike J1 2021).

**F12 — Feasibility.** Every target (goals, SOT, corners, yellows,
total shots) exists for all 1,049 matches **including the virgin
season 2025/2026** — all five candidates are buildable:
G-DK, S-DK, C-DK, K-DK, T-DK. Windows: dev = 2021/2022–2024/2025
(n=772), virgin = 2025/2026 (n=193, complete), confirmatory
2026/2027 reserved un-read.
