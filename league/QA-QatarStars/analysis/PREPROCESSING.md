# Step 2 — Preprocessing: QA-QatarStars

Builder: `data/build_data.py` (adapted from the EC-SerieA builder;
derivation rules unchanged unless QA-forced and noted). Outputs
`data/qa_matches.csv` (714 rows) and `data/qa_team_matches.csv`
(1,428 rows), sorted by (date, match_id). CSV match count == index
count (714); match-id sets are identical to `index_535.csv`. Index
paths are warehouse-relative (`data_enrichment/fotmob_world/...`); the
release tar stores the same files under `data_enrichment/Qatar/...`,
so the builder strips the `data_enrichment/fotmob_world/` prefix.

Rules, as in the reference:
- Missing stays missing (NaN) with provenance flags; targets are never
  imputed; absent feeds are never read as zeros.
- Scores come from the header `scoreStr` (authoritative; event-goal
  counts are a cross-check — 3 mismatches: 4543706 in 2024/2025, a
  duplicated Goal event at 7' vs header 0–1; 5099043 and 5099029 in
  2025/2026, corrupt/flipped goal events vs header 3–0; header kept).
  The 3 mismatched matches are excluded from the halves-goals share
  (their event feeds are corrupt); they are ordinary rows elsewhere.
- HT goals and HT cards from event times, first half = event time ≤ 45
  (FotMob files 45+2' under time 45). A match WITH an events payload and
  no goal/card events gets HT 0–0; a match with an empty events payload
  gets HT missing (`ht_source = none`).
- **Empty-events rule (QA-specific, measured)**: 27 matches have
  `events: []`. They are ALL scoreless (0–0), so no goal information is
  lost, but every events-derived field for these matches is missing,
  never zero. Note the `ev_*` count columns sum to 0 on such matches by
  construction; they are evidence columns, not targets — the EDA treats
  them as missing whenever `has_events` is false.
- **Cards target (QA-forced)**: the unified target is **stats yellows**
  (`yellow_cards_home + yellow_cards_away`), source flag
  `cards_source = stats`; before the stats era (i.e. all of dev)
  yellows are missing. The dev-era event feed carries no plain Yellow
  events at all (only Red / YellowRed), so an event-derived dev target
  would count second yellows only and is rejected pre-fitting. Event
  card counts are kept in `ev_*` columns as evidence of the absence.
  Stats-feed yellow/red are also kept in `stats_yellow_*` /
  `stats_red_*` columns.
- **Phase**: single phase `regular` for every row — `general.leagueName`
  is `Qatar Stars League` in all 714 JSONs. Phases are ordinary rows,
  never dropped.
- **Referee** from `content.matchFacts.infoBox.Referee.text`, empty
  string stored as missing; `has_referee` flags named referees.
- **Team names**: every team id carries exactly one spelling across the
  corpus (verified in the builder; no canonicalisation was needed). All
  logic is keyed by FotMob team id.
- Stats halves come from the feed's FirstHalf/SecondHalf period splits;
  `has_stats_half` flags their presence (132/132 in 2025/2026, 54/54 in
  2026/2027, 0 in dev). The single 2024/2025 stats match (4543697) has
  All only.
- Shotmap aggregates: none — the feed has no shotmap in any match
  (`has_shotmap` false for 714/714).
- Season label is the split-season string (`2021/2022` … `2026/2027`);
  `season_start` is the first year and defines all windows. All windows
  in this build are season-based: dev ≤ 2024/2025, virgin = 2025/2026,
  2026/2027 untouched.

## Spot checks (3 matches verified by hand against raw JSON)

1. **3689099, 2021/2022** (Al-Gharafa 2–0 Al-Shamal, round 1): no stats,
   no referee, no shotmap, no lineup; goal events at 20' and 33'
   (home) → HT 2–0. Score from header 2–0. ✓
2. **4543697, 2024/2025** (Al-Khor 3–0 Umm Salal): the only 2024/2025
   stats match — All period only, total_shots 21–18, corners 8–7,
   yellows 3–4, `cards_source = stats`; goal events at 45' (home),
   58' (home), 90' (home) → HT 1–0 (the 45' goal counts as first
   half). ✓
3. **4821329, 2025/2026** (Al-Rayyan 3–1 Al-Sailiya): full stats era —
   total_shots 18–3, corners 12–0, yellows 2–2, referee Abdulla Ali Al
   Athba Al Marri; goals at 20' (away), 68', 81', 90' (home) → HT
   0–1; no Card events in the payload (2025/2026 events carry no plain
   Yellows). ✓
