# Phase 1 — Data Understanding: IR Azadegan League (Iran, FotMob 9372)

Source: the FotMob world warehouse. Index:
`data_enrichment/fotmob_world_index.csv` filtered to `league_id = 9372`
(1,564 rows, league name `Azadegan League`, country Iran). Per-match
JSONs at the index `path` column
(`data_enrichment/fotmob_world/Iran/Azadegan League/<season>/<id>.json`,
same matchDetails format as the J.League warehouse). All coverage
figures below were measured from the **payload contents** of all 1,564
files, never from the index `has_*` flags (which read all-False here
and are in any case unreliable program-wide).

## Inventory

| season | index rows | played | teams | rounds | date range |
|---|---:|---:|---:|---:|---|
| 2021/2022 | 306 | 305 | 18 | 1–34 | 2021-10-16 – 2022-05-31 |
| 2022/2023 | 272 | 272 | 17 | 1–34 | 2022-08-28 – 2023-05-24 |
| 2023/2024 | 306 | 306 | 18 | 1–34 | 2023-08-26 – 2024-06-05 |
| 2024/2025 | 306 | 306 | 18 | 1–34 | 2024-08-29 – 2025-05-19 |
| 2025/2026 | 306 | 305 | 18 | 1–34 | 2025-08-28 – 2026-07-16 |
| 2026/2027 | 68 | 68 | 16 | 1–9 (round 9 partial, 4/8) | 2026-09-15 – 2026-11-08 |
| **total** | **1,564** | **1,562** | **42 ids** | | |

Played n = 1,562: two index rows are matches that were never played
(status `finished` False, `started` False, placeholder 0-0 in the
index) and are excluded from every analysis — 3743953 (2021/2022,
round 3, Arman Gohar Sirjan vs Shahrdari Hamedan) and 5098083
(2025/2026, round 19, Niroye Zamini vs Mes Kerman). See
`PREPROCESSING.md`. Note the second exclusion sits in the virgin
season, so the virgin window is n = 305, not 306.

## Format

Double round-robin, 34 rounds, 18 teams — except 2022/2023 (17
teams, one club idle per round, still 34 rounds: 17 × 16 = 272) and
2026/2027 (16 teams so far, 8 matches per round; rounds 1–8
complete, round 9 partial at the warehouse cutoff). No playoffs, no
split, no relegation round: every season is rounds 1–34 only
(`infoBox.Tournament.round` runs 1–34 in each complete season; the
`hasPlayoff` key present in some payloads is a FotMob UI flag with no
playoff rounds behind it). The regular season is modelled honestly
as one double round-robin per season.

Churn is extreme: 5–6 clubs turn over every season (6, 6, 6, 5
entrants into 2022/2023–2025/2026; 4 so far into 2026/2027). Over
the six seasons 42 distinct team ids appear, but only a core of
~11–12 clubs is present in most seasons. Promoted clubs arrive from
the tier below and relegated Persian Gulf Pro League clubs arrive
from above (e.g. Fajr Sepasi, Paykan, Nassaji Mazandaran, Havadar,
Mes Rafsanjan in recent transitions) — identified by name only;
there is no in-corpus tier label for them (see the Persian Gulf flag
in §4).

## Field coverage per season (played matches, payload-verified)

| field | 21/22 | 22/23 | 23/24 | 24/25 | 25/26 | 26/27 | total |
|---|---:|---:|---:|---:|---:|---:|---:|
| FT score (header/index) | 305/305 | 272/272 | 306/306 | 306/306 | 305/305 | 68/68 | 1,562/1,562 |
| stats block non-null | 0 | 0 | 0 | 0 | 0 | 0 | **0** |
| shotmap shots > 0 | 0 | 0 | 0 | 0 | 0 | 0 | **0** |
| lineup non-null | 0 | 0 | 0 | 0 | 0 | 0 | **0** |
| referee text non-empty | 0 | 0 | 0 | 0 | 0 | 0 | **0** |
| event feed non-empty | 247 | 218 | 260 | 249 | 233 | 54 | 1,261 |
| Half marker (of non-empty) | 247 | 218 | 260 | 249 | 233 | 54 | 1,261/1,261 |
| period splits | 0 | 0 | 0 | 0 | 0 | 0 | **0** |

