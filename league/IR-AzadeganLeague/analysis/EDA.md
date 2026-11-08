# IR Azadegan League — exploratory findings

All figures below are descriptive measurements from `eda_summary.json`
(`compute_summaries.py`, read off the built CSV); no model is fitted
and no virgin outcome is used for arm selection. 2025/2026 levels are
design-level aggregates only. Played n = 1,562 (the two never-played
placeholder rows are excluded everywhere).

## F1 — levels and home advantage

| season | n | goals | home goals | away goals | H/D/A % | BTTS % | over 2.5 % | over 3.5 % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2021/2022 | 305 | 1.97 | 1.17 | 0.80 | 42.6 / 36.7 / 20.7 | 40.7 | 33.4 | 13.8 |
| 2022/2023 | 272 | 1.90 | 1.21 | 0.69 | 44.1 / 36.4 / 19.5 | 35.7 | 31.6 | 14.3 |
| 2023/2024 | 306 | 1.94 | 1.17 | 0.77 | 47.1 / 29.7 / 23.2 | 35.3 | 31.7 | 11.4 |
| 2024/2025 | 306 | 1.77 | 1.04 | 0.73 | 37.9 / 37.9 / 24.2 | 32.4 | 25.2 | 11.1 |
| 2025/2026 | 305 | 1.60 | 0.91 | 0.70 | 39.3 / 38.0 / 22.6 | 30.2 | 22.6 | 6.9 |
| 2026/2027 (partial, n=68) | 68 | 1.79 | 1.03 | 0.77 | 38.2 / 35.3 / 26.5 | 33.8 | 29.4 | 11.8 |

Pooled dev (2021/2022–2024/2025, n = 1,189): 1.89 goals/match,
home win 42.9%, draw 35.2%, over-2.5 30.4%. Scored dev
(2022/2023–2024/2025, n = 884): 1.87 goals/match, over-2.5 29.4%
(260/884). Home advantage (home minus away goals per match) runs
+0.38 / +0.52 / +0.39 / +0.31 in the dev seasons — a normal home
edge, carried mostly by home attack.

Two things stand out against the program's reference points (J1
~2.7 goals/match, Tweede Divisie 3.24, Eredivisie ~3.1):

1. **Azadegan is one of the lowest-scoring leagues in the program**
   (dev 1.89), and it is getting lower: goals/match falls in every
   step from 2023/2024 (1.94) through the virgin season (1.60), and
   the over-2.5 rate falls with it (31.7% → 25.2% → 22.6%). The
   virgin season is the lowest-scoring complete season in the
   corpus by a clear margin. Any model fitted on dev seasons will
   face a virgin window drawn from a lower-scoring regime — that is
   exactly what the calibration leg is for, and it is why the
   virgin must stay the most recent complete season rather than
   being swapped for a friendlier one.
2. **Draws are frequent** (35.2% pooled dev, 38.0% in the virgin
   season) and home wins modest — the 1X2 distribution is flatter
   than in most leagues, which compresses what ratings can win
   over climatology on RPS.

## F2 — team-trait reliability (goals)

Pooled split-half r across team-seasons (min 8 matches):

| trait | chronological split r | random split-half, 60 reps (mean, range) |
|---|---|---|
| goals for | **0.272** (n = 105 team-seasons) | 0.380 (0.24–0.54) |
| goals against | **0.511** (n = 105) | 0.528 (0.43–0.67) |

Season-by-season chronological r (min 8 team rows): GF
0.40 / 0.66 / 0.69 / 0.12 / 0.46 (2021/2022–2025/2026; 2026/2027
partial −0.21, meaningless at 9 rounds); GA 0.72 / 0.61 / 0.40 /
0.81 / 0.52 (partial 0.07).

Verdict: **MIXED — GA is SIGNAL, GF is WEAK.** Defensive team
quality persists across a season about as well as in J2/J3
(0.62–0.68 pooled there); attacking quality is much less stable
here (J2/J3 GF r = 0.66–0.69; Azadegan 0.27 chronological, 0.38
random-split). A scores-only ratings fit has real signal — carried
disproportionately by the defensive side — but less than in most
program leagues, and the per-season GF numbers swing wildly
(0.12 in 2024/2025, 0.69 in 2023/2024). The DC fit's attack
ratings will be noisier here than the program is used to; the dev
gate, not optimism, decides whether that is enough.

## F3 — half shares and true variance (goals only)

