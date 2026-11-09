# Indonesia Liga 2 (FotMob id 10056) — coverage probe, 2026-11-09

**Verdict: genuine FotMob data absence, not a planner bug.** Every
world-pull run planned 0 matches for Liga 2 (`planned Indonesia |
Liga 2: 0`) and no files exist. Probing the league's FotMob entry
directly (via the puller's own client, `api/data/leagues`) shows why:

- `details`: name "Liga 2", `selectedSeason` = `latestSeason` =
  "2026/2027" — the entry exists and is the real league.
- `allAvailableSeasons` = `["2026/2027"]` — the current season only.
  `league_season_params()` therefore correctly returns
  `["2026/2027"]`.
- The `fixtures` object has **no `allMatches` key at all** (only
  `hasOngoingMatch`); `seasons` = `[]`, `playoff` = null,
  `table` = null, `overview.matches` = `{"hasOngoingMatch": false}`,
  `overview.table` = null, `stats` empty. FotMob serves no fixture
  list, table or season archive for this league entry.
- Brute-forcing the season params the planner never tries
  (`2021/2022` … `2025/2026`) changes nothing: FotMob ignores the
  param, snaps `selectedSeason` back to "2026/2027" and still
  returns zero fixtures.

Control case: Indonesia Super League (id 8983, same endpoint, same
planner code) returns 17 seasons in `allAvailableSeasons` and 306
`fixtures.allMatches` for the current season — the endpoint and the
planner work; Liga 2's FotMob entry is simply an empty shell.

Consequence: nothing to pull and nothing to fix in
`pull_fotmob_world.py` for this league. If FotMob later populates
the entry, the normal pull will pick it up unchanged, because
planning reads `allAvailableSeasons` live on every run.
