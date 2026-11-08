# Phase 2 — Preprocessing: ES-PrimeraFederacion

Builder: `league/ES-PrimeraFederacion/data/build_data.py` (reads the
FotMob world warehouse in the main checkout — the JSONs are
git-ignored, so the worktree has no `fotmob_world/` dir; same
`MAIN_REPO` pattern as `league/ES-LaLiga2/data/build_data.py`).
Outputs (gitignored `*.csv`, regenerable): `data/espf_matches.csv`
(4,081 rows) and `data/espf_team_matches.csv` (8,162 rows).

## Inclusion rules

1. **Played matches only.** All 4,081 index rows are finished
   matches; 0 cancelled, 0 unplayed. Every row is included.
2. **Score** from `header.status.scoreStr` (asserted parseable on
   every row). No other score source exists.
3. **Play-off matches are ordinary rows** (`phase='playoff'`,
   rounds `1/2` / `final`); no phase feature is used anywhere. The
   9 extra-time play-off scores are used as-is (DATA_UNDERSTANDING
   §3); the 17 awarded scores are used as-is.
4. **No imputation, ever.** Where a quantity does not exist (all
   stats, all shotmap, referee names), the column is absent or 0 by
   construction — never filled from another season, league, or
   model. The CSV carries only what the payloads contain: scores,
   event-feed goals/cards, group labels, flags.
5. **First-half goals from events.** `ht_home_goals` /
   `ht_away_goals` count Goal events with `time <= 45` per side.
   `goal_events_complete` flags whether the Goal-event count equals
   the score total (4,065/4,081 = 99.6%; the 16 exceptions are the
   awarded 2021/2022 matches, whose HT goals are 0 by construction
   and excluded from the halves-constant estimation). Zero-event
   matches are all 0–0, so their HT goals are genuinely 0.
6. **Cards from events only, for evidence.** `ev_yellow_*` /
   `ev_yellowred_*` / `ev_red_*` count Card events by `card` field
   and side. They are recorded to prove cards are not buildable
   (995 events total); no cards target is derived from them.
7. **Groups from the fixture graph.** Per season, the regular-season
   (rounds 1–38) fixture graph is split into its two 20-team
   connected components; components are labelled 1/2 deterministically
   (alphabetically-first team name in the component). Every match
   carries `group_home` / `group_away` (each side's own regular-season
   group; play-off matches are therefore usually cross-group).
   Assertions: components exactly [20, 20] every season; zero
   cross-group regular matches.
8. **Season labels as in the warehouse** (`2021/2022` … `2026/2027`).
   2026/2027 is partial (rounds 1–11, 220 matches) and is never used
   in dev or virgin fitting.
9. **Team identity is FotMob team_id everywhere.** Names are display
   only (14 ids carry multiple spellings; see DATA_UNDERSTANDING §1).
   The one name-keyed operation in the program (X2 mover membership
   in EDA) uses accent-normalised names and was verified to match
   the id-keyed lists exactly; the engine itself keys movers on
   team_id (MODEL_DESIGN §2).
10. **Flags are measured from payloads, not from the index.**
    `has_stats_all` / `has_stats_half` / `has_shotmap` are set from
    `content.stats.Periods` / `content.shotmap.shots` in each JSON
    (all 0 — verified, not assumed). `referee` is the infoBox
    Referee text (empty in 4,081/4,081).

## Builder assertions (fail loudly)

- 4,081 index rows; 4,081 output rows; unique match_ids.
- Per-season counts exactly {2021/2022: 767, 2022/2023: 774,
  2023/2024: 774, 2024/2025: 774, 2025/2026: 772, 2026/2027: 220}.
- Every row finished, not cancelled; every score parses.
- Group components exactly [20, 20] per season.
- `has_stats_all` and `has_shotmap` sums are 0.
