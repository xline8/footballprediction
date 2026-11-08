# Phase 2 — Preprocessing: Honduras Liga Nacional

Builder: `league/HN-LigaNacional/data/build_data.py`
(regenerates `league/HN-LigaNacional/data/hn_matches.csv`, which is
gitignored by repo norm — commit the builder, not the CSV).
Source: the FotMob world warehouse index
(`data_enrichment/fotmob_world_index.csv`, filter `league_id = 337`)
and the per-match JSONs at the index `path` column (read from the
main checkout when the worktree has no warehouse copy — see the
builder's `warehouse_root()` fallback).

## Inclusion rules

1. **Played matches only.** Every index row whose payload says
   `header.status.finished == true` enters the table. All 1,132
   rows pass; nothing is excluded at this step.
2. **One row per match**, keyed by `match_id`, sorted by
   (date, match_id). No duplicates exist in the index.
3. **FT goals are the official header scores**
   (`header.teams[].score`). Goal-event counts are a cross-check
   only; they disagree with the header in exactly 2 matches, both
   awarded (see rule 6).
4. **HT goals are event-derived** (`jleague_lib.ht_from_events`:
   goal events with `time ≤ 45`, credited side). Blank where the
   event feed is absent (52 matches) or the match is awarded
   (rule 6). No HT value is ever fabricated or imputed.
5. **Teams keyed by FotMob team id** (`header.teams[].id`), never
   by name (two ids have two diacritic spellings — see
   DATA_UNDERSTANDING §3.5).

## Stage rule (regular vs playoff) — frozen

Per phase, let `lastreg` be the maximum date among matches whose
round label is the phase's maximum numeric round label. Then:

- `stage = "playoff"` if the round label is non-numeric (`1/4`,
  `1/2`, `final`) **or** the match date is after `lastreg`;
- else `stage = "regular"`.

The date clause is essential: in 2025/26 the 12 semifinal-group
matches reuse round labels 1–6 and are dated after the regular
phase ends (DATA_UNDERSTANDING §3.2). The builder asserts the
resulting counts: regular 90 per 2021/22–2024/25 phase, 110 per
2025/26 phase, 84 for 2026/27 Apertura; total regular 1,024,
playoff 108, total 1,132. Only `stage == "regular"` rows are
eligible for fitting or scoring; playoff rows are retained in the
table for completeness and descriptive use.

## Awarded matches — frozen

Three matches carry `status.awarded == true`: `3796146`,
`3796174`, `5066531`. Their official FT scores (3–0, 3–0, 0–0)
are kept as the goals target — they are the settled results.
Their HT columns are blanked: the event feed of `3796146`
describes a played 1–1 whose HT (0–1) is incoherent against the
awarded away-goals total of 0, and the other two have no event
feed at all. The `awarded` column flags all three.

## Season labels

Season labels are taken verbatim from the warehouse index
(`2021/2022 - Apertura`, …, `2026/2027 - Apertura`). The `phase`
column is derived from the label (Apertura/Clausura). No
re-labelling, no merging of phases: each Apertura/Clausura is its
own tournament for walk-forward purposes (see MODEL_DESIGN).

## Columns

`match_id, season, phase, date, home_id, home, away_id, away,
home_goals, away_goals, ht_home, ht_away, stage, round, awarded,
has_stats, has_shotmap, shot_count, has_period_splits,
referee_named, event_yellows_home, event_yellows_away,
event_cards_total, has_card_event, events_present, lineup_present`

Coverage columns (`has_stats`, `has_shotmap`, `referee_named`,
`lineup_present`, `event_yellows_*`) are all-zero in this league
by payload fact; they are recorded so the absence is machine-
checkable rather than asserted in prose.

## Split-source rules

- Period splits exist nowhere in this corpus; no 1H/2H split is
  ever taken from a stats feed. The only half split is the
  event-derived HT score above, and it is descriptive only.
- No stats, shotmap, lineup, referee, or xG source exists, so no
  column is ever filled from one.
