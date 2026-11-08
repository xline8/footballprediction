# Step 1 — Data Understanding: MD-NationalDivision

## Format

Moldova tier 1, FotMob league_id 231, split seasons
2021/2022–2026/2027, **8 teams in every season**. Format by era
(measured from `general.leagueName` + row counts):
- 2021/2022: single phase, 112 matches (quadruple round-robin),
  leagueName `National Division` in all 112.
- 2022/2023–2024/2025: two phases, 86 matches = 56 `Super Liga`
  (main) + 30 `Super Liga Championship Group` (championship).
- 2025/2026 (virgin): 114 = 84 main + 30 championship (main phase
  expanded).
- 2026/2027 (reserve, in progress): 72, all main so far.
Phase is a flag on ordinary rows (`main` / `championship`), never
filtered — the championship group is the same 8 clubs playing for
the title, not a different population.

## Identity / naming

The league was renamed after 2021/2022: `National Division` →
`Super Liga` (FotMob leagueName evidence; same league_id 231, same
clubs). 12 distinct team ids in the corpus; two ids carry two
spellings each, both diacritic variants (8012: FC Balti /
FC Bălți; 1900141: Real Sireți / Real Sireti). All logic keys by
FotMob team id; the name shown is the id's first-seen spelling.

## Feeds (measured, `eda_summary.json` / `inventory_summary.json`)

- **Stats feed: 0/556 matches in EVERY season** (no
  `content.stats.Periods` key anywhere). Period splits 0/556.
- **Shotmap: 0/556.** Lineup: 0/556. **Referee: 0/556.**
- Events: 504/556 (99 / 76 / 84 / 77 / 104 / 64 by season). The 52
  event-less matches are NOT all scoreless (10 of them contain 30
  goals) — missing events stay missing; the FT score always comes
  from the header.
- Card events exist but **plain Yellow events total ZERO in every
  season** (corpus: YellowRed 25, Red 56+). No yellows target
  exists in any era.
- Scores-only league, measured not assumed (BRIEF confirmed).

## Scores

FT score from `header.status.scoreStr`; all 556 index rows are
finished and present in the CSV (556 = index count). 0
score-vs-event mismatches corpus-wide. 10 awarded matches (9 in
2021/2022, 1 in 2024/2025) — ordinary rows with `awarded=true`,
header score used.

## Split (frozen)

Per BRIEF: warm-up 2021/2022 (n=112); dev scored
2022/2023–2024/2025 (n=258); **virgin = 2025/2026 (n=114, complete
season)** read once, only for dev-passing arms; 2026/2027 (n=72,
in progress) untouched as confirmatory reserve.
