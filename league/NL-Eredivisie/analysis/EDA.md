# Phase 3 — EDA: Netherlands Eredivisie (2021/2022 – 2026/2027)

Computations: `eda.py` (digest in `eda_summary.json` +
`inventory_summary.json`); halves/referee/newcomer checks verified by
the coordinator through independent recomputation (see Verification
note). Sample: 1,638 regular-season matches (306 per full season × 5
+ 108 partial 2026/2027). Standard (same as J1): a trait is a signal
candidate only if it reproduces on disjoint halves of the same
teams' matches (split-half, career-pooled per team ≥24 matches, 60
random splits averaged; ratio traits as **ratios of sums**) or
survives a variance decomposition against its sampling-noise floor
(per-match floor `mean(p(1−p)/n_i)`).

## Levels (regular season)

| Quantity (per match) | Pooled | Season range | J1 (ref) | Top-5 spine (ref) |
|---|---|---|---|---|
| Goals | **3.12** (SD≈1.76) | 2.86 – 3.24 (full seasons) | 2.55 | 2.84 |
| Home goals / away goals | 1.72 / 1.40 | — | 1.38 / 1.18 | — |
| Home win / draw / away win % | 43.5 / 24.4 / 32.1 | — | 41.3 / 26.8 / 31.9 | — |
| BTTS % / Over 2.5 % | 57.4 / 60.0 | — | 50.4 / 47.0 | — |
| Total shots | 27.40 | 26.0 – 28.2 | 24.8 | ~25.6 |
| SOT | 9.81 | 9.2 – 10.4 | 8.08 | — |
| Corners | 10.24 | 9.7 – 10.6 | 9.47 | — |
| Yellow cards | 2.94 | 2.84 – 3.12 | 2.34 | 4.04 |
| Red cards | 0.15 | — | 0.11 | — |
| Team xG (match total) | 2.97 | 2.66 – 3.16 | 2.52 | — |

Dispersion (variance/mean of the match total): goals 0.99
(Poisson-like), SOT 1.14, corners 1.14, yellows 1.12, total shots
1.33. Mild overdispersion in the count markets — the same regime as
production; NB sizes will be large but finite.

Context: the Eredivisie is a **high-event league** — more goals
(3.12 vs 2.84 top-5, 2.55 J1), more shots, more SOT, more corners,
but far fewer cards than the top-5 (2.94 vs 4.04). Any ported level
prior from Europe or Japan is wrong here by construction — the
empirical core of 1-league-1-model. The partial 2026/2027 segment
runs extremely hot (3.89 goals, 72% over 2.5) — an Aug–Nov segment
only, NOT comparable to full seasons, and reserved as confirmatory.

## Findings

**F1 — Levels drift by season.** Goals: 2.86, 3.06, 3.24, 2.99,
3.18 across the five full seasons; shots 26.0 → 28.2; xG tracks
goals. Home edge +0.32 goals pooled. Verdict: **SIGNAL**
(descriptive). Per-league levels with time-decayed fitting, as in
production.

**F2 — Core team traits are exceptionally reliable.** Career
split-half r: shots-for **0.927**, SOT-for **0.924**, xG-for
**0.938**, goals-for **0.909**, corners-for 0.849, big-chance-for
0.912, possession-for 0.944; against-traits 0.71–0.91; yellows-for
0.502 / yellows-against 0.487 (the weakest, still real). These are
materially higher than J1's (goals-for 0.71) — the Eredivisie's
team-strength spread (Ajax/PSV/Feyenoord vs the bottom) is wide and
stable. Verdict: **SIGNAL (strong)** — a ratings architecture has
real signal everywhere. Coordinator's independent recomputation
from the match table: SOT-for r = 0.922, goals-for r = 0.908 —
agrees.

**F3 — Half shares are noise here too; frozen constants it is.**
Measured on the splits era (2023/2024+, n = 1,113 matches with
splits and FT total > 0; goals via event-HT on the same matches,
n = 1,066): true variance of the per-match 1H share (observed minus
per-match binomial floor): goals **−0.0056**, SOT **−0.0018**,
total shots **−0.0006**, corners **+0.0041**, yellows **+0.0123**.
Team-level split-half r of the 1H share: goals −0.19, SOT −0.26,
corners 0.06, shots 0.09, yellows 0.09 — **no team has a half
tendency**. The two small positive match-level excesses (corners,
yellows) come with team r ≈ 0.06–0.09, i.e. match-level
heterogeneity (game state), not a team trait; per the program rule
they do not open per-match half modelling. Verdict: **NOISE** for
modelling; frozen league constants are the only halves mechanism.
**Frozen constants (ratio of sums)**: goals **0.444** (events HT
over all 1,638 matches, 5,110 goals; splits-era cross-check 0.436;
per-season range 0.404–0.478 — era wander, as in the top-5 audit),
SOT **0.446**, corners **0.462**, total shots **0.449**, yellows
**0.333** (stats splits; event-feed cross-check on the same era
0.343).

**F4 — Newcomers (promoted clubs) arrive ≈ half a goal down.**
Teams present in season S but absent in S−1 (3 per season, from the
Eerste Divisie — outside this corpus, so the gap is measured
against the league, J1-F4 style): pooled over the four complete
transitions (2022/2023–2025/2026, 12 team-seasons): GF 1.11/match
vs league team mean ≈ 1.56 → **gap −0.45**; GA 1.82 vs 1.56 →
**gap +0.26** (per-season GA gaps +0.49, +0.38, +0.13, +0.05 — the
defensive gap is shrinking across eras and is the noisier side).
Verdict: **SIGNAL** for the attack side, weaker for defence. A
preregistered newcomer-offset arm for the goals candidate uses
exactly these magnitudes (−0.45 / +0.26), per the template's
G-J2-lesson allowance.

