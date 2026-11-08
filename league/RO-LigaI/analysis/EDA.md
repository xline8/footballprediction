# Step 3 — EDA (RO-LigaI)

All numbers on the modelling inclusion set (phase != ecl_playoff,
n = 1,694). Dev era = 2021/2022–2024/2025; virgin = 2025/2026.

## F1 — Levels by season

| Season | Goals/m | Home win | Draw | OU2.5 over | SOT/m | Corners/m | Shots/m (raw) | Yellows/m (events) |
|---|---|---|---|---|---|---|---|---|
| 2021/2022 | 2.321 | .451 | .241 | .394 | 8.34 (n=310) | 8.93 | 18.73 | 4.70 |
| 2022/2023 | 2.384 | .444 | .263 | .416 | 8.15 (n=304) | 8.72 | 17.77 | 4.42 |
| 2023/2024 | 2.600 | .422 | .308 | .486 | 8.51 (n=305) | 9.21 | 18.13 | 4.56 |
| 2024/2025 | 2.327 | .410 | .311 | .387 | 8.20 (n=315) | 9.53 | 17.90 | 4.35 |
| 2025/2026 (virgin) | 2.514 | .444 | .270 | .457 | 8.48 (n=315) | 9.70 | 26.12 ⚠ | 4.18 |
| 2026/2027 (partial) | 2.622 | .521 | .252 | .471 | 9.45 | 9.37 | 29.38 ⚠ | 4.32 |

Goals are low by European standards (≈2.3–2.6 vs J1 ≈2.5–2.7 and
top-5 ≈2.8–3.0) with a high draw share in mid-era seasons.
⚠ Shots: definition break at the rich-feed boundary (Step 1) — the
raw series is not one target across eras.

## F2 — Team-trait reliability (split-half, team-season odd/even, n=96 units)

| Trait | r | Spearman–Brown |
|---|---|---|
| total shots for | 0.831 | 0.908 |
| possession | 0.766 | 0.868 |
| on-target rate (SOT/shots) | 0.703 | 0.826 |
| SOT for | 0.611 | 0.758 |
| SOT against | 0.427 | 0.599 |
| corners for | 0.439 | 0.610 |
| corners against | 0.374 | 0.544 |
| goals for / against | 0.358 / 0.356 | 0.527 / 0.525 |
| yellows for / against | 0.237 / 0.254 | 0.384 / 0.405 |

Target traits are reliable (shots/SOT/corners); yellows-for is weak
(0.237, CH-like 0.256) — the naive component is still defined
identically and the gate decides. On-target rate is a real trait
here (0.703; unlike CH where it was noise) — it is consumed only
inside the v5 ratio architecture, not as a standalone covariate.

## F3 — Halves (frozen constants; splits exist only 2025/2026+)

Measured on the split era pooled (2025/2026 + 2026/2027, n = 434,
presentation only — never a fitting input):

| Market | 1H share |
|---|---|
| goals (event HT) | 0.453 |
| SOT | 0.455 |
| corners | 0.477 |
| total shots | 0.459 |
| yellows (event times) | 0.330 |

Per-match half shares are treated as noise around these constants
(the programme-wide finding; no per-team half modelling).

## F4 — Movers / tiers

16-team league with promotion/relegation to Liga II. Liga II is a
separate warehouse league and is NOT part of this build; no tier
offset is estimated (X2 dropped, FEATURES). Promoted clubs enter
with thin in-league history — the risk the goals SHRINK arm exists
for (sanctioned G-J2 lesson).

## F5/F6/F7 — xG family: NOT MEASURABLE

No xG, no set-play/open-play splits, no shotmap, no xGOT in any
season. Set-play share (J1 F5), xG/shot (F6) and xGOT (F7) checks
cannot be run; the corresponding features are dropped on data
absence, not on reliability failure.

## F8 — Referee strictness (event yellows)

22 referees with ≥20 matches; split-half r = 0.568 (SB 0.724) on
match total yellows — a real trait, comparable to J1/CH. Coverage
99.4% overall (100% in 2021/2022, ≥99.4% in every complete season).

## F9 — Territorial covariates

Possession r = 0.766 (strong; corners Gate Zero covariate, all eras
available). Box touches / big chances exist only in the rich era
(2025/2026+) → no dev-era measurement possible; dropped (X7).

## F10 — Lineup/absence: CLOSED (programme-wide; not revisited).

## F11 — xG calibration: not applicable (no xG published).

## F12 — Cards artefact

See DATA_UNDERSTANDING: stats feed undercounts events by
≈0.21 yellows/match where both exist (exact agreement 76.5%).
Event-unified target frozen (PREPROCESSING).
