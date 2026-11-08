# Phase 3 — EDA: Brazil Série A (2021 – 2026 partial)

Computations on `data/br_matches.csv` (n=2,239; 30 teams ever;
split-half checks are career-pooled per team, ≥24 matches/team,
60 random splits averaged — the J1/DK standard). Virgin-window
discipline: design-level aggregates only; no fitting touched 2025.

## Levels

| Season | Goals | SOT | Corners | Unified yellows | Reds | Shots | xG* |
|---|---|---|---|---|---|---|---|
| 2021 | 2.22 | 8.27 | 10.21 | 4.50 | 0.13 | 25.42 | 2.35 |
| 2022 | 2.37 | 8.77 | 11.01 | 4.90 | 0.18 | 27.15 | 2.50 |
| 2023 | 2.49 | 9.11 | 10.57 | 5.18 | 0.28 | 27.01 | 2.53 |
| 2024 | 2.44 | 9.13 | 10.16 | 5.06 | 0.34 | 26.84 | 2.43 |
| 2025 | 2.52 | 8.80 | 9.93 | 4.79 | 0.26 | 26.12 | 2.54 |
| 2026 (partial) | 2.67 | 9.21 | 10.57 | 4.53 | 0.25 | 28.14 | 2.71 |
| **Pooled** | **2.45** | **8.87** | **10.42** | **4.87** | **0.25** | **26.68** | — |

*xG levels for 2021/2022 are computed over the ~7–10% rich-feed
subset only and are not league levels; 2023+ xG is a league level.

Home/away goals 1.42/1.03 (home edge +0.39); HW/D/AW
47.2/27.2/25.6%; Over 2.5 = 45.3%, BTTS = 50.1%. Dispersion
(var/mean): goals 0.94 (mildly under-dispersed), SOT 1.06,
corners 1.15, unified yellows 1.65 (heavily over-dispersed — the
NB in the cards reference earns its place), shots 1.31.

Context: BR is a **low-goals, high-cards** league. Goals 2.45 —
below J1 (2.55) and well below DK (2.90) and the top-5 (2.84).
SOT 8.87 sits between J1 (8.08) and DK (9.22); corners 10.42 above
both (J1 9.47, DK 9.98); unified yellows 4.87 are the highest in
the program so far (top-5 4.04, DK 3.51, J1 2.34), and home
advantage (+0.39 goals, 47.2% home wins) is the strongest measured
in the conveyor. Levels are league facts; the 1-league-1-model
rule stands.

## Findings

**F1 — Levels drift modestly; the cards "drift" was a feed break.**
Goals creep up across the window (2.22 → 2.52, 2026 partial 2.67);
corners ease down from the 2022 peak. The apparent yellows jump
(2.9 → 5.2) is the stats-feed undercount of 2021–2022, resolved by
the unified source (4.50 → 5.18 → 4.79 — a real, mild hump, not a
cliff). Verdict: **SIGNAL** (descriptive). Per-league, time-decayed
fitting as in production.

**F2 — Core team traits are strongly reliable.** Career split-half
r: SOT-for 0.749, goals-for 0.736, xG-for 0.708, shots-for 0.697,
goals-against 0.659, corners-for 0.597, yellows-for 0.708 (the
last measured on the era-mixed stats feed in the team table; the
unified target's own trait is what the K harness's naive baseline
will exercise). Verdict: **SIGNAL** — a ratings architecture has
real signal in every market.

**F3 — Half shares are noise, again.** True variance of the
per-match 1H share (observed − binomial floor), complete-splits
era 2023–2025: goals −0.006 (events, all-era n=2,067 with goals),
SOT +0.0004, corners +0.0006, shots +0.0003, yellows +0.0022 —
zero or below the floor everywhere. Team 1H goal-share split-half
r = **−0.02**. **Frozen BR constants (complete-splits era
2023–2025, ratio of sums): goals 0.455, SOT 0.462, corners 0.474,
total shots 0.463, yellows 0.366.** Verdict: **NOISE — constants
adopted.** BR plays a touch more of its corner game before
half-time than J1 (0.474 vs 0.447) and far more of its goals than
J1 (0.455 vs 0.412); yellows 0.366 vs DK's strikingly low 0.319.

