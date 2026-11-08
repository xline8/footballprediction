# Preprocessing — IS-2Deild

`data/build_data.py` filters index league 10226 rows, excludes `error=true` placeholders, and keeps only `header.status.finished == true`. Dates come from the payload's `header.status.utcTime`, falling back to `content.matchFacts.infoBox["Match Date"].utcTime`; the index date is never used. Team ids, never names, are the identity key.

FT goals are the official `scoreStr`. The event cross-check asserts that the count of `Goal` events equals the FT total for every match. HT goals count events with `type == Goal`, `time <= 45`, grouped by `isHome`. The event's `homeScore`/`awayScore` are pre-goal running scores and are not used for HT. Card events are retained only as an artefact count by side. Missing stats, shotmaps, and referee values are represented by the specified structural zeros/empty string; no target or feature is fabricated.

Outputs are 776 match rows and 1,552 team-match rows. The mover JSON derives season membership for 2. Deild and 1. Deild (FotMob 216), then classifies entrant transitions from the previous completed season.
