# Phase 2 — Preprocessing

Builder: `league/AR-PrimeraBNacional/data/build_data.py`.

1. Read only index rows with league_id `8965`; resolve each JSON through the
   warehouse fallback chain and require the verified 3,966-row inventory.
2. Exclude a match when the Tournament or competition league name contains
   `Playoff` (the bracket-round fallback is retained). Keep all other rows as
   `phase='group'`; do not mix playoff football into league-phase targets.
3. Use header team ids and header scores for home/away identity and full-time
   goals. Canonicalize names by id to the most recent spelling.
4. Derive `ht_hg` and `ht_ag` by counting non-shootout Goal events whose
   integer `time <= 45`. If the event feed is absent, leave both NaN.
5. Derive `ht_yellow_home` and `ht_yellow_away` by counting Yellow Card
   events whose integer `time <= 45`, using the same first-half rule. If the
   event feed is absent, or for 2021–2022, leave both NaN.
6. Derive cards from events only: Yellow is yellow; Red and YellowRed are
   separate columns. For 2021–2022 all six card columns are NaN because the
   target feed is absent, not zero. From 2023 onward zero is a real count.
7. Read referee from `infoBox.Referee.text`; absent text becomes an empty
   string. No referee is imputed.
8. Emit `stats_present=False` and `shotmap_present=False` after asserting
   that no payload has non-empty stats or shots. No stats or shot features are
   fabricated.
9. Emit one team row per side with goals, event-derived halves, cards,
   opponent keys, and referee; retain NaN missingness exactly.
10. Sort both outputs chronologically by `(date, match_id)` (team rows add
   side as a final stable key).
11. Assert index/group/playoff counts, season counts, unique match ids,
    two team rows per match, exact group score/event reconciliation, and zero
    non-empty stats/shotmap payloads.
