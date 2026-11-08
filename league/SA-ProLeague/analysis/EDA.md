# Phase 3 — EDA: SA-ProLeague

All numbers computed by `analysis/eda_compute.py` from the built CSV
(raw dump: `analysis/eda_numbers.json`). J1 checklist replicated,
plus the two league-specific measurements the brief requires: the
2023 regime break (F1b) and the cards feed check (documented in
DATA_UNDERSTANDING §3.1, decided on dev-era evidence only).

## Levels per season (per match, both teams)

| Season | Goals | xG | SOT | Corners | Shots | Yellows (events) | Yellows (stats) | Reds |
|---|---|---|---|---|---|---|---|---|
| 2021/2022 | 2.654 | — (2.5% cov) | 8.371 | 8.854 | 23.917 | 4.233 | 3.383 | 0.204 |
| 2022/2023 | 2.700 | — (13.3% cov) | 8.200 | 9.867 | 23.208 | 3.775 | 3.538 | 0.171 |
| 2023/2024 | 2.971 | 2.766 | 8.745 | 9.676 | 24.095 | 3.866 | 3.719 | 0.239 |
| 2024/2025 | 2.948 | 2.852 | 9.330 | 9.680 | 25.196 | 4.281 | 4.147 | 0.206 |
| 2025/2026 (virgin) | 3.010 | 2.916 | 8.908 | 10.052 | 24.353 | 4.013 | 3.925 | 0.248 |
| 2026/2027 (partial, n=104) | 3.029 | 3.221 | 8.990 | 9.663 | 25.875 | 3.654 | 3.471 | 0.154 |

## F1 — Levels and drift

Within the post-break era the level is fairly stable (goals
2.95–3.01, SOT 8.7–9.3); the dominant movement is the break itself
(F1b). Per-league fitting with time decay is justified; a single
pooled level across the break is not.

## F1b — The 2023 regime break (measured explicitly)

| Quantity | Pre (2021/22–2022/23, n=480) | Post-dev (2023/24–2024/25, n=612) | Δ |
|---|---|---|---|
| Goals/match | 2.677 | 2.959 | +0.282 |
| SOT/match | 8.285 | 9.038 | +0.753 |
| Total shots/match | 23.562 | 24.645 | +1.083 |
| Corners/match | 9.360 | 9.678 | +0.318 |
| Yellows (events)/match | 4.004 | 4.074 | +0.070 |
| Home goal edge | +0.269 | +0.175 | −0.094 |
| Home-win rate | 45.8% | 43.0% | −2.8pp |
| OU2.5 over-rate | 51.5% | 56.5% | +5.0pp |
| SD of team GD means | 0.663 | 0.896 (post incl. virgin) | widened |

Trait stability across the break (16 ever-present clubs, per-team
mean pre vs post): shots-for **r=0.922**, SOT-for 0.871, goals-for
0.779, corners-for 0.739, goals-against 0.608. Reading: strengths
persisted in rank but the spread widened and the league level
jumped — a decay-weighted fit can carry pre-break history, but
**scored dev evidence must be post-break** (MODEL_DESIGN), and the
first post-break season's fits (trained almost entirely on
pre-break data under the season-blocked protocol) are expected to
be the hardest dev fold. That is the honest price of the break,
paid in the open.

## F2 — Team trait reliability (split-half; career-pooled / post-era)

| Trait | Career | Post-era (n=23 teams) | Verdict |
|---|---|---|---|
| box touches-for | 0.929 | 0.953 | SIGNAL |
| possession | 0.924 | 0.962 | SIGNAL |
| shots-for | 0.907 | 0.929 | SIGNAL |
| xG-for | 0.928 | 0.900 | SIGNAL (post-era only — feed era) |
| SOT-for | 0.767 | 0.887 | SIGNAL |
| corners-for | 0.752 | 0.910 | SIGNAL |
| big-chance-for | 0.925 | 0.878 | SIGNAL |
| goals-for | 0.799 | 0.806 | SIGNAL |
| yellows-for (stats) | 0.102 | 0.196 | WEAK |
| yellows-for (events, unified) | 0.205 | 0.264 | WEAK |

Attacking/count traits are as reliable as anywhere in the program.
**Team yellow traits are not**: r ≈ 0.20–0.26 in either feed, far
below SCO's 0.639. The cards candidate therefore leans on the
league level and whatever the reference architecture extracts; the
dev gate decides, with no referee help available (F8).

## F3 — Half shares: frozen-constant question

Measured on the complete-splits era 2023/2024–2025/2026 (n≈918;
goals/yellows via events):

| Market | 1H share | True SD of per-match share |
|---|---|---|
| goals | **0.4251** | ≈ noise (events-based share, tiny denominators) |
| SOT | **0.4469** | 0.000 |
| corners | **0.4740** | 0.063 |
| total shots | **0.4559** | 0.004 |
| yellows (events) | **0.3509** | ≈ noise (obs. SD 0.273 at small counts) |

Verdict (same as J1/SCO): frozen league constants only,
presentation only. Corners carry a small true component (0.063),
nowhere near enough for a per-match model — the program's standing
conclusion, re-confirmed here.

## F5 — Set-play xG share reliability (post-era): r = **0.514** (SIGNAL-CANDIDATE)
Measured only where the feed exists (2023/2024+). Near the J1
accepted range; arm status.
## F6 — xG per shot reliability (post-era): r = **0.654** (SIGNAL-CANDIDATE)
## F7 — xGOT per shot, era-guarded (2024/2025+ population era):
r = **0.545**, 24 teams — passes the reliability bar, but its
population era starts inside the *last* dev season, so it cannot
be honestly dev-tested across the dev window (the SCO/BR X6
lesson). Adopted as a feature, **not run as an arm** in this build.
## F8 — Referee yellow rate reliability (post-era dev seasons):
r = **−0.279** (13 referees with ≥10 matches) — NOISE, and the
virgin season names a referee in 0.7% of matches. X8 is dead twice
over; K-SA runs Gate Zero only.
## F10 — Climate: highland home edge −0.088 (n=68) vs lowland
+0.193 — no altitude signal (DATA_UNDERSTANDING §4). No feature.
## F11 — xG calibration (post-break): goals/xG 1.074 / 1.034 /
1.032 by season — FotMob xG is usable for this league; the blend
pattern (X1) is legitimate from 2023/2024, goals-only before.

## Feasibility summary

All five targets (goals, SOT, corners, cards, total shots) exist
in 100% of matches in every season including the virgin season →
**five candidates** (MODEL_DESIGN). The shotmap era boundary
(2023/2024) does not remove any candidate — SOT/corners/shots are
stats-feed targets — but it confines every xG feature (X1 blend,
X3, X4) to the post-break era, which coincides with the dev era by
design.
