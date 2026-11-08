# Phase 3 — EDA: Costa Rica Primera Division (2021/2022 – 2026/2027)

Computations: `eda.py` (digest in `eda_summary.json`, inventory in `inventory_summary.json`).
Tables: Phase 2 outputs in `data/`. Sample sizes: 1,350 matches all, 1,290 regular-season;
reliable-cards regular era (2023/2024+) n = 798. Every pattern below carries a verdict under the
halves-audit standard: **a trait is a signal candidate only if it reproduces on disjoint halves of
the same teams' matches (split-half) or survives a variance decomposition against its sampling-noise
floor.** Split-half figures are career-pooled per team (≥24 matches/team, 60 random splits averaged,
odd/even split included); with 14–15 teams per trait, an |r| under ~0.3 has a wide confidence interval
and is treated as weak evidence at best.

## Levels (regular season unless stated)

| Quantity (per match) | CR pooled | 21/22 | 22/23 | 23/24 | 24/25 | 25/26 | 26/27* |
|---|---|---|---|---|---|---|---|
| Goals | 2.66 | 2.73 | 2.89 | 2.69 | 2.47 | 2.47 | 2.76 |
| Home goals / away goals | 1.53 / 1.13 | 1.64 / 1.09 | 1.67 / 1.22 | 1.57 / 1.13 | 1.40 / 1.07 | 1.38 / 1.09 | 1.51 / 1.25 |
| Home win / draw / away win % | 46.8 / 25.7 / 27.5 | 48.9 / 27.3 / 23.9 | 49.1 / 23.7 / 27.2 | 47.3 / 23.9 / 28.8 | 43.9 / 28.2 / 27.9 | 43.8 / 27.6 / 28.6 | 48.8 / 18.8 / 32.5 |
| BTTS % / Over 2.5 % | 52.6 / 50.5 | 54.5 / 51.5 | 57.9 / 55.3 | 49.6 / 53.0 | 51.1 / 45.8 | 49.5 / 46.9 | 53.8 / 48.8 |
| Yellow cards | — (see F4) | 0.25† | 2.82† | 4.00 | 4.19 | 5.36 | 4.79 |
| Red cards | 0.22 | 0.18 | 0.30 | 0.21 | 0.26 | 0.17 | 0.19 |

\* 2026/2027 is an Aug–Nov segment only, NOT comparable to full seasons. † Card-feed broken (F4).

Dispersion (variance/mean of the match total): goals 0.91–1.13 by season, pooled 0.99 (near-Poisson);
yellows 1.19 on the reliable era (mild overdispersion — Negative Binomial sizes will be large but finite,
the same regime as the top-5 production markets).

Context vs the J.League reference points (J1: 2.55 goals, 2.34 yellows, HW 41.3%, home edge +0.20):
Costa Rica scores slightly more (2.66), is far less disciplined on the reliable era (4.47 yellows vs 2.34),
wins at home far more often (46.8% vs 41.3%) with a much bigger home edge (+0.41 goals vs +0.20).
Any ported model whose level prior comes from Europe or Japan is wrong here by construction — which is
the empirical core of the 1-league-1-model decision.

## Findings

**F1 — League levels are league facts, and they drift by season.**
Goals by regular season: 2.73, 2.89, 2.69, 2.47, 2.47 (2.76 partial). Home advantage declines
steadily: +0.55, +0.45, +0.44, +0.33, +0.29 (+0.26 partial) — the early-seasons home edge is nearly
double the recent one. Yellows on the reliable era rise: 4.00 → 4.19 → 5.36 (4.79 partial); whether
the 2025/26 jump is a refereeing trend or a feed change is unknowable from this corpus — the per-season
fitted league means in the engines absorb it, and the virgin window (2024/25, 4.19) sits below the
2025/26 level, which the confirmatory read will have to reckon with.
Verdict: **SIGNAL** (descriptive fact). Design consequence: per-league fitting with time decay;
the DC home advantage is fitted per target season from the expanding window, so it tracks the drift.

