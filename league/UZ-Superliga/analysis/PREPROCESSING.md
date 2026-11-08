# Phase 2 — Preprocessing: Uzbekistan Superliga (FotMob 540)

## Builder

`league/UZ-Superliga/data/build_data.py` regenerates
`data/uz_superliga_matches.csv` (gitignored by repo norm; the builder is
committed). It reads the world index (`league_id = 540`), parses each
payload, and asserts:

- `header.status.finished` is True (215/215);
- index `score` equals `header.teams[0].score`-`header.teams[1].score`
  (215/215 exact);
- exactly 215 rows (fails loudly if the warehouse changes).

Run `python3 league/UZ-Superliga/data/build_data.py --verify` to re-print
payload coverage and the round table.

## Inclusion rules

- Played matches only: all 215 index rows are finished matches with
  scores, so 215/215 are included. No exclusions.
- Season label as in the warehouse: `2026`.
- One row per match: `match_id, date, round, home, away, home_goals,
  away_goals, total_goals, result, home_goals_ht, away_goals_ht`.

## Split-source rules

- FT score: `header.teams` scores (cross-checked against the index).
- HT score: derived from the `matchFacts` Half event at minute 45,
  validated per match (exactly one HT Half event, 0 ≤ HT ≤ FT, Goal-event
  count == FT goal total). Present in 99/215 matches; blank elsewhere.
  **Never fabricated**: matches without the event carry blank HT columns.
- No other splits exist: no stats, no shotmap, no lineups, no referee.
  Nothing is imputed, interpolated, or borrowed from another league.

## Known gaps (carried, not repaired)

- Round 26 missing fixture: Bunyodkor Tashkent vs Neftchi Fargona (not
  in the warehouse; presumed postponed). Bunyodkor and Neftchi each have
  26 matches; the other 14 teams have 27.
- Rounds 28–30 (~25 matches) not yet played at the warehouse snapshot
  (last date 2026-11-08). The 2026 season is incomplete: 215/240.
- HT scores missing for 116/215 matches (no event feed before round 14,
  except one match in round 10).
