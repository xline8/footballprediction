# EDA — EE-Meistriliiga

All figures are generated from `data/ee_matches.csv`; 2021 is partial. Yellow
cards are shown only for 2025–2026 because the event feed is missing yellows
before 2025.

| season | n | goals | H/A goals | H / D / A | OU1.5 | OU2.5 | OU3.5 | BTTS | home advantage |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2021 | 156 | 3.321 | 1.750 / 1.571 | .429 / .173 / .397 | .814 | .660 | .423 | .538 | .179 |
| 2022 | 180 | 3.050 | 1.706 / 1.344 | .456 / .194 / .350 | .767 | .544 | .328 | .506 | .361 |
| 2023 | 180 | 2.544 | 1.356 / 1.189 | .372 / .278 / .350 | .756 | .467 | .228 | .467 | .167 |
| 2024 | 180 | 2.994 | 1.528 / 1.467 | .417 / .222 / .361 | .806 | .578 | .367 | .500 | .061 |
| 2025 | 180 | 3.178 | 1.739 / 1.439 | .467 / .133 / .400 | .833 | .683 | .383 | .550 | .300 |
| 2026 | 180 | 3.100 | 1.772 / 1.328 | .478 / .133 / .389 | .811 | .633 | .383 | .572 | .444 |

Yellow cards are 3.950/match in 2025 and 4.233/match in 2026. Goal traits are
reliable under 60 deterministic random split-halves of each team’s
career-pooled match list (minimum 24 matches/team): goals-for r=0.876 (SD
0.061), goals-against r=0.874 (SD 0.055), 13 eligible team ids. This supports
a goals ratings architecture, not additional stats features. The season-level
split-half r values (same 60-split method; 10 eligible clubs per season) are:

| season | GF r | GA r |
|---|---:|---:|
| 2021 | 0.7873 | 0.7722 |
| 2022 | 0.7457 | 0.8420 |
| 2023 | 0.6752 | 0.6964 |
| 2024 | 0.7753 | 0.7101 |
| 2025 | 0.7300 | 0.8619 |
| 2026 | 0.7371 | 0.6760 |

Entrants were defined by id absence in the immediately prior season. Their
first-season deviations from the season league mean goals per team-match are:

| target | entrant id | GF/m | GA/m | dGF | dGA |
|---|---:|---:|---:|---:|---:|
| 2022 | 49578 | 1.167 | 2.556 | −.358 | +1.031 |
| 2023 | 673053 | .750 | 1.694 | −.522 | +.422 |
| 2024 | 584714 | .611 | 2.194 | −.886 | +.697 |
| 2025 | 673053 | 1.361 | 1.944 | −.228 | +.356 |
| 2026 | 584714 | 1.639 | 2.250 | +.089 | +.700 |

Pooled entrant deviation over all five entrants is dGF=−0.381 and
dGA=+0.641 over 180 entrant team-matches (descriptive only). The X2
mover arm does NOT use that pooled figure: its offset for target season
S is the expanding pooled deviation over entrants in seasons strictly
before S only, so no virgin-season outcome enters any offset — the
2026 entrant row above is descriptive and excluded. The frozen offsets
are: 2022 — none (no prior entrant; X2 inactive, ≡ Gate Zero); 2023 —
dGF −0.358333, dGA +1.030556 (36 team-matches); 2024 — dGF −0.440278,
dGA +0.726389 (72); 2025 — dGF −0.588889, dGA +0.716667 (108); 2026
(virgin) — dGF −0.498611, dGA +0.626389 (144). This is directionally
systematic in every window, so X2 is adopted.

Referee coverage and strictness record:

| season | referee coverage | yellow cards / covered match |
|---|---:|---:|
| 2021 | 0/156 | n/a |
| 2022 | 0/180 | n/a |
| 2023 | 0/180 | n/a |
| 2024 | 0/180 | n/a |
| 2025 | 61/180 | 3.590 |
| 2026 | 72/180 | 4.347 |

This is record-only and no referee feature enters goals.

No halves constant is possible: no payload has a period split. Presentation is
FT-only; no halves values are invented.