**F4 — The tier bridge exists and is real (X2 analogue).**
Série B is in the warehouse (id 8814), so promoted clubs' step up
is directly measurable. Promoted sides (4/season) in their first
Série A season vs their own Série B season before: goals-for
1.34/1.32/1.27/1.41 (B) → 1.02/1.24/1.04/1.12 (A); goals-against
0.83/0.76/0.92/0.89 (B) → 1.34/1.26/1.51/1.34 (A). Against the
Série A league mean (~1.21–1.26 per team-match) the movers land
~0.1–0.2 goals short in attack and concede ~0.1–0.3 extra. The
jump is mostly **defensive** (GA +0.45…+0.59 vs own B level).
Verdict: **SIGNAL** — justifies the X2 mover-offset arm in G-BR,
estimated inside the dev fit per the J1 leakage guard; the same
thin-data exposure also makes the sanctioned SHRINK prior arm
relevant (4 new sides open every season with 0 in-league matches).

**F5 — Set-play xG share is a real team identity, weaker than J1.**
Split-half r = **0.473** (ratio of sums; measurable only where the
xG feed exists — effectively the 2023+ era plus the sparse subset).
Verdict: **SIGNAL-CANDIDATE** — justifies the X3 arm in G-BR
(J1: 0.621, DK: 0.567), with the min-8 rule leaving the arm
inactive until a team's window fills with xG-covered matches.

**F6 — Shot quality is genuinely real here; outcomes are not.**
xG/shot split-half r = **0.571** — the strongest X4 reading in the
program (J1 0.437, DK 0.348). On-target rate r = 0.264 (weak;
still far below shot volume 0.697). Finishing (goals − xG)
r = 0.110 → **NOISE**. Design consequence: S-BR keys on volume +
the X4 quality arm; the RS arm still tests v5's ratio shrinkage;
no finishing/conversion/on-target covariates.

**F7 — xGOT: the era guard lands inside the virgin season — DROP.**
xGOT population reaches ~100% of shots only in 2025 (32–37% in
2021–2023, 67% in 2024). Era-guarded (2025+) split-half
r = **0.348** (24 teams ≥20 era matches — and the "era" is the
virgin season plus the reserved 2026 partial). An X6 arm could
not be exercised in dev at all: by construction it would first
activate *during* the virgin read, untested. The unguarded
all-era number (r = 0.816) is a population-rule artefact, exactly
the trap J1's F7 warned about. Verdict: **DROPPED** — weak
reliability *and* no dev window. Revisit only under a future
prereg once 2025+ is a dev-era quantity.

**F8 — Referee strictness is weakly real.** Referee yellow-rate
split-half r = **0.353** (24 referees with ≥20 matches). Coverage:
0% in 2021, 92.6% 2022, 96.6% 2023, 97.9% 2024, 90.0% in the
virgin 2025. Verdict: **SIGNAL-CANDIDATE (weak)** — justifies the
X8 arm in K-BR on the DK X4 precedent (adopted at r=0.348, gate
decides), with the standard operational caveat: no published
appointment ⇒ base arm, no imputation. Note K-J1's lesson: the
arm's virgin value depends on virgin referee coverage — BR's
90% is healthy, unlike J1's 0.5% collapse.

**F9 — Territorial pressure is elite.** Opp-box-touches-for
split-half r = **0.803**, against r = **0.789**; possession-for
r = 0.928, big-chances-for r = 0.785 — the production Gate Zero
covariates (X9) are strong in BR too. Coverage caveat: touches
exist for only ~45% of 2021–2023 matches (100% from 2024), so the
min-8 rule governs the X7 arm's early-dev activity. Verdict:
**SIGNAL-CANDIDATE** — X7 arm vs a strong Gate Zero, as in J1/DK
(where β fitted to 0 both times; the gate decides).

**F10 — Star absence: not re-tested.** CLOSED by V10 (top-5) and
its J1 replication; no new reliability evidence sought.
Lineup/absence features remain forbidden.

**F11 — FotMob xG is calibrated for BR in the full-feed era.**
Goals/xG on covered matches: 0.984 (2023), 1.007 (2024), 0.993
(2025). The sparse 2021/2022 covered subsets read 0.76/0.89 on
n=36/28 — a non-random rich-feed subset, recorded as such and
never used. Verdict: **SIGNAL** (input quality) — the blend's xG
input is sound from 2023; before that the blend is goals-only by
coverage, not by calibration failure.

**F12 — Feasibility.** Targets: goals exist for all 2,239; SOT,
corners, total shots (stats feed) for all seasons **including the
virgin 2025**; unified yellows for all but one match. All five
candidates are buildable: G-BR, S-BR, C-BR, K-BR, T-BR. Windows:
dev = 2021–2024 (warm-up 2021, scored 2022–2024, n=1,140),
virgin = **2025 (complete, n=380)** read ONCE per candidate,
2026 partial (n=339) reserved un-read as the confirmatory window.
(Virgin choice, frozen here at design time: the warehouse
contains a *complete* 2025, so it serves as the primary virgin —
the stronger design — and the in-progress 2026 takes the
transitional/confirmatory role DK gave its partial season.)
