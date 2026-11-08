# Phase 3 — EDA: AM-PremierLeague

All numbers measured on `league/AM-PremierLeague/data/am_matches.csv`
(881 matches; 874 after excluding the 7 awarded matches — the level
table below uses awarded-excluded matches throughout, because the
awarded 3-0/0-3 scorelines are administrative, not played football;
the virgin 2026/2027 row has no awarded matches so it is unaffected).
Summary JSON: `eda_summary.json`.

## F1 — Levels per season (goals, awarded-excluded)

| Season | n | Teams | Mean goals | Home | Away | HW% | D% | AW% | Over 2.5 | BTTS |
|---|---|---|---|---|---|---|---|---|---|---|
| 2021/2022 | 144 | 9 | 2.42 | 1.29 | 1.13 | 40.3 | 25.0 | 34.7 | 40.3 | 45.8 |
| 2022/2023 | 180 | 10 | 2.48 | 1.22 | 1.26 | 39.4 | 19.4 | 41.1 | 46.7 | 39.4 |
| 2023/2024 | 180 | 10 | 2.79 | 1.48 | 1.32 | 45.0 | 18.9 | 36.1 | 50.6 | 51.7 |
| 2024/2025 | 158 | 11 | 3.15 | 1.72 | 1.43 | 44.9 | 15.8 | 39.2 | 60.8 | 47.5 |
| 2025/2026 | 135 | 10 | 2.58 | 1.39 | 1.19 | 41.5 | 23.0 | 35.6 | 46.7 | 44.4 |
| 2026/2027* | 77 | 12 | 2.95 | 1.71 | 1.23 | 49.4 | 19.5 | 31.2 | 59.7 | 48.1 |
| Pooled | 874 | — | 2.71 | 1.44 | 1.27 | 42.9 | 20.1 | 37.0 | 50.1 | 46.0 |

\* In progress (rounds 1–13 + one early round-15 fixture). The league
is **high-scoring and getting higher**: 2.42 → 2.48 → 2.79 → 3.15
(2024/25) → 2.58 → 2.95 (virgin, running hot on n=77). For reference,
J1 runs ~2.6 goals/match and AL ~2.26; Armenia's pooled 2.71 is the
highest of the three, and its Over 2.5 rate is 50.1% pooled (60.8%
in 2024/25). The draw rate is low (pooled 20.1%, vs ~30% in AL) and
the away-win rate high (37.0%). Home advantage is positive in every
season **except 2022/2023**, when away goals (1.26) exceeded home
goals (1.22) and away wins (41.1%) exceeded home wins (39.4%) — the
one inverted season in the corpus. The 2024/25 spike (3.15) is not
an awarded artefact: the 7 awarded matches are excluded above, and
including them barely moves the level (3.14). Part of the spike is
compositional — the 11-team season added Gandzasar (GD −1.42/match)
while West Armenia collapsed — but the level stays elevated in the
virgin window, so the model must not assume a return to 2.4.

## F2 — Team traits are STRONG (split-half by season)

Per season, each team's matches are split at random into two halves;
the correlation of the team's per-match rate across halves
(chart method — `make_charts.py`, seed 7, GF all seasons, then GA;
an independent per-season Random(7) split gives the same picture:
GF means 0.78 / GA 0.76):

| Season | GF r | GA r |
|---|---|---|
| 2021/2022 | 0.651 | 0.610 |
| 2022/2023 | 0.796 | 0.764 |
| 2023/2024 | 0.775 | 0.698 |
| 2024/2025 | 0.909 | 0.879 |
| 2025/2026 | 0.761 | 0.844 |
| Mean (complete seasons) | **0.778** | **0.759** |
| 2026/2027 (partial) | 0.438 | 0.692 |

**STRONG.** The 5-season means (GF 0.78, GA 0.76) are the highest of
any scores-only sibling so far — above BA (0.59/0.62) and J1/J2
(0.62–0.69), and the opposite pole from AL (0.27/0.14). Every single
complete season is ≥0.61 on both traits; there is no sign-flip
season. Two caveats, stated plainly: with only 9–11 teams per season
a single season's split-half r has a standard error of ~0.3, so one
season proves nothing; but five seasons all pointing the same way,
with the same ordering, is the evidence — and it is consistent with
the steep tiers below (top-to-bottom gap 2.59 GD/match, vs ~1.0 in
AL). A scores-only ratings fit has real team signal to find here.
The dev gate is still the real test — F2 justifies the build; it
does not pre-pass it.

