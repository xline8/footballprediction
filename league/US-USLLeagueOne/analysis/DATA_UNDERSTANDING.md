# Stage A — Data Understanding: USA USL League One

The builder filters `fotmob_world_index.csv` to `league_id=="9296"` and
produces 1,174 indexed match rows. All indexed rows are finished and carry a
score. Seasons are calendar labels `2021`–
`2026`; 2026 is inventory only and is in progress.

| season | matches | regular / playoff | stats | shotmap | period splits | referee | xG |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2021 | 173 | 168 / 5 | 99.4% | 0.0% | 2.9% | 0.0% | 0.0% |
| 2022 | 170 | 165 / 5 | 100.0% | 0.0% | 0.6% | 97.1% | 0.0% |
| 2023 | 197 | 192 / 5 | 99.5% | 0.0% | 96.4% | 95.4% | 0.0% |
| 2024 | 139 | 132 / 7 | 98.6% | 0.0% | 92.8% | 92.1% | 0.0% |
| 2025 | 217 | 210 / 7 | 100.0% | 0.0% | 100.0% | 95.9% | 0.0% |
| 2026 | 278 | 278 / 0 | 100.0% | 0.0% | 100.0% | 66.9% | 0.0% |

The competition runs March–November as a single table followed by single-
elimination playoffs. Phase is derived from the league-name suffix
(`Playoff`); it agrees with the phase classification on all rows. Playoff
inventory is 5–7 ties per season in 2021–25. The frozen rule is that all
playoff rows remain in the CSV and are phase-flagged, but are excluded from
every fitting and scoring window because knockout ties can include extra
time or shootouts.

The 2026 feed labels all 278 rows `regular`, but its rounds include
`Championship - Quarter-finals/Semi-finals`. The regular season ended
2026-10-25; semi-finals were played 2026-11-08/09; the final is absent.
It is therefore reserved/transitional inventory and is not used for model
decisions.

Teams per season are 12 / 11 / 12 / 12 / 14 / 17 (2021→2026). There is no
promotion/relegation anywhere in US soccer. Churn is classified as follows:

- Expansion entrants: Central Valley Fuego FC and Northern Colorado
  Hailstorm FC (2022); Lexington SC and One Knoxville SC (2023); Spokane
  Velocity FC (2024); AV Alta, FC Naples, Portland Hearts of Pine, Texoma,
  and Westchester SC (2025). The five 2025 entrants are the virgin-season
  population with zero prior in-league matches.
- Voluntary division moves: Charlotte Independence down from USL
  Championship (2022); North Carolina FC up to Championship (2024);
  Lexington SC up to Championship (2025).
- Departures/folding: Fort Lauderdale CF, New England Revolution II, North
  Texas SC, and Toronto FC II left after 2021 for MLS NEXT Pro; FC Tucson
  after 2022; Central Valley Fuego FC and Northern Colorado Hailstorm FC
  after 2024.

There is no mover population in the pro/rel sense. Thin-team risk is
handled by the pre-registered SHR shrinkage arm, not an X2 offset.

Team identity is stable: there is a perfect 1:1 mapping of team_id to name
and name to team_id over the corpus. Engines key on `team_id` regardless.

The event feed carries no card events in 2021–2025. Stats-feed yellows are
broken in 2021–22, become plausible from 2023, and are therefore valid only
from 2023 when the stats key is present. Shotmap and xG are absent in every
season. Opp-box-touch coverage ramps from 20.2% / 28.8% / 30.5% in 2021–23
to 92.8% in 2024 and 100% in 2025–26.
