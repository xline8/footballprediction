# Phase 3 — EDA

Tool: `analysis/eda.py`; raw numbers in `analysis/eda_summary.json`;
charts in `analysis/charts/`. Dev = 2021–2024/2025 (n = 738); eval
seasons 2022–2024/2025 (n = 654); virgin 2025/2026 (n = 182) appears
in levels only. 2026/2027 (n = 49, in progress) appears in levels only.

## Findings

**F1 — levels and drift.** Finished goals/match by season are 2021
2.31, 2022 2.44, 2023 2.37, 2023/2024 2.70, 2024/2025 2.47, 2025/2026
2.63, 2026/2027 (partial) 2.69. Pooled dev 2.50. No monotone drift;
the 2023/2024 peak (+0.33 vs 2023) reverts the next season. Home win
rate by season: 0.54, 0.44, 0.37, 0.46, 0.40, 0.43, 0.47 (partial).
Draw rate is high and volatile (0.14 in 2021, 0.37 in 2023, dev pooled
0.31). BTTS 0.35–0.57. Levels sit in the normal European range — this
is not a goals-famine or goals-flood league.

**F2 — trait reliability.** Split-half reliability is chronological
(first half of each season's fixtures vs second half), teams with
≥5 matches in each half. Goals-for r by season: 2021 0.21, 2022 0.75,
2023 0.28, 2023/2024 0.70, 2024/2025 0.65 (mean 0.52). Goals-against r:
0.14, 0.20, 0.07, −0.14, 0.39 (mean 0.13). Attack trait is moderately
reliable (the 2023 dip is the split-group season: ~9–10 matches per
half per team, so the halves are noisy); defence trait is weak — the
DC fit's defence ratings will be mostly shrinkage toward the mean in
effect, which is what the production fit does anyway. No other target
exists to reliability-test (SOT/corners/shots/cards all absent).

**F3 — halves.** HT score comes from the Half-event marker,
cross-validated 924/924 against goal times ≤45. Dev 1H goals share
(2021–2024/2025): **0.4468** (1,831 goals, 695 matches); by season
0.433, 0.426, 0.467, 0.444, 0.459. Per-match 1H share variance is
0.1320 against a binomial-noise expectation of 0.1243 (excess variance
0.0077, i.e. a true per-match SD of ≈0.09 around the constant — small).
Team-level 1H share split-half r = 0.24 (n = 17 teams; between-team
variance 0.0067 vs within-team 0.1838). Verdict: per-match 1H share is
≈ noise; **the frozen constant 0.4468 is presentation-only** (FT → 1H
via the constant, 2H = FT − 1H). No per-team or per-match halves
modelling. (Virgin 2025/2026 share 0.4665 is reported for the record
only; the constant is frozen from dev.)

**F4 — entrants (descriptive only, no arm).** The warehouse starts in
2021, so all 14 teams of 2021 are "first appearances" by construction
— not real entrants. Real post-seed entrants (no prior in-league
season): 2023 Khanh Hoa (GF diff −0.18, GA +0.04) and Cong An Ha Noi
(GF +0.77, GA −0.13); 2023/2024 one entrant (GF −0.04, GA +0.04).
Mean over the 3 real entrants: GF diff +0.18, GA diff −0.02 — **no
systematic entrant weakness** (one entrant was the season's strongest
attack). No mover prior is estimable, and no X2 arm is registered.
There is no Vietnamese sibling league in the warehouse.

**F5 — coverage.** Stats, shotmap, period splits, named referees:
0/969 in every season. Lineups: 0/556 in 2021–2023/2024, 413/413 from
2024/2025. PlayerStats: null everywhere. Events: 924/969 (95.4%);
the 45 event-less matches are exactly the 45 without an HT score.

**F6 — identity.** 21 FotMob team ids; 11 ids carry 2–3 name spellings
(diacritics + two rename chains: HCM City → Ho Chi Minh City FC →
Cong An Ho Chi Minh City; FLC Thanh Hoa → Thanh Hoa FC). Keying on
ids is exact; keying on names would split eleven clubs.

**F7 — calendar / format.** Mixed labelling verified disjoint
(§DATA_UNDERSTANDING 3). 2021 truncated at round 12 (COVID). 2023
split-group (phase 1 + championship/relegation groups, 43 phase-2
matches). 2022: 13 teams; all other complete seasons: 14 teams,
26 rounds, balanced. No playoff fixture exists in any season.

**F8 — virgin.** 2025/2026 is the virgin window: 182 matches, 14
teams, 26 rounds, 2025-08-15 – 2026-06-07, complete. Read ONCE, only
for arms passing the dev gate. 2026/2027 (49 matches, rounds 1–7,
through 2026-11-08) is in progress and reserved for a season-end
confirmatory read.

**F9 — target feasibility.** Goals are the only observed, consistent
target in every season. SOT / corners / total shots: target absent in
every season. Cards: plain-Yellow events are 0 in all four dev
seasons that precede 2024/2025 and appear only from 2024/2025 — no
valid virgin window contains the target in dev, so K is not buildable.

**F10 — event completeness.** 45 matches have no events at all (4 in
2021, 9 in 2022, 20 in 2023, 10 in 2023/2024, 2 in 2025/2026). Those
matches still have official FT scores and enter the goals fit; they
contribute no HT score. One score/event mismatch (match 4688919,
official 1–0 vs 2 event home goals) — official score kept, flagged.

**F11 — line selection.** On pooled dev eval seasons 2022–2024/2025
(n = 654): OU1.5 over-rate 0.716, OU2.5 0.445, OU3.5 0.240. **Primary
line OU2.5** (closest to 50%). Home-win rate pooled 0.417.

**F12 — home advantage.** Dev pooled (2021–2024/2025, n = 738): home
1.390 goals/match vs away 1.091 — a +0.30 goal edge, in line with the
production DC fitted home parameter's usual range. The DC fit fits
home advantage per fit; no separate home-edge feature is needed.

**F13 — SHRINK bite.** Prior in-league match counts at each
target-season start: 2022 — all 13 teams have 6–23; 2023 — 12 teams
24+, 2 teams 0; 2023/2024 — 11 teams 24+, 2 teams 6–23, 1 team 0;
2024/2025 — all 14 teams 24+; 2025/2026 — 12 teams 24+, 2 teams 0.
**Zero teams fall in the 1–5 prior-match band at any target-season
start**, so SHRINK is expected to be identical to Gate Zero — the
verdict must verify that from the results file rather than assume it.

**F14 — 2026/2027 restriction.** Any 2026/2027 number in inventory /
levels is descriptive only. No 2026/2027 row enters any fit, any
reliability check, or any gate. The season-end confirmatory read is
noted in MODEL_DESIGN, not executed here.
