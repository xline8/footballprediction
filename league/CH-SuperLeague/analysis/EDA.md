# Phase 3 — EDA: Switzerland Super League (2021/2022 – 2026/2027)

Computations on `data/ch_matches.csv` (n=1,122; 17 teams ever;
split-half checks are career-pooled per team, ≥20 team-matches, 60
random splits averaged — with only 14 eligible teams, |r| under ~0.3
has a wide interval and is treated as weak at best, the same standard
as J1/DK). Virgin-window discipline: design-level aggregates only;
no fitting touched 2025/2026.

## Levels

| Season | Goals | SOT | Corners | Yellows | Shots | xG |
|---|---|---|---|---|---|---|
| 2021/2022 | 3.25 | 9.64 | 9.93 | 4.66 | 28.43 | 3.13 |
| 2022/2023 | 2.98 | 9.03 | 10.47 | 4.82 | 26.99 | 2.85 |
| 2023/2024 | 2.83 | 9.18 | 10.07 | 4.27 | 26.92 | 2.65 |
| 2024/2025 | 2.98 | 9.61 | 10.32 | 4.23 | 27.53 | 2.91 |
| 2025/2026 | 3.29 | 9.87 | 10.17 | 4.36 | 28.51 | 3.21 |
| 2026/2027 (partial) | 3.76 | 10.22 | 10.72 | 4.40 | 30.69 | 3.51 |
| **Pooled** | **3.11** | **9.47** | **10.20** | **4.47** | **27.72** | **2.99** |

Home/away goals 1.72/1.39 (home edge +0.33, the largest in the
program so far); HW/D/AW 43.8/26.5/29.8%; Over 2.5 = 59.9%,
BTTS = 63.0%. Dispersion (var/mean): goals 0.95, SOT 1.10, corners
1.07, yellows 0.94, shots 1.33.

Context: CH is the highest-scoring league measured in the program —
goals 3.11 vs top-5 2.84, DK 2.90, J1 2.55; SOT 9.47 vs J1 8.08;
corners 10.20; yellows 4.47, above even the top-5's 4.04. Levels are
league facts; the 1-league-1-model rule stands.

## Findings

**F1 — Levels swing by season, and the virgin season ran hot.**
Goals: 3.25 → 2.83 (2023/2024, the first new-format season) → 3.29
in the virgin 2025/2026; the reserved 2026/2027 partial is at 3.76.
Yellows step down at the format break (4.82 → 4.27) and stay down.
Verdict: **SIGNAL** (descriptive). Time-decayed fitting and trailing
baselines as in production; virgin calibration legs will be read
against a hot season, exactly as G-J1's was.

**F2 — Core team traits are strongly reliable — except yellows.**
Career split-half r: shots-for 0.937, xG-for 0.890, SOT-for 0.875,
goals-for 0.806, goals-against 0.614, corners-for 0.795 — but
**yellows-for only 0.256**. Verdict: **SIGNAL** for goals/SOT/
corners/shots ratings; the cards candidate's team component is
**weak** here (DK measured 0.599) — K-CH leans correspondingly more
on its referee arm and its baselines, and the gate decides.

**F3 — Half shares are noise, again.** True variance of the
per-match 1H share (observed − binomial floor), complete-splits era
(2023/2024–2025/2026): goals −0.003, SOT −0.002, corners −0.001,
shots −0.001 — zero or below the floor. Yellows show the usual small
positive excess (+0.007) — a level fact about the league constant,
not a team tendency. **Frozen CH constants (complete era,
ratio of sums, n≈682): goals 0.437, SOT 0.453, corners 0.471,
total shots 0.456, yellows 0.357.** Verdict: **NOISE — constants
adopted.** CH plays a slightly smaller share of its game before
half-time than DK (0.463/0.488) and a larger share than J1 (0.412).

**F4 — No in-corpus tier bridge.** Promoted sides arrive from the
Challenge League, which this corpus does not contain, so no
cross-tier offset is estimable (contrast J1 F4). The thin-data
problem is real: each season 1–2 sides open with 0–2 in-league
matches, exactly the G-J2 failure mode. The sanctioned response is
a pre-registered shrinkage arm in the goals candidate — nothing else.

**F5 — Set-play xG share is a weak-moderate team identity.**
Split-half r = **0.369** (ratio of sums, all seasons). Weaker than
J1 (0.621) and DK (0.567) but above the noise floor. Verdict:
**SIGNAL-CANDIDATE (arm only)** — justifies the X3 decomposition arm
in G-CH, gated against Gate Zero; nobody should expect it to win.

**F6 — Shot quality is weak; on-target rate is noise.** xG/shot
split-half r = **0.247**; on-target rate r = **−0.121** (pure noise).
Verdict: xG/shot **fails the arm standard** DK applied at 0.348 —
**X4 analogue DROPPED**; S-CH runs Gate Zero + RS only. No finishing
/ conversion / standalone on-target-rate covariates.

**F7 — xGOT attacking trait FAILS its reliability check here.**
Era-guarded (2024/2025 onward, where xGOT is populated for ~100% of
shots): split-half r = **0.212** — the identical number DK measured
and dropped on. Verdict: **NOISE/weak — X6 analogue DROPPED.** No
xGOT arm is built.

**F8 — Referee strictness is a real trait.** Referee yellow-rate
split-half r = **0.549** (15 referees with ≥20 matches; coverage
89.8% overall, ~99–100% from 2023/2024). Verdict:
**SIGNAL-CANDIDATE** — justifies the X8 referee arm in K-CH (J1:
0.646; DK: 0.561), with the inherited operational caveat: warehouse
records are post-match snapshots; fixtures without a published
appointment fall back to the base arm, no imputation. The thin
2021/2022 referee coverage (47.2%) means early dev-season X8 values
are often the shrunk league mean — the arm is effectively tested on
2022/2023 onward.

**F9 — Territorial pressure: box touches are elite here too.**
Opp-box-touches-for split-half r = **0.933**, against r = **0.835**.
Possession-for r = 0.920, big-chances-for r = 0.811 — the production
Gate Zero covariates (X9) are themselves strong in CH. Verdict:
**SIGNAL-CANDIDATE** — X7 box-touch multiplier arm vs a genuinely
strong Gate Zero, as in J1/DK (where β fitted to 0 both times; the
gate, not optimism, decides).

**F10 — Star absence: not re-tested.** The question is CLOSED by
V10 (top-5) and its J1 replication; no new reliability evidence
exists in this corpus and none was sought. Lineup/absence features
remain forbidden.

**F11 — FotMob xG runs low for CH.** Goals/xG pooled ≈ 1.04; per
season 1.022–1.075 (every season ≥ 1.02). Verdict: **SIGNAL**
(input-quality fact) — the production blend has a usable input from
the first season (no goals-only era, unlike J1 2021), but fitted
ratings will absorb a consistent ~+4% finishing-over-xG level.

**F12 — Feasibility.** Every target (goals, SOT, corners, yellows,
total shots) exists for all 1,122 matches **including the virgin
season 2025/2026** — all five candidates are buildable: G-CH, S-CH,
C-CH, K-CH, T-CH. Windows: dev = 2021/2022–2024/2025 (n=816; scored
walk-forward seasons 2022/2023–2024/2025, n=636), virgin = 2025/2026
(n=228, complete), confirmatory 2026/2027 reserved un-read.
