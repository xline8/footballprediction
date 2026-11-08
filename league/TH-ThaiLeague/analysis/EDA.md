# Step 3 — EDA: TH-ThaiLeague

All figures from `eda_numbers.json` (computed by `eda_compute.py` from the
league CSV; coordinator spot-verified against the raw payloads).

## Levels by season

| Season | Goals/match | OU2.5 over | SOT | Corners | Cards (stats) | Total shots |
|---|---|---|---|---|---|---|
| 2021/2022 | 2.562 | 0.492 | — | — | — | — |
| 2022/2023 | 2.696 | 0.492 | 8.42 | 9.83 | 3.06 | 24.75 |
| 2023/2024 | 3.067 | 0.604 | 9.32 | 9.67 | 4.34 | 26.82 |
| 2024/2025 | 3.050 | 0.571 | 9.64 | 9.71 | 4.10 | 26.48 |
| 2025/2026 (virgin) | 2.675 | 0.467 | 9.03 | 9.64 | 4.09 | 26.43 |

(Cards 2024/2025 mean is 4.096; the stats-card level jumps from 3.06 in
2022/2023 to ≈4.1–4.3 afterwards — a level shift between the first stats
season and the rest, visible in both stats (3.06 → 4.34 → 4.10) and in the
virgin (4.09). The walk-forward design, which re-fits state continuously,
is the mitigation; no rescaling is applied.)

Reference points: goals 2.68–3.07/match is a normal-to-high scoring league
(J1 ≈2.6–2.8); the virgin season is the lowest-scoring of the stats era
(2.675, OU2.5 over-rate 0.467 vs dev 0.556) — a level drop the goals gate
will judge mechanically. Home win/draw/away pooled: 0.464/0.269/0.266;
home goal advantage +0.44 goals pooled. SOT home advantage +1.15,
corners +0.89, total shots +2.82, cards −0.24 (away teams carded more).

## Trait reliabilities (split-half by team-season, pre-virgin seasons, r)

| Trait | For | Against |
|---|---|---|
| Goals | 0.734 | 0.374 |
| SOT | 0.694 | 0.594 |
| Corners | 0.690 | 0.506 |
| Total shots | 0.687 | 0.771 |
| Yellow cards (stats) | 0.522 | 0.380 |
| Possession | 0.849 | 0.849 |
| Big chance | 0.564 | 0.493 |
| Opp-box touches | 0.819 | 0.751 |

Every count trait is genuinely reliable (r ≥ 0.37) — team identity carries
real signal in this league at career scale. Referee strictness is the
exception: split-half r = **0.199** over 27 referees / 669 matches — weak,
and the virgin referee coverage collapse (9/240) kills X8 regardless.

## Halves (split-era dev seasons; n = 529 split matches, goals n = 672 via HT events)

| Market | 1H share | Obs. var | Noise var | True var |
|---|---|---|---|---|
| Goals | 0.4402 | 0.1058 | 0.1085 | −0.0028 (≈0) |
| SOT | 0.4447 | 0.0320 | 0.0313 | +0.0007 (≈0) |
| Corners | 0.4622 | 0.0284 | 0.0294 | −0.0010 (≈0) |
| Total shots | 0.4522 | 0.0101 | 0.0099 | +0.0003 (≈0) |
| Yellow cards | 0.3076 | 0.0730 | 0.0650 | +0.0080 (small) |

Per-match 1H share variance is ≈ pure noise for goals/SOT/corners/shots —
the frozen-constant treatment is correct, exactly as in J1 and the top-5
audit. Cards show a small positive true variance but the programme rule is
unchanged: frozen constant, presentation only. Constants frozen in
`config.yaml` / FEATURES: goals 0.4402, SOT 0.4447, corners 0.4622,
total shots 0.4522, yellow cards 0.3076. Every market has a legitimate
split source in this league, so no market is FT-only.

## Movers (X2 descriptives, vs Thai League 2 id 9498)

Entrants to Thai League 1 whose previous season is observed in the Thai
League 2 warehouse window (n = 6): first-T1-season GF gap **−0.262**/match
and GA gap **+0.503**/match vs the T1 mean — promoted clubs score less and
concede much more, the standard mover pattern (a further 9 entrants fall
outside the available T2 window; their gaps are similar: −0.328 / +0.342).
This justifies the sanctioned SHRINK arm for goals (no hard-coded offset).

## Cards artefact

See Step 1 for the full table. Headline: dev-era events carry no plain
yellows (unified mean ≈0.02–0.11 vs stats 3.06–4.34); virgin-era stats
undercount unified by ≈0.19/match. Frozen target: stats yellows; virgin
unified sensitivity preregistered in the cards prereg.

## Line choice (scored dev seasons only, 2023/2024–2024/2025, n = 480)

Over-rates closest to 0.50: SOT **9.5** (0.473; 8.5 is 0.602), corners
**9.5** (0.498), cards **4.5** (0.438; 3.5 is 0.619), total shots **26.5**
(0.494; 25.5 is 0.562). Goals primary line is the standard OU 2.5
(dev over-rate 0.556 over 2022/2023–2024/2025).
