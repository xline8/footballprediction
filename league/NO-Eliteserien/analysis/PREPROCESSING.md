# Phase 2 — Preprocessing: NO-Eliteserien

Builder: `league/NO-Eliteserien/data/build_data.py` (adapted from the
AT-Bundesliga builder, itself from the J.League pattern in
`league/jleague_lib.py` + `league/build_league_data.py`). It reads
`data_enrichment/fotmob_world_index.csv` filtered to `league_id = 59`
and writes two CSVs (gitignored by repo norm; the builder is the
committed artifact):

- `data/no_matches.csv` — one row per played match (1,407 rows).
- `data/no_team_matches.csv` — the team-match long form (2,814 rows).

## Inclusion rules

1. **Played matches only** — every index row for league 59 is a played
   match with a `scoreStr`; all 1,407 are included. No row is dropped
   for missing secondary feeds; missing data stays missing (NaN) with
   provenance flags — targets are never imputed and absent feeds are
   never read as zeros.
2. **Score of record** = `header.status.scoreStr`. Goal events are
   cross-checked into `ev_goals_*` + `score_events_mismatch` (1
   mismatch — the awarded match, Phase 1 §3.1 — kept, flagged).
3. **Season labels as in the warehouse**: calendar-year strings
   `"2021"` … `"2026"`. `season_start = int(season[:4])`.
4. **Phase**: `regular` for every row (rounds 1–30 only exist in this
   league_id; Phase 1 §1). The column is retained so the CSV shape
   matches the other conveyor leagues.
5. **Period splits only where present**: `fh_*` / `sh_*` stat columns
   come from `Periods.FirstHalf/SecondHalf` and are NaN for
   2021–2022 (splits exist in 1 of 240 matches in 2021, 0 in 2022,
   all from 2023). HT goals come from the event feed (`ht_source =
   "events"` for all 1,407), which exists independently of the stats
   splits. No half quantity is ever derived or fabricated for a match
   whose split feed is absent.
6. **Shotmap aggregates** exclude shootout attempts (none exist);
   `sm_sot` counts on-target, unblocked shots per the J.League rule;
   own-goal crediting follows the builder's `credited_home` rule.
   `sm_xgot` / `sm_xgot_n` carry the raw populated count so era
   guards (F7) can be applied downstream, never silently.
7. **Unified cards target (AMENDED post-build, before any cards
   fitting)**: `yellow_*` = **event-feed** Yellow + YellowRed per side
   (`cards_source = "events"` for every row); `red_*` keeps the
   stats-feed total (reds are never a target). The original rule took
   the stats feed; a per-match audit (Phase 1 §3.5) showed the stats
   feed undercounts yellows in every season of this league (corpus
   4,353 vs 4,625 event yellows; 171/1,407 matches disagree, 156
   stats-low), so the target follows the AR/BR feed-artefact
   precedent: the complete feed wins. Event counts are also kept as
   `ev_yellow_*` / `ev_yellowred_*` / `ev_red_*` columns and the
   stats-feed counts as `yellow_cards_*` cross-check columns. The
   builder's header comment records the amendment; the one stats-
   target cards dev run produced before the audit (single-arm,
   coordinator-reviewed only after the amendment decision was taken
   on the audit numbers) is discarded in full and re-run on the
   corrected target — see PREREG_K_NO's amendment header.
8. **Referee** = `matchFacts.infoBox.Referee.text`, NaN where absent
   (23.7% of 2021; 0% from 2022). Never imputed at build time.
9. **Sorting** is by `(date, match_id)`; kickoff is
   `general.matchTimeUTCDate`. All walk-forward code consumes this
   order and strictly pre-match windows.

## Verification

- Row counts: 1,407 matches / 2,814 team rows == index count for
  league_id 59 (asserted in the builder).
- Match ids unique (asserted). Season counts: 240 × 5 complete
  seasons (2021–2025) + 207 (2026 partial) = 1,407.
- Team-match rows reproduce match totals (goals, SOT, corners,
  yellows) by construction from the same parsed fields.
