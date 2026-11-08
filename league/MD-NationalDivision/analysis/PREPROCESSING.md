# Step 2 — Preprocessing: MD-NationalDivision

## Derivation rules (program standard, none negotiable)

Implemented in `data/build_data.py` (adapted from the
BY-PremierLeague scores-only build):

- FT score from `header.status.scoreStr`.
- Team stats from `content.stats.Periods` (All / FirstHalf /
  SecondHalf where present) — absent in all 556 matches, so every
  stats column is empty (missing, never zero); `has_stats_all` /
  `has_stats_half` are 0 throughout.
- Cards recorded BOTH ways: stats-feed yellows (absent — column
  empty) and event-derived yellows (Card events; Yellow and
  YellowRed count one each). The event feed carries **zero plain
  Yellow events in any season**, so the event-derived columns count
  YellowRed only (corpus total 25) — no target is built from them
  (EDA F5).
- 1H goals / 1H yellows counted from event times (time ≤ 45 incl.
  45+ stoppage). Matches without events get `ht_source=none` and
  NaN halves — never zero.
- Phase from `general.leagueName`: `National Division` → main,
  `Super Liga` → main, `Super Liga Championship Group` →
  championship. All rows kept as ordinary rows.
- Keyed by FotMob team id throughout (two ids have two spellings
  each — diacritic variants; see DATA_UNDERSTANDING.md).
- Awarded matches (10) kept as ordinary rows with the flag; the
  header score is authoritative (0 score-vs-event mismatches in
  the whole corpus, so no conflict arises).

## Verification

- CSV rows 556 == index rows for league_id 231; team rows 1,112.
- Season counts 112 / 86 / 86 / 86 / 114 / 72 match the index and
  the BRIEF.

## Spot checks (3 raw JSONs, by hand)

- 3612634 (2021/2022): CSV 0–1, raw scoreStr `0 - 1`, finished ✓.
- 4235218: CSV 0–1, raw scoreStr `0 - 1`, finished ✓.
- 5952932 (2026/2027): CSV 1–4, raw scoreStr `1 - 4`, finished ✓.
