# Phase 3 — EDA: AL-KategoriaSuperiore

All numbers measured on `league/AL-KategoriaSuperiore/data/al_matches.csv`
(969 matches; 955 regular-season after excluding the 14 playoff
matches — the level table below uses regular-season matches only,
because the playoffs are a different format; the virgin 2026/2027
row has no playoffs yet so it is unaffected).
Summary JSON: `eda_summary.json`.

## F1 — Levels per season (goals, regular season)

| Season | n | Teams | Mean goals | Home | Away | HW% | D% | AW% | Over 2.5 | BTTS |
|---|---|---|---|---|---|---|---|---|---|---|
| 2021/2022 | 180 | 10 | 2.27 | 1.27 | 0.99 | 41.1 | 29.4 | 29.4 | 37.2 | 45.0 |
| 2022/2023 | 180 | 10 | 2.22 | 1.23 | 0.98 | 40.0 | 27.8 | 32.2 | 38.3 | 45.6 |
| 2023/2024 | 180 | 10 | 2.28 | 1.19 | 1.09 | 38.9 | 28.9 | 32.2 | 38.9 | 45.0 |
| 2024/2025 | 180 | 10 | 2.22 | 1.24 | 0.98 | 41.1 | 36.7 | 22.2 | 40.6 | 50.6 |
| 2025/2026 | 180 | 10 | 2.21 | 1.25 | 0.96 | 42.2 | 31.1 | 26.7 | 35.6 | 47.2 |
| 2026/2027* | 55 | 10 | 2.58 | 1.45 | 1.13 | 47.3 | 23.6 | 29.1 | 47.3 | 58.2 |
| Pooled | 955 | — | 2.26 | 1.25 | 1.01 | 41.0 | 30.4 | 28.6 | 38.6 | 47.3 |

\* In progress (rounds 1–11). The five complete regular seasons are
remarkably stable (2.21–2.28 goals/match) — far more stable than BA
(2.16–2.78). Home advantage is steady: home goals exceed away by
0.10–0.27 every complete season (pooled +0.24). The virgin window is
running hot (2.58 on n=55) — a small-window fluctuation to watch, not
a level to fit on. For reference, J1 runs ~2.6 goals/match; Albania
is a lower-scoring, flatter league with a high draw rate (~30%).

## F2 — Team traits are WEAK (split-half by season)

Per season, each team's matches are split at random into two halves;
the correlation of the team's per-match rate across halves
(seed 7, BA chart order — GF all seasons, then GA):

| Season | GF r | GA r |
|---|---|---|
| 2021/2022 | 0.919 | 0.163 |
| 2022/2023 | 0.512 | 0.348 |
| 2023/2024 | 0.046 | 0.343 |
| 2024/2025 | 0.081 | −0.056 |
| 2025/2026 | −0.208 | −0.102 |
| Mean (complete seasons) | **0.270** | **0.139** |
| 2026/2027 (partial) | 0.068 | 0.867 |

**WEAK / MIXED.** The 5-season means (GF 0.27, GA 0.14) are far below
BA (0.59/0.62) and J1/J2 (0.62–0.69), and individual seasons
sign-flip — including a −0.21 GF season. Two caveats, stated plainly:
with only 10 teams per season a single season's split-half r has a
standard error of ~0.33, so one season proves nothing; but the
5-season mean is the evidence, and it says team traits in this league
are faint. This is consistent with the flat tiers below (top-to-bottom
gap ~1.0 goals/match, vs ~2.5 in BA): there is simply less team
signal to find. A scores-only ratings fit may still beat climatology
— home advantage alone is worth something, and the DC fit pools
across seasons with decay — but F2 does **not** justify the build
the way it did for BA. The dev gate is the real test; if Gate Zero
fails dev, G-AL fails with it.

