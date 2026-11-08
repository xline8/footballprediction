# Step 2 — Preprocessing: RS-SuperLiga

Builder: `data/build_data.py` (adapted from the FI-Veikkausliiga reference builder), output
`data/rs_matches.csv` (1,592 rows = index count, verified in Phase 1) + `data/rs_team_matches.csv`
(3,184 rows). Regenerate: `python3 league/RS-SuperLiga/data/build_data.py` from the workspace root.
This document records the frozen rules; the EDA in `analysis/eda.py` re-derives nothing silently.

Inclusion rules (frozen):
1. Played matches only (`header.status.finished`), league_id 182, seasons 2021/2022–2026/2027
   as labelled in the warehouse. All 1,592 index rows survive into the CSV; the EDA then
   excludes the 2026/2027 reserve season from every computation (see DATA_UNDERSTANDING.md).
2. FT score from `header.status.scoreStr`. Phase from `general.leagueName` + `general.matchRound`:
   regular / championship / relegation / qualification (counts per season in
   DATA_UNDERSTANDING.md). Phase is a flag — except that the design doc excludes the
   cross-tier qualification rows from fitting (MODEL_DESIGN.md); the exclusion is documented
   there and in `eda_summary.json: qualification_matches`, never silent. The awarded match
   4271663 keeps its FT score 0–3 (the authoritative score); its 7 Goal events are NOT used
   to overwrite it.
3. Stats targets (SOT, corners, total shots, possession, touches, fouls, keeper saves) from
   `content.stats.Periods.All`; period-split values from FirstHalf/SecondHalf where they exist
   (virgin only). A match whose stats block is missing — all 1,192 dev matches — gets NULL
   targets and is excluded from that market's scoring. Never imputed, never read as zero.
   The 36 stats keys are enumerated in `inventory_summary.json: by_season.2025/2026.stats_keys_all`.
4. Cards: BOTH feeds are stored. Stats-feed yellows/reds (`stats_yellow_*`, `stats_red_*`)
   exist only in the virgin season. Event-derived yellows (`yellow_*` = Card events with
   `card in {Yellow, YellowRed}`, one each; reds recorded separately as `Red` + `YellowRed`)
   exist nominally in all seasons — but in dev they are YellowRed-only (0.041–0.120/match),
   i.e. the event cards feed is broken before 2025/2026 (DATA_UNDERSTANDING.md). The frozen
   target rule from FI (event-derived unified yellows) is therefore NOT adopted for RS:
   there is no cards target that covers dev and virgin with the same meaning, and K-RS is
   not built (MODEL_DESIGN.md). The stats-vs-events comparison (virgin only) is in EDA.md F6.
5. Halves inputs: 1H goals and 1H yellows counted from event times (`time <= 45` = first half,
   including 45+ stoppage). SOT / corners / total shots halves exist ONLY as virgin period
   splits — there is no dev halves source for them, so their halves shares are null in
   `eda_summary.json: halves_splits_dev` and no constant is frozen for them. The goals halves
   constant comes from dev event times, league-member rows only, excluding the awarded match
   4271663 (`eda_summary.json: halves_goals_dev_league_only`); see EDA.md F3.
6. Team key = FotMob team id (25 ids in dev+virgin, 7 with two diacritic-variant spellings).
   Ordering everywhere is (date, match_id); same-date matches never see each other in any
   walk-forward.
7. Windows frozen pre-fitting: goals warm-up 2021/2022, dev scored 2022/2023–2024/2025,
   virgin 2025/2026 (read once, only for the dev-passing G arm — no other candidate has a
   dev-passing arm). The dev harness never loads virgin rows; the reserve season is never loaded.
   Stats/cards/total-shots markets have NO dev scored window at all (no dev data), so no
   warm-up/dev/virgin protocol exists for them.
8. Missing stays missing (NaN + provenance flag): `ht_source` (`events`/`none`), `cards_source`,
   `has_stats_all` / `has_stats_half` / `has_shotmap` / `has_events` are carried on every row.
   Matches with no events (82 in dev) have `ht_home_goals`/`ht_away_goals`/`goals_1h_total` NULL
   and `ev_yellow_*` = 0 only in the sense that zero Card events were recorded — the EDA treats
   the dev cards feed as absent-by-breakage, not as a measured zero (see EDA.md F6).
