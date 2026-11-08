# RESULT — UY-LigaAUF [Muse-2]

Prereg frozen and pushed BEFORE any fitting: commit
`7d43257df3460bcfa1bf07c8c94d2ff4466f2074` (branch `wip-uy-ligaauf`).
Dev ≤ 2024 (goals scored 2022–2024, warm-up 2021); virgin = 2025
(n=300) read ZERO times — no arm passed dev, so no virgin was scored;
2026 untouched confirmatory reserve. Gates exactly as pre-registered;
none moved.

## Verdicts

| Candidate | Verdict | Gate numbers |
|---|---|---|
| G-UY goals | **FAIL** (dev gate) | Virgin not read. Dev pooled (n=895): DC Gate Zero 1X2 LL 1.0705 / RPS 0.2228 / OU2.5 LL 0.6869 vs climatology 1.0939 / 0.2305 / 0.6806 and naive trailing-10 1.1465 / 0.2280 / 0.7296 — beats BOTH baselines on 1X2 LL and RPS, but loses OU2.5 LL to climatology (0.6869 vs 0.6806), so the dev gate (all three metrics vs BOTH baselines) fails on the OU leg alone. ENTRANT also fails: 1.0753 / 0.2244 / 0.6858 (worse than Gate Zero pooled on 1X2 LL and RPS, sign check 0/3 seasons, moot). |
| S-UY SOT | **NOT-BUILDABLE** | No target in any season: stats feed 0% in 2021–2026 (0/1,717 matches, 0 stats keys in any raw JSON), no shotmap, no event-derived SOT substitute. No trait reliability, no 1H share, no line selectable on dev. |
| C-UY corners | **NOT-BUILDABLE** | Same stats-absence cause as S-UY: no corners target in any season under any source; X7 input (`touches_opp_box`) absent too. |
| K-UY cards | **NOT-BUILDABLE** | No consistent cards target in dev under either source: stats yellows absent in every season; event feed carries zero plain Yellow events in 2021–2022 (Red 40/63, YellowRed 44/63) — plain Yellows only from 2023, a target-definition break inside dev (NO-2Divisjon precedent). Referee named in 0/1,717 matches. |
| T-UY total shots | **NOT-BUILDABLE** | Same stats-absence cause as S-UY: no total-shots target in any season, no shotmap. |

**Nothing ships from UY-LigaAUF.** No arm passed all legs; no
predictions directory is shipped (deliberately — there is no virgin
output to ship, and no `results_virgin.json` exists anywhere in this
folder).

## What Jarvis should check specifically

1. Prereg-before-fitting order: prereg commit `7d43257`
   predates every engine/results artifact. Full snapshot history on
   branch `wip-uy-ligaauf`: fase 1 `dcc1cd6`, fase 2 `8ee129d`,
   prereg `7d43257`, fase 6-7 `ef8946f`.
2. Virgin discipline: there is NO `results_virgin.json`, no
   `virgin_rows_*.csv`, no `fitted_params_virgin.json` in this folder.
   G-UY failed the dev gate, so under the frozen mechanical reading
   the virgin was never read. 2026 was not scored or fitted on.
3. The central EDA finding — this is a scores-only league in the
   strongest sense: stats feed 0% in EVERY season (0/1,717 matches,
   0 stats keys in any raw JSON), shotmap 0/1,717, referee named
   0/1,717, period splits 0/1,717. No `expected_goals` key anywhere,
   so the X1 blend runs in its documented goals-only fallback. The
   frozen split was NOT moved to manufacture a dev window for S/C/K/T.
4. The cards target check: the event feed DOES carry plain Yellows
   from 2023 (1,659 / 1,597 / 1,586 / 1,543 per season 2023–2026),
   but zero in 2021–2022 — so an event-derived yellows target breaks
   inside dev (warm-up + first scored season have no target). K stays
   not-buildable on the NO precedent, not on the QA precedent (QA's
   event feed had zero plain Yellows in dev AND virgin).
5. Data build: `uy_matches.csv` 1,717 rows = index rows, match-id sets
   identical; `uy_team_matches.csv` 3,434 rows; 3 raw-JSON spot checks
   pass (recorded in `analysis/PREPROCESSING.md`). Two header/event
   score mismatches (3834312 awarded 0–3, events 2–1; 4425121 scoreStr
   5–0 vs 6 Goal events; header wins; both excluded from the halves
   share only). 26 team ids (16/season); 3 accent-variant names
   canonicalised to the majority spelling per id; all logic keyed by
   team id. 38 matches have a wholly empty events payload; all are
   scoreless (0–0); their events-derived fields are missing, never zero.
6. Halves constants: only `goals_1h_share: 0.4276` is frozen (dev-era
   event times, 2,664 goals, 1,096 matches; per-season 0.4138–0.4373).
   All four count-market halves constants are `null` — 0 matches in
   any season have period splits, so none is computable. No halves
   model was built for any count market.
7. Diagnosis, recorded not acted on: the OU failure is narrow and
   OU-specific (0.0063 nats vs climatology pooled). Mean predicted
   OU2.5 over-rate 0.378 vs actual 0.4045 pooled; per season 0.438 vs
   0.383 in 2022, 0.361 vs 0.400 in 2023, 0.336 vs 0.431 in 2024 — the
   model over-predicts overs in the low-scoring 2022 season
   (2.191 goals/match) and under-predicts them in the higher-scoring
   2024 season (2.434 goals/match), i.e. its season-level totals do
   not track the year-to-year level shift. The 1X2/RPS legs pass vs
   both baselines, so the ratings carry real signal. No post-hoc
   repair was attempted inside this prereg.
