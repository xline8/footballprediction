# Phase 1 — Data Understanding: Portugal Liga Portugal (FotMob id 61)

Corpus: the FotMob world warehouse, index
`data_enrichment/fotmob_world_index.csv` filtered to `league_id = 61`:
**1,628 played matches**, seasons 2021/2022 – 2026/2027 (306 in each of
the first five seasons — a complete 18-team double round robin — and
98 so far in 2026/2027, the in-progress season). Every one of the 1,628
index rows has `has_stats = True` and `has_shotmap = True`, and content
checks confirm it: the stats block and a non-empty shotmap exist in
all 1,628 payloads. Per-match JSON layout is the same matchDetails
format as the J.League warehouse (parsing reference:
`league/jleague_lib.py`).

Warehouse-location note: the JSON files are gitignored and live in the
main checkout's `data_enrichment/fotmob_world/`; the builder resolves
that root explicitly (see PREPROCESSING.md).

## League format

- 18 teams, double round robin, 306 matches per full season. No split
  into championship/relegation rounds in these seasons; the regular
  season *is* the competition. Relegation/promotion is with Liga
  Portugal 2 (not part of this league's corpus).
- Calendar: August–May, European split-season labels as stored in the
  warehouse (`2021/2022` …).
- 2026/2027 is in progress (98 matches, 2026-08-07 → 2026-11-08 at
  pull time): it is the TRANSITIONAL virgin window, exactly as J1's
  2026 was; a confirmatory read at season end is reserved.

## Coverage by season (measured on content, not index flags)

| Season | n | FT stats | xG | Period splits (1H/2H) | Box touches | Referee named | Shotmap |
|---|---|---|---|---|---|---|---|
| 2021/2022 | 306 | 306 | 306 | 35 | 217 | 163 (53%) | 306 |
| 2022/2023 | 306 | 306 | 306 | 107 | 209 | 304 (99%) | 306 |
| 2023/2024 | 306 | 306 | 306 | 306 | 252 | 306 | 306 |
| 2024/2025 | 306 | 306 | 306 | 306 | 306 | 306 | 306 |
| 2025/2026 | 306 | 306 | 306 | 306 | 305 | 306 | 306 |
| 2026/2027 | 98 | 98 | 98 | 98 | 98 | 98 | 98 |

Quirks that matter:

1. **xG is complete from the first season** (unlike J1's 2022 start):
   the goals blend never needs its goals-only fallback here except by
   construction, never by missing data.
2. **Period splits arrive gradually**: only 35 matches in 2021/2022
   and 107 in 2022/2023 carry FirstHalf/SecondHalf stat blocks; full
   from 2023/2024. Half-time *score* is nevertheless recoverable for
   all 1,628 matches from goal events (verified 44/44 against shotmap
   FirstHalf goals on a stride sample).
3. **Referee is empty in about half of 2021/2022**, then essentially
   complete. The referee arm's early-dev seasons therefore run partly
   on the no-imputation fallback.
4. **Box touches** (`touches_opp_box`) are partial (209–252) until
   2024/2025, then complete.
5. **Shotmap xGOT** (`expectedGoalsOnTarget`) is populated only for
   on-target shots before 2024/2025 (~2.5k of ~7.8k shots per season)
   and for ~all shots from 2024/2025 (7,307/7,355) — the same era
   break J1 found; the xGOT trait is era-guarded to 2024/2025+.
6. **Team-name accent variants**: a handful of matches spell the same
   club with/without accents (Famalicao/Famalicão, Vitória de
   Guimarães, Marítimo, Académico Viseu), and Belenenses SAD appears
   under its stadium name Cova da Piedade SAD in 2021/2022. All
   identity work is keyed on FotMob team **ids**; there are 18
   distinct ids per season.
7. Stat values arrive mixed-typed (ints, floats, numeric strings,
   percent strings); the extractor takes the leading number, as in
   `jleague_lib._num`. Duplicated stat keys across groups agree.

## Levels snapshot (full detail in EDA.md)

Goals 2.49–2.87 per match (2023/2024 the hot season), SOT 8.0–8.7,
corners 8.9–10.6, yellows falling steadily 5.66 → 4.76 across the five
complete seasons (virgin partial season 4.21 so far), total shots
24.0–25.6, xG 2.53–2.76.
