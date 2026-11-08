# Phase 1 — Data Understanding: FotMob Azerbaijan Premier League

Corpus: `data_enrichment/fotmob_world/Azerbaijan/Premier League/`, indexed
by league id 262. Inventory is measured by `analysis/eda.py` and stored in
`inventory_summary.json`; the CSV is built by `data/build_data.py`.

## Integrity headline

- 914 index rows, 914 unique finished payloads, and 914 built match rows.
- Season counts are 112, 180, 180, 180, 198, and 64. There are 14 FotMob
  team ids. The only spelling variants are ids 2103, 7981, and 213987.
- Stats, shotmap shots, lineups, playerStats, and named referees are absent
  in all 914 payloads. Events are present in 844; coverageLevel is `lower`
  throughout.

## Payload anatomy

| Section | Use |
|---|---|
| `general` | match id, season, round, date, team ids/names |
| `header.status.scoreStr` | official FT target and finished flag |
| `content.matchFacts.events.events` | goals, Half markers, Red/YellowRed cards |
| `content.stats.Periods` | empty in all payloads |
| `content.shotmap.shots` | empty in all payloads |
| `content.matchFacts.infoBox.Referee` | empty text in all payloads |

## Format and identity

2021/2022 has 8 teams and 28 rounds (112 matches; each pair meets four
times). 2022/2023 through 2024/2025 have 10 teams and 36 rounds (180 each;
four meetings per pair). 2025/2026 has 12 teams and 33 rounds (198; three
meetings per pair), recording the 10-to-12 expansion. 2026/2027 is partial:
rounds 1–11, 64 matches through 2026-11-08; round 2 has four matches and two
fixtures are absent from the index. There is no split group or playoff.

Team identity is keyed by FotMob id. Id 2103 changes from Keshla to Shamakhi
FK; ids 7981 and 213987 have later diacritic spellings Qarabağ and Sumqayıt.
Canonical output names are the most frequent spellings.

## Quirks and events

The official score is the source of truth. Match 4946647 is the one flagged
event/score disagreement; the official score is 0–3 while the event list
contains one home goal. Half markers exist in 844 matches and agree with goal
times through 45 minutes in all 844 checked cases. Overall event counts are
Half 1,688, Goal 2,344, and Card 154. Cards are only Red and YellowRed; plain
Yellow, substitutions, and missed penalties do not occur.
