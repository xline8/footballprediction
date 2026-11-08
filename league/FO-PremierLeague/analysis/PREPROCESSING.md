# Phase 2 — Preprocessing

Builder: [`data/build_data.py`](../data/build_data.py). Run from the
worktree with:

```text
python3 league/FO-PremierLeague/data/build_data.py \
  --repo-root /home/hatch/workspace/footballprediction \
  --out league/FO-PremierLeague/data/fo_premier_league_matches.csv
```

The output has 810 source rows plus a header. The 809 rows with
`excluded=0` are the fitting corpus; the one awarded row remains for audit.
The builder asserts 810 index rows, 810 halftime markers, 809 non-awarded
goal-score reconciliations, and played-season counts 135, 134, 135, 135, 135,
135 for 2021–2026.

## Derivation rules

1. Match identity, date, round, team ids, and official score come from the
   index/general payload. Teams are keyed by id; names are canonicalized to
   the most frequent spelling per id.
2. Goal columns record the event-feed played score. This preserves the
   contradiction on match 3822183; that row is flagged `awarded=1,
   excluded=1` and is not fitted.
3. Half-time goals come from the unique time-45 `Half` event's
   `homeScore`/`awayScore`. No halftime split is fabricated.
4. `yellow_*` counts `Card` events with `card=Yellow`; `yellowred_*` counts
   `YellowRed`; `red_*` counts straight `Red` only. Each is assigned by
   `isHome`. `cards_source=events` for every row.
5. Missing feed is not converted to zero. No stats, shot, xG, SOT, or corner
   columns are emitted because those measurements are absent.

The CSV is chronological by date and match id and is deliberately a narrow
match-level table. 2026 is retained for EDA inspection and is the virgin
season, not a fitting season in Phase A.
