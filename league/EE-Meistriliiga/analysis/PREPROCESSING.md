# Preprocessing — EE-Meistriliiga

`data/build_data.py` reads only index rows with `league_id == 248`, loads the
referenced JSON, and includes a row only when `header.status.finished` is true
and `scoreStr` parses to two integers. The audit asserts 1,056/1,056 rows pass.

Home and away ids from `general.homeTeam.id` and `general.awayTeam.id` are the
join keys. Names are descriptive source fields only; Nõmme/Nomme, Pärnu/Parnu
and Tallinna/Tallinna spellings are not merged by string replacement.

The FT score is the target source of record. Result is H/D/A from that score.
Goal-minute lists are copied from Goal events when a minute exists. Cards are
event-derived: `card == Yellow` populates yellow columns; `Red` and `YellowRed`
populate red columns, split by `isHome`. This is not a stats-feed measure.

The card feed is materially incomplete: 34, 41, 49 and 44 card events in
2021–2024, with no yellow events, versus 761 and 800 events in 2025–2026.
Accordingly, pre-2025 yellow values are zeros from missing feed content, not
fabricated no-card observations, and cards are not modelled. No half-time
values or constants are fabricated because no period splits exist.
