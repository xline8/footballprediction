# Cyprus 2. Division — preprocessing

Builder: `data/build_data.py` (warehouse root defaults to the main
checkout `~/workspace/footballprediction`, which holds the
untracked `data_enrichment/fotmob_world/` store; worktrees do not
carry it). Regenerate with:

```
python3 league/CY-2Division/data/build_data.py
```

Outputs (in `data/`, gitignored — builder + docs are the committed
artifacts):

| File | Rows | Content |
|---|---|---|
| `cy2_matches.csv` | 1,210 | one row per played match |
| `cy2_team_matches.csv` | 2,420 | two rows per match (one per team) |

## Reconciliation (no silent loss)

- Warehouse index rows for league 9100: 1,210 → match rows 1,210,
  asserted in the builder; match ids unique; phase counts asserted
  per season (240; 120/56/42; 120/56/56 ×3; 56).
- Team rows = 2 × matches = 2,420 exactly.
- Row order: chronological by kickoff date, then match id.

## Derivation rules

1. **FT goals** (`home_goals`, `away_goals`) = `header.status.scoreStr`,
   the official score. Never the event feed.
2. **HT goals** (`ht_home_goals`, `ht_away_goals`) = count of
   matchFacts Goal events with `time ≤ 45` by credited side
   (`ht_source='events'`). Matches without events (306, incl. all of
   2021/2022) get blank + `ht_source='none'` — HT is unknown, never 0.
3. **Event-goal cross-check** (`ev_goals_*`,
   `score_events_mismatch`): goal-event counts vs rule 1. Flags 0
   matches — perfect agreement where events exist.
4. **Cards, event-only** (`ev_yellow_*`, `ev_red_*`, `yellow_*`,
   `red_*`, `cards_source='events'`): direct Yellow + YellowRed for
   yellows (direct Yellow = 0 everywhere — the feed omits plain
   yellows); straight Red + YellowRed for reds. The `yellow_*`
   column therefore counts second-yellow dismissals only and is
   NOT a yellow-cards target; it is carried for provenance only.
5. **No stats columns exist.** There is no stats feed to flatten:
   no SOT, corners, total shots, xG, possession, or period splits
   in any season. The CSV carries presence flags only
   (`has_stats_all` = 0 everywhere).
6. **Flags, never silent repairs**: `has_events`, `has_stats_flag`
   (index flag, 0 everywhere), `has_period_splits_content`,
   `has_shotmap`, `has_lineup` — all 0 except `has_events`.
7. **Team identity**: keyed on FotMob team id everywhere. The two
   two-spelling ids stay one team.
8. **Season identity**: `season` is the warehouse folder label
   (`2021/2022`…`2026/2027`); `2026/2027` is a partial season
   (56 matches so far, regular phase only) and is labelled as such
   in every analysis.

## Missingness rules (explicit; no imputation anywhere)

- **Targets are never imputed.** FT goals exist for all 1,210
  matches. HT goals are blank for the 306 event-less matches.
- **Absent feed ≠ zero.** A missing stats block leaves no stat
  columns at all; a missing event feed leaves HT blank and card
  counts at their observed (zero-event) values, with `has_events`
  = 0 marking them as unobserved.
- **Anomalies are flagged, not fixed**: the 2022/2023 Relegation
  Group's 7-team shape (Alki Oroklinis absent) is a format fact,
  preserved as-is.
