# RESULT — QA-QatarStars [Muse-2]

Prereg frozen and pushed BEFORE any fitting: commit
`be4814af3534c69ba912694a4a80cc3fea42f9c1` (branch `wip-qa-qatarstars`).
Dev ≤ 2024/2025 (goals scored 2022/2023–2024/2025, warm-up 2021/2022);
virgin = 2025/2026 (n=132) read ZERO times — no arm passed dev, so no
virgin was scored; 2026/2027 untouched confirmatory reserve. Gates
exactly as pre-registered; none moved.

## Verdicts

| Candidate | Verdict | Gate numbers |
|---|---|---|
| G-QA goals | **FAIL** (dev gate) | Virgin not read. Dev pooled (n=396): DC Gate Zero 1X2 LL 1.0485 / RPS 0.2302 / OU2.5 LL 0.7275 vs climatology 1.0512 / 0.2419 / 0.6469 and naive trailing-10 1.0106 / 0.2253 / 0.6866 — beats climatology on 1X2 LL and RPS, but loses 1X2 LL and RPS to naive trailing-10 and loses OU2.5 LL to BOTH baselines, so the dev gate (all three metrics vs BOTH baselines) fails. ENTRANT also fails: 1.0431 / 0.2277 / 0.7239 (better than Gate Zero pooled on all three, sign check 2/3 seasons, moot). |
| S-QA SOT | **NOT-BUILDABLE** | No dev window: stats feed 0% in 2021/2022–2023/2024, 1 match in 2024/2025, 132/132 in 2025/2026. No trait reliability, no 1H share, no line selectable on dev. |
| C-QA corners | **NOT-BUILDABLE** | Same stats-era cause as S-QA: no dev season with a stats feed. |
| K-QA cards | **NOT-BUILDABLE** | No cards target in dev under either source: stats yellows from 2025/2026 only; event feed carries zero plain Yellow events 2021/2022–2024/2025 (Red 83 / YellowRed 50) — and zero in the virgin season too (Red 38 only). Referee named in 0 dev matches. |
| T-QA total shots | **NOT-BUILDABLE** | Same stats-era cause as S-QA: no dev season with a stats feed. |

**Nothing ships from QA-QatarStars.** No arm passed all legs; no
predictions directory is shipped (deliberately — there is no virgin
output to ship, and no `results_virgin.json` exists anywhere in this
folder).

## What Jarvis should check specifically

1. Prereg-before-fitting order: prereg commit `be4814a`
   predates every engine/results artifact. Full snapshot history on
   branch `wip-qa-qatarstars`: fase 2 `bf95aa1`, prereg `be4814a`,
   fase 6-7 `65d44b3` (+ `82ea952` pycache cleanup).
2. Virgin discipline: there is NO `results_virgin.json`, no
   `virgin_rows_*.csv`, no `fitted_params_virgin.json` in this folder.
   G-QA failed the dev gate, so under the frozen mechanical reading
   the virgin was never read. 2026/2027 was not scored or fitted on.
3. The central EDA finding — the stats era starts in 2025/2026, not
   in dev: 0% stats in 2021/2022–2023/2024, 1 match in 2024/2025 (All
   only, no splits), 132/132 in 2025/2026, 54/54 in 2026/2027. The
   brief's "58.8% across the last three seasons" is entirely
   2025/2026–2026/2027. No `expected_goals` key and no shotmap in any
   of the 714 payloads. The frozen split was NOT moved to manufacture
   a dev window for S/C/K/T.
4. The cards target check: stats-vs-events yellows in 2025/2026 agree
   exactly in only 25.8% of matches (mean stats−events +3.22/match) —
   descriptive only, and the gap is structural (the event feed counts
   reds/second yellows only there); no cards model was built because
   neither source yields a dev target.
5. Data build: `qa_matches.csv` 714 rows = index rows, match-id sets
   identical; `qa_team_matches.csv` 1,428 rows; 3 raw-JSON spot checks
   pass (recorded in `analysis/PREPROCESSING.md`). Three header/event
   score mismatches (4543706, 5099043, 5099029; header wins; the
   mismatched matches are excluded from the halves-goals share only).
   16 team ids, every id carries exactly one name spelling; all logic
   keyed by team id.
6. Halves constants: only `goals_1h_share: 0.4385` is frozen (dev-era
   event times, 1,749 goals, 505 matches). All four count-market
   halves constants are `null` — 0 dev matches have period splits, so
   none is computable. No halves model was built for any count market.
7. Diagnosis, recorded not acted on: the DC score matrix
   systematically under-predicts total goals — mean predicted OU2.5
   over-rate 0.4996 vs actual 0.6641 pooled (per season 0.486 / 0.497 /
   0.517 predicted vs 0.629 / 0.697 / 0.667 actual). The fitted model
   carries a single home intercept (the sanctioned reference pattern,
   DK `dc.py` `lambdas`), so the away-goals level has no intercept of
   its own; in a league with a near-absent home advantage (pooled dev
   scored home 1.707 vs away 1.641 goals/match; 2021/2022 away teams
   outscored home teams 1.659 vs 1.553) the fitted away lambdas
   underfit (2021/2022 fit: mean fitted away lambda 1.170 vs actual
   1.659), and the OU2.5 probabilities inherit the shortfall. The
   naive trailing-10 baseline wins 1X2 LL and RPS outright. No
   post-hoc repair was attempted inside this prereg.
