# Phase 3 — EDA: Uzbekistan Superliga 2026 (n=215, scores-only)

Computations: `analysis/eda.py` (digest in `analysis/eda_summary.json`).
Charts: `analysis/charts/` (regenerate with `make_charts.py`).
Single partial season; every number below is descriptive — no model was
fitted and no gate was run.

## Levels (2026, rounds 1–27)

| Quantity (per match) | UZ 2026 | J1 reference (pooled, n=2,091) |
|---|---|---|
| Goals | 2.628 (565 total) | 2.55 |
| Home goals / away goals | 1.391 / 1.237 | 1.38 / 1.18 |
| Home win / draw / away win % | 41.4 / 23.3 / 35.3 | 41.3 / 26.8 / 31.9 |
| BTTS % / Over 2.5 % | 56.3 / 53.5 | 50.4 / 47.0 |
| Over 1.5 % / Over 3.5 % | 71.6 / 27.0 | — |
| Home clean sheet % / away clean sheet % | 26.5 / 25.6 | — |

UZ scores a touch more than J1 (2.63 vs 2.55) and is more open at the
top end: Over 2.5 at 53.5% vs J1's 47.0%, BTTS 56.3% vs 50.4%. Home
advantage is ordinary (home goals 1.39 vs away 1.24; home win 41.4% vs
J1 41.3%). The draw rate (23.3%) is a little low vs J1 (26.8%) — on
n=215 the SE is ~2.9pp, so this is within noise, not a finding.

Goal distribution (total goals per match): 0: 18, 1: 43, 2: 39, 3: 57,
4: 32, 5: 16, 6: 6, 7: 3, 8: 1. No excess of goalless matches.

## Round-by-round

Goals per match by round swings 1.71–3.63 (round 20: 3.63, round 26:
1.71 on 7 matches) — round-level noise on n=7–8 matches per round
(SE ~0.6 goals/match per round). No trend across the season is claimed.
See `charts/goals_per_round.png`.

## Team traits (attack / defence)

Per-team GF/GA per match (26–27 matches each): strongest attack
Neftchi Fargona 2.35 GF/match, Navbahor Namangan 1.70, Pakhtakor
Tashkent 1.78; weakest Mashal Muborak 0.44, Surkhon-2011 0.74, Xorazm
0.85. Best defence Neftchi 0.88 GA/match, Nasaf Qarshi 0.89, Navbahor
0.93; worst Sogdiana 1.96, Mashal 1.96, Bunyodkor 1.65.
See `charts/team_attack_defence.png`.

## Split-half trait reliability (within 2026: rounds 1–13 vs 14–27)

The J1 checklist replicated on the only split available — first vs
second half of the single season, n=16 teams:

- Team GF/match: Pearson r = **0.696** — attack rates reproduce across
  halves; a real team trait at this sample size.
- Team GA/match: Pearson r = **0.179** — defence rates barely reproduce;
  weak evidence at n=16 (SE of r ≈ 0.24), consistent with defence being
  noisier and with only ~13 matches per team per half.

These numbers describe the 2026 season only. They do not rescue
buildability: a trait can be reliable within a season and still have no
gateable window, because there is no second season to train-then-test
against. See `charts/split_half_attack_reliability.png`.

## Halves (goals): the frozen-constant question

HT scores exist for 99/215 matches (rounds 10, 14–27): HT goals 128 vs
FT goals 279 in the same matches — HT share **0.4588**, HT goals 1.293
per match. This is a descriptive measurement on late-season-only
coverage, NOT a frozen constant: the 116 matches without an event feed
are mostly rounds 1–13, so the 99-match subset is not a representative
sample of the season, and no halves presentation ships under this
verdict. For reference, J1's frozen goal 1H share is 0.412; UZ's
0.459 on n=99 (SE ≈ 0.03) is higher, but the coverage bias forbids any
conclusion.

## Referee / cards

No referee in any payload (blank 215/215); 29 Card events in 99
matches with an event feed. No referee strictness or card level can be
measured. Cards are not a target.

## What does not exist (all confirmed from payloads)

Shots, shots on target, corners, xG, referee effects — absent in
215/215 payloads. SOT / corners / cards / total shots have no target
and no reliability check to run.
