# France Ligue 2 — model design candidates

No fitting is performed in Phase A. Dev frame: seed 2021/2022, evaluation
2022/2023–2024/2025 (pooled n=1,065 played: 380 + 379 + 306); virgin =
2025/2026 (complete, n=306), read ONCE and only for dev-passing arms;
2026/2027 (partial, n=108) is reserved confirmatory and UNREAD.
Calibration is always **actual − predicted** in this league (state it in
every verdict). Team state is keyed on FotMob team_id everywhere.

Gates (frozen program standard): goals dev — an arm must beat climatology
on 1X2 LL **and** RPS **and** beat the base rate on OU2.5 LL, else dead.
Count dev — an arm must beat **both** the league base rate **and** naive
trailing-10 on the primary-line LL, else dead. Virgin (dev-passers only):
PASS if virgin LL ≤ best baseline **and** |calibration| ≤ 1pp;
PROVISIONAL if the calibration breach is within 1 SE of the 1pp boundary;
else FAIL. If Gate Zero fails its dev gate, variants are moot, the
verdict is FAIL and the virgin is NOT read. Both-pass: lower virgin LL
ships; ties → the simpler arm. Halves are presentation only via the
frozen constants (goals 0.4457, SOT 0.4738, corners 0.4803, total shots
0.4702, yellows 0.3736).

Primary lines (dev evaluation over-rates, closest to 0.5, coordinator-
verified from the built CSV): goals OU **2.5** (46.1%); SOT **8.5**
(43.7%; 7.5 is 56.6% — 8.5 is marginally closer); corners **8.5**
(53.8%; 9.5 is 44.4%); cards **3.5** on event yellows (48.5%; 4.5 is
29.1%); total shots **22.5** (52.4%; 23.5 is 45.3%).

| Candidate | Reference | Arms |
|---|---|---|
| G-FR goals | production DC (model_v2 pattern), **goals-only** — X1/X3 era-dead: expected_goals coverage in dev seasons is 0.3/0.8/0.0/1.6%, the xG era starts inside the virgin (100% in 2025/2026), exactly the ES-LaLiga2 pattern | Gate Zero; SHRINK (sanctioned G-J2-lesson arm); X2 mover tier offset (Ligue 1 deltas GF +0.227 / GA −0.151; Ligue 3 deltas GF −0.177 / GA +0.161 vs league mu 1.252, pooled entry seasons) |
| S-FR SOT | production model_sot.py v5 | Gate Zero; RS (BB prior 200 → 20,000). X4/X6 era-dead (shotmap 0–1.6% in dev) — NOT built |
| C-FR corners | production model_corners_v3 | Gate Zero (X9 covariates possession + big chance); X7 box-touch multiplier (touches reliability 0.771/0.732) |
| K-FR cards | production model_cards.py; target = **event-feed yellows** (stats feed undercounts in every season: dev totals events 5,205 vs stats 4,857; exact agreement only 86.1% pooled dev — the program's cards artefact, 7th league) | Gate Zero only. X8 DROPPED: referee strictness split-half r = 0.028 on dev (noise), despite high coverage from 2022/2023 |
| T-FR total shots | shots family (T-J1 pattern) | A v1 pattern; B v2 level layer; C E9 trailing-r |

Notes:
- X2 evidence is strong and two-sided: 13 Ligue-1 entry team-seasons
  (493 team-matches) enter at GD +0.377/match; 11 Ligue-3 (National,
  league_id 8970) entry team-seasons (346 team-matches) at −0.338.
  Churn is 5–6 of 20/18 clubs per season.
- SHRINK rationale: every mover (5–6 clubs/season) starts a season with
  zero prior in-league matches, and early-season opponents of movers are
  priced off thin ratings. (The EDA `thin_data_team_seasons_lt6 = 0`
  figure counts total season matches per team, not prior-match counts —
  it does not measure this exposure and is not used; recorded as an EDA
  defect, coordinator-noted.)
- Phase rule (frozen from the data): the league_id-110 index slice
  contains only numeric regular rounds 1–38 (20-team seasons) / 1–34
  (18-team seasons); no promotion play-off or relegation play-out rows
  exist in this slice, so all built rows are `phase='regular'`. One
  regular match is missing from the warehouse in 2023/2024 (round 36
  holds 9 matches; season n=379 not 380).
- Format change: 20 teams through 2023/2024, 18 from 2024/2025
  (verified from the data) — season sizes 380/380/379/306/306.
- Cards halves: the yellows 1H share's true SD (0.0804) exceeds the
  goals/SOT pattern, but halves remain frozen-constant presentation
  only, never modelled (program rule).
- Predictions-only: no FR-Ligue2 odds/settlement source in-system.
