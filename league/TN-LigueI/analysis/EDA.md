# Step 3 — EDA: Tunisia Ligue I

Source: `league/TN-LigueI/data/tn_matches.csv` (1,060 rows;
model rows n=1,051, awarded excluded). Windows: warm-up 2021/22
(n=156); dev scored 2022/23–2024/25 (n=602); virgin 2025/26
(n=237, complete — levels shown for inventory only, not fitted);
confirmatory reserve 2026/27 partial (n=56 — inventory only). All
levels below are MODEL rows (all phases, awarded excluded,
PREPROCESSING.md). All numbers are reproducible from
`analysis/eda.py` → `eda_summary.json`.

## F1 — Levels per season (goals)

| Season | n | Goals/match | Home | Away | HW | D | AW | OU1.5 | OU2.5 | OU3.5 | BTTS |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2021/2022 | 156 | 1.70 | 1.02 | 0.68 | .462 | .314 | .224 | .474 | .288 | .071 | .333 |
| 2022/2023 | 195 | 2.05 | 1.23 | 0.82 | .467 | .272 | .262 | .595 | .323 | .154 | .344 |
| 2023/2024 | 170 | 1.90 | 1.17 | 0.73 | .482 | .282 | .235 | .541 | .347 | .135 | .341 |
| 2024/2025 | 237 | 2.03 | 1.19 | 0.85 | .447 | .291 | .262 | .582 | .346 | .160 | .376 |
| 2025/2026 | 237 | 1.72 | 1.02 | 0.70 | .460 | .283 | .257 | .506 | .270 | .089 | .262 |
| 2026/2027* | 56 | 1.96 | 1.21 | 0.75 | .536 | .286 | .179 | .554 | .339 | .125 | .464 |

\* partial season (rounds 1–7), reserve — inventory only. Dev scored
pooled (2022/23–2024/25, n=602): 2.00 goals/match (H 1.20 / A 0.81),
HW .463, D .282, AW .254, OU1.5 .575, OU2.5 .339, OU3.5 .151,
BTTS .355.

Tunisia is a LOW-scoring league by every reference point in the
program (J1 ≈ 2.6–2.7 goals/match; NI dev 2.83; top-5 ≈ 2.6–2.9):
OU2.5 over-rate is only 0.339 in the dev window, and the virgin
season drops to 1.72 goals/match with OU2.5 at 0.270. The draw rate
is high (0.27–0.31 every season; dev 0.282 vs NI's 0.186 and J1's
≈0.24) — a low-scoring league with many stalemates, which is
exactly the regime where a Dixon-Coles low-score correction matters
and where 1X2 log-loss is dominated by the draw mass. The level
moves around without a trend (1.70 → 2.05 → 1.90 → 2.03 → 1.72);
season-to-season swings of ±0.3 goals/match, no drift direction;
the DC fit's 270-day half-life decay is the mechanism that absorbs
it, and no era split is imposed. Home advantage is large in goal
terms: home goals exceed away by 0.34–0.48 per match in every
complete season (dev +0.39); HW rate 0.45–0.48, AW rate 0.22–0.26.

Levels by phase (model rows, all seasons pooled): group 1.82
(n=307), championship 1.96 (n=114), relegation 1.99 (n=98),
single-table regular 1.89 (n=530), placement 5.50 (n=2 — two
high-scoring one-offs, pure noise at this n, noted not acted on).
No phase is scored materially differently from the others; nothing
in the phase split argues for excluding or down-weighting any
phase, which supports the all-phases model-data decision.

## F2 — Team traits: real but phase-attenuated (goals)

Split-half by team-season (each team's matches in a season split
chronologically into first/second half; per-match GF and GA rates
correlated across halves), the program-standard check:

| Window | Team-seasons | GF split-half r | GA split-half r |
|---|---|---|---|
| Dev era 2021/22–2024/25 | 62 | **0.235** | **0.251** |
| Scored window 2022/23–2024/25 | 46 | **0.168** | **0.302** |

These are WEAK by the program standard (NI: 0.591/0.735; J1:
0.69/0.62) — and the reason is measurable, not mysterious. The
chronological split cuts each team-season exactly where the league
regroups: the first half is group-phase matches, the second half is
championship/relegation-group matches against systematically
stronger (or weaker) opposition. A team's second-half GF/GA is
therefore measured against a different opponent pool, which
attenuates the correlation. Two diagnostics confirm the mechanism:

- **Random split-half** (same team-seasons, matches randomly
  assigned to halves, mean over 20 seeds): GF r = 0.389, GA r =
  0.463 — markedly higher than the chronological 0.235/0.251.
- **Regular-phase-only chronological split** (single-table seasons,
  where no regrouping exists): GF r = 0.497, GA r = 0.622 (n=32
  team-seasons) — in the normal range for a ratings fit.

Team-season GF means also show real dispersion (per-season min/max
0.36–1.61 in 2022/23, 0.60–1.90 in 2024/25; SD 0.24–0.35) — the
league has genuine strong/weak teams (Esperance / US Monastir at
the top, promoted sides at the bottom). Verdict: **SIGNAL, weak to
moderate, phase-attenuated.** The goals candidate is justified —
the DC fit pools many seasons and fits ratings across the regrouping
rather than splitting on it — but expectations are modest, and the
dev gate (not this EDA) decides whether the ratings carry enough
signal to beat climatology. (Method note: the split is within
team-season, so promotion/relegation turnover does not inflate the
correlation; n is team-seasons, not teams.)

## F3 — Halves: the frozen-constant question (goals)

1H share of goals from goal-event times (minute ≤ 45), dev scored
window 2022/23–2024/25: **0.4539** (547 / 1,205 goals, 602 matches
used; awarded matches contribute nothing — their halves are
missing). Per-season shares: 2021/22 0.4415 (117/265), 2022/23
0.4200 (168/400), 2023/24 0.4892 (158/323), 2024/25 0.4585
(221/482), virgin 2025/26 0.4804 (196/408), reserve 2026/27 0.4818
(53/110). The per-season wobble (0.42–0.49) is consistent with
binomial noise around the constant (per-season SE ≈ 0.025–0.03).

Per-match variance test (dev, scored matches with ≥1 goal, n=518):
observed variance of the per-match 1H share = 0.1424; binomial-noise
expectation E[var] = mean p(1−p)/goals = 0.1442; ratio 0.988;
implied true variance ≈ 0.0000, implied true SD ≈ 0.00pp. The
per-match 1H share variance is, within measurement error, EXACTLY
the binomial noise around a constant — there is no per-match signal
in the 1H share. The frozen-constant treatment is therefore the
correct one: **goals_1h_share = 0.4539**, applied at presentation
time only, never fitted per team or per match. (Same conclusion as
J1, LU and NI; the TN constant 0.4539 sits above NI's 0.4376 and
J1's 0.412.)

## F4 — Format, turnover, and the mover question

- Format: group era (2021/22–2023/24) then single table (2024/25+);
  14–16 teams; see DATA_UNDERSTANDING.md. One or two teams are
  promoted/relegated every season.
- Entrants by team id (Ligue II arrivals, not in the warehouse):
  2022/23 Stade Tunisien (102116), EO Sidi Bouzid (405956);
  2023/24 Gafsa (102103), Avenir de La Marsa (102105); 2024/25 AS
  Gabes (206148), JS Omrane (1669235); 2025/26 JS Kairouanaise
  (177179); 2026/27 PS Sakiet Eddaïer (2147000). Exactly 1–2 per
  season; every one arrives from Ligue II, which is NOT in the
  warehouse.
- **X2 mover offset: not estimable.** There is no sibling Tunisian
  league in the warehouse (only FotMob id 544 for Tunisia), so no
  in-warehouse prior-tier history exists for any Tunisian club and
  no mover tilt can be estimated from transitions. No ENTRANT arm.
- **SHRINK expectation:** the sanctioned G-J2-lesson variant is
  expected to be numerically identical to Gate Zero in this league:
  no team has 1–5 prior in-league matches in any scored season's
  training data (entrants have n=0; incumbents have n≥26 per prior
  season, i.e. n≥52 for a two-season fit) — the dev run states the
  fact mechanically either way.

## F5 — What does not exist (negative findings)

- SOT / corners / total shots: no stats feed and no shotmap in any
  of the 1,060 payloads, in any season. No candidate can be built;
  no virgin window contains these targets.
- Cards: no yellow-card data anywhere (events carry Red/YellowRed
  only, 241 events in 216 matches — fragmentary, not a target).
  Referee identity never present (empty text in all 1,060
  payloads), so no referee strictness trait.
- xG: absent in every season — the goals model is goals-only
  throughout (the reference blend's documented fallback).
