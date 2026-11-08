# PA-LPF data understanding

The index has 811 rows: 76 error placeholders (all 2023, with empty index
date/team/score) and 735 playable payloads. By match-id sequence and tournament
totals, the 76 are inferred to be the missing 2023 Apertura 72 regular and 4
final-stage matches. Playable date ranges are 2023-01-14→12-09,
2024-01-20→11-30, 2025-01-18→11-29, and 2026-01-17→11-07.

| season | playable | regular | after awarded | final stage |
|---|---:|---:|---:|---:|
| 2023 | 130 | 120 | 120 | 10 |
| 2024 | 206 | 192 | 191 | 14 |
| 2025 | 206 | 192 | 191 | 14 |
| 2026 | 193 | 186 | 186 | 7 |

Regular tournament counts are 2023 Apertura 24 / Clausura 96; 2024 96/96;
2025 96/96; 2026 Apertura 90 / Clausura 96. A complete tournament is 96
regular plus seven final-stage matches. **Naming flip:** in folders
2023–2025 Apertura runs Jan–May and Clausura Jul–Nov, while in folder
2026 the labels swap (Clausura Jan–May, Apertura Jul–Nov) — verified in
both `general.leagueName` and the infoBox Tournament name. Labels are kept
as labelled; modelling keys on folder season + date, so this is a quirk,
not a defect.

| field | coverage of playable |
|---|---:|
| score | 735/735 |
| stats non-null | 0/735 |
| shotmap non-empty | 0/735 |
| events non-empty | 669/735 |
| referee text | 0/735 |
| real lineups | 0/735 |
| real playerStats | 0/735 |

Payloads use `general` (matchId, leagueId/Name, home/away team id + name),
`header.status` (utcTime, finished, scoreStr, reason, red-card counts) and
`content` (`matchFacts` events + infoBox, `stats` null, `shotmap` with an
empty shot list, `lineup`/`playerStats` empty shells, `table`/`h2h` post-match
snapshots — leakage, never used). Events are
`content.matchFacts.events.events`. Event totals are Goal 1,831, Half 1,346,
Card 214, PenaltyShootout 6. Cards are 159 Red + 55 YellowRed and zero
Yellow. Sixty-six event-empty matches are all 0–0. Goal events agree with
`scoreStr` 733/735; the two mismatches (4399534, 4845610) are awarded 0–3
matches. Reasons are FT 725, Pen 6, AET 2, AW 2; all Pen/AET are final-stage.
`Half` events mark minute 45 (669) and 90 (669), plus 120 (8, extra-time
finals); HT goals derived from Goal events with `time <= 45` (45+stoppage
goals carry `time = 45` with `overloadTime`) agree with the minute-45
`Half` event scoreline in 626/626 cross-checkable CSV rows.

There are 12 ids per tournament. 2025 has 13 across the year: Potros del Este
in Apertura and SD Atletico Nacional in Clausura. Name spelling variants are
therefore keyed by id. No other Panama league id exists in the index, so no
sibling-team history is available. Raw counts are in `inventory_summary.json`.
