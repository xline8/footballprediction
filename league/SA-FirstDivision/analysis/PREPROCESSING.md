# Phase A preprocessing — Saudi First Division

- Use `safd_matches.csv` as the match source and `safd_team_matches.csv` as
  the team-match source.
- Exclude `awarded=1` matches from every fit and scored window. Do not replace
  their supplied score with an inferred score.
- Exclude `phase=playoff` from every fit and scored window. This frozen phase
  rule applies to both promotion-playoff semifinals and final.
- Use the season labels exactly as supplied: `2024/2025`, `2025/2026`, and
  `2026/2027`.
- Canonicalise team names by FotMob team id; the id, not the display spelling,
  is the team identity.
- Use period splits only when the corresponding stats period is present.
  Never fabricate missing period values.
- Derive HT goals from goal events with event time <= 45 only when events are
  present; otherwise keep HT goals null and `ht_source=none`.
- The cards target is event-unified yellows: Yellow + YellowRed. Stats-feed
  `yellow_cards` remains a cross-check column, not the target.
- Shotmap columns are explicit empty sentinels: `sm_shots_* = 0` and
  `sm_xg_*` / `sm_xgot_* = null`. No xG value is imputed.
- No fitting, calibration, or 2026/2027 outcome-level computation belongs in
  this Phase A preprocessing step.
