# Cyprus 2. Division — data understanding

Phase A uses the FotMob world index league id 9100 and its local
response store. The builder produces `data/cy2_matches.csv` and
`data/cy2_team_matches.csv` (1,210 rows / 2,420 team rows).

The inventory is 1,210 matches: 240 / 218 / 232 / 232 / 232 / 56 by
season from 2021/2022 through 2026/2027. Format: 16 teams every
season. 2021/2022 is a single double round-robin (240 matches, no
split). From 2022/2023 the season splits after a 15-round single
round-robin (120 matches) into a Promotion Group (top 8, double
round-robin, 56) and a Relegation Group (bottom 8, double
round-robin, 56) — except 2022/2023, whose Relegation Group has only
42 matches: 7 teams, because Alki Oroklinis (id 676004) played the
regular season but no group matches (withdrew / excluded after the
regular season; no group fixture exists for them in the warehouse).
All phases are modelled as ordinary matches, phase flagged, no phase
feature.

The stats feed is ABSENT in all 1,210 payloads: no `Periods` block
at all, in any season. The world-index `has_stats` flag is False for
all 1,210 rows — here the flag happens to be right, but the claim
below is from payload content, not the flag. There is no shotmap, no
lineups, no player stats, and the referee field is empty in all
1,210 payloads. `coverageLevel` is `lower` throughout.

Events are present in 904 payloads and absent in 306: the whole
2021/2022 season has NO events (240), plus 16 / 17 / 11 / 16 / 6
scattered event-less matches in later seasons. Where events exist
they carry goals, Half markers, and red-family cards only — plain
`Yellow` cards NEVER occur (0 in all 1,210 payloads); the only card
events are `YellowRed` (51) and straight `Red` (86). The event feed
therefore omits yellow cards by provider design (same pattern as
J3). Cards are NOT a buildable target in this league.

Score/event agreement is perfect where events exist: 0 mismatches
in 904 event-present matches (goal-event counts reproduce
`scoreStr` exactly). Team identity is stable by FotMob team id
(32 distinct ids); two ids carry two name spellings
(154797: PO Achyronas-Onisilos / Onisilos Sotira; 154791:
Chalkanoras Idaliou / Halkanoras Idaliou) — keying on ids is exact.

Turnover is high: every season 2–3 teams arrive relegated from
CY-1Division, 3–4 leave promoted to it, and 3–4 brand-new ids enter
from outside the two-league warehouse system (see EDA F4).
