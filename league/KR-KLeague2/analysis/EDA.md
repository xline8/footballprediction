# Phase 3 — EDA: KR-KLeague2

All figures on the REGULAR-season population (play-offs excluded) from
`analysis/eda.py` → `eda_summary.json`; charts in `analysis/charts/`.

Levels per match by season:

| Season | goals | HW% | draw% | over2.5% | shots | SOT | corners | yellows (stats) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2021 | 2.417 | 34.4 | 28.3 | 46.1 | – | – | – | – (no stats) |
| 2022 | 2.527 | 42.3 | 29.5 | 49.1 | 24.76 | 8.57 | 8.65 | 1.07 (artefact) |
| 2023 | 2.568 | 42.3 | 24.4 | 47.9 | 23.91 | 8.21 | 9.28 | 2.93 |
| 2024 | 2.632 | 32.9 | 29.9 | 51.3 | 24.70 | 8.95 | 8.57 | 3.08 |
| 2025 | 2.513 | 35.2 | 29.3 | 45.4 | 23.32 | 8.13 | 8.51 | 3.71 |
| 2026* | 2.746 | 37.5 | 30.9 | 52.7 | 24.90 | 8.83 | 8.85 | 3.57 |

*2026 in progress, reserved. Pooled: 2.575 goals, home 1.342 / away
1.233 — a smaller home edge than KR-KLeague1 (home-win share only
37.4% pooled; 2024 home wins fell to 32.9% with away goals 1.342 >
home 1.291). Count dispersion (var/mean, pooled): goals 1.04, SOT
1.13, corners 1.26, shots 1.33, yellows 3.19 in the mixed-era pool
(the 2022 artefact inflates the yellow figure).

Trait reliability (split-half r, career-pooled, 60 splits, teams with
≥24 matches; stats traits on their available eras):

| trait | for | against |
|---|---:|---:|
| goals | 0.718 | 0.662 |
| total shots | 0.761 | 0.634 |
| SOT | 0.642 | 0.725 |
| corners | 0.715 | 0.489 |
| yellows (stats) | 0.752 | 0.663 |
| big chance | 0.743 | 0.607 |
| possession | 0.867 | 0.867 |
| box touches | 0.804 | 0.683 |
| on-target ratio (SOT/shots) | 0.006 | – |

Team traits are real in this league for every count target, and box
touches are the strongest auxiliary trait. The on-target RATIO is not
a team trait at all (r = 0.006): the production SOT ratio construction
has nothing to stand on here (see FEATURES.md).

Halves (splits era 2023–2025; per-match 1H share variance vs the
binomial noise floor): true variance is ≈ 0 for goals (−0.0029), SOT
(+0.0007), total shots (−0.0003), small for corners (+0.0032) and
cards (+0.0087). Frozen constants are justified; halves are
presentation-only (FEATURES.md).

Referees: 59 named referees cover 400 of 1,397 regular matches; only
3 referees reach ≥20 matches in the whole corpus (2 in the stats
era), so a split-half strictness reliability cannot be estimated
(the estimator returns no splits). X8 is dropped (FEATURES.md).

Movers (X2 feasibility): entering teams by season, classified against
the KR-KLeague1 corpus (league/KR-KLeague1/data/kr_matches.csv) by ID:
2022 Gwangju FC (from K1), Gimpo FC (K3, no corpus); 2023 Gimcheon
Sangmu + Seongnam FC (K1), Cheonan City + Cheongju FC (K3); 2024 Suwon
Samsung Bluewings (K1); 2025 (virgin) Incheon United (K1), Hwaseong FC
(K3); 2026 (reserved) Daegu FC + Suwon FC (K1). A true ID-linked
mover-offset arm is measurable in every scored dev season and in the
virgin.
