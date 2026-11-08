# Step 2 — Preprocessing: SE-Superettan

Builder: `data/build_data.py` (adapted from the SE-Allsvenskan builder), output
`data/se2_matches.csv` (1,440 rows, gitignored, reproducible) + `se2_team_matches.csv`.

Inclusion rules (frozen):
1. Played matches only (`header.status.finished`), league_id 168, seasons 2021–2026
   as labelled in the warehouse. All 1,440 index rows survive (240 x 6).
2. FT score from `header.status.scoreStr`. Phase = "regular" for every row
   (phase rule in DATA_UNDERSTANDING: the feed contains no play-off rows).
3. Stats targets (SOT, corners, total shots, possession) from
   `content.stats.Periods.All` only — the sole period that exists. A match whose
   stats block is missing/empty gets NULL targets and is excluded from that
   market's scoring (never imputed, never fabricated).
4. Cards target = event-derived unified yellows: Card events with
   `card in {Yellow, YellowRed}` per side (a YellowRed contributes one yellow);
   reds recorded separately (`Red` + `YellowRed`) and are not part of the target.
   Available for all 1,440 matches.
5. Halves inputs: 1H goals and 1H yellows counted from event times
   (`time <= 45` = first half, including 45+ stoppage, which FotMob reports as
   time 45 with overload). No other market has a halves source; nothing is
   fabricated from FT totals.
6. Team key = FotMob team id (names vary for id 8482). Ordering everywhere is
   (date, match_id); same-date matches never see each other in any walk-forward.
7. Windows frozen pre-fitting: goals/cards warm-up 2021, dev scored 2022–2025,
   virgin 2026; stats markets warm-up 2022, dev scored 2023–2025, virgin 2026.
   The dev harness never loads virgin rows; the virgin is read once, only for
   dev-passing arms.