**F2 — Team traits are reliable: a ratings fit has real signal.**
Split-half (career-pooled, regular season): goals-for r = 0.795 (odd/even 0.813), goals-against
r = 0.793 (0.823), n = 15 teams. Yellows-for r = 0.621 (0.559), yellows-against r = 0.614 (0.482),
n = 14 teams, reliable era only. These are as strong as, or stronger than, the J1 equivalents
(goals-for 0.76/0.80, yellows-for 0.66/0.51).
Verdict: **SIGNAL**. Design consequence: Dixon-Coles team ratings for goals and decayed team card
rates for yellows are both justified on this corpus.

**F3 — Halves are frozen constants, not team traits (the halves-audit standard, replicated).**
Goals 1H share (ratio of sums, HT present, regular): pooled **0.460** (n = 1,194 matches); per-season
0.436, 0.481, 0.437, 0.480, 0.475, 0.459. Variance decomposition: observed per-match share variance
0.1174 vs binomial noise floor 0.1185 → **true variance −0.0011 (≈ 0)**. Team split-half of the 1H share
r = 0.274 / 0.213 — weak and contradicted by the variance decomposition, exactly the J1 F3 pattern.
Yellows 1H share (reliable era): pooled **0.379** (n = 772); per-season 0.388, 0.360, 0.379, 0.410.
Observed variance 0.0735 vs noise floor 0.0704 → true variance +0.0032 (4% of the observed variance);
team split-half r = −0.460 / −0.101 — **negative**, i.e. no team trait at all. The small positive residual
is not a team property and does not license per-team halves modelling.
Verdict: **NOISE for per-match/per-team halves; SIGNAL for the frozen constants.** Design consequence:
halves presentation uses frozen constants only — goals 0.460, yellows 0.379. No halves modelling of any kind.

**F4 — Card-feed completeness: the reliable era starts 2023/2024.**
Monthly means pin it down: 2021/22 means 0.00–0.41 all year (221/280 zero-card); Apertura 2022/23
Jul–Oct means 0.11–0.35; the feed turns on Jan 2023 (Clausura monthly means 3.93–5.00) but stays
patchy — 14/132 regular matches zero-card (10.6%) against an NB-implied ~2% at mean 4.70, including
an 8-match zero cluster in Feb 2023 (rounds 5–10, spread across teams). From 2023/24 onward zero-card
rates are NB-consistent (≈4%: 12/264 in 2023/24, 11/262 in 2024/25, 1/192 in 2025/26).
Playoff card events are missing for 2021–2024 (29/60 zero-card, incl. all 6 Dec-2023 Final Stage matches).
Verdict: **SIGNAL** (a coverage fact). Design consequence: cards fitting uses 2023/2024 onward only;
2022/2023 is excluded from cards entirely (not even as warm-up — its false zeros would bias the NB-size
estimate). Cards dev = 2023/24 Apertura warm-up + 2023/24 Clausura scored (132 + 132 regular matches).

**F5 — Format and churn.**
One promotion/relegation per year 2022–2025 (Puntarenas FC in / Jicaral Sercoba out; AD Municipal
Liberia in / Guadalupe FC out; Santa Ana FC in / Municipal Grecia out). The 2025/26 shrink drops
Santos de Guapiles, AD Guanacasteca and Santa Ana FC and brings Guadalupe FC back (12 → 10 teams,
22 → 18 rounds). 2026/27 adds two brand-new ids (Inter San Carlos, Escorpiones). Each dev/virgin target
season has exactly one team with zero prior regular-season matches (the promoted side); no team ever
has 1–9 prior matches (thin-history table in `eda_summary.json`). 2022/23 Apertura rounds 17–22 and
two 2024/25 Clausura round-22 matches are warehouse gaps.
Verdict: **SIGNAL** (descriptive fact). Design consequence: new teams start at the league mean in
Gate Zero (already the reference behaviour); the G-J2 thin-history shrinkage variant is vacuous here —
no team sits in the 1–9-match band it was designed for — so G-CR ships Gate Zero only (see FEATURES.md).

**F6 — Referee identity is absent.**
`Referee.text` is empty in 1,328/1,350 matches (0 non-empty in 5 of 6 seasons; 22 in 2025/26 only).
Verdict: **NO DATA**. Design consequence: no referee feature, no referee arm; K-CR ships Gate Zero only.
The operational check in the verdict records this plainly: even the 22 known 2025/26 referees are
post-match snapshots with no publication timestamp.