Team tiers (complete seasons 2021/22–2025/26, regular season only,
per-match GF−GA): Partizani **+0.32** (1.31 GF / 0.98 GA), KF Tirana
+0.31, Vllaznia +0.27, Egnatia +0.18, Elbasani +0.18, Laçi +0.13,
Vora −0.03, Dinamo Tirana −0.06, Teuta Durrës −0.16, Flamurtari
−0.17, Kukesi −0.21, Skënderbeu −0.30, Bylis −0.37, KF Erzeni −0.56,
Kastrioti −0.65. The hierarchy is shallow and compressed — no
dominant club (nobody above +0.35) — which is why newly promoted
clubs (who arrive with no in-league history) are only a mild
thin-data risk here, and why the SHRINK arm is likely to be
degenerate in the same way it was for BA (see MODEL_DESIGN).

## F3 — Half shares: frozen constant, no per-team signal

- Pooled goals 1H share (875 regular-season matches with an HT
  score): **0.4267** (920 1H goals / 2,156 FT goals). By complete
  season: 0.407, 0.419, 0.455, 0.416, 0.426. The partial 2026/27
  reads 0.458 on n=54 — sampling noise on a small window, not a
  regime break (it is not used to set the constant; the constant
  pools all HT-present regular-season matches, as the J1 design
  does).
- Variance decomposition: observed per-match 1H-share variance
  0.1231 vs binomial-noise expectation 0.1305 (p(1−p)/G averaged
  over matches with G>0). Excess variance −0.0074 (negative) →
  implied true SD ≈ **0.000** (0.0pp). The per-match share is, if
  anything, *less* dispersed than pure binomial noise.
- Team 1H-share split-half r by season: −0.40, +0.34, −0.21, −0.42,
  +0.22, −0.04 (partial) — mean ≈ −0.09, sign-flipping — **no
  stable per-team trait**.
- **Verdict: NOISE, frozen constant.** Halves presentation uses
  the single frozen constant 0.4267 (1H λ = 0.4267·FT λ,
  2H λ = 0.5733·FT λ). No per-team or per-match half-share
  modelling, exactly as the J1 book was closed.

## F4 — Movers: no estimable tier offset (see FEATURES X2)

No Albanian second tier exists in the warehouse, so no mover prior
can be estimated from a sibling league. Within-league, 2 clubs
change per season, but a promoted club's arrival deviation cannot
be estimated without its feeder-tier history. The thin-data
treatment is SHRINK (ratings shrunk toward the league mean for
clubs with <6 prior in-league matches), not a mover offset.

## F5–F9 — Not testable in this league

- Set-play xG (F5 analogue), xG/shot (F6), xGOT (F7), box touches
  (F9): no stats, no shotmap — **no data, checks not run**.
- Referee strictness (F8 analogue): referee field empty 969/969
  — **no data**.
- SOT / corners / cards traits: targets do not exist — **no data**.

## F13 — Coverage verdict (feasibility)

| Market | Target exists? | Virgin window has target? | Candidate? |
|---|---|---|---|
| Goals (G-AL) | Yes — FT score, all seasons | Yes — 2026/27 in progress, n=55 | **Yes** |
| SOT (S-AL) | No (stats null, shotmap empty) | No | **No — not buildable** |
| Corners (C-AL) | No | No | **No — not buildable** |
| Cards (K-AL) | No (0 Yellow events; no stats) | No | **No — not buildable** |
| Total shots (T-AL) | No (shotmap empty) | No | **No — not buildable** |

Cards note: the only card signal is 230 red-family events
(0.24/match; 68 YellowRed + 162 Red). A reds-only target is a
rare-event count with no reliability evidence and no production
analogue; it is not a candidate.

## F12 — Game state (descriptive only)

HT scores exist for 92% of matches (see F3). No other in-match
quantities exist (no substitutions, no shot timelines). Nothing
here is a pre-match feature.

## F14 — Playoff note (descriptive only)

The 14 playoff matches average 2.43 goals/match (vs 2.26 regular)
— a small, top-4-only sample, not a level to model. They are
excluded from every fit and evaluation (DATA_UNDERSTANDING §4.1).
