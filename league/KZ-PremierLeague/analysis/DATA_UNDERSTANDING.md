# Data understanding — Kazakhstan Premier League (FotMob 225)

The warehouse contains 1,124 Premier League payloads in calendar-year
seasons 2021–2026. The inventory is payload-derived in
[inventory_summary.json](inventory_summary.json); the analysis CSV is
built by [../data/build_data.py](../data/build_data.py). All 1,124
payloads are finished (`header.status.finished == true`); the finished
filter drops nothing. Header team scores match the index score in all
1,124 payloads. Goal events total 2,872, matching the index-goal total
exactly once the 4 score/event mismatches below are accounted for.

`content.stats` is empty in every season (`Periods` has no keys),
shotmaps are empty, period splits are absent, and lineup coverage is
zero in every season in the starter sense: 81 payloads carry a
non-empty `lineup` dict, but it contains only `unavailable` / injury
lists, never starters or formations. `playerStats` is absent in all
1,124 payloads. Events are present for 1,058/1,124 payloads (66 empty:
12, 10, 10, 11, 13, 10 across 2021–2026). The only event types are
Goal, Half, and Card. Cards are Red and YellowRed only; plain Yellow
is zero in every season (dev: Red 127, YellowRed 68, Yellow 0).
Referee text is not populated in these payloads (0/1,124 named),
despite the `infoBox.Referee` key being present.

## Format

Calendar-year seasons, March–October/November, single round-robin
table, no split group and no playoff phase: rounds run 1–26 in
2021–2025 (7 matches per round; 2024 has 13 teams, 6 matches per
round plus one bye) and 1–30 in 2026 (8 matches per round). Team
counts by FotMob id are 14, 14, 14, 13, 14, 16; every team plays a
balanced schedule (26 matches, 24 in 2024, 30 in 2026). The
`hasPlayoff` schema key is `False` in all 2025 and 2026 payloads and
absent earlier — there is no playoff to model. 2026 is complete
(Mar 7 – Oct 31, 240/240 matches), so it is the virgin window, not a
transitional one.

FotMob IDs are the team key. Two ids carry two name spellings:
200279 Kaspyi Aktau / Kaspiy Aktau (2 + 106 matches) and 732295
Altai Semey / FC Altai Oskemen (25 + 5; the 2026 entrant under the new
name). They are canonicalised to one id each; they are not separate
clubs. 22 team ids appear in total.

## Score / event agreement

Goal-event counts reproduce the official `scoreStr` in 1,054 of the
1,058 event-bearing matches. The 4 mismatches are flagged, never
silently repaired, and the official score is kept in every case:

| match_id | season | official | events say | note |
|---|---|---|---|---|
| 3829884 | 2022 | 0–3 | 0–0 | awarded |
| 4115095 | 2023 | 3–0 | 2–1 | awarded |
| 4735506 | 2025 | 3–0 | 1–2 | awarded |
| 4430676 | 2024 | 2–2 | 3–2 | not awarded; one extra home goal in the feed (disallowed goal left in, same pattern as J1 3520767) |

## Half-time derivation

No explicit HT score field exists. HT goals are derived from goal
events with `time ≤ 45` by credited side. The derivation is
cross-validated against the `Half` events' own HT home/away scores:
agreement **1,040 / 1,040** matches where both exist. HT is therefore
available for all 1,058 event-bearing matches and missing (NaN) for
the 66 event-less ones.
