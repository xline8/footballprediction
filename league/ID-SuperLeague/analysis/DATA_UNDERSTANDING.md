# Step 1 — Data understanding: Indonesia Super League (FotMob 8983)

All numbers below were measured from the payload content of the 1,620
warehouse JSONs for league_id 8983, not from the index flags. The index
flags lie for this league in both directions (see §4).

## 1. Corpus and format

- 1,620 finished matches, seasons 2021/2022–2026/2027 (index labels).
  306 matches in each completed season, 80 so far in 2026/2027, plus 2
  stray rows the index labels "2021/2023" (§3).
- 18 teams per season, double round-robin = 306 regular matches.
  Split-year seasons, roughly August–May. The league was Liga 1 and
  was renamed Super League for 2025/2026; the FotMob league id (8983)
  and team ids are continuous across the rename.
- 2021/2022 was played largely as a centralised Bali bubble series
  (COVID): home advantage that season is absent (home goals 1.176 vs
  away 1.235 per match; §EDA). This is a format fact, not a data error.
- 2023/2024 used a championship series after the regular season: the
  top 4 played two-legged semi-finals, a final and a 3rd-place tie
  (8 matches, 14–31 May 2024, Bali United / Persib Bandung / Madura
  United / Borneo Samarinda). These 8 payloads are exactly the ones
  with `content.hasPlayoff == True`. They are knockout ties — a
  different population — and are excluded from all modelling.
- 2026/2027 is in progress (80 finished, Sep–Nov 2026 at snapshot).

## 2. Field coverage, measured from payloads

Score: present in all 1,620 (header.status.scoreStr).

Stats feed (`content.stats.Periods`): only period `All` ever exists —
there are no FirstHalf/SecondHalf splits anywhere. When present, the
`All` block carries exactly four keys with content: `BallPossesion`,
`total_shots`, `ShotsOnTarget`, `corners`. There is no
`expected_goals`, no `fouls`, no `yellow_cards`/`red_cards`, no
`touches_opp_box`, no `big_chance` in any payload. Coverage by season
(regular + playoff rows as indexed):

| season | stats rows | window |
|---|---|---|
| 2021/2022 | 140/306 | only from 2022-01-13 |
| 2022/2023 | 306/306 | complete |
| 2023/2024 | 153/314 | only until 2023-10-30 |
| 2024/2025 | 8/306 | scattered Jan–May 2025 |
| 2025/2026 | 0/306 | — |
| 2026/2027 | 0/80 | — |

Shotmap: the key exists in every payload but the shots list is empty
in all 1,620. xG does not exist in this league's data in any form.

Events (`content.matchFacts.events.events`): types seen are Goal,
Card (Yellow / YellowRed / Red), Substitution, Half, MissedPenalty,
PenaltyShootout. Goal events reconcile exactly with the score in
1,618/1,620 matches; the two exceptions are stated in §4. The event
feed is however truncated for part of the corpus: some matches carry
only Goal/Half events (no substitutions, no cards), which marks a
truncated feed — substitutions occur in effectively every real match.
We flag `events_complete` = feed contains both Substitution and Half
events. Completeness (regular season): 2021/2022 267/306, 2022/2023
306/306, 2023/2024 144/306 (the truncated block is the same era in
which the stats feed also died), 2024/2025 281/306, 2025/2026 306/306,
2026/2027 72/80.

Referee: `content.matchFacts.infoBox.Referee` exists in all 1,620
payloads but its `text` field is empty in all 1,620. There is no
referee identity in this league's data.

Lineups: present (index flag true for most rows); not used by any
adopted feature (see FEATURES.md R-items).

## 3. The stray "2021/2023" rows

Index rows 4183841 / 4183842 (Bali United vs PSM Makassar, 6 and 10
June 2023, both 1-1) are a two-legged playoff between the champions of
2021/2022 and 2022/2023 for an AFC slot. They belong to no league
season. Flagged `stray_playoff` and excluded; the builder stores them
under season 2022/2023 with `season_label_raw = "2021/2023"` retained.

## 4. Defects and flag lies, stated plainly

1. **Index `has_stats` is unreliable here.** It totals 609 for this
   league; the content-measured total is 607 + the pattern matters
   more than the count: the flag does not tell you the era ends in
   October 2023, nor that 2024/2025 has only 8 rows, nor that the
   virgin season has none.
2. **2023/2024 `total_shots` is corrupted.** In every 2023/2024 stats
   payload, `total_shots` equals `ShotsOnTarget` exactly (100% of
   rows, corr 1.0; verified in raw JSON, e.g. both fields 6/3 in the
   same match). The values are on the SOT scale (~9 per match, vs
   17–19 for true total shots in 2021/2022–2022/2023), so the
   total-shots field was overwritten by the SOT values. 2023/2024
   total shots are unusable as total shots.
3. **Two matches have broken event feeds.** Match 3764008
   (Persikabo 1973 vs Persebaya, 2022-01-10): event goals 4-4 vs
   score 2-3. Match 3798327 (Persipura vs Madura United, 2022-02-21):
   no events at all. Both are excluded from event-derived measurement
   by the `goals_events_match_score` flag; their scores still count
   for the goals target.
4. **`hasPlayoff` key presence means nothing** (it is present with
   value False for most 2024/2025+ payloads); only the value True
   (8 matches, all 2023/2024) marks the championship series.
5. **Team names are unstable; ids are stable.** Id 185749 appears as
   Bhayangkara FC / Bhayangkara Presisi Indonesia FC / Bhayangkara
   Presisi Lampung FC across seasons; id 1665351 is Malut United in
   2024/2025–2025/2026 but "Java United F.C." in 2026/2027. All logic
   keys on ids. 28 distinct ids appear across the corpus.

## 5. Feasibility consequences

- Goals: scores always exist → buildable, virgin 2025/2026.
- Cards: no stats-feed cards exist, but event cards exist and the
  virgin season's event feed is complete (306/306) → buildable on the
  event-unified yellow target, scored on complete-feed matches only.
- SOT / corners / total shots: the target's era ends Oct 2023 (plus 8
  matches in 2024/2025) and the virgin season contains zero target
  observations → NOT BUILDABLE under the programme rule (a candidate
  needs a valid virgin window containing the target). Forcing an
  earlier "virgin" would break the programme's season convention.
- Halves: no period splits exist. Goal and card event times (event
  order vs the half-time marker) are a legitimate halves source for
  goals and cards only. SOT/corners/total shots have no halves source
  and would be FT-only even if buildable.
