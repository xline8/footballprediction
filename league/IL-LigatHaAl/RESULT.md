# RESULT — IL-LigatHaAl [Muse-2]

Prereg frozen and pushed BEFORE any fitting: commit
`e9dd3b0` (branch `wip-il-ligataal`,
2026-11-10 04:46:01 UTC). Dev ≤ 2024/2025 (goals scored 2022/2023–2024/2025,
warm-up 2021/2022); virgin = 2025/2026 (n=240) read ONCE — both arms
passed dev, so the virgin was scored once; 2026/2027 untouched
confirmatory reserve. Gates exactly as pre-registered; none moved.

## Verdicts

| Candidate | Verdict | Gate numbers |
|---|---|---|
| G-IL goals | **FAIL** (virgin legs) | Dev pooled (n=720): DC Gate Zero 1X2 LL 1.0186 / RPS 0.2091 / OU2.5 LL 0.6918 and ENTRANT 1.0115 / 0.2062 / 0.6920 — both beat climatology (1.0851 / 0.2337 / 0.6954) and naive trailing-10 (1.0853 / 0.2200 / 0.7283) on all three metrics, so both passed the dev gate; ENTRANT sign check 3/3 dev seasons. Virgin (n=240, read once): Gate Zero 1X2 LL 1.0623 / RPS 0.2242 / OU2.5 LL 0.6963 — beats climatology (1.0812 / 0.2329 / 0.6994) but loses 1X2 LL to naive trailing-10 (1.0238), failing leg (i); OU2.5 calibration gap −11.70pp (predicted over-rate 0.4330 vs actual 0.5500), failing leg (ii); home-win gap +0.65pp PASS clean. ENTRANT virgin 1.1173 / 0.2385 / 0.6926, OU gap −11.16pp — fails legs (i) and (ii). |
| S-IL SOT | **NOT-BUILDABLE** | No dev window: stats feed 0% in 2021/2022–2024/2025, 239/240 in 2025/2026. No trait reliability, no 1H share, no line selectable on dev. |
| C-IL corners | **NOT-BUILDABLE** | Same stats-era cause as S-IL: no dev season with a stats feed. |
| K-IL cards | **NOT-BUILDABLE** | No cards target in dev under either source: stats yellows from 2025/2026 only; event feed carries zero plain Yellow events 2021/2022–2024/2025 (Red/YellowRed only). Referee named in 0 dev matches. |
| T-IL total shots | **NOT-BUILDABLE** | Same stats-era cause as S-IL: no dev season with a stats feed. |

**Nothing ships from IL-LigatHaAl.** No arm passed all legs; no
predictions directory is shipped (deliberately — the virgin output
exists as evidence in `engine/goals/virgin_rows_*.csv` and
`results_virgin.json`, but no arm ships, so no predictions file is
produced).

## What Jarvis should check specifically

1. Prereg-before-fitting order: prereg commit `e9dd3b0` (04:46:01 UTC)
   predates every engine/results artifact (first fitting output
   `results_dev.json` 04:46:52 UTC). Full snapshot history on branch
   `wip-il-ligataal`: fase 1 `ee8a884`, prereg `e9dd3b0`, fase 6
   (this delivery).
2. Virgin discipline: `results_virgin.json` exists exactly once per
   dev-passing arm (Gate Zero + ENTRANT, n=240 each), with
   `virgin_rows_GateZero.csv` / `virgin_rows_ENTRANT.csv` and
   `fitted_params_virgin.json` (fit on all matches ≤ 2024/2025, rho
   −0.05, home 0.1669). The virgin was NOT re-run. 2026/2027 was not
   scored or fitted on.
3. The central EDA finding — the stats era starts in 2025/2026, not in
   dev: 0% stats in 2021/2022–2024/2025, 239/240 in 2025/2026, 69/70
   in 2026/2027. The brief's "56.0% across the last three seasons" is
   entirely 2025/2026–2026/2027. No `expected_goals` key and no
   shotmap in any of the 1,270 payloads. The frozen split was NOT
   moved to manufacture a dev window for S/C/K/T.
4. The cards target check: stats-vs-events yellows in 2025/2026 agree
   exactly in 68.6% of matches (mean stats−events −0.53/match,
   largely mechanical: the event count adds YellowRed, the stats feed
   books a second yellow as a red) — descriptive only; no cards model
   was built because neither source yields a dev target.
5. Data build: `il_matches.csv` 1,270 rows = index rows, match-id sets
   identical; `il_team_matches.csv` 2,540 rows; 3 raw-JSON spot checks
   pass (recorded in `analysis/PREPROCESSING.md`). Three header/event
   score mismatches (3606698, 4516796, 4516800), all awarded wins
   (header wins); 7 awarded matches in total. 19 team ids, each with
   exactly one spelling — no canonicalisation needed. Phase from
   `leagueName` + `matchRound` (2025/2026+ carries the group in the
   round name): regular 182 + championship 30 + relegation 28 per
   full season.
6. Halves constants: only `goals_1h_share: 0.4497` is frozen (dev-era
   event times, 2,493 goals, 902 matches, awarded matches excluded).
   All four count-market halves constants are `null` — 0 dev matches
   have period splits, so none is computable. No halves model was
   built for any count market.
7. Diagnosis, recorded not acted on: the scoring-level rise flagged
   pre-fitting materialised — virgin goals/match 2.967 vs dev scored
   mean 2.656 (+0.31), virgin OU2.5 over-rate 0.5500 vs dev 0.4875.
   The pre-season-fitted DC ratings under-predict virgin totals by
   ~11–12pp on the over-rate, which breaks the OU calibration leg and,
   via the score matrix, the 1X2 LL leg against the trailing-10
   baseline (the naive baseline adapts inside the virgin season; the
   DC fit is frozen pre-season). ENTRANT's dev advantage (pooled 1X2
   LL 1.0115 vs Gate Zero 1.0186) reverses on the virgin (1.1173 vs
   1.0623). No post-hoc repair was attempted inside this prereg.
