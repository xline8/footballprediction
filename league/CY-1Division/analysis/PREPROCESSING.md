# Preprocessing

Rows are read from the league-136 FotMob index, sorted by date and match id, and phase is derived from `general.leagueName`. Playoff suffixes are stripped into `championship_playoff` and `relegation_playoff`; regular naming variants are unified. Team ids, not display names, are the stable key.

Goals and event-unified yellows are retained as match and team-side fields. Missing FT stats remain null and are excluded market-by-market. The feed has no usable halves stats. Events supply first-half goal/card counts and the cards target. No model-fitting code is read or used in Phase A.
