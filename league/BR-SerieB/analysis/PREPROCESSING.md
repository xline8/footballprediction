# Phase 2 — Preprocessing: Série B analysis tables

`data/build_data.py` includes every finished index row for league 8814 and
produces 2,270 match rows plus 4,540 team-match rows. It uses FT scores from
`header.status.scoreStr`, first-half goals from events at `time <= 45`, and
stats-period values without filling missing values.

All/FirstHalf/SecondHalf columns are retained for the standard stat keys.
`has_stats_half` is a real-feed flag. Shotmap aggregates are regulation shots
only and include `sm_shots`, `sm_sot`, `sm_xg`, `sm_xgot`, population counts,
and first-half shot counts. These columns are intentionally empty before the
2025 shotmap era. Referee text is retained as-is.

Cards use `yellow_unified_*`: stats-feed yellow cards from 2023 onward and
`None` before 2023, with `yellow_unified_source` documenting the rule. This is
not an imputation. Cards scoring uses only the valid target window (warm-up
2023, scored 2024, n=380, virgin 2025). Missing target rows are excluded from
that market only. The same per-market missingness rule applies to xG-derived
arms.
