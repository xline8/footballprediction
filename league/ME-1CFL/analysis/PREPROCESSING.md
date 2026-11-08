# Phase 2 — Preprocessing: From Warehouse JSONs to Analysis Tables

Builder: `data/build_data.py` (adapted from
`league/LT-Toplyga/data/build_data.py` — same payload anatomy, same
rules, different league). Regenerate with:

```
python3 league/ME-1CFL/data/build_data.py --warehouse-root /home/hatch/workspace/footballprediction
```

(The `--warehouse-root` must point at a checkout carrying
`data_enrichment/fotmob_world/`; the 24 GB corpus is gitignored and
is not present in this worktree. Default is the repo root.)

Outputs (in `data/`, gitignored — regenerable; builder + docs are
the committed artifacts):

| File | Rows | Content |
|---|---|---|
| `me_matches.csv` | 971 | one row per played match |
| `me_team_matches.csv` | 1,942 | two rows per match (one per team) |

## Reconciliation (no silent loss)

- Warehouse index rows 972 → played match rows 971. The single
  difference is the never-started ghost fixture 3818692, excluded
  by rule (see rule 8); the builder asserts exactly one exclusion
  with that id.
- Team rows = 2 × matches = 1,942 exactly.
- Row order: chronological by kickoff, then match id.
- Season counts asserted in the builder: 2021/2022: 179,
  2022/2023: 180, 2023/2024: 180, 2024/2025: 179, 2025/2026: 180,
  2026/2027: 73.

## Derivation rules (numbered; the builder implements exactly these)

1. **FT goals** (`home_goals`, `away_goals`) = `header.status.scoreStr`,
   the official score. Never the event feed, never the shotmap
   (neither exists as a source here anyway).
2. **HT goals** (`ht_home_goals`, `ht_away_goals`) = count of
   matchFacts Goal events with `time ≤ 45` by credited side
   (`ht_source='events'`). Stoppage-time goals keep `time = 45`
   in this feed, so the ≤45 rule is exact. Available for 884/971
   matches.
3. **Event-goal cross-check** (`ev_goals_*`, `score_events_mismatch`):
   goal-event counts vs rule 1. Flags exactly 1 played match
   (`4711154`, phantom "<TBD>" goal — Phase 1 §4.2), whose HT
   split is stored as NaN with `ht_source='mismatch_phantom'`.
   The official score is kept. The ghost fixture's mismatch is
   not counted: it is excluded before this rule runs.
4. **Team stats**: none exist. There are no stats columns beyond
   the presence flags (`has_stats_content`, `has_shotmap`,
   `has_lineup`), all 0 on every row. No stat is ever imputed.
5. **Shotmap aggregates**: none — the shots list is empty on every
   row, so no `sm_*` columns are built at all.
6. **Cards, event counts only** (`card_yellow_count`,
   `card_yellowred_count`, `card_red_count`): counts of matchFacts
   Card events by `card` value. Totals over 971 matches: Yellow 0,
   YellowRed 51, Red 74. These are provenance columns, not targets.
7. **Referee** (`referee`): infoBox `Referee.text`, empty string on
   every row.
8. **Exclusion — unplayed matches**: a row is included only if the
   payload is a finished, played match. Exactly one index row fails
   this: 3818692 (`started` False, `finished` False, no `scoreStr`).
   It is excluded, and the builder asserts the exclusion count and
   id. The missing 2024/2025 round-36 fixture (Buducnost vs Decic)
   has no index row at all, so there is nothing to exclude — it is
   simply absent, and the 179 count is asserted, not repaired.
9. **Flags, never silent repairs**: `awarded` (0 matches),
   `score_events_mismatch` (1), plus presence flags `has_events`,
   `has_stats_content`, `has_shotmap`, `has_lineup` — all measured
   by content.
10. **Team identity**: keyed on FotMob team id everywhere. The
    display name in the match table is the name as listed in that
    match; the two two-spelling ids (8100, 8627 — diacritic
    variants in 2026/2027) stay one team.
11. **Season identity**: `season` is the warehouse folder label
    (`2021/2022` … `2026/2027`); sorting is by season start year.
    `2026/2027` is a partial season (data through 2026-11-08,
    rounds 1–15) and is labelled as such in every analysis.
12. **Team-match long table**: one row per team per match with
    venue, goals for/against, HT goals for/against, result/points
    from the official score, and `awarded`.

## Missingness rules (explicit; no imputation anywhere)

- **Targets are never imputed.** FT goals exist for all 971 played
  matches. HT goals are NaN for the 86 event-less matches and the
  1 phantom-HT match — analyses of halves either exclude them (and
  say so) or do not run.
- **Absent feed ≠ zero.** A missing stats block leaves every stat
  column absent (here: the columns do not exist at all). Zero is
  only ever a value the feed itself reported (e.g. a 0-0 score, or
  0 Yellow card events — which is a measured zero of a feed that
  demonstrably carries Red/YellowRed events but no Yellow ones).
- **Partial seasons are data, with flags.** The in-progress
  2026/2027 season (73 rows, round 10 short two fixtures) is
  carried in the tables but reserved as confirmatory; no gate
  reads it.
- **Anomalies are flagged, not fixed** (rules 3 and 9). The phantom
  goal event is preserved in `ev_goals_*` and flagged; only its
  HT derivation is withheld.

## Column dictionary (match table; `_home`/`_away` suffixes throughout)

Identity: `match_id, season, date, kickoff_utc, round, home_team_id,
home_team, away_team_id, away_team, coverage_level`.
Scores: `home_goals, away_goals, ht_home_goals, ht_away_goals,
ht_source, ev_goals_home/away, score_events_mismatch`.
Flags: `awarded, has_events, finished, has_stats_content,
has_shotmap, has_lineup, referee, has_playoff_value`.
Event cards: `card_yellow_count, card_yellowred_count,
card_red_count`.

Team-match table columns: `match_id, season, date, round, team_id,
team, opponent_id, opponent, venue, goals_for, goals_against,
ht_goals_for, ht_goals_against, result, points, awarded`.
