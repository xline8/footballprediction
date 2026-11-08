# Phase 6 — Model Design: KR-KLeague2 candidates

Design only; no fitting. Population: regular season only (play-offs
excluded, frozen). Virgin = complete 2025 (273) for every candidate;
2026 is in progress and reserved as confirmatory, unread here.
Primary line per candidate = the line whose over-rate is closest to
0.50 on that candidate's scored dev window (frozen rule).

| Candidate | Dev (seed → scored) | Primary line / scored-dev over-rate | Arms |
|---|---|---|---|
| G-KR2 goals | 2021 → 2022–2024 (688) | OU 2.5 / 0.494 | Gate Zero (DC, goals-only); SHRINK; X2 mover offset |
| S-KR2 SOT | 2022 → 2023–2024 (461) | OU 8.5 / 0.492 | Gate Zero; X7 box-touch multiplier |
| C-KR2 corners | 2022 → 2023–2024 (461) | OU 8.5 / 0.521 | Gate Zero; X7 box-touch multiplier |
| K-KR2 cards | 2023 → 2024 (229) | OU 2.5 / 0.620* | Gate Zero only (X8 dropped in FEATURES) |
| T-KR2 total shots | 2022 → 2023–2024 (461) | OU 24.5 / 0.477 | Gate Zero; X7 box-touch multiplier; E9 trailing-200 r |

*Cards scored window is the single season 2024: OU 2.5 over-rate
0.620 (distance 0.120) vs OU 3.5 0.371 (distance 0.129) — 2.5 is the
mechanical pick; 3.5 and 4.5 are reported as secondary lines.

Count-market Gate Zero (production pattern): season-blocked
walk-forward — for each target season, fit Poisson team attack/
defence ratings (iterative proportional fitting, exponential decay
half-life 270 days at the season-start cutoff, same iteration as the
goals DC core) on all earlier matches with the target present;
expected total = λ_home + λ_away; over-probabilities from a Negative
Binomial whose r is the frozen moment estimate on the training window
(cards model formula, capped [2, 500]). Baselines: league base rate
(prior-seasons over-rate at the line) and naive trailing-10 (each
team's last-10-match for/against means before the season starts,
combined as in the production cards naive).

X7 construction (frozen): from matches before the target season,
team box-touch for/against per match (matches with touches data
only); index = team rate / league rate; active only if both teams
have ≥8 such matches; multiplier on each side =
sqrt(att_index × opp_def_index) clipped to [0.5, 2.0].

E9 construction (frozen, total shots only): NB r estimated by the
moment formula on the last 200 training matches only, instead of the
full training window.

Goals Gate Zero: production Dixon-Coles (rho grid {0, −0.05, −0.10,
−0.15}, half-life 270 days, 14 IPF iterations) on goals only — the X1
blend has no xG to blend in this league. SHRINK: fitted log-ratings
of teams with <6 prior K2 matches are scaled by count/6 (the
pre-registered new-team shrinkage from the template). X2: for a team
whose immediately preceding season was in K League 1 (ID match
against the KR-KLeague1 corpus) and which has no K2 matches before
the target season, add log(att_rel) to its attack rating and
log(def_rel) to its defence rating, where att_rel / def_rel are its
prior-season K1 goals-for / goals-against per match, shrunk with a
10-match prior at the K1 league mean and divided by that mean.

Gate legs (identical in every prereg): dev gate first; virgin read
once, only for dev-passing arms; if Gate Zero fails dev the candidate
fails and the virgin is NOT read. Calibration: |breach| ≤ 1 pp clean
PASS; ≤ 1 pp + 1 SE PROVISIONAL PASS; else FAIL. Gates never move.
