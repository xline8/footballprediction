# KW-PremierLeague — EDA (Steps 3–4)

All numbers from `analysis/eda.py` → `eda_summary.json` /
`inventory_summary.json`; charts in `charts/` (levels_by_season,
coverage_by_season, trait_reliability, halves_constants). Dev era =
2021 (warm-up) + 2021/2022–2024/2025 (scored). Virgin (2025/2026)
and reserve (2026/2027) appear in inventory only; nothing below is
chosen using them.

## F1 — Era structure of every feed: scores-only, absolutely

| season | played | stats | splits | shotmap | lineup | referee | events |
|---|---|---|---|---|---|---|---|
| 2021 | 64 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2021/2022 | 69 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2022/2023 | 120 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2023/2024 | 122 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2024/2025 | 111 | 0 | 0 | 0 | 0 | 0 | 87 |
| 2025/2026 (virgin) | 111 | 0 | 0 | 0 | 0 | 0 | 105 |
| 2026/2027 (reserve) | 45 | 0 | 0 | 0 | 0 | 0 | 45 |

No stats feed, no shotmap, no xG key, no referee in ANY season.
The event feed switches on only in 2024/2025. Consequences:
X1 runs in its goals-only fallback (no xG exists to blend);
X3/X4/X6/X7/X9 have no inputs in any era; X8 has no referee data.
S/C/K/T have no target in the dev era → not-buildable (F5 for K).

## F2 — Corpus integrity

642 played of 711 index rows; 69 unplayed fixtures excluded
(placeholder "0-0", never started — concentrated in the first four
seasons). Dual 2021 labels are distinct seasons (PREPROCESSING
decision 1). Event goals match the header score in 237/237 event
matches. 405 matches have no events at all, and they are NOT
scoreless (374 have goals; 1,219 goals in them) — event-derived
fields in those matches are missing, never zero.

## F3 — Halves constant (goals): 0.4411, thin base — flagged

The event feed exists in the dev era only in 2024/2025, so the
frozen goals 1H share comes from that single season's 87 event
matches: **0.4411** (131 of 297 goals in 1H, event times, awarded
excluded — the one awarded match has no events and is not in the
base). This is the thinnest halves base in the programme so far;
it is a presentation constant only (it enters no gate), and the
thin base is recorded here and in config.yaml. No halves constant
exists for SOT/corners/total shots (no period splits anywhere) or
for cards (no yellows target, F5).

## F4 — Entrant (X2) evidence: KEPT

8 completed entrant transitions in the dev era (2 per season —
constant churn in a 10-team league from a 14-team pool):

- mean GF diff **−0.390** (7/8 negative — entrants score less),
- mean GA diff **+0.404** (5/8 positive — entrants concede more,
  driven by large positives: +1.04, +0.82, +0.66, +0.58, +0.48),
- clamped log offsets: g_log **−0.2231**, c_log **+0.2231** (both
  clamp at the [log 0.8, log 1.25] bounds — the largest tilt class,
  same magnitude as BY).

Sign consistency on GF (7/8) matches the FI/BY adopt pattern; the
GA side is noisier but its mean is large and in the expected
direction. X2 is **adopted** as the third arm, with the rule (not
the realised numbers) frozen in the prereg: offsets recomputed from
completed transitions strictly before each predicted season.

## F5 — Cards target check: NO yellows target exists in any era

- Stats yellows: feed absent in all 711 payloads.
- Event yellows: plain Yellow events = **0 in every season**;
  YellowRed = **0 in every season**. The event feed records only
  straight Red cards (53 total: 18 in 2024/2025, 26 virgin, 9
  reserve; reds/match ≈ 0.21–0.25 where events exist).
- Referee named in 0/711 → no X8 arm possible.

This is stronger than the BY/NO case (there, plain Yellows existed
in a late era): here a yellows target never exists under either
source in any season. **K-KW is not-buildable.** S/C/T are likewise
not-buildable (F1: no SOT, corners or total-shots target in any
season; no shotmap substitute).

## F6 — Levels and evaluation lines (dev scored, n=422)

- Goals/match by dev season: 3.06 (warm-up 2021) / 2.93 / 3.27 /
  3.03 / 3.21 — high-scoring league, no trend.
- OU over-rates on dev scored: 1.5 → 0.8152, **2.5 → 0.5877**,
  3.5 → 0.3863. Primary line frozen at **OU 2.5** (closest to 0.5).
- Home win rate 0.4265, draw rate 0.2370 (dev scored).
- Mean team goals 1.5640/match (1,320 goals / 422 matches / 2).

## F7 — Trait reliability (goals): strong

Split-half on dev-era team matches (n=13 teams): GF r = **0.786**,
GA r = **0.922**. Season-to-season team-mean correlations (8 common
teams per adjacent pair): GF 0.68 / 0.17 / 0.84 / 0.82,
GA 0.41 / 0.57 / 0.61 / 0.74 — mostly moderate-to-strong; the
2021/2022→2022/2023 GF dip (0.17) is the one weak link. The
expanding-window Dixon-Coles fit has real signal to track.

## F8 — Format

10 teams every dev season; phases main/championship/relegation as
ordinary rows (championship+relegation = 34 played in 2022/2023,
42 in 2023/2024, 21 in 2024/2025, 0 in 2021 and 2021/2022).
One awarded match (2022/2023), none in the virgin.
