# Step 2 — Preprocessing: EC-SerieA

Builder: `data/build_data.py` (adapted from the CH-ChallengeLeague builder;
derivation rules unchanged unless EC-forced and noted). Outputs
`data/ec_matches.csv` (1,565 rows) and `data/ec_team_matches.csv`
(3,130 rows), sorted by (date, match_id). CSV match count == index count
(1,565); match-id sets are identical to `index_246.csv`.

Rules, as in the reference:
- Missing stays missing (NaN) with provenance flags; targets are never
  imputed; absent feeds are never read as zeros.
- Scores come from the header `scoreStr` (authoritative; event-goal
  counts are a cross-check — 2 mismatches, 3528060 in 2021 and 3816510
  in 2022, both header 3–0 vs events 2–0, header kept).
- HT goals and HT cards from event times, first half = event time ≤ 45
  (FotMob files 45+2' under time 45). A match WITH an events payload and
  no goal/card events gets HT 0–0; a match with an empty events payload
  gets HT missing (`ht_source = none`).
- **Empty-events rule (EC-specific, measured)**: 67 matches have
  `events: []`. They are mostly but not all scoreless (6 goals across
  them), so every events-derived field for these matches is missing,
  never zero. Note the `ev_*` count columns sum to 0 on such matches by
  construction; they are evidence columns, not targets — the EDA treats
  them as missing whenever `has_events` is false.
- **Cards target (EC-forced)**: the unified target is **stats yellows**
  (`yellow_cards_home + yellow_cards_away`), source flag
  `cards_source = stats`; before the stats era (i.e. all of dev)
  yellows are missing. The dev-era event feed carries no plain Yellow
  events at all (only Red / YellowRed), so an event-derived dev target
  would count second yellows only and is rejected pre-fitting. Event
  card counts are kept in `ev_*` columns as evidence of the absence.
- **Phase** from `general.leagueName`: `first_stage` / `second_stage` /
  `final_stage` / `other` (2025–2026 `Serie A` / `Ecuador Liga Pro`).
  Phases are ordinary rows, never dropped.
- **Referee** from `content.matchFacts.infoBox.Referee.text`, empty
  string stored as missing; `has_referee` flags named referees.
- **Team names**: 4 team ids carry accent-variant spellings; the builder
  canonicalises each id to its most frequent spelling (see
  DATA_UNDERSTANDING.md). All logic is keyed by FotMob team id.
- Stats halves come from the feed's FirstHalf/SecondHalf period splits;
  `has_stats_half` flags their presence (311/311 in 2025, 285/285 in
  2026, 0 in dev). The single 2024 stats match (4412193) has All only.
- Shotmap aggregates: none — the feed has no shotmap in any match
  (`has_shotmap` false for 1,565/1,565).
- Season label is the calendar year (`2021` … `2026`); `season_start`
  is that year and defines all windows. All windows in this build are
  season-based: dev ≤ 2024, virgin = 2025, 2026 untouched.

## Spot checks (3 matches verified by hand against raw JSON)

1. **3528006, 2021** (Universidad Catolica 3–0 Olmedo, First Stage):
   empty events payload → HT goals missing, `has_events` false,
   no stats, no referee, no shotmap. Score from header 3–0. ✓
2. **4412193, 2024** (El Nacional 2–1 Tecnico Universitario, Second
   Stage): the only 2024 stats match — All period only, total_shots
   14–18, corners 5–4, yellows 6–1, `cards_source = stats`; goal
   events at 22' (home), 45' (away), 53' (home) → HT 1–1 (the 45'
   goal counts as first half). ✓
3. **4720459, 2025** (Manta 2–3 Barcelona SC): full stats era —
   total_shots 7–22, corners 3–8, yellows 1–4, stats and event yellows
   agree exactly (1–4); goals at 3', 14', 49', 85', 90' → HT 1–1;
   Yellow events at 28' (away) → HT yellows 0–1. ✓
