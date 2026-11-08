# Phase 3 — EDA: DE-3Liga (numbers: `eda_numbers.json`, computed by `eda_compute.py`)

## F1 — Levels by season (per match)

| Season | n | goals | SOT | corners | yellows (events) | total shots |
|---|---:|---:|---:|---:|---:|---:|
| 2021/2022 | 342 | 2.781 | 9.493 | 10.745 | 4.383 | 26.991 |
| 2022/2023 | 380 | 2.916 | 9.342 | 10.274 | 4.655 | 27.711 |
| 2023/2024 | 380 | 2.805 | 9.153 | 10.492 | 4.737 | 27.187 |
| 2024/2025 | 380 | 2.903 | 9.418 | 10.063 | 4.995 | 26.803 |
| 2025/2026 (virgin) | 380 | 3.208 | 9.874 | 10.613 | 4.813 | 27.732 |
| 2026/2027 (partial, reserved) | 130 | 3.262 | 9.662 | 9.600 | 4.838 | 27.362 |

Pooled complete-era: goals 2.925, home win 44.4% / draw 24.8% /
away win 30.8%, Over 2.5 55.5%, BTTS 58.2%. Home edge: 1.597 home
goals vs 1.328 away. Note the virgin season ran hot on goals
(3.208 vs dev-era ≈2.85) — recorded here pre-fitting; gates are
applied mechanically regardless.

## F2 — Split-half trait reliabilities (team-season, n=40 teams)

goals for 0.583 / against 0.655; SOT for 0.704 / against 0.673;
corners for 0.593 / against 0.555; total shots for 0.701 / against
0.745; touches-opp-box for 0.848 / against 0.821; possession 0.901;
big chance for 0.689 / against 0.743. All count traits are real
team traits in this league (all r ≥ 0.55). Referee strictness
(yellows/match, referees with ≥20 matches, n=39): r = 0.483 —
moderate but real; combined with 88–99% coverage from 2022/2023
this passes the X8 adoption bar.

## F3 — Halves shares (complete-splits era 2023/2024–2025/2026, presentation only)

| Market | n | 1H share | true variance of per-match share |
|---|---:|---:|---:|
| goals | 1,072 | 0.4454 | −0.0029 (≈0) |
| SOT | 1,128 | 0.4474 | 0.0007 |
| corners | 1,127 | 0.4662 | 0.0008 |
| total shots | 1,128 | 0.4515 | −0.0004 (≈0) |
| yellow cards | 1,121 | 0.3605 | 0.0054 |

True share variance ≈ noise for goals/SOT/corners/shots → frozen
constants, never modelled (program-wide closed rule). Cards carry
a small positive true variance (0.0054) but the constant is still
frozen — halves are presentation only.

## F4 — Cards artefact (checked EARLY, before any design)

Stats yellows vs event yellows (stats-present n=1,963): exact
81.0%, stats lower in 14.2%, stats higher in 4.7%, mean
stats − events = −0.178/match; including YellowRed events worsens
it (−0.277). → Event-unified target (sixth league with the
artefact family; unlike DE-2's BE/DK shape, here the amendment IS
needed). Stats columns retained for audit.

## F5 — Movers (entrants per season vs league)

7 entrants in each dev transition (266 entrant matches), 6 in the
virgin transition. Entrant deltas (GF/GA vs league): 2022/2023
−0.059/+0.057; 2023/2024 +0.015/−0.053; 2024/2025 −0.072/+0.007 —
small and sign-inconsistent (the virgin transition −0.161/+0.291
is recorded but cannot justify an arm fitted on dev). Regionalliga
(the up-feeder) is not in the warehouse, so direction-specific
offsets are only half-identifiable. → X2 DROPPED (FEATURES.md);
the sanctioned SHRINK arm remains as the goals candidate's
thin-data guard.

## F6 — Dev over-rates (primary-line choice; dev n≈1,481–1,482)

SOT: 8.5 → 0.581, **9.5 → 0.458**, 10.5 → 0.327.
Corners: 9.5 → 0.590, **10.5 → 0.467**, 11.5 → 0.365.
Yellows: 3.5 → 0.704, **4.5 → 0.499**, 5.5 → 0.339.
Total shots: 25.5 → 0.585, **26.5 → 0.518**, 27.5 → 0.451.
Primary line = the .5 line whose dev over-rate is closest to 0.5.