Team tiers (complete seasons 2021/22–2025/26, awarded-excluded,
per-match GF−GA): Ararat Armenia **+1.17** (2.01 GF / 0.84 GA),
Pyunik +1.06, FC Noah +0.70, Urartu FC +0.59, Alashkert FC +0.09,
Van −0.48, Ararat −0.51, Noravank −0.59, BKMA −0.68, Shirak −0.82,
West Armenia −1.13, Lernayin Artsakh −1.19, Gandzasar −1.42. The
hierarchy is steep and stable — a genuine top 4 (all ≥ +0.59) and a
genuine bottom 3 (all ≤ −1.13) — which is why newly promoted clubs
(who arrive with no in-league history) are a real thin-data risk
here, and why the SHRINK arm is not decorative in this league the
way it was for BA/AL (see MODEL_DESIGN).

## F3 — Half shares: frozen constant, no per-team signal

- Pooled goals 1H share (827 awarded-excluded matches with an HT
  score): **0.4335** (1,027 1H goals / 2,369 FT goals). By complete
  season: 0.422, 0.437, 0.410, 0.449, 0.443. The partial 2026/27
  reads 0.449 on n=74 — sampling noise on a small window, not a
  regime break (it is not used to set the constant; the constant
  pools all HT-present awarded-excluded matches, as the J1 design
  does).
- Variance decomposition: observed per-match 1H-share variance
  0.1097 vs binomial-noise expectation 0.1183 (p(1−p)/G averaged
  over matches with G>0). Excess variance −0.0086 (negative) →
  implied true SD ≈ **0.000** (0.0pp). The per-match share is, if
  anything, *less* dispersed than pure binomial noise.
- Team 1H-share split-half r by season (own-goals definition:
  a team's own 1H goals / own FT goals): +0.24, −0.09, +0.18,
  +0.10, −0.07, −0.07 (partial) — mean ≈ **+0.08**, sign-flipping
  — **no stable per-team trait**. Method note: the naive
  alternative definition (a team's 1H goals / total match goals)
  returns r ≈ 0.83 pooled — but a binomial-resampling null test
  returns r ≈ 0.82 for the same definition, i.e. it is confounded
  by team strength (a strong team's share of match goals persists
  across halves), not a timing trait. The own-goals definition is
  the valid test, and it says noise.
- **Verdict: NOISE, frozen constant.** Halves presentation uses
  the single frozen constant 0.4335 (1H λ = 0.4335·FT λ,
  2H λ = 0.5665·FT λ). No per-team or per-match half-share
  modelling, exactly as the J1 book was closed.

## F4 — Movers: no estimable tier offset (see FEATURES X2)

No Armenian second tier exists in the warehouse, so no mover prior
can be estimated from a sibling league. Within-league, 1–2 clubs
change per season, but a promoted club's arrival deviation cannot
be estimated without its feeder-tier history. The thin-data
treatment is SHRINK (ratings shrunk toward the league mean for
clubs with <6 prior in-league matches), not a mover offset. Note
the shape differs from AL/BA here: in 2025/2026 no new club
entered at all, and in 2026/2027 two new clubs (Sardarapat,
Syunik) enter together — the virgin window is the season where
the thin-data treatment is most load-bearing.

## F5–F9 — Not testable in this league

- Set-play xG (F5 analogue), xG/shot (F6), xGOT (F7), box touches
  (F9): no stats, no shotmap — **no data, checks not run**.
- Referee strictness (F8 analogue): referee field empty 881/881
  — **no data**.
- SOT / corners / cards traits: targets do not exist — **no data**.

## F13 — Coverage verdict (feasibility)

| Market | Target exists? | Virgin window has target? | Candidate? |
|---|---|---|---|
| Goals (G-AM) | Yes — FT score, all seasons | Yes — 2026/27 in progress, n=77 | **Yes** |
| SOT (S-AM) | No (stats null, shotmap empty) | No | **No — not buildable** |
| Corners (C-AM) | No | No | **No — not buildable** |
| Cards (K-AM) | No (0 Yellow events; no stats) | No | **No — not buildable** |
| Total shots (T-AM) | No (shotmap empty) | No | **No — not buildable** |

Cards note: the only card signal is 186 red-family events
(0.21/match; 135 Red + 51 YellowRed). A reds-only target is a
rare-event count with no reliability evidence and no production
analogue; it is not a candidate.

## F12 — Game state (descriptive only)

HT scores exist for 94% of matches (see F3). No other in-match
quantities exist (no substitutions, no shot timelines). Nothing
here is a pre-match feature.

## F14 — Awarded matches note (descriptive only)

The 7 awarded matches are all 3-0/0-3 administrative scorelines
involving West Armenia in 2024/2025 (DATA_UNDERSTANDING §4.1).
Including them would move the 2024/25 level from 3.15 to 3.14 —
negligible for levels, but they are excluded from every fit and
evaluation anyway because an unplayed forfeit carries no team
signal at all.
