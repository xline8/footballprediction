# Preprocessing and source rules

`data/build_data.py` reads the worktree index and resolves the JSON warehouse
with the same explicit/local/main-checkout fallback used by the parent
Liga Portugal builder. It writes one row per finished match to
`data/pt2_matches.csv` and asserts 1,619 rows.

## Inclusion and source rules

- Include only index rows for FotMob league 185 whose header status is
  `finished`; sort by date and match ID.
- Use header team IDs/names and full-time scores. Team identity is always the
  ID.
- Recover `ht_home`/`ht_away` only from usable goal events; otherwise leave
  them blank. No half-time score is inferred from a season average.
- Keep stats-feed SOT, corners, total shots, and stats yellows in separate
  columns. A missing source remains blank. The builder never replaces a
  missing stats yellow with event yellows.
- Count event yellows separately from the event list (`type=Card` and
  `card=Yellow`). `has_card_event` records any Card event, including red and
  yellow-red events.
- Preserve `has_stats`, `has_shotmap`, `has_period_splits`, xG-key presence,
  lineup presence, shot count, referee text, and both yellow sources as
  coverage fields.

## Cards source-quality check, before any virgin read

There are 393 matches across the corpus with both a stats block and at least
one Card event; the requested 2025/2026 overlap is 303 matches (306 stats
matches, 303 with a Card event). However, the stats feed has no
`yellow_cards` key in any match: stats-yellow availability is 0/1,619,
including 0/303 in that 2025/2026 overlap. Consequently the comparable
sample is n=0 and the exact-agreement rate, mean
`stats_yellows - event_yellows`, and the number disagreeing at the 4.5 line
are all **not estimable**, rather than zero. This rules out a stats-vs-events
validation decision and leaves cards event-sourced only.

In 2026/2027, 17/89 matches have at least one Card event. This is an event
coverage observation only; that season is reserved as confirmatory and is
not used in any fitting.
