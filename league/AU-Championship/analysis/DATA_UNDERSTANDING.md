# Step 1 — Data understanding: AU-Championship (FotMob 8938)

**Headline finding (read this first): FotMob id 8938 is not one league.
It is a parent container holding ten competitions.** The index lists
1,333 rows for id 8938, but only 87 of them are the Australian
Championship. The other 1,246 are nine separate state NPL leagues
(plus their playoffs) that share the parent id, never play each
other, and have ~50% of their scores unrecorded. Any model fitted
on the pooled 1,333 rows would be fitting ten disjoint competitions
as if they were one league. This build uses only the 87 true
Championship matches, and on those 87 no candidate is buildable
(see MODEL_DESIGN.md). Every number below is payload-verified:
1,333/1,333 JSONs were read (not the index flags — the flags are
wrong in the same direction as everywhere in this program: the
`has_*` columns say `False` for all 1,333 rows, while the payloads
do contain an (empty-skeleton) shotmap key in all 1,333).

## 1. What id 8938 actually contains (payload `general.leagueName`)

| Sub-competition (leagueName) | Season | n | Dates |
|---|---|---|---|
| New South Wales | 2025 | 240 | 2025-02-07..2025-09 |
| Victorian | 2025 | 182 | 2025-02-06..2025-09 |
| Queensland | 2025 | 132 | 2025-02..2025-08 |
| Northern New South Wales | 2025 | 132 | 2025-02..2025-08 |
| Southern | 2025 | 132 | 2025-02..2025-08 |
| Western | 2025 | 132 | 2025-02..2025-08 |
| Tasmania Premier League | 2025 | 84 | 2025-02..2025-08 |
| Capital | 2025 | 84 | 2025-02..2025-08 |
| Northern | 2025 | 84 | 2025-02..2025-08 |
| State playoffs (9 comps) | 2025 | 44 | 2025-08..2025-09 |
| Tasmania Premier League Playoff | 2026 | 6 | 2026-08-15..2026-09-05 |
| **Australian Championship Grp. A–D** | **2025** | **48** | **2025-10-10..2025-11-16** |
| **Australian Championship Final Stage** | **2025** | **7** | **2025-11-21..2025-12-06** |
| **Australian Championship Grp. A–D** | **2026** | **32** | **2026-10-15..2026-11-08** |

State total: 1,246. Championship total: 87. Index total: 1,333
(1,295 in "2025", 38 in "2026"). Files on disk: 1,333 = index rows.
Every payload carries `general.parentLeagueId = 8938` and
`general.leagueId = 8938`; the sub-competition is identified only by
`general.leagueName` (and the `infoBox.Tournament.link`
`/leagues/8938/overview/<slug>`). `coverageLevel` is `lower` in
1,333/1,333 payloads.

## 2. The true Australian Championship (n = 87)

- **Format (frozen from payloads).** 16 clubs in 4 groups of 4
  (Grp. A–D), double round-robin: 6 rounds, 12 matches per group.
  Top 2 per group advance to a 7-match final stage: 4 quarter-finals
  (round `1/4`), 2 semi-finals (`1/2`), 1 final. 2025 is complete:
  48 group + 7 final = 55 matches, 2025-10-10..2025-12-06.
  Champion: South Melbourne (final 2-0 vs Marconi Stallions,
  2025-12-06). 2026 is TRANSITIONAL: 32 group matches, rounds 1–4
  of 6, 2026-10-15..2026-11-08 (the last date is the warehouse pull
  date); rounds 5–6 and the final stage are not in the warehouse,
  and no future fixtures are stored anywhere in the index.
- **Teams.** 16 clubs per season, 20 distinct clubs across the two
  seasons; 12/16 retained 2025 → 2026. New in 2026: Adelaide City,
  Lions FC, Oakleigh Cannons, Sutherland Sharks. Out after 2025:
  Heidelberg United, Moreton City Excelsior, North Eastern Metro
  Stars, Spirit FC. Clubs qualify via their state leagues, so
  turnover of 4/16 a year is structural, not an anomaly.
  Per-team matches 2025: finalists South Melbourne and Marconi
  Stallions 9 each; semi-finalists Moreton City Excelsior and
  Heidelberg United 8 each; the other 12 clubs 6 each. 2026: 4 each.
