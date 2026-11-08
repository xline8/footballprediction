# Phase 3 — EDA: Germany 2. Bundesliga (2021/2022 – 2026/2027)

Computations on `data/de2_matches.csv` (n=1,629; 33 team ids ever;
split-half checks are career-pooled per team, ≥20 team-matches, 60
random splits averaged, seed 42 — the BE/CH/DK standard; scripts:
`analysis/eda_compute.py` → `eda_numbers.json`,
`analysis/movers.py` → `movers.json`).
Virgin-window discipline: design-level aggregates only; no fitting
touched 2025/2026.

## Levels

| Season | Goals | SOT | Corners | Yellows | Shots | xG |
|---|---|---|---|---|---|---|
| 2021/2022 | 2.92 | 9.30 | 10.04 | 3.96 | 27.74 | 2.80 |
| 2022/2023 | 2.94 | 9.17 | 9.89 | 4.24 | 27.04 | 2.79 |
| 2023/2024 | 3.10 | 9.55 | 10.48 | 4.02 | 27.61 | 2.98 |
| 2024/2025 | 3.02 | 9.21 | 10.38 | 4.65 | 27.06 | 2.97 |
| 2025/2026 | 2.93 | 9.06 | 10.04 | 4.46 | 26.83 | 3.06 |
| 2026/2027 (partial) | 2.99 | 10.23 | 11.01 | 4.00 | 30.34 | 3.20 |
| **Pooled (complete)** | **2.98** | **9.26** | **10.17** | **4.27** | **27.26** | **2.90** |

Home/away goals 1.63/1.35 (home edge +0.285); HW/D/AW 43.5/25.5/31.0%;
Over 2.5 = 59.1%, BTTS = 58.6%. Dispersion (var/mean): goals 0.97,
SOT 1.10, corners 1.12, yellows 0.94, shots 1.17.

Context: DE-2 is a high-scoring second tier — goals 2.98 sits above
BE (2.85) and the top-5 pooled level (2.84), close to DK (2.90);
only CH (3.11) and NO (3.12) run hotter among conveyor leagues.
SOT 9.26, corners 10.17, shots 27.26 are all mid-to-high; yellows
4.27 (stats feed) sit above BE's 3.81, below CH's 4.47. Team trait
spreads are wide, as the yo-yo traffic suggests: per-season team
GF means span 0.68–2.29 with SD 0.34–0.39. Levels are league facts;
the 1-league-1-model rule stands.

## Findings

**F1 — Levels are stable; yellows step up late.** Goals hold
2.92–3.10 across all five complete seasons with no trend; SOT,
corners and shots are similarly flat. Yellows step up in the last
two complete seasons (4.02 → 4.65 → 4.46). The reserved 2026/2027
partial runs hot on volume (30.3 shots, 10.2 SOT) at a normal goals
level. Verdict: **SIGNAL** (descriptive). Time-decayed fitting and
trailing baselines as in production.

**F2 — Core team traits are reliable; defence and yellows split.**
Career split-half r: shots-for 0.788, xG-for 0.787, SOT-for 0.739,
goals-for 0.707, corners-for 0.644, **yellows-for 0.558** (strong
for a cards trait — DK 0.599 is the only higher conveyor reading),
but **goals-against only 0.438** — the weakest defensive trait
among the European conveyor leagues, consistent with chaotic
yo-yo-club seasons (Schalke 04's 2023/2024: GF max one year, leaky
the next). Verdict: **SIGNAL** for goals/SOT/corners/shots ratings;
the cards candidate has a genuinely strong team component here;
defensive ratings carry more noise, which the gates will price.

**F3 — Half shares are noise, again.** True variance of the
per-match 1H share (observed − binomial floor), complete-splits era
(2023/2024–2025/2026): goals −0.004, SOT −0.001, corners −0.001,
shots +0.001 — zero or below the floor. Yellows show the usual small
positive excess (+0.005) — a level fact about the league constant,
not a team tendency. **Frozen DE-2 constants (complete era, ratio
of sums, n≈918): goals 0.450, SOT 0.443, corners 0.454, total
shots 0.447, yellows 0.346.** Verdict: **NOISE — constants
adopted.** DE-2's yellows share (0.346) sits between BE (0.317)
and CH (0.357); its goals share (0.450) is close to BE (0.458).

**F4 — Format: nothing to decide.** No split, no play-offs in the
corpus, no phase question (DATA_UNDERSTANDING §1). Every match is
an ordinary row in every window. The relegation play-off is absent
from the warehouse pull, so no cross-tier one-off tie contaminates
any window.

**F5 — Movers: heavy churn, and the two directions differ.**
4–5 entrants per season (19 entrant-seasons over four transitions).
Direction (neighbour membership, `movers.py`): 2 per season arrive
from the Bundesliga, 2–3 from 3. Liga. First-season performance vs
the league mean, pooled over the dev-era transitions (into
2022/2023–2024/2025):

