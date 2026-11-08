# Phase 4 — Candidate model design (no fitting)

Design authority for the five preregistrations. Calibration sign
convention is actual minus predicted everywhere in this build.
Dev: training seed 2021/2022, scored walk-forward seasons
2022/2023–2024/2025 (n = 720). Virgin: 2025/2026 (n = 240, last
COMPLETE season), read ONCE per candidate and only for arms that
pass the dev gate. 2026/2027 is in progress (112 matches) and is the
reserved confirmatory window — never read in this build.

Format (verified from the data): 16 teams, double round-robin,
30 matches per team, single regular phase in every season
(phase = "regular" throughout; no play-off or split-phase matches in
the warehouse). Promotion/relegation movers exist every season
(2–3 clubs) but no second-tier corpus is built, so X2 is not
consumed; the measured newcomer gaps (GF −0.250, GA +0.259, n = 12)
motivate the goals SHRINK arm instead.

Invasion-era decision (frozen here, before fitting): NO dev-season
exclusion. The pre/post 2022-02-24 split of 2021/2022 shows no goals
break (2.667 before, 2.656 after); 2022/2023 is a one-season level
excursion (3.042 goals) that fully reverts in 2023/2024 (2.654).
That is not the persistent regime break of the SA precedent, so dev
is scored on all three scored seasons and the per-season refits
absorb the excursion. No sensitivity re-scoring is registered.

xG era: stats-feed xG / set-play xG / shotmap exist essentially only
from the virgin season, so the goals model is the production DC
pattern with the X1 blend pair whose fallback (goals-only) fires on
effectively every dev and virgin-fit match. X3/X4/X6 are dropped
(virgin-era data cannot be dev-gated). X8 is dropped: referee
strictness reliability is r = 0.178 pooled and season-unstable
(0.658 / 0.368 / −0.398 / 0.205 / 0.025), with coverage as low as
40.0% (2021/2022) and 70.4% (virgin).

Cards artefact (frozen here, before fitting): PRESENT — exact
stats/events agreement 76.5%, mean stats − events = −0.550, stats
lower in 21.7% vs higher in 1.8%, max |diff| 11. The cards target is
therefore EVENT-UNIFIED yellows (`ev_yellow_home + ev_yellow_away`,
direct Yellow + YellowRed events). Primary line 4.5 (dev
seed+scored over-rate 0.472, closest to 0.5; 3.5 is 0.642).

| candidate | target | Gate Zero | variant arms | primary line |
|---|---|---|---|---|
| goals G-RU | home/away goals (DC) | production DC pattern, X1 pair (goals-only in practice) | SHRINK (thin-history/newcomer shrinkage, G-J2 lesson) | OU 2.5 (dev over 0.525) |
| SOT S-RU | ShotsOnTarget total (stats) | production v5 pattern | RS (BB prior 200 → 20,000) | 8.5 (0.537) |
| corners C-RU | corners total (stats) | production corners_v3 pattern with X9 covariates | X7 (box-touch multiplier replacing X9) | 9.5 (0.496) |
| cards K-RU | event-unified yellows | production cards pattern on the event target | — (X8 dropped; no variant) | 4.5 (0.472) |
| total shots T-RU | total_shots total (stats) | shots family arm A (v1 pattern) | B (v2 level layer), C (E9 trailing-r) | 25.5 (0.518) |

Halves: presentation only, via the frozen constants in config.yaml
(goals 0.4472, SOT 0.4612, corners 0.4801, total shots 0.4602,
yellows 0.3519 — the yellows constant is computed from stats period
splits, the only split source; presentation only). Per-match half
shares are noise in this league too (observed variance ≈ noise
expectation for SOT/corners/total shots; goals n = 665 split rows),
so no half modelling is registered.

No model is fit and no preregistration file is created in Phase A.
