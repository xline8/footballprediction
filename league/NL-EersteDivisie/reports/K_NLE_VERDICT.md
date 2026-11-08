# K-NLE Verdict — Eerste Divisie cards model

Date: 2026-11-09. Branch `build/nl-eerste`. Prereg:
`league/NL-EersteDivisie/prereg/PREREG_K_NLE.md` (commit f267312,
frozen before any fitting). Engine:
`league/NL-EersteDivisie/engine/cards/`. Implementation by Codex
(gpt-5.6-luna); pooled dev LLs were recomputed independently by
the coordinator from the per-match dev predictions CSV and the
constant base rate was recomputed from the league CSV.
Calibration = actual − predicted. Target: event-unified yellows
(stats-vs-events mismatch on 10.89% of matches pooled — see
PREPROCESSING.md; the artefact pattern seen in 7 other leagues
appears here too, milder: stats undercount in five of six
seasons, reversing in the virgin season).

## Verdict: FAIL — both arms die at the dev gate (naive leg); virgin NOT read

The referee arm (X8) improves on Gate Zero in **every** dev
season and beats the base rate — and still loses to the naive
trailing-10, by 0.0017. Gate Zero loses to both baselines. Under
the frozen legs both arms are dead, the virgin window was **not
read**, and nothing ships.

## Dev results (per-match walk-forward, warm-up 2021/2022, scored 2022/2023–2024/2025, n = 1140)

LL@3.5 (binary log-loss on P(over 3.5)):

| Season | Gate Zero | X8 (referee) | Base (league-mean NB) | Naive t-10 |
|---|---|---|---|---|
| 2022/2023 | 0.7215 | 0.7160 | — | — |
| 2023/2024 | 0.6950 | 0.6862 | — | — |
| 2024/2025 | 0.6970 | 0.6810 | — | — |
| **Pooled** | 0.7045 | **0.6944** | 0.6983 | **0.6927** |

Dev gate (pooled LL@3.5 beats BOTH baselines): Gate Zero **FAIL**
(0.7045 > 0.6983 and > 0.6927). X8 **FAIL** (0.6944 > naive
0.6927, by 0.0017; it beats the base). The outcome is invariant
to the base-rate definition: against the coordinator's constant
prior-seasons over-rate (pooled 0.7055) both arms pass the base
leg and still fail the naive leg.

Two documentation notes on the reference architecture, stated
plainly:

- The J1-family port this engine copies estimates the NB size
  from the **warm-up window** per method (here: model 19.33,
  base 17.24, naive 15.51) rather than using production's frozen
  112.39. The prereg text (inherited from the NL prereg) said
  112.39; the port's warm-up-estimated mechanism is what Gate
  Zero means in every league built from this port (J1, NL
  included), the estimation touches warm-up data only, and it is
  applied symmetrically to arms and baselines. The engine follows
  the port; the prereg sentence was the error.
- X8 fallback behaviour in dev: matches with an empty referee
  string or a referee with < 8 prior in-league matches take
  factor 1.0 (Gate Zero), never an imputation — per the prereg's
  operational condition.

Reading: the referee trait is real in this league (split-half
r = 0.420, coverage 95.8–100% in scored dev seasons) and X8
captures something genuine (+0.0101 pooled over Gate Zero, wins
all three seasons head-to-head). What neither arm can beat is
the trailing-10 team card means — Eerste Divisie card levels are
team-persistent enough (cards-for/against reliability ~0.47)
that the naive is the hurdle, and the ratings+referee stack
falls 0.0017 short of it. That is a finding, not a near-miss to
be rescued: no rescue arm is permitted under this prereg.

## Virgin window — NOT read

No arm passed dev. No virgin metrics, no fitted params, no
predictions file for K-NLE. 2026/2027 was never touched.