- **Scores**: every played match has a parseable FT score; the index
  score, `header.status.scoreStr`, and `header.teams[].score` agree
  on all 1,562 played matches.
- **Stats / xG / shotmap / lineup / referee**: absent in **all**
  1,564 payloads, in every season. `content.stats` is JSON null;
  `content.shotmap` is `{"shots": [], "Periods": ...}` with an empty
  shot list; `content.lineup` is null; `infoBox.Referee.text` is
  empty/absent. There is no xG anywhere, no SOT, no corners, no
  total-shots, no cards-from-stats target — in any season, including
  the virgin window. This is a scores-only corpus, end to end.
- **Events**: present in 1,261/1,562 played matches (80.7%), at a
  stable rate in every season (76–85%). Every non-empty feed carries
  Half markers (2,521 Half events). Event types are only Half, Goal
  (2,783), and Card (133). Goal events reproduce the FT score in
  1,258 of the 1,261 feeds; the 3 exceptions are documented in
  `PREPROCESSING.md` and their HT is set to NaN. HT goals are
  therefore derivable for 1,258 matches + 276 goalless empty-feed
  matches (HT 0-0 by the same feed) = 1,534 matches.
- **Cards from events**: 133 Card events in 117 matches — all Red
  (122) or YellowRed (11); **zero Yellow events in 1,564 matches**.
  Cards exist only as rare red-family events (0.085/match). No
  yellows target exists anywhere.

## Quirks

- **Team renames (same FotMob id, new name)**: id 1082763 Arman
  Gohar Sirjan → Shahr Raz (during 2022/2023); id 1528916 Mes Sungun
  → Kara Gostar (2025/2026); id 1602400 Shenavarsazi Qeshm → Qeshm
  Island (2026/2027). Team identity is the FotMob id throughout;
  the builder and the fit key on ids, never names. No name maps to
  more than one id.
- **2022/2023 has 17 teams**: the league ran one club short that
  season (7 clubs left after 2021/2022, 6 entered). Nothing is
  imputed for the missing club; the season is 272 matches, complete
  as played.
- **2026/2027 shrank to 16 teams** (8 matches/round, 68 matches
  through round 9 at the cutoff). It is the transitional season:
  descriptive levels only, reserved as the confirmatory virgin
  window, never touched by fitting or by the dev harness.
- **Goal-event feed gaps**: 301 played matches (19.3%) have an empty
  event feed — mostly (276) 0-0s, 25 with goals. Those 25 have no HT
  split; they keep their FT score and enter the goals fit normally.
  The 3 feeds that disagree with the FT score (3863817 undercounts
  2-1 as 2 goals; 4321829 undercounts 3-0 as 1; 4159522 totals 3 but
  attributes two goals to the wrong side) are flagged
  `score_events_mismatch` and their HT is NaN.
- **No shootouts, no extra-time scores**: the FT score is the
  regulation score in every match; `penaltyShootoutEvents` is empty
  throughout.

## §4 — Persian Gulf flag (coordinator decision needed)

The task brief for this league states Iran has no other league in
the warehouse. That premise is **wrong on the index**: the warehouse
index contains a second Iranian league, **Persian Gulf (FotMob id
523), 1,245 rows across the same six seasons** (2021/2022–2026/2027),
and `data_enrichment/fotmob_world/Iran/` holds both `Azadegan
League/` and `Persian Gulf/` folders. The folders and index rows
were verified present on disk in the main checkout.

Per the brief's explicit instruction ("no parent/sibling tier exists
for an X2 newcomer prior — do not invent one"), **no Persian Gulf
data was used anywhere in this build**: no mover prior, no feature,
no gate input. The X2 feature is recorded DROPPED in `FEATURES.md`
on the brief's scope, and the within-league evidence (EDA F4:
pooled dev entrant gaps GF +0.002 / GA −0.034) independently gives
no entrant prior to fit anyway. This flag is recorded here, in
`config.yaml`, and in `MODEL_DESIGN.md` so the coordinator can
decide whether a future X2 amendment (fresh prereg, before any
fitting) should draw on the Persian Gulf corpus. Nothing in this
build depends on that decision.
