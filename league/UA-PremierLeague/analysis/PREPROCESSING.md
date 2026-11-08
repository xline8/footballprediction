# Step 2 — Preprocessing: UA-PremierLeague

Builder: `data/build_data.py` (adapted from the RU-PremierLeague
builder; warehouse root = main checkout). Outputs
`data/ua_matches.csv` (1,191 rows) + `data/ua_team_matches.csv`
(2,382 rows), one row per played match, keyed on FotMob team ids.

Rules (frozen):
1. Played matches only — all 1,191 index rows carry a score and
   finished=1; none excluded on that ground.
2. STUB RULE: a stats row is valid only if NOT (total_shots home
   and away, SOT home and away, and corners home and away all
   zero). 22 flagged-stats rows fail this (2021/22: 0, 2022/23: 9,
   2023/24: 6, 2024/25: 6, 2025/26: 1, 2026/27: 0) and are treated
   as stats-missing everywhere (never scored, never update state).
   Valid stats rows: dev scored seasons 462, virgin 223.
3. WAR-ERA / ERA RULE: 2021/2022 is EXCLUDED from every fit, seed
   and scored window (terminated season, pre-invasion, dissolved
   clubs — SA/CN regime-break precedent). It remains in the CSV
   for the record. Fit era = 2022/2023 onward.
4. Cards target = EVENT-UNIFIED yellows (direct Yellow + YellowRed
   counted once as a yellow, per the RU builder convention:
   `ev_yellow_*` = direct + yellowred). The stats-vs-events
   artefact check is degenerate here: the stats feed has NO
   yellow_cards key in any payload, so no stats target exists to
   compare — the event feed is the only possible target, frozen
   here before fitting (same position as RU-1Division).
5. Halves: NO period splits exist. Goal and card 1H counts come
   from event times (time ≤ 45, builder columns ht_*); SOT,
   corners and total shots have NO halves source (no splits, no
   events) and are FT-only by construction.
6. Phase: `regular` for every row (single-group format, Step 1).
7. Season labels as in the warehouse ("2022/2023" style).
