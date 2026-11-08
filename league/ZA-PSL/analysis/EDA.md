# Step 3 — EDA: ZA-PSL

All figures from `eda_numbers.json` (computed by `eda_compute.py` from the
league CSV; coordinator spot-verified against the raw payloads).

## Levels by season

| Season | Goals/match | OU2.5 over | SOT | Corners | Cards (stats) | Total shots |
|---|---|---|---|---|---|---|
| 2021/2022 | 1.996 | 0.342 | — | — | — | — |
| 2022/2023 | 2.096 | 0.342 | 7.19 | 9.03 | 2.23 | 22.79 |
| 2023/2024 | 2.033 | 0.342 | 6.87 | 8.76 | 3.75 | 21.70 |
| 2024/2025 | 2.014 | 0.310 | 7.01 | 8.91 | 3.75 | 21.89 |
| 2025/2026 (virgin) | 2.013 | 0.304 | 7.35 | 8.71 | 3.30 | 22.58 |

This is a **low-event league on every market**: goals ≈ 2.0/match (J1
≈ 2.6–2.8, TH 2.7–3.1), SOT ≈ 7.0, corners ≈ 8.8, total shots ≈ 22, and a
very high draw rate (pooled home/draw/away ≈ 0.39/0.35/0.26 — the
2021/2022 draw rate is 0.383). Home goal advantage is small (+0.20 to
+0.30 goals/match by season). Levels are remarkably stable across
seasons; the two level breaks are recording artefacts, not football:
stats cards jump 2.23 → 3.75 between the seed and the scored dev seasons
(Step 1), and the virgin cards level (3.30) sits below the dev seasons —
the cards gate will judge that mechanically.

## Trait reliabilities (split-half by team-season, pre-virgin seasons, r)

| Trait | For | Against |
|---|---|---|
| Goals | 0.480 | 0.217 |
| SOT | 0.607 | 0.340 |
| Corners | 0.249 | 0.567 |
| Total shots | 0.751 | 0.630 |
| Yellow cards (stats) | 0.578 | 0.608 |
| Possession | 0.847 | 0.847 |
| Big chance | 0.552 | 0.442 |
| Opp-box touches | 0.651 | 0.725 |

Team identity carries real signal for SOT, total shots, cards, possession
and opp-box touches. Corners-for is the weak trait here (0.249) while
corners-against is solid (0.567) — the corners gate will judge whether
the production pattern still extracts anything. Goals-against (0.217) is
weak. Referee strictness is noise: split-half r = **0.080** over 10
referees / 213 matches with referee text — and virgin referee coverage
is 13/240, so X8 fails on both legs (Step 5).

## Halves (split-era dev seasons; period splits n = 507, goals n = 607 via HT events)

| Market | 1H share | Obs. var | Noise var | True var |
|---|---|---|---|---|
| Goals | 0.4724 | 0.1347 | 0.1422 | −0.0075 (≈0) |
| SOT | 0.4736 | 0.0409 | 0.0433 | −0.0025 (≈0) |
| Corners | 0.4679 | 0.0335 | 0.0336 | −0.0001 (≈0) |
| Total shots | 0.4584 | 0.0130 | 0.0121 | +0.0009 (≈0) |
| Yellow cards | 0.3253 | 0.0806 | 0.0755 | +0.0051 (small) |

Per-match 1H share variance is ≈ pure noise for goals/SOT/corners/shots —
the frozen-constant treatment is correct, exactly as in J1, TH and the
top-5 audit. Cards show a small positive true variance but the programme
rule is unchanged: frozen constant, presentation only. Constants frozen
in `config.yaml` / FEATURES: goals 0.4724, SOT 0.4736, corners 0.4679,
total shots 0.4584, yellow cards 0.3253. (The goals/SOT/corners 1H shares
≈ 0.47 are high by programme standards — this league's first halves are
relatively eventful — but they are constants, not features.) Every
market has a legitimate split source in this league, so no market is
FT-only.

## Entrants (X2 descriptives — previous tier NOT observed)

No South African second tier exists in the warehouse, so an entrant's
previous-tier record cannot be measured. Entrants (team ids absent the
previous season) in the pre-virgin window, n = 5 (Richards Bay 2022/2023;
Cape Town Spurs, Polokwane City 2023/2024; Marumo Gallants, Magesi FC
2024/2025): first-season GF gap **−0.271**/match and GA gap
**+0.147**/match vs the league mean — the standard promoted-club pattern
in direction (score less; concede more, though the concede gap is
smaller and noisier than TH's +0.503). This supports the sanctioned
SHRINK arm for goals (no hard-coded offset; X2's tier offset itself is
not estimable here and is dropped — Step 5).

## Cards artefact

See Step 1 for the full table. Headline: dev-era AND virgin-era events
carry no plain yellows (unified mean ≈ 0.05 vs stats 3.30–3.75); full
yellow events exist only in the confirmatory season, where stats
undercount unified mildly (3.205 vs 3.370). Frozen target: stats
yellows in dev and virgin; no virgin unified sensitivity exists.

## Line choice (scored dev seasons only, 2023/2024–2024/2025, n = 448)

Over-rates closest to 0.50: SOT **6.5** (0.536; 7.5 is 0.406, 5.5 is
0.679), corners **8.5** (0.542; 9.5 is 0.388), cards **3.5** (0.526, n =
447; 4.5 is 0.320), total shots **21.5** (0.522; 22.5 is 0.429). Goals
primary line is the standard OU 2.5 (dev over-rate 0.332 over
2022/2023–2024/2025). This league's levels are far below the J1/TH
reference points, so every ladder is shifted down accordingly — the
programme rule (line closest to a 0.50 over-rate on scored dev) is what
fixes them, not the reference leagues' lines.