Goals from events across all seasons: 1H share **0.4148** (ratio of
sums, 1,152/2,777; n = 1,534 matches with a usable HT split).
Per-season shares: 0.426 / 0.433 / 0.399 / 0.382 / 0.427 / 0.459
(partial). Observed per-match share variance 0.14056; binomial
noise floor (pooled league share, per-match) 0.14468; **true
variance −0.00411**, i.e. at or below zero. Team split-half r of
the 1H share is **−0.083** (n = 90 team-seasons).

Conclusion, same as every league in the program: the per-match 1H
share is pure noise around a frozen league constant. The constant
is **0.415** for reporting splits only; no team or per-match halves
feature exists. (SOT/corners/cards/total-shots half shares do not
exist — no stats feed.) The per-season wobble (0.382 in 2024/2025
vs 0.433 in 2022/2023) is sampling noise on ~200–260 matches a
season, consistent with the variance decomposition — not a trend
to model.

## F4 — entrants and the (non-)case for a mover prior

Entrants per transition (clubs absent from this league the prior
season) and their first-season gaps vs the league team-goal mean:

| transition | entrants | GF gap | GA gap |
|---|---|---:|---:|
| into 2022/2023 | Chadormalu Ardakan SC, Chooka Talesh, Darya Caspian Babol, Fajr Sepasi, Shahin Bandar Ameri, Van Pars Naqsh Jahan | −0.016 | +0.124 |
| into 2023/2024 | Ario Islamshahr, Damash, Mes Kerman, Mes Sungun, Naft Gachsaran, Naft Masjed Soleyman FC | −0.005 | −0.059 |
| into 2024/2025 | Beasat Kermanshah, Naft Bandar Abbas, Niroye Zamini, Paykan, Sanat Naft Abadan, Shahrdari Nowshahr | +0.028 | −0.168 |
| into 2025/2026 (virgin transition, descriptive only) | FC Fard, Havadar SC, Nassaji Mazandaran FC, Navad Urmia, Shenavarsazi Qeshm | +0.034 | −0.002 |
| into 2026/2027 (partial, descriptive only) | Foolad Khuzestan B, Mes Rafsanjan, Naft Masjed Soleyman FC, Shahin Bandar Ameri | +0.186 | −0.067 |

Pooled over the three **dev** transitions only (n = 18 entrant
teams, 600 entrant team-matches; the virgin transition is
deliberately excluded from any frozen magnitude so no virgin
outcome sets an arm parameter): GF gap **+0.002**, GA gap **−0.034**.

Verdict: **NO SIGNAL — there is no entrant prior to fit.** Entrants
— a mix of promoted lower-tier clubs and relegated Persian Gulf
sides — perform at the league mean on arrival, on both sides of
the ball, in every transition. The per-transition signs flip and
the pooled gaps are two orders of magnitude smaller than J1's
±0.5. Combined with the brief's scope (no parent/sibling tier for
an X2 prior), **X2 is DROPPED, not gated**: there is no parameter
here, and inventing one from the Persian Gulf corpus (see
DATA_UNDERSTANDING.md §4) would contradict both the brief and
this measurement. Entrants start at the league mean in every arm,
exactly as Gate Zero specifies.

## F5 — format churn

42 distinct team ids across six seasons; only ~11–12 clubs are
present in most seasons. Six clubs turn over per season on
average, so at every season start roughly a third of the league
has no in-league history and starts at the league mean under
season-blocked fitting. That is a structural feature of this
league, not a data gap: the SHRINK arm (pre-registered, expected
vacuous under season-blocked fitting per the NLTD precedent) is
run so the fact is measured, not assumed. The 17-team 2022/2023
season and the 16-team 2026/2027 partial are complete as played;
nothing is imputed for absent clubs.

## F6 — cards (reds only, no yellows)

Zero Yellow events in 1,564 matches. Red-family events total 133
(122 Red + 11 YellowRed) in 117 matches — 0.085/match. Team
split-half r for reds is **0.071** pooled (per-season −0.34 /
−0.16 / +0.51 / +0.08 / −0.09 — sign-flipping noise). No cards
candidate of any kind is buildable: there is no yellows target,
and reds are a rare-event count with no reliability evidence. Reds
are not a target and not a covariate.

## F7 — missing xG/shotmap and target implications

There is no expected-goals key, no shotmap, no stats block, no
lineup, and no referee text in any season. xG blend, set-play xG,
xG/shot, xGOT, box touches, possession, referee strictness, and
lineup/absence features are all unavailable. SOT, corners, cards,
and total shots have no target in any season, including the virgin
window — none of them is a candidate, and none can become one
without new data. The goals candidate is the only buildable one,
and it is goals-only by necessity: the reference blend's xG half
never exists here.
