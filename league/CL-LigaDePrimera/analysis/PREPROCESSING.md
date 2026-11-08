# Step 2 — Preprocessing — CL-LigaDePrimera

Builder: `data/build_data.py` (committed; regenerates both CSVs from
the warehouse index + JSONs). Outputs (gitignored by repo norm):
`data/cl_matches.csv` (1,448 rows) and `data/cl_team_matches.csv`
(2,896 rows).

Rules:
1. Inclusion: index rows with `league_id = 273` whose payload is a
   finished match; all 1,448 index rows qualify. Played matches
   only — no fixture without a score enters.
2. Scores from `header.status.scoreStr`; HT goals counted from
   goal events (`time <= 45`), `ht_source = events`.
3. Teams keyed by FotMob team id; display name canonicalised to the
   last-seen spelling per id (four multi-spelling ids, listed in
   DATA_UNDERSTANDING). Raw spellings retained in
   `home_team_raw`/`away_team_raw`.
4. `phase = regular` for every row (format finding, Step 1).
5. Stats flattened from `content.stats.Periods` for All / FirstHalf
   (`fh_`) / SecondHalf (`sh_`) where present; never fabricated —
   2021–2022 half columns are null because the feed has no splits
   there, and the 60 split-less 2023 matches stay null.
6. Cards: both provenances stored — stats `yellow_cards_*` and
   event counts `ev_yellow_*` (direct + YellowRed). The modelling
   target is the event-unified count (artefact, Step 1); the RU-1
   builder's stats-first fallback is **disabled** here: `yellow_*`
   in this league's CSV is set from events on every row and
   `cards_source = events` throughout (the builder patch is in the
   committed script's league adaptation — stats yellows remain
   available as `yellow_cards_*`).
7. Referee from `infoBox.Referee.text`, empty string where absent.
8. Shotmap columns exist for schema parity and are null throughout
   (no shotmap exists in this league).
