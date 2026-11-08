# Step 1 — Data Understanding: Israel Leumit League (IL-Leumit)

Status: **STEP 1 COMPLETE — build then HELD by coordinator order
2026-11-09 18:30 WIB (focus shifted to Bulgaria). Steps 2–6, prereg
and all fitting NOT started.** Branch `build/il-leumit`.

League: Leumit League (Israel, tier 2). FotMob league_id = 128.
Source: FotMob world warehouse, index
`data_enrichment/fotmob_world_index.csv` (filter league_id = 128),
per-match JSONs at the index `path` column under
`data_enrichment/fotmob_world/Israel/Leumit League/<season>/<id>.json`
(main checkout only — the warehouse is gitignored data).

## Inventory (verified from the index + a full JSON scan, 2026-11-09)

- **n = 1,581 matches**, all with a final score (`header.status.scoreStr`,
  `finished = True` in the sampled payloads).
- Seasons (warehouse labels) and counts:

| Season | Matches | Teams (distinct names) | Rounds present |
|---|---|---|---|
| 2021/2022 | 296 | 16 | 1–37, 8 per round |
| 2022/2023 | 296 | 16 | 1–37, 8 per round |
| 2023/2024 | 296 | 17 | 1–37, 8 per round |
| 2024/2025 | 296 | 16 | 1–37, 8 per round |
| 2025/2026 | 296 | 16 | 1–37, 8 per round |
| 2026/2027 | 101 | 16 | 1–13 (in progress; round 13 has 5) |

- Five complete seasons (2021/2022–2025/2026) of exactly 296 matches;
  2026/2027 is the in-progress season (101 played at pull time).

## League format (frozen fact for the design steps)

- 16 teams. Rounds 1–30 = regular season (double round-robin,
  16 × 30 / 2 = 240 matches).
- Rounds 31–37 = split phase (7 rounds × 8 = 56 matches): after
  round 30 the league splits into a promotion group and a relegation
  group; split-phase matches are played matches against same-group
  opponents and count in the warehouse like any other.
- **Phase rule to carry into preprocessing/design: rounds 1–30 =
  `regular`, rounds 31–37 = `split` (phase-flag the rows; the split
  is part of the real season, not a separate competition).**
- No format change across the five complete seasons: every season
  has the identical 37-round / 296-match shape.
- Quirk, unresolved at Step 1: 2023/2024 shows 17 distinct team
  *names* over a 16-slot league — most likely a club name variant in
  the feed, not a 17th club. Step 2 (preprocessing) must resolve
  team identity by FotMob team **id**, not name, and record the
  variant explicitly.

## Field coverage (the decisive fact of this league)

From the index flags, over all 1,581 matches:

| Field | Coverage |
|---|---|
| Score (FT) | 100% (1,581 / 1,581) |
| `has_stats` | **0% (0 / 1,581)** |
| `has_shotmap` | **0% (0 / 1,581)** |
| `has_lineup` | 0% in sampled rows |
| `has_period_splits` | 0% in sampled rows |

The JSON payloads carry the standard keys (`content.stats`,
`content.shotmap`, `content.matchFacts`, …) but the index flags say
the stats and shotmap payloads are empty for this league — there is
**no xG, no SOT, no corners, no shots, no cards target anywhere in
the corpus**. (Event/referee detail inside `matchFacts` was not
separately audited: with no stats targets at all it cannot create a
buildable market, and the goals candidate does not need it.)

## Feasibility matrix (consequence, frozen)

- **Goals (G-IL) — the ONLY candidate.** FT scores exist for every
  match; a Dixon-Coles goals-only fit is buildable.
- **SOT / corners / cards / total shots — NOT BUILDABLE**, documented
  here with the coverage numbers above (0% stats, 0% shotmap), per
  the exception-wave brief: no stats targets at all.
- No period splits → no halves constants; if the goals candidate
  ships, presentation is **FT only**.

## Cross-tier note (for Step 5 / prereg, NOT decided here)

- Ligat ha'Al (FotMob id 127, the tier above) IS in the warehouse:
  n = 1,270, same season span (240 per complete season, 70 in
  2026/2027). So the mover question (X2 cross-tier prior /
  shrinkage for promoted/relegated clubs) genuinely exists for
  Leumit, which receives relegated Ligat ha'Al clubs and sends
  promoted clubs up every season.
- Whether an X2/SHRINK arm is pre-registered must be decided from
  the Step 3 EDA mover measurement and frozen in the prereg —
  **no decision taken at Step 1.**

## Window facts (for Step 6 / prereg, NOT frozen here)

- Last complete season = **2025/2026 (n = 296)** — the natural virgin
  candidate. 2026/2027 is in progress (n = 101) and would be the
  reserved/confirmatory window. The prereg freezes this before any
  fitting; nothing has been fitted or read against any window yet.