**F5 — Set-play xG share is a stable team identity.** Split-half
r = **0.610** (ratio of sums). Verdict: **SIGNAL-CANDIDATE** —
justifies the X3 decomposition arm in the goals design (as in J1).

**F6 — Shot quality is real; finishing is mildly real here;
on-target rate is real here (unlike J1).** Split-half r: xG per
shot **0.759**, finishing (goals − xG) **0.407**, on-target rate
(SOT/shots) **0.581**. This league differs from J1 (0.437 / 0.153 /
0.06): with ~170 career matches per ever-present team and a wide
quality spread, all three clear the standard. Consequences, stated
carefully: (i) X4 (xG/shot) is a strong SOT arm candidate; (ii) the
on-target-rate result does **not** license a standalone trailing
SOT-rate covariate — v5's internal Beta-Binomial ratio component
already carries that information, and the harder-shrinkage arm
(RS) is retained precisely to test how much team ratio signal the
gate believes; (iii) finishing is **not consumed** by any arm: the
DC blend (X1) fits on goals directly, so team finishing is already
inside the goals ratings — adding it again would double-count.
Verdict: **SIGNAL-CANDIDATE** (X4), recorded-not-consumed
(finishing, on-target rate).

**F7 — xGOT: attacking post-shot quality is real in the complete
era.** Population rule (Phase 1 §2): xGOT is populated for ~all
shots only from **2024/2025**. Era-restricted (2024/2025+,
ratio of sums, ≥16 era matches/team, 21 teams): split-half
r = **0.522** attacking. (The all-era figure, 0.858, mixes the
on-target-only population of earlier eras and is not comparable —
do not use it.) No defensive-side claim is made (not measured as a
separate trait here; J1's defensive side was NOISE and the design
excludes it). Verdict: **SIGNAL-CANDIDATE, era-guarded to
2024/2025+** — the X6 arm in the SOT design.

**F8 — Referee strictness is a real trait.** Yellows per match by
referee: split-half r = **0.512** (23 referees with ≥20 matches;
odd/even 0.381). Referee coverage is **100%** in every season —
the operational condition (appointment known pre-match) is a live-
pipeline question, but the warehouse field is complete. Verdict:
**SIGNAL-CANDIDATE** for the cards design (X8 arm), subject to the
walk-forward gate.

**F9 — Territorial pressure: box touches are the corners proxy,
where present.** Team opp-box-touches trait: split-half r =
**0.959** for / 0.876 against (measured on matches where the key is
present — 69–85% of 2021/2022–2023/2024, 100% from 2024/2025).
Production's own covariates are also strong here (possession-for
0.944, big-chance-for 0.912). Verdict: **SIGNAL-CANDIDATE** — the
C-NL design runs the box-touch multiplier (X7) against Gate Zero's
production covariates (X9), with the FEATURES min-8 trailing rule
absorbing the early gaps, exactly as C-J1 did for J1 2021.

**F10 — Star absence: NOT re-tested.** The question is closed
program-wide (V10 null on top-5, replicated null on J1); no new
reliability evidence exists in this corpus that could meet the
reopening standard, and none was sought. Lineup/absence features
remain forbidden.

**F11 — FotMob xG is calibrated for the Eredivisie.** Goals per
unit xG by season: 1.074, 1.042, 1.043, 1.056, 1.006, 1.125
(partial) — pooled ≈ 1.05, a mild systematic under-forecast of
goals by xG but inside the ±8% seasonal wobble band J1 showed.
Verdict: **SIGNAL** (input quality fact) — the production blend
idea (fit on goals + xG) has a sound input here.

**F12 — Feasibility boundary (fact).** Every market's target exists
for **all 1,638 matches in all seasons** (goals, SOT, corners,
yellows, total shots; xG and shotmap 100%). Period splits exist
only from 2023/2024 (complete) — that limits halves *grading*, not
any FT market. The virgin window (2025/2026, complete, n = 306)
contains every target. **All five candidates are feasible**:
G-NL (goals), S-NL (SOT), C-NL (corners), K-NL (cards), T-NL
(total shots).

## Verification note (coordinator, independent of the EDA script)

- Levels and counts recomputed from the raw index + JSONs:
  1,659 index rows, 21 playoff exclusions, 306 regular matches per
  full season, 0 score/event mismatches.
- Split-half reliability recomputed through a second implementation
  straight from the match table: SOT-for 0.922 (script: 0.924),
  goals-for 0.908 (script: 0.909).
- Halves variance decomposition recomputed with the per-match noise
  floor (the script's first version used a mean-n floor, which
  understates the floor and inflates true variance — corrected in
  the committed `eda.py`); yellows 1H share cross-checked through
  the event feed (0.343 vs stats-splits 0.333).
- Newcomer gaps: the first script version subtracted the league's
  *match* goal mean instead of the *team* goal mean (gap −1.99 —
  impossible on its face); corrected in the committed `eda.py`
  (−0.45 / +0.26, verified by hand from the per-season table).
- Ratio traits: the first script version used means of per-match
  ratios; the committed version uses ratios of sums, per the
  program standard.
