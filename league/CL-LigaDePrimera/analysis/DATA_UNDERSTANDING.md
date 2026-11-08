# Step 1 — Data Understanding — CL-LigaDePrimera (Chile, FotMob id 273)

Source: FotMob world warehouse, index filter `league_id = 273`
(`data_enrichment/fotmob_world_index.csv`), per-match JSONs under
`data_enrichment/fotmob_world/Chile/Liga de Primera/<season>/<id>.json`.

## Inventory

| season | matches | teams (by FotMob id) | stats cov | period-split cov | referee cov | dates |
|---|---|---|---|---|---|---|
| 2021 | 272 | 17 | 272/272 | 0/272 | 0/272 | 2021-03-27 – 2021-12-05 |
| 2022 | 240 | 16 | 239/240 | 0/240 | 221/240 | 2022-02-04 – 2022-11-06 |
| 2023 | 240 | 16 | 240/240 | 180/240 | 230/240 | 2023-01-20 – 2023-12-09 |
| 2024 | 240 | 16 | 240/240 | 239/240 | 204/240 | 2024-02-17 – 2024-11-10 |
| 2025 | 240 | 16 | 240/240 | 240/240 | 199/240 | 2025-02-15 – 2025-12-07 |
| 2026 | 216 | 16 | 214/216 | 214/216 | 159/216 | 2026-01-30 – 2026-11-08 (in progress) |

Total 1,448 matches; stats on 1,445 (99.8%). Shotmap on **0** matches
and `expected_goals` on **0** payloads in every season: there is no
xG of any kind in this league's warehouse era. The goals model is
therefore goals-only (Dixon-Coles on goals, no blend pair).

## Format (verified from the feed, not assumed)

Chile historically ran Apertura/Clausura tournaments and play-offs,
but **the warehouse era contains none of that**: every payload's
`general.leagueRoundName` is a plain round number (1–34), each season
is a single competition instance (`general.leagueId` is a per-season
instance id under `parentLeagueId = 273`), and the match counts are
exact double round-robins — 2021: 17 teams × 32 rounds = 272;
2022 onward: 16 teams × 30 rounds = 240. No split phase, no
championship/relegation group, no play-off rows exist in the feed.
Phase rule: **every row is `phase = regular`** (frozen in the
preregs). Seasons are calendar-year, single-tournament blocks;
walk-forward blocking is by season, which automatically respects
the (only) tournament boundary there is.

2026 is **incomplete** (216 of the 240 fixtures played at warehouse
snapshot): it is the reserved confirmatory window and is never read
in this build. The last complete season, and therefore the virgin,
is **2025**. Dev = scored 2022–2024 with 2021 as warm-up/seed.

## Team identity

25 distinct FotMob team ids across the era. Ids are **stable**;
names are not. Four ids carry multiple name spellings, all verified
to share one id: 49559 = Atletico Nublense / CD Nublense / Ñublense;
6458 = Universidad Catolica / Universidad Católica; 192435 = Union
La Calera / Unión La Calera; 162905 = Curico Unido / Curicó Unido.
The builder keys everything on team id and canonicalises the display
name to the last-seen spelling (see PREPROCESSING).

## Field coverage quirks

- Period splits (`Periods.FirstHalf/SecondHalf`) exist **only from
  2023** (75% that season, ~100% from 2024). Halves constants are
  therefore estimated on the 2023+ split era for stats markets;
  goals halves come from goal-event times, present in all seasons.
- Referee (`content.matchFacts.infoBox.Referee.text`) is absent for
  all of 2021 and present on 74–96% of later matches.
- Stats keys present (All period, essentially every stats match):
  total_shots, ShotsOnTarget, ShotsOffTarget, blocked_shots,
  corners, yellow_cards, red_cards, fouls, touches_opp_box,
  big_chance, keeper_saves, BallPossesion. Identity check on 1,444
  matches: `total_shots == ShotsOnTarget + ShotsOffTarget +
  blocked_shots` holds **exactly in 1,444/1,444** — the total-shots
  target is the stats `total_shots` key, blocked shots included.
- **Cards artefact (checked before any fitting, per program rule):**
  the stats feed's `yellow_cards` and the event feed's unified
  yellows (direct Yellow + YellowRed second yellows) disagree
  systematically in **every** season, stats always lower:
  mean(stats − events) per match = −1.20 (2021), −1.28 (2022),
  −0.49 (2023), −0.44 (2024), −0.16 (2025), −0.38 (2026); exact
  per-match agreement only 58–77% of matches. Unlike the TH/ZA
  artefact, the event feed here **does** carry plain yellows in
  every season (1,203 direct-yellow events in 2021 alone), so an
  event-unified target is supportable across the whole era. The
  cards target is frozen as **event-unified yellows** in the
  prereg, with this paragraph as the recorded reason; the stats
  yellows are retained in the CSV for audit only.
