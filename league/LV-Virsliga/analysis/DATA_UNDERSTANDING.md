# Step 1 — Data Understanding: LV-Virsliga (FotMob 226)

Source: FotMob world warehouse, `data_enrichment/fotmob_world_index.csv`
filtered to league_id 226; per-match payloads under
`fotmob_world/Latvia/Virsliga/<season>/`. All counts below were
computed from the payload CONTENTS (full 1,017-file scan in
`analysis/inventory.py` → `inventory_summary.json`), not from the
index flags — the index `has_stats` flag is a key-presence flag and
is not trusted in this program.

## Inventory

| season | n | dates | teams | stats (All) | 1H/2H splits | events | yellow events | referee | shotmap |
|---|---|---|---|---|---|---|---|---|---|
| 2021 | 112 | 2021-03-13 – 2021-11-06 | 8 | 0 | 0 | 95 | 11 | 0 | 0 |
| 2022 | 182 | 2022-03-11 – 2022-11-27 | 11 | 0 | 0 | 172 | 19 | 0 | 0 |
| 2023 | 182 | 2023-03-11 – 2023-11-25 | 11 | 0 | 0 | 174 | 23 | 0 | 0 |
| 2024 | 182 | 2024-03-08 – 2024-11-23 | 11 | 0 | 0 | 172 | 24 | 0 | 0 |
| 2025 | 180 | 2025-03-05 – 2025-11-09 | 10 | 180 | 180 | 180 | 862 | 40 | 0 |
| 2026 | 179 | 2026-03-06 – 2026-11-08 | 10 | 179 | 179 | 179 | 782 | 55 | 0 |

## The era map (the decisive fact of this league)

There is a hard feed break at the start of 2025:

- **2021–2024: no stats block at all.** The events feed is a
  reduced feed — only `Goal`, `Half`, and `Card` events. Plain
  `Yellow` events are near-absent (11/19/23/24 per season); the
  `Card` events that exist are mostly reds / second yellows.
  A yellows target therefore does not exist in this era, and no
  SOT / corners / total-shots target exists either.
- **2025–2026: every match is rich** — stats block present with
  `Periods.All`, `FirstHalf`, and `SecondHalf` (180/180, 179/179),
  full events (incl. substitutions), plain yellows at a plausible
  level (4.79/match in 2025, 4.37 in 2026).

The stats era is therefore frozen as **seasons 2025+** (359 matches).

## Format (verified from `general.matchRound` / `leagueRoundName`)

- Calendar-year seasons, March–November. 2025/2026 are a straight
  10-team quadruple round-robin: rounds 1–36 × 5 matches = 180,
  no championship/relegation split phase in the feed
  (`hasPlayoff` absent in all 1,017 payloads; rounds run 1–36
  continuously). 2026 holds 179 played matches: round 36 has 4,
  the RFS–Riga FC fixture is absent from the warehouse (unplayed
  at pull time); the virgin is the 179 played matches.
- 2022–2024: 36 rounds × 5 = 180 league matches PLUS a 2-legged
  relegation final (`leagueRoundName == 'final'`, 2 per season, 6
  total: 9th-place Virsliga side vs a 1. liga side). The finals are
  NOT league matches and are excluded from every table (see
  PREPROCESSING).
- 2021: 8 teams × 28 matches = 112 (truncated season); the feed's
  round labels are messy that year (36 distinct labels, 1–6
  matches each) and are not trusted for structure.

## Stats feed content (stats era)

Where present, the stats feed carries 29 keys under
`Periods.All` (and the same keys under `FirstHalf`/`SecondHalf`),
including `BallPossesion`, `total_shots`, `ShotsOnTarget`,
`big_chance`, `yellow_cards`, `corners`, `fouls`, `red_cards`,
`shots_inside_box`, `shots_outside_box`, `ShotsOffTarget`,
`blocked_shots`, `passes`, `accurate_passes`, `Offsides`,
`keeper_saves`. Two holes, both verified from payload contents:

- **No `expected_goals` and no `touches_opp_box` in ANY of the
  1,017 payloads.** No xG anywhere; shotmap is empty in every
  season (`content.shotmap.shots` always `[]`).
- **`big_chance` is dead: exactly 0 in all 359 stats-era matches.**
  The key exists; the feed never populates it.
- **`yellow_cards` (stats) is unreliable in 2025: 43/180 matches
  read exactly 0/0 while the event feed records 187 yellows in
  those same matches** (hole Mar–Aug 2025; gone Sep–Nov; other
  stats keys are sane in those matches, so the hole is
  yellow-specific). 2026 is near-clean (6 zero matches, 4 of them
  genuine 0-event-yellows). Cards target is therefore the EVENT
  feed (see PREPROCESSING), never the stats key.

## Events cross-checks

- Goal events reconcile with the index score in 1,010/1,011 league
  matches. Exceptions: 2021, where 17 matches have no events at
  all (incl. awarded 0–3 results) so 15 matches cannot reconcile
  from events; and one 2022 match (FS Metta/LU–Auda 3–0, only 2
  goal events). The index score is authoritative everywhere;
  event-time halves for goals use the events where present.
- Referee: `infoBox.Referee.text` is empty pre-2025 and populated
  in only 40/180 (2025) and 55/179 (2026) matches. In 2025 that is
  ~12 distinct referees (after merging diacritic variants, e.g.
  Edgars Malcevs / Maļcevs) with 1–5 matches each — too thin for
  any referee feature (X8 DROPPED).
- Team identity: 16 distinct team ids across the corpus. Two ids
  carry two name spellings each (8016 'FK Liepaja'/'FK Liepāja',
  662738 'Grobina'/'Grobiņa' — diacritics change in 2025).
  Referee names show the same diacritic drift. All logic keys on
  team ids, never names.

## Virgin-hygiene disclosure

Step-1 inventory aggregates above include 2026 (per-season counts,
coverage, yellow totals). These are era facts, as in every prior
league's DATA_UNDERSTANDING: no per-match model output and no gate
quantity was computed from 2026. The virgin is NOT burned. The
same disclosure is recorded in every prereg.
