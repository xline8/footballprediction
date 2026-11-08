# CA-PremierLeague preprocessing

`data/build_data.py` writes `ca_matches.csv` and the two-row-per-match `ca_team_matches.csv` (plus a small team-name table). It uses official `scoreStr` for full-time goals; event Goal rows with `time <= 45` for first-half goals. FotMob represents stoppage-time first-half goals as `time=45` plus `overloadTime`, so they are correctly included. Event cards are retained as `ev_yellow`, `ev_yellowred` and `ev_red`; stats cards are retained separately as `stats_yellow` and `stats_red`.

All/FirstHalf/SecondHalf stats are flattened without imputation. Missing stats stay empty. The match table carries phase, inclusion, official and event-goal cross-checks, referee, xG/shotmap presence flags, and raw stat fields. Team-match rows carry goals, SOT, corners, possession, big chances, box touches, shots, cards and referee for/against pairs.

The analysis population is `included == 1` (numeric matchRound regular phase). 2026 may appear in inventory levels only; it is excluded from all trait reliability, halves, expansion, referee-strictness and primary-line calculations. No model, pre-registration, prediction, engine or report artifact is generated in Phase A.
