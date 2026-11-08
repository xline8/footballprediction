# Phase 3 — EDA: ES-PrimeraFederacion

All numbers from `analysis/eda_compute.py` → `eda_numbers.json`
(built CSV). Frozen model inputs use DEV seasons only
(2021/2022–2024/2025); virgin-season figures are descriptive levels
only and feed no fitted quantity. Charts in `analysis/charts/`.

## F0 — Levels by season (goals exist in 100% of matches)

| Season | n | Goals/match | Home goals | Away goals | H% | D% | A% | OU2.5 |
|---|---|---|---|---|---|---|---|---|
| 2021/2022 | 767 | 2.407 | 1.385 | 1.022 | 46.8 | 24.6 | 28.6 | 44.6% |
| 2022/2023 | 774 | 2.217 | 1.271 | 0.946 | 43.8 | 30.5 | 25.7 | 37.9% |
| 2023/2024 | 774 | 2.231 | 1.296 | 0.935 | 44.1 | 28.7 | 27.3 | 40.4% |
| 2024/2025 | 774 | 2.411 | 1.377 | 1.034 | 42.8 | 31.9 | 25.3 | 42.5% |
| 2025/2026 (virgin) | 772 | 2.337 | 1.348 | 0.988 | 45.5 | 29.3 | 25.3 | 41.2% |
| 2026/2027 (partial) | 220 | 2.618 | 1.536 | 1.082 | 48.2 | 28.6 | 23.2 | 45.9% |

Dev pooled (3,089 matches): mu = **1.1581** goals per team per
match. Dev-eval pooled (2,322): OU2.5 **40.3%**, H 43.5%, D 30.4%,
A 26.1%. Total-goals distribution (dev): 0: 317, 1: 699, 2: 796,
3: 665, 4: 334, 5: 176, 6: 70, 7: 25, 8: 5, 9: 2.
**Home advantage (dev):** home-win rate 44.35%, home goals 1.3321
vs away 0.9841 per match, home goals share **0.5751** — a strong
home edge, in line with the third tier's travel/venue spread.
The virgin season sits inside the dev range on every level (goals
2.337 vs dev 2.217–2.411; OU2.5 41.2% vs 37.9–44.6%) — no regime
break to re-litigate after the fact. The partial 2026/2027 runs hot
(2.618) on 220 matches; it is not read in this build.

## F1 — Team goal traits: modest reliability (split-half by season)

Per team-season, first half vs second half of the team's matches
(n = 160 team-seasons, DEV):

| Split | GF/match r | GA/match r |
|---|---|---|
| Chronological halves | **0.296** | **0.376** |
| Rounds 1–19 vs 20–38 (regular only) | **0.278** | **0.415** |

Team attack/defence traits are real but modest — weaker than the
program's stat-rich leagues (where trait r runs 0.55–0.90), and
churn-diluted by design: 14 of 40 teams are new every season, so a
multi-season rating carries less signal here than in a stable
league. Defence is the more reliable trait in both splits. The DC
fit's expanding window is the right consumer of this signal (no
trailing-window covariate arm is built on top of it).

## F2 — Trailing target-rate means

Not separately measurable beyond F1: the only target in the league
is goals, and the DC ratings are the trailing-goals mechanism.
There is no SOT / corners / shots / yellows series to split-half
(stats feed absent). The naive baseline for the goals gate is the
expanding climatology (prior-seasons H/D/A + OU2.5 rates), per the
prereg — not a trailing-10.

## F3 — Halves: per-match 1H share is NOISE; frozen constant only

First-half goal share from Goal events (matches with complete goal
events only — the 16 awarded 2021/2022 matches are excluded from
both numerator and denominator; an earlier pass that divided by all
goals including the 35 awarded goals understated the share at
0.4280 and was corrected before freezing):

| Season | HT share | n (matches with goals) |
|---|---|---|
| 2021/2022 | 0.4522 | 683 |
| 2022/2023 | 0.4347 | 686 |
| 2023/2024 | 0.4233 | 681 |
| 2024/2025 | 0.4105 | 706 |
| **DEV pooled** | **0.4301** | **2,756 (3,062 / 7,120)** |
| 2025/2026 (virgin, descriptive) | 0.4473 | 686 |
| 2026/2027 (partial) | 0.4167 | 205 |