- **Scores are genuine.** All 87 Championship matches are
  `header.status.finished = True`, and the index score matches
  `header.teams[0/1].score` in 87/87. The 7 recorded 0-0s (8.0%)
  are finished matches — genuine scoreless draws, corroborated in
  2026 by the shootout field (all 8 drawn 2026 group matches went
  to a shootout; see §4). No Championship match is postponed,
  abandoned, or cancelled (the 5 such matches in the parent are all
  state-league fixtures).

## 3. The state leagues — why they are excluded (and unusable anyway)

- **Disjoint competitions.** 104 distinct team names appear across
  the parent; the nine state leagues never play each other (the only
  cross-state meetings in the whole parent are the 87 Championship
  matches). A pooled Dixon-Coles fit over 1,333 rows would have a
  block-diagonal design: team ratings are not comparable across
  blocks, and the shared home advantage would be the only identified
  cross-block parameter. That is not a league model.
- **Scores ~50% unrecorded.** Of the 1,246 state matches, 603
  (48.4%) have `header.status.finished = False` and are recorded
  0-0 — the `finished` flag separates them exactly (every
  not-finished state match is recorded 0-0; only 19 finished state
  matches are genuine 0-0s). A further 5 are explicitly postponed
  (4) / abandoned (1), all recorded 0-0. The finished state matches
  (643) look normal (non-0-0 subset: mean 3.60 goals, home win
  45.2%, draw 14.6%, over 2.5 67.1%), so the missingness is a
  recording failure, not a different sport — but a 48% hole that is
  indistinguishable from a genuine 0-0 without the `finished` flag
  makes the state data unusable for fitting without external
  verification, and it is out of scope regardless: each state league
  would be its own league build with its own slug.
- **Only 2026 state football in the warehouse** is the 6-match
  Tasmania Premier League Playoff (2026-08-15..2026-09-05). No other
  2026 state season is present.

## 4. Field coverage — payload-verified, all 1,333 JSONs

| Field | Present (non-empty) | Note |
|---|---|---|
| Score (`header.teams[].score`) | 1,333/1,333 | Championship 87/87 cross-checked vs index |
| `content.stats` | 0/1,333 | `null` everywhere — no corners, SOT, total shots, cards, xG, period splits |
| `content.shotmap.shots` | 0/1,333 | Key present (`shotmap: {shots: [], Periods: {All: []}}`) — empty skeleton; index `has_shotmap=False` is right by accident |
| `content.matchFacts.events.events` | 0/1,333 | Empty list everywhere — no goal/card events |
| Referee (`infoBox.Referee.text`) | 0/1,333 | Blank string everywhere |
| `content.lineup` | 15/1,333 | Non-null only in 2025 Championship group rounds 1–2 (2025-10-10..19); no stats attached |
| Red cards (`header.status.numberOf*RedCards`) | 1,333/1,333 fields present | But ≥1 red in only 12 matches — the fields are near-zero-filled and cannot serve as a cards target (and there are no yellows anywhere) |
| Period splits / 1H scores | 0/1,333 | `header.status.halfs` holds timestamps only, no scores |
| Extra time | 1/87 champ | 2025 QF APIA–Marconi 1-1 (ET + pens, Marconi advanced); stored 1-1 may include ET goals — flagged, never repaired |
| Shootouts | 9/87 champ | Format change: 2025 group draws 0/12 to shootouts; 2026 group draws 8/8 to shootouts, no ET. Stored score stays the drawn score |

**Consequence: the only target that exists in this league is goals
(from the score).** SOT, corners, cards (yellow/total), and total
shots have no target in any of the 87 payloads. There is no xG, no
referee, no period split, and no trailing team statistic of any kind
beyond the scores themselves.

## 5. The sibling check (X2)

AU-ALeague (FotMob 113, built, 4 PASS / 1 FAIL) is the tier above.
Its 13 senior clubs and the Championship's 20 clubs are **disjoint
— zero overlap** (the Championship has no A-League senior side; the
A-League youth sides — Central Coast Mariners Youth, Brisbane Roar
FC Youth, etc. — play in the state leagues, not in the
Championship). There is therefore no cross-tier mover prior to
borrow from the sibling. Borrowing same-club state-league form
instead is rejected in MODEL_DESIGN.md (same-season concurrent
form, not a prior-season mover offset; 48% of state scores missing;
unvalidatable — no dev or virgin window exists in-competition).

## 6. Calendar

Southern-hemisphere season: state leagues Feb–Sep, Championship
Oct–Dec. The Championship launched in October 2025 — there is no
2021–2024 history for it in the warehouse or anywhere else. The
"2021–2026 history" the index row count suggests does not exist for
this competition.
