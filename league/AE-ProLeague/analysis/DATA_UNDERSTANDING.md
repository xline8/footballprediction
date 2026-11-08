# Step 1 — Data Understanding: UAE Pro League (FotMob id 538)

Corpus: FotMob world warehouse, `data_enrichment/fotmob_world/United Arab
Emirates/Pro League/`, index rows league_id=538. All numbers measured on
the files by `data/build_data.py` + `analysis/eda_compute.py`
(`eda_numbers.json`), never taken from index flags alone.

## 0. Integrity headline

- 959 files = 959 index rows = 959 CSV rows. Seasons: 2021/2022–2025/2026
  complete at 182 each (14 teams × 26 rounds × 7 = double round-robin),
  2026/2027 partial (49 played at pull). No duplicates, no gaps.
- Index flags verified by content: `has_stats=True` for all 959 and the
  stats block is genuinely populated in all 959; `has_shotmap=False` for
  all 959 and the shotmap block is an empty shell everywhere (0 shots).
  **There is no xG anywhere in this league** (no `expected_goals` key in
  any payload, any season) — the goals model is goals-only by the
  reference blend's documented fallback.
- Goal events reproduce `scoreStr` in 956/959. Exceptions: two awarded
  matches (3640606 in 2021/2022, 4211602 in 2023/2024 — official 0–3 / 3–0
  awarded wins, flagged `awarded=1` and excluded from every fit and score)
  and 4722300 (2024/2025, 8 goal events vs a 2–3 score — an event-feed
  error; its score stands, its event-derived HT is flagged unreliable).

## 1. Format (verified from the feed)

- Straight league: single double round-robin, rounds 1–26, 14 teams in
  every season, **no play-offs, no split, no championship/relegation
  groups** in the id-538 feed in any season. `general.leagueName` is
  "Pro League" for 929 matches and "UAE Pro League" for 30 matches in
  2026/2027 — a naming variant of the same competition, not a phase.
- Calendar: split-year seasons, ~Aug–May. 19 distinct team ids across the
  corpus (14 per season; promotion/relegation churn below). One id
  carries two names (209190: "Al Ittihad Kalba" → "Kalba FC"); all logic
  keys on team **ids**.

## 2. Coverage matrix (content-measured, % of matches)

| Season | n | Stats FT | Period splits | Events | Referee named | Shotmap/xG |
|---|---|---|---|---|---|---|
| 2021/2022 | 182 | 100 | 0 | 100 | 45/182 (25%) | 0 |
| 2022/2023 | 182 | 100 | 50/182 (27%) | 100 | 115/182 (63%) | 0 |
| 2023/2024 | 182 | 100 | 100 | 100 | 92/182 (51%) | 0 |
| 2024/2025 | 182 | 100 | 100 | 100* | 122/182 (67%) | 0 |
| 2025/2026 (virgin) | 182 | 100 | 100 | 100* | **6/182 (3%)** | 0 |
| 2026/2027 (partial) | 49 | 100 | 100 | 100 | 45/49 (92%) | 0 |

*Events exist but the plain-Yellow card events collapse in 2024/2025 and
2025/2026 — see §3.

Stats keys present in 100% of matches (FT): possession, total shots, SOT,
off target, blocked, big chances, corners, yellows, reds, fouls,
`touches_opp_box` (134/182 in 2021/2022, 175/182 in 2022/2023, 100%
after). Period splits (`FirstHalf`/`SecondHalf`) ramp in during
2022/2023 and are complete from 2023/2024 — a legitimate halves source
for every count market from that era, plus event-minute HT derivation
for goals in all seasons.

## 3. The cards artefact (decided here, before any fitting)

Two yellow sources disagree by era:

| Season | Stats yellows/match | Event yellows/match | Exact agreement |
|---|---|---|---|
| 2021/2022 | 3.19 | 3.99 | 69% |
| 2022/2023 | 3.82 | 4.03 | 85% |
| 2023/2024 | 3.81 | 3.93 | 84% |
| 2024/2025 | 3.91 | **0.01** | 3% |
| 2025/2026 | 3.89 | **0.01** | 2% |
| 2026/2027 | 3.00 | 3.33 | 78% |

The event feed carries essentially **no plain Yellow events in
2024/2025 and 2025/2026** (2 YellowRed per season survive; Red events
remain). An event-unified target therefore cannot exist in the dev
fold 2024/2025 nor in the virgin 2025/2026. The stats feed is complete
in every season with a stable level (3.19–3.91). **The cards target is
frozen as the stats-feed yellows** (the KR-KLeague2 precedent: stats
target frozen with the reason written), with the caveat recorded that
the stats feed undercounts the event feed where both live (−0.81/match
in 2021/2022, shrinking to −0.13 by 2023/2024) — a level fact about the
target definition, applied identically in dev and virgin.

## 4. Referee

Named in only 380/959 payloads overall and **6/182 in the virgin
season**. Split-half strictness reliability on the named subset is
r=0.43 (9 referees with ≥16 matches) — a real but thin trait that is
operationally absent in the virgin window. X8 is dropped in FEATURES.

## 5. Levels (context)

High-scoring league: goals 2.85 / 3.02 / 3.42 / 3.20 / 2.82 per match by
season (OU2.5 over-rate 0.52–0.66); home-win rate low (0.37–0.46) with
an unusual 2023/2024 where away goals (1.73) exceeded home goals (1.69).
SOT 8.2–9.6, corners 9.1–10.6 (falling in the last two seasons), total
shots 24.5–26.9, stats yellows 3.2–3.9 per match.
