# Step 2 — Preprocessing: CH-ChallengeLeague

Builder: `data/build_data.py` (adapted from the program's shared
J.League-pattern builder in the assignment bundle; derivation rules
unchanged unless CH-forced and noted). Outputs `data/ch_matches.csv`
(966 rows) and `data/ch_team_matches.csv` (1,932 rows), sorted by
(date, match_id).

Rules, as in the reference:
- Missing stays missing (NaN) with provenance flags; targets are never
  imputed; absent feeds are never read as zeros.
- Scores come from the header `scoreStr` (authoritative; event-goal
  counts are a cross-check — 2 mismatches in 2024/2025, header kept).
- HT goals from goal events, first half = event time ≤ 45 (FotMob files
  45+2' under time 45). A goalless match WITH an events payload gets
  HT 0–0; a match with an empty events payload gets HT missing.
- **Empty-events rule (CH-specific, measured)**: 47 matches (all 0–0)
  have `events: []`. Their stats-era members provably had cards
  (mean 4.4 stats yellows), so every events-derived field for these
  matches is missing, never zero.
- **Cards target (CH-forced divergence from FI)**: FI used event-derived
  yellows because its stats feed lacked card keys early. CH is the
  mirror image: the event feed lacks cards (0.01–0.16/match) while the
  stats feed carries `yellow_cards`/`red_cards` from 2023/2024. The
  unified CH target is therefore **stats yellows** (`yellow_cards_home +
  yellow_cards_away`), source flag `cards_source = stats`; before
  2023/2024 yellows are missing. Event card counts are kept in `ev_*`
  columns as evidence of the absence, never as a target.
- Stats halves come from the feed's FirstHalf/SecondHalf period splits;
  `has_stats_half` flags their presence (179/181 in the virgin season —
  the 2 rows without splits simply miss halves fields; their All-period
  totals are present and are what the engines score).
- Shotmap aggregates: none — the feed has no shotmap in any match.
- Season label written FotMob-style (`2021/2022`); `season_start` is its
  first year and defines all windows. All windows in this build are
  season-based: dev ≤ 2024/2025, virgin = 2025/2026, 2026/2027 untouched.
