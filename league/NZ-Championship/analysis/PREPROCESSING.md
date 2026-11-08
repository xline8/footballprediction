# Preprocessing — NZ-Championship

The builder reads the shared index at
`/home/hatch/workspace/footballprediction/data_enrichment/fotmob_world_index.csv`
(the indexed payload paths resolve from that checkout), filters
league id 8870 and finished, non-cancelled matches, and writes
`nz_matches.csv` (221 rows) plus `nz_team_matches.csv` (442 rows).

1. Inclusion: only matches with `header.status.finished` true and
   not cancelled. Eight 2022 index rows are unfinished scheduled
   fixtures with no `scoreStr` (ids listed in
   DATA_UNDERSTANDING.md) and are excluded; the builder asserts 221
   built rows with seasons 38/46/46/56/35 and unique match ids.
2. 90-minute score: `home_goals` / `away_goals` are Goal events with
   `time <= 90`, credited by `isHome`, when the match has events;
   `header.status.scoreStr` when it has no events (all of 2022 plus
   five scattered matches). The builder asserts the event-derived
   90-minute score equals `scoreStr` for every event-backed match
   EXCEPT the 2024 and 2025 finals (where it is 1-1 against recorded
   1-2 and 2-2), and asserts the all-times event goal count equals
   `scoreStr` for every event-backed match with no exception. Nothing
   is repaired silently.
3. Phase: `final` when `general.leagueRoundName == "final"`,
   otherwise `regular`. Finals remain in the fit/scoring scope at
   their 90-minute score. Only four finals exist in the corpus
   (2022–2025); 2026 has none yet.
4. First-half goals are counted from Goal events with `time <= 45`,
   credited by `isHome`. If the event list is empty, both HT fields
   are missing and `ht_source=none`; no imputation is performed.
5. The event card field is deliberately named `ev_red_home/away`: it
   counts Red and YellowRed events together. There are no plain
   Yellow events in this corpus, so no yellow target is created.
6. `has_extra_time` is 1 when any Goal event has `time > 90` or a
   PenaltyShootout event exists (exactly the 2024 and 2025 finals).
7. Stats, period splits, shotmaps/xG and referee names are absent
   (or, for shotmaps, present-but-empty) in every payload. Structural
   `sm_*` zeros are retained only as coverage markers and are never
   treated as observations. `referee` is always "".
8. Team identity is always keyed by FotMob team ID; display names
   are retained as published (613344 appears as both "Eastern
   Suburbs" and "Eastern Suburbs AFC").