Per-match 1H-share SD: observed 0.3558 vs binomial noise 0.3586
(dev pooled) → **true SD 0.0**. The J1 question answers the same
way here: per-match half shares are pure noise around the constant.
**Frozen: goals_1h_share = 0.4301** (dev pooled, presentation only;
FT + 1H/2H for the goals market). No per-team half-share model is
built, for any market. (For reference, the all-complete-seasons
pooled share is 0.4336 — the frozen dev-only figure is the
conservative one; the difference is 0.004.)

## F4 — Mover tier offsets (the X2 feature)

Entry-season performance of clubs whose previous season was in
LaLiga2 (warehouse index id 140, accent-normalised name matching,
verified against id-keyed lists) or below (new id, absent from
LaLiga2 in the prior season — Segunda Federación is not in the
warehouse). Frozen magnitudes use **dev entry seasons only**
(2022/2023–2024/2025: 12 + 30 team-seasons), so no frozen input
touches the virgin (stricter than the ES-LaLiga2 precedent, which
pooled entry seasons through 2026/2027):

| Entry source | Team-matches | GF/match | GA/match | GD/match | ΔGF vs mu 1.1581 | ΔGA vs mu |
|---|---|---|---|---|---|---|
| from LaLiga2 | 476 | 1.240 | 1.008 | **+0.231** | **+0.081** | **−0.150** |
| from below (Segunda Fed) | 1,144 | 1.104 | 1.169 | **−0.065** | **−0.054** | **+0.011** |

**SIGNAL, asymmetric and defence-led for the relegated clubs:**
a relegated LaLiga2 club is, on entry, nearly a quarter-goal per
match better than the average Primera Federación club — almost all
of it defensive (GA −0.150; GF only +0.081). A promoted fourth-tier
club's problem is small and split (GF −0.054, GA +0.011; GD −0.065)
— far weaker than ES-LaLiga2's promoted-club penalty (−0.136),
because the fourth-to-third step is smaller than the third-to-second.
Descriptive check (pooled incl. virgin entry seasons, NOT frozen):
from LaLiga2 GD +0.253 (n=628), from below −0.056 (n=1,530) — same
directions, same order of magnitude. These magnitudes freeze the X2
arm's offsets in PREREG_G_ESPF (ENGCH X2 formulation, applied only
at prediction time in the mover's entry season).

Every season contributes exactly 4 from-LaLiga2 + 10 from-below
movers (mover lists per season in `eda_numbers.json`).

## F5–F7 — xG family: NOT MEASURABLE (no xG era exists)

Set-play xG share, xG per shot, xGOT per shot: no xG, no shotmap,
no stats in any season. There is no era to guard and no future
window in which these become measurable without a FotMob coverage
change. X1/X3/X4/X6 all dropped on availability (FEATURES). Unlike
ES-LaLiga2, this is not an era break — it is a permanent property
of the league's coverage until FotMob changes it.

## F8 — Referee: NOT MEASURABLE (no referee data, no cards target)

Referee text is empty in 4,081/4,081 payloads (0% coverage). Even
if it were populated, there is no cards target to attach it to.
X8 dropped (FEATURES). The ES-LaLiga2 reliability question (r=0.180)
does not arise here — there is nothing to correlate.

## F9 — Cards feed audit (why K-ESPF is not buildable)

Card events per season: 168 / 205 / 160 / 172 / 220 / 70
(0.219 / 0.265 / 0.207 / 0.222 / 0.285 / 0.318 per match); matches
with any card event: 19.2% / 22.7% / 18.1% / 19.1% / 24.7% /
26.4%. Total 995 events in 4,081 matches. There is no stats feed
to cross-check against (stats empty), so the deficit cannot be
repaired or even bounded per match — the event feed is a sparse
subset of unknown selection. No cards model is built, on any
definition of the target.

## Feasibility summary

Goals exist in 100% of matches; SOT / corners / total shots / cards
exist in 0% in any usable sense. **One buildable candidate: G-ESPF
(goals).** Everything else is recorded NOT BUILDABLE with the
payload-level evidence above, not deferred.