| Direction | Clubs | GF | GA | League GF | ΔGF | ΔGA |
|---|---|---|---|---|---|---|
| Up (from 3. Liga) | 9 | 1.150 | 1.654 | 1.510 | **−0.360** | **+0.143** |
| Down (from Bundesliga) | 6 | 1.608 | 1.588 | 1.510 | +0.097 | +0.078 |

Promoted sides are clearly weaker — above all in attack (−0.36
GF/match, the same sign and a similar size to J.League's J2→J1
step). Relegated Bundesliga sides are NOT the dominant force one
might assume: they score slightly more (+0.10) but concede more
too (+0.08) — roughly league-average overall, on a small n
(6 clubs). Verdict: **SIGNAL for the up-step; weak/descriptive for
the down-step.** This justifies the direction-specific X2 arm
(offsets estimated inside each fit from transitions completed
before the target season — never hard-coded from this table) AND
the generic SHRINK thin-data arm; the gate decides between them.

**F6 — Set-play xG share is a real team identity here.**
Split-half r = **0.558** (ratio of sums, all seasons) — close to
BE (0.599) and J1 (0.621). Verdict: **SIGNAL-CANDIDATE (arm)** —
justifies the X3 decomposition arm in G-DE2, gated against
Gate Zero.

**F7 — Shot quality is reliable; on-target rate is weak.**
xG/shot split-half r = **0.529** — the strongest xG/shot reading
in the program (BE 0.435, J1 0.437). Verdict:
**SIGNAL-CANDIDATE (arm)** — X4 analogue **ADOPTED** for S-DE2.
Shotmap on-target rate r = 0.299 is weak; per the J1 template it
stays out as a standalone covariate regardless — v5's internal
Beta-Binomial ratio component is architectural, and the RS arm
tests its shrinkage. No finishing/conversion covariates.

**F8 — xGOT attacking trait FAILS its reliability check here.**
Era-guarded (2024/2025 onward, where xGOT is populated for ~99.7%
of shots): split-half r = **0.182** — noise (J1 0.518 adopted;
DK dropped at 0.212). Verdict: **NOISE — X6 analogue DROPPED.**
No xGOT arm is built.

**F9 — Referee strictness is a moderate trait.** Referee
yellow-rate split-half r = **0.470** (38 referees with ≥20
matches; coverage 46.4% in 2021/2022 → 88–100% from 2022/2023).
Verdict: **SIGNAL-CANDIDATE (arm only)** — justifies the X8
referee arm in K-DE2 (J1: 0.646; DK: 0.561; CH: 0.549; BE: 0.378),
with the inherited operational caveat: warehouse records are
post-match snapshots; fixtures without a published appointment
fall back to the base arm, no imputation. The thin 2021/2022
coverage means early dev-season X8 values are often the shrunk
league mean. Combined with F2's strong yellows trait (0.558),
DE-2 is one of the program's more promising cards leagues on
paper — the gate, not optimism, decides.

**F10 — Territorial pressure: box touches are strong here too.**
Opp-box-touches-for split-half r = **0.842**, against r =
**0.619**. Possession-for r = 0.906, big-chances-for r = 0.772 —
the production Gate Zero covariates (X9) are themselves strong
in DE-2. Verdict: **SIGNAL-CANDIDATE** — X7 box-touch multiplier
arm vs a genuinely strong Gate Zero, as in J1/BE/DK/CH (where β
fitted to 0 in all four; the gate, not optimism, decides).
Coverage 61–80% before 2024/2025, 100% from 2024/2025 — the
min-8 rule absorbs the early gaps.

**F11 — Star absence: not re-tested.** The question is CLOSED by
V10 (top-5) and its J1 replication; no new reliability evidence
exists in this corpus and none was sought. Lineup/absence
features remain forbidden.

**F12 — FotMob xG runs low for DE-2 in the dev era.** Goals/xG
per season: 1.042, 1.057, 1.040, 1.018, 0.960 (virgin), 0.935
(partial); pooled ≈ 1.03. Verdict: **SIGNAL** (input-quality
fact) — the production blend has a usable input from the first
season; fitted ratings absorb the dev era's ~+4% finishing-over-xG
level. The virgin season flips sign (0.960) — a calibration
headwind the virgin leg will price honestly.

**F13 — Feasibility.** Every target (goals, SOT, corners, yellows,
total shots) exists for all 1,629 matches **including every match
of the virgin season 2025/2026** — all five candidates are
buildable: G-DE2, S-DE2, C-DE2, K-DE2, T-DE2. Windows: dev =
2021/2022–2024/2025 (n=1,224; scored walk-forward seasons
2022/2023–2024/2025, n=918), virgin = 2025/2026 (n=306,
complete), confirmatory 2026/2027 reserved un-read.
