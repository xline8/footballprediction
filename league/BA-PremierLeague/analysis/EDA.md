# Phase 3 — EDA: BA-PremierLeague

All numbers measured on `league/BA-PremierLeague/data/ba_matches.csv`
(1,036 matches; awarded matches excluded from rate computations
where noted — pooled rates below exclude the 4 awarded matches only
where the text says so; the level table uses all matches because the
awarded scorelines are 3-0/0-3 and move the means by <0.01).
Summary JSON: `eda_summary.json`.

## F1 — Levels per season (goals)

| Season | n | Teams | Mean goals | Home | Away | HW% | D% | AW% | Over 2.5 | BTTS |
|---|---|---|---|---|---|---|---|---|---|---|
| 2021/2022 | 198 | 12 | 2.28 | 1.38 | 0.90 | 44.9 | 33.8 | 21.2 | 37.4 | 44.9 |
| 2022/2023 | 198 | 12 | 2.47 | 1.52 | 0.95 | 52.0 | 23.2 | 24.7 | 43.9 | 43.9 |
| 2023/2024 | 198 | 12 | 2.78 | 1.69 | 1.10 | 55.1 | 19.2 | 25.8 | 51.0 | 46.5 |
| 2024/2025 | 198 | 12 | 2.67 | 1.46 | 1.21 | 45.5 | 18.7 | 35.9 | 50.0 | 43.4 |
| 2025/2026 | 180 | 10 | 2.16 | 1.28 | 0.88 | 47.2 | 26.1 | 26.7 | 37.8 | 36.1 |
| 2026/2027* | 64 | 10 | 2.58 | 1.45 | 1.13 | 46.9 | 28.1 | 25.0 | 42.2 | 51.6 |
| Pooled | 1,036 | — | 2.48 | 1.48 | 1.01 | 48.8 | 24.4 | 26.7 | 44.0 | 43.6 |

\* In progress (rounds 1–13). Levels move season to season
(2.16–2.78 goals/match) — per-league fitting with time decay is
justified; no single global level. Home advantage is strong and
stable: home goals exceed away by 0.40–0.59 every season
(pooled +0.47). For reference, J1 runs ~2.6 goals/match with a
smaller home edge; BA is a lower-scoring, more home-tilted league
with a markedly higher draw rate in 2021/22 (33.8%).

## F2 — Team traits are reliable (split-half by season)

Per season, each team's matches are split at random into two halves;
the correlation of the team's per-match rate across halves:

| Season | GF r | GA r |
|---|---|---|
| 2021/2022 | 0.739 | 0.495 |
| 2022/2023 | 0.627 | 0.435 |
| 2023/2024 | 0.565 | 0.671 |
| 2024/2025 | 0.445 | 0.885 |
| 2025/2026 | 0.589 | 0.617 |
| Mean (complete seasons) | **0.593** | **0.621** |
| 2026/2027 (partial) | 0.328 | 0.636 |

**SIGNAL.** Goals-for and goals-against team traits are stable at
~0.6 split-half — comparable to J1/J2 (0.62–0.69) given the shorter
seasons (33–36 matches/team vs 34–38). A scores-only ratings fit
has real signal; this is the entire justification for building G-BA.

Team tiers (complete seasons 2021/22–2025/26, per-match GF−GA):
Zrinjski Mostar **+1.39** (2.01 GF / 0.62 GA), Borac Banja Luka
**+0.95**, FK Sarajevo +0.47, Velež +0.22, Željezničar +0.11, then a
long tail to GOSK Gabela −1.12 and Zvijezda 09 −1.18. The top-to-
bottom gap is ~2.5 goals/match — a steep hierarchy, and the reason
newly promoted clubs (who arrive from a tier with no warehouse
sibling) are the thin-data risk the SHRINK arm addresses.

## F3 — Half shares: frozen constant, no per-team signal

- Pooled goals 1H share (961 matches with an HT score):
  **0.4493** (1,156 1H goals / 2,573 FT goals). By complete season:
  0.470, 0.434, 0.456, 0.453, 0.463. The partial 2026/27 reads
  0.376 on n=57 — sampling noise on a small window, not a regime
  break (it is not used to set the constant; the constant pools
  all HT-present matches, as the J1 design does).
- Variance decomposition: observed per-match 1H-share variance
  0.1296 vs binomial-noise expectation 0.1275 (p(1−p)/G averaged
  over matches with G>0). Excess variance 0.0021 → implied true
  SD ≈ 0.046 (4.6pp).
- Team 1H-share split-half r by season: −0.16, −0.58, +0.51,
  +0.44, −0.12 (mean ≈ +0.02, sign-flipping) — **no stable
  per-team trait**.
- **Verdict: NOISE, frozen constant.** Halves presentation uses
  the single frozen constant 0.4493 (1H λ = 0.4493·FT λ,
  2H λ = 0.5507·FT λ). No per-team or per-match half-share
  modelling, exactly as the J1 book was closed.

## F4 — Movers: no estimable tier offset (see FEATURES X2)

No Bosnian second tier exists in the warehouse, so no mover prior
can be estimated from a sibling league. Within-league, 2 clubs
change per season on average, but a promoted club's arrival
deviation cannot be estimated without its feeder-tier history.
The thin-data treatment is SHRINK (ratings shrunk toward the
league mean for clubs with <6 prior in-league matches), not a
mover offset.

## F5–F9 — Not testable in this league

- Set-play xG (F5 analogue), xG/shot (F6), xGOT (F7), box touches
  (F9): no stats, no shotmap — **no data, checks not run**.
- Referee strictness (F8 analogue): referee field empty 1,036/1,036
  — **no data**.
- SOT / corners / cards traits: targets do not exist — **no data**.

## F13 — Coverage verdict (feasibility)

| Market | Target exists? | Virgin window has target? | Candidate? |
|---|---|---|---|
| Goals (G-BA) | Yes — FT score, all seasons | Yes — 2026/27 in progress, n=64 | **Yes** |
| SOT (S-BA) | No (stats null, shotmap empty) | No | **No — not buildable** |
| Corners (C-BA) | No | No | **No — not buildable** |
| Cards (K-BA) | No (0 Yellow events; no stats) | No | **No — not buildable** |
| Total shots (T-BA) | No (shotmap empty) | No | **No — not buildable** |

Cards note: the only card signal is 205 red-family events
(0.20/match; 77 YellowRed + 128 Red). A reds-only target is a
rare-event count with no reliability evidence and no production
analogue; it is not a candidate.

## F12 — Game state (descriptive only)

HT scores exist for 93% of matches (see F3). No other in-match
quantities exist (no substitutions, no shot timelines). Nothing
here is a pre-match feature.
