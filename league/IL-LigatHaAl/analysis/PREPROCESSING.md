# Step 2 — Preprocessing: IL-LigatHaAl

Builder: `data/build_data.py` (adapted from the EC-SerieA builder;
derivation rules unchanged unless IL-forced and noted). Outputs
`data/il_matches.csv` (1,270 rows) and `data/il_team_matches.csv`
(2,540 rows), sorted by (date, match_id). CSV match count == index count
(1,270); match-id sets are identical to `index_127.csv`.

Rules, as in the reference:
- Missing stays missing (NaN) with provenance flags; targets are never
  imputed; absent feeds are never read as zeros.
- Scores come from the header `scoreStr` (authoritative; event-goal
  counts are a cross-check — 3 mismatches, all awarded wins: 3606698,
  4516796, 4516800; header kept).
- HT goals and HT cards from event times, first half = event time ≤ 45
  (FotMob files 45+2' under time 45). A match WITH an events payload and
  no goal/card events gets HT 0–0; a match with an empty events payload
  gets HT missing (`ht_source = none`).
- **Empty-events rule (IL-specific, measured)**: 57 matches have
  `events: []`. They are mostly but not all scoreless (9 goals across
  them), so every events-derived field for these matches is missing,
  never zero. Note the `ev_*` count columns sum to 0 on such matches by
  construction; they are evidence columns, not targets — the EDA treats
  them as missing whenever `has_events` is false.
- **Cards target (IL-forced)**: the unified target is **stats yellows**
  (`yellow_cards_home + yellow_cards_away`), source flag
  `cards_source = stats`; before the stats era (i.e. all of dev)
  yellows are missing. The dev-era event feed carries no plain Yellow
  events at all (only Red / YellowRed), so an event-derived dev target
  would count second yellows only and is rejected pre-fitting. Event
  card counts are kept in `ev_*` columns as evidence of the absence.
- **Phase** from `general.leagueName` plus `general.matchRound`:
  2021/2022–2024/2025 carry the group in `leagueName` ("Ligat HaAl
  Championship Group" / "Ligat HaAl Relegation Group"); 2025/2026+
  carry it in `matchRound` ("Championship Round - Round 1" /
  "Relegation Round - Round 1") with a plain `leagueName`. Both sources
  are checked, so every full season classifies as regular 182 /
  championship 30 / relegation 28. Phases are ordinary rows, never
  dropped.
- **Awarded matches**: 7 in total (`awarded` flag from
  `header.status.awarded`); their FT score is the awarded score. The
  halves-goals computation in EDA excludes them (their event goals do
  not sum to the awarded FT score).
- **Referee** from `content.matchFacts.infoBox.Referee.text`, empty
  string stored as missing; `has_referee` flags named referees.
- **Team names**: 19 team ids, each with exactly one spelling in the
  corpus — no canonicalisation needed. All logic is keyed by FotMob
  team id.
- Stats halves come from the feed's FirstHalf/SecondHalf period splits;
  `has_stats_half` flags their presence (239/239 in 2025/2026, 69/69 in
  2026/2027, 0 in dev).
- Shotmap aggregates: none — the feed has no shotmap in any match
  (`has_shotmap` false for 1,270/1,270).
- Season label is the split season (`2021/2022` … `2026/2027`);
  `season_start` is its first year and defines all windows. All windows
  in this build are season-based: dev ≤ 2024/2025, virgin = 2025/2026,
  2026/2027 untouched.

## Spot checks (3 matches verified by hand against raw JSON)

1. **3606543, 2021/2022** (Hapoel Haifa 0–0 Maccabi Netanya): empty
   events payload → HT goals missing, `has_events` false, no stats, no
   referee, no shotmap. Score from header 0–0. ✓
2. **1000010981, 2025/2026** (Hapoel Beer Sheva 3–0 Hapoel Petah Tikva,
   Championship Round): full stats era — total_shots 23–6, corners
   11–2, yellows 0–3, stats and event yellows agree exactly (0–3);
   event-time goals give HT 2–0. ✓
3. **4864270, 2025/2026** (Hapoel Jerusalem FC 1–2 FC Ashdod): full
   stats era — total_shots 10–16, corners 3–4, yellows 3–5, stats and
   event yellows agree exactly (3–5); goals → HT 1–0; Yellow events
   at 28' etc. ✓
