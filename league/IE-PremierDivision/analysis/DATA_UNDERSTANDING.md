# Phase 1 — Data Understanding: Ireland Premier Division

Corpus: FotMob league 126, seasons 2021–2026. The complete ledger contains
1,080 built rows, six seasons of 180 matches. The 2026 season ends on
2026-10-30 and is virgin; its only design use is the coverage inventory in
`eda_numbers.json`.

## Format

The round inventory is 36 rounds with 5 matches in every season, and the
phase inventory is `regular` for every row. This is the expected quadruple
round-robin: 10 teams and 180 matches per season. No split or playoff phase
was found.

## Coverage and definitions

The exact per-season coverage counts and dates are in `eda_numbers.json`.
The 2021 feed is sparse for stats; 2022 onward has full All-period match
coverage, with incomplete period splits in 2022 and 2023. Touches coverage
is partial in 2022–2023 and complete from 2024. xG and shotmap-derived xG
fields occur only in the 2025–2026 era. Referee infoBox coverage is complete,
but named referee text is less complete; reliability uses named referees.

FT goals come from `header.status.scoreStr`; first-half goals come from goal
events at time ≤45. SOT, total shots, corners and production covariates come
from `content.stats.Periods`. The target yellow count is event-unified:
Card events with `card` in Yellow or YellowRed, attributed by `isHome`.
Strict Yellow and Red-plus-YellowRed audit counts are also emitted.
