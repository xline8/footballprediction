# Step 2 — Preprocessing: QA-SecondDivision

Builder: `data/build_data.py` → `data/qasd_matches.csv` (141 rows) +
`data/qasd_team_matches.csv` (282 rows). The CSVs are gitignored (`*.csv`
repo norm); the builder regenerates them from the world warehouse.

## Inclusion rules

- **Played matches only**: all 141 index rows are played (`ongoing` false in
  every payload; every row carries a score). No fixture, awarded, or
  abandoned row exists in this corpus; no row is dropped.
- **Phase**: single phase `regular` for every row (see DATA_UNDERSTANDING —
  the `Second Division` leagueName variant is a naming quirk, not a phase).
  No playoff, split, or cup rows exist.
- **Season labels** as in the warehouse: `2024/2025`, `2025/2026`, `2026/2027`.

## Split-source rules

- **Score / date / team names**: authoritative from the index (the
  world-warehouse JSONs carry `general`/`header` as null). Cross-checked
  against the payload: infoBox "Match Date".utcTime agrees with the index
  date in 141/141; lineup team names agree with index team names in 141/141
  (asserted in the builder; mismatch id lists are empty in `eda_summary.json`).
- **Team identity**: FotMob team id from `content.lineup.homeTeam/awayTeam.id`
  (13 ids, one name each — canonicalised, no variants).
- **Goals**: header/index score (event goal counts reconcile in 141/141, so
  no conflict exists to resolve; the score is authoritative by construction).
- **Period splits**: used only where present. Stats splits exist in 123/141
  matches (38 in 2024/2025 rounds 6–14, 56 in 2025/2026, 29 in 2026/2027);
  split-derived columns are missing (never zero) elsewhere. Splits are
  internally consistent (All = FH + SH exactly, 123/123) so no reconciliation
  is needed.
- **1H goals / 1H event-yellows**: from event times (minute ≤ 45). A match
  with an events payload and no goal/card events gets 1H 0; no match in this
  corpus has an empty events payload, so no 1H field is missing for goals.
- **Cards target (unified yellows)**: event-derived, Yellow + YellowRed, for
  every match (`cards_source='events'`). Stats yellows are kept as evidence
  columns (`yellow_cards_*`, `stats_yellow_*`) — they undercount events
  one-directionally (see DATA_UNDERSTANDING) and are never the target.
- **xG / shotmap / touches_opp_box**: absent in every payload; the columns
  exist in the CSV and are null throughout. Nothing is imputed or fabricated.
- **Degenerate keys** (`big_chance`, `shots_inside_box`, `shots_outside_box`):
  carried in the CSV as 0/0; never used as features or targets.
- **Referee**: `content.matchFacts.infoBox.Referee.text`, null unless named
  (1 match in 2026/2027 only).
- **Lineups**: 11-starter lineups present in 141/141; formation + coach kept
  as columns only. No lineup-derived feature is built.

## Windows (frozen; see MODEL_DESIGN.md / prereg for the gate text)

- Goals: warm-up 2024/2025 rounds 1–7 (28 matches, never scored); scored
  2024/2025 rounds 8–14 (28); virgin 2025/2026 complete (56); 2026/2027
  confirmatory, untouched.
- S/C/T/K: warm-up 2025/2026 rounds 1–7 (28 matches, never scored); scored
  2025/2026 rounds 8–14 (28); virgin 2026/2027 partial (29, TRANSITIONAL).
  Fit history for scored matches also includes the 2024/2025 stats-era
  matches (rounds 6–14, 38) — strictly-before-kickoff history, never scored.
