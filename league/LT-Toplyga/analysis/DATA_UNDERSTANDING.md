# Lithuania Toplyga — data understanding

The builder reads the FotMob world warehouse (league id 228) and writes
`data/lt_matches.csv` (1,044 matches) and `data/lt_team_matches.csv` (2,088
team-match rows). All indexed matches are finished and retained.

## Inventory and format

| warehouse season | matches | teams | rounds | matches/round |
|---|---:|---:|---:|---:|
| 2021 | 180 | 10 | 36 | 5 |
| 2022 | 180 | 10 | 36 | 5 |
| 2023 | 180 | 10 | 36 | 5 |
| 2024 | 180 | 10 | 36 | 5 |
| 2025 | 180 | 10 | 36 | 5 |
| 2026 | 144 | 9 | 36 | 4 |

There is one round-robin phase in every season: no split groups and no
playoff matches. The 2026 payloads carry `content.hasPlayoff=false`; the
older 720 payloads carry the generic/null value. Dainava Alytus and Riteriai
are out after 2025; FK TransINVEST is the 2026 entrant. The 2026 season is
complete through 2026-11-08, not partial.

## Payload coverage

The measured coverage matrix is in `inventory_summary.json`. The content
stats block is null in all 1,044 payloads; shotmap shots, lineups and referee
text are absent/empty in all rows; `coverageLevel` is `lower` throughout.
The world-index `has_stats` flag was not used to make these claims.

The brief's claim that events exist in all rows does not reproduce: 954 rows
have a non-empty event list and 90 rows have an empty list. Where present,
events include goals, half markers and red-family cards. Plain Yellow occurs
0 times; YellowRed occurs 69 times and straight Red 101 times. Cards are not
a buildable target.

FT goals are official `header.status.scoreStr`. Goal events agree with that
score in 1,042 rows. The two explicit awarded exceptions are 2023
`4172018` (FA Siauliai–Dziugas Telsiai, official 3–0, events 0–1) and 2024
`4475286` (Dainava Alytus–Suduva, official 0–3, events 1–2). They remain
flagged; their HT fields are blank. Non-awarded rows with empty events also
retain unknown HT rather than fabricated zeros.

Team identity is FotMob team id, never the display name. The full measured
id-to-spelling map is committed in `inventory_summary.json`; multi-spelling
ids include Dziugas/Džiugas Telšiai, FK Panevezys/FK Panevėžys,
Zalgiris/Žalgiris Vilnius, Suduva/Sūduva, FA Siauliai/FA Šiauliai,
FK Kauno Zalgiris/FK Kauno Žalgiris, and Hegelmann/Hegelmann Litauen.
Per-season IN/OUT id turnover is also in that JSON.

## Definition alignment

Goals are the only usable target. FT uses the official score. HT is derived
from credited Goal events with minute ≤45 only when the event list is present;
awarded mismatches are excluded from the HT-derived set. SOT, corners, total
shots, xG, possession, player/lineup features, attendance and referee are
not present. Yellow cards do not exist in this corpus; red-family events are
not a yellow-card substitute or a target.
