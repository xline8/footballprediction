# Step 1 — Data Understanding: SE-Ettan (FotMob id 169)

Source: FotMob world warehouse, `data_enrichment/Sweden/Ettan/<2021 ... 2026>/*.json`
(release `bundle-se-ettan`), index filter league_id = 169 (`index_169.csv`, 2,880 rows).
One row per played match. All numbers measured by `analysis/eda.py`
(`analysis/eda_summary.json`). **Season 2026 is never read in this
analysis** — its rows exist in the built CSVs (program precedent) but
were filtered out at load in `eda.py`; no 2026 raw JSON was opened.
Virgin 2025 appears in the inventory table only; no downstream number
uses it.

## Inventory (played matches only; 2026 excluded)

| Season | Matches | Stats rows | Period splits | Events rows | Lineup (11) | Referee named | Goals/match |
|---|---|---|---|---|---|---|---|
| 2021 | 262 | 0 | 0 | 0 | 0 | 0 | 3.290 |
| 2022 | 480 | 0 | 0 | 480 | 480 | 0 | 3.025 |
| 2023 | 480 | 0 | 0 | 480 | 480 | 0 | 2.875 |
| 2024 | 480 | 0 | 0 | 480 | 480 | 0 | 3.063 |
| 2025 (virgin, inventory only) | 480 | 0 | 0 | 480 | 480 | 0 | 3.198 |

- **Format**: two groups every season — Ettan Norra and Ettan Södra
  (`general.leagueName`, phase `norra` / `sodra`), 16 teams per group,
  30 rounds × 8 matches = 240 matches per group per season, 480 per
  season. No playoffs, no championship/relegation split in this feed:
  every row is an ordinary regular-season row; nothing is dropped.
  Calendar-year seasons. 62 distinct FotMob team ids in 2021–2025
  (66 including the untouched 2026 season). No team switched groups
  between seasons in 2021–2025 (0 group switches).
- **The 2021 anomaly — the index overstates played matches.** The
  index lists 480 rows for 2021, but only **262 were actually played**.
  The other 218 are fixtures that were never started
  (`header.status.finished` false, no `scoreStr`); the index carries a
  placeholder score of `"0-0"` for all 218 of them. Raw JSON is ground
  truth: the 218 are **excluded** from the CSVs, never counted as 0–0
  (see PREPROCESSING.md). Played by group: Norra 145 / unplayed 95,
  Södra 117 / unplayed 123. The gap is heaviest in rounds 1–12 (56
  played of 192 fixtures; Norra 38/96, Södra 18/96) and lighter in
  rounds 13–30 (206 played of 288; Norra 107/144, Södra 99/144) — but
  unplayed fixtures exist in **every** round of both groups, so 2021
  is a partial season, not a truncated one. Played 2021 matches run
  2021-04-02 to 2021-11-21. Consequence: 2021 is a **partial warm-up**
  season for goals (262 matches, no events at all) and contributes
  nothing to any halves constant.
- **Stats feed — absent in every season, not an era break.** `content.stats`
  is null in all 2,880 payloads; the raw scan finds **zero stats keys in
  any period of any season 2021–2025** (the index agrees:
  `has_stats` false on all 2,880 rows). Splits coverage is 0/2,182.
  Consequence, decided in EDA: **no stats target exists in any season**,
  so SOT / corners / total shots / stats yellows have no dev scored
  window at all and are not-buildable (see EDA.md / MODEL_DESIGN.md).
  This is the QA case in its strongest form: in QA the stats era at
  least started in the virgin season; here it never starts.
- **No xG anywhere**: zero `expected_goals*` entries in any payload,
  any season. No shotmap anywhere (`has_shotmap` false for 2,182/2,182
  analysed matches; 0 shotmap matches in the raw scan 2021–2025).
  Goals is a goals-only problem (X1 documented fallback); every
  shotmap/xG arm is impossible by absence and is recorded as such,
  never faked.
- **Event feed — goals yes, and (unlike QA) plain Yellow cards yes.**
  Events exist in 480/480 matches in 2022–2025 and in **0/262 played
  matches in 2021** (no events payload at all that season). Event
  kinds per season 2022–2025: Goal 1,452 / 1,380 / 1,471 / 1,535;
  Substitution 3,421 / 3,563 / 3,744 / 3,774; Card 1,683 / 1,623 /
  1,650 / 1,624; Half 960 every season; MissedPenalty 17 / 23 / 17 /
  18. Card kinds: plain Yellow 1,613 / 1,537 / 1,595 / 1,567,
  YellowRed 37 / 38 / 23 / 24, Red 33 / 48 / 32 / 33. Dev totals
  (2021–2024): plain Yellow 4,745, YellowRed 98, Red 113.
  Event-derived yellows (Yellow + YellowRed) run 3.4375 / 3.2813 /
  3.3708 per match in 2022–2024 (3.3146 in virgin 2025, inventory
  only). This is the one feed fact that keeps K worth a careful
  verdict rather than a one-line dismissal — see EDA.md F5 for why K
  is still not-buildable under the frozen split, and what would have
  to change for Jarvis to revisit it.
- **Target-definition check (score vs events)**: goal events
  reconcile with the header score in all but **1** of 1,920
  event-carrying matches (2022–2025): match **4398485** (2024, Norra,
  AFC Eskilstuna 0–3 Umeå), an **awarded** match — header score 0–3,
  event feed shows 3–1. The header score is authoritative; the match
  is kept as an ordinary row with `awarded=True` and
  `score_events_mismatch=True`, and is excluded from the halves-goals
  share (its event feed is corrupt for that purpose). No other
  mismatch exists in 2021–2025.
- **Lineups**: a `lineup` object is present in 480/480 matches in
  2022–2025 but in only 2/480 raw JSONs in 2021 — and in 2021 neither
  object carries 11 starters, so the builder's 11-starter flag is 0
  in 2021 and 480/season after. Formations are recorded in only 13 of
  2,662 built matches and coach names in 9 — no lineup/formation
  feature is attempted. (`has_player_stats` is false everywhere.)
- **Referee**: `content.matchFacts.infoBox.Referee.text` is empty in
  every analysed match (0% coverage in all seasons 2021–2025; 0
  distinct referees in the raw scan). No referee feature is attempted
  in dev (X8 dropped, FEATURES.md).
- **Team-name stability**: 62 FotMob team ids in 2021–2025; 5 ids
  carry two spellings each and were canonicalised in the build
  (most-common spelling kept): 191433 IF Karlstad Fotboll (75) /
  IF Karlstad (75); 6571 IF Sylvia (79) / Lindoe FF (11); 1011931
  FC Stockholm Internazionale (86) / FC Stockholm (34); 1144284
  Nordic United FC (60) / United IK (30); 1331261 Ariana FC (70) /
  AFC Malmoe (20). All logic is keyed by FotMob team id.
- **Coverage level**: `lower` for all 2,662 built matches.
