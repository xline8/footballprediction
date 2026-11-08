# RESULT — EC-SerieA [Muse-2]

Prereg frozen and pushed BEFORE any fitting: commit
`1a2eb966f78fe43570c2f4a1177bf27b14ba2a6e` (branch `wip-ec-seriea`,
2026-11-10 04:00:07 UTC). Dev ≤ 2024 (goals scored 2022–2024,
warm-up 2021); virgin = 2025 (n=312) read ZERO times — no arm passed
dev, so no virgin was scored; 2026 untouched confirmatory reserve.
Gates exactly as pre-registered; none moved.

## Verdicts

| Candidate | Verdict | Gate numbers |
|---|---|---|
| G-EC goals | **FAIL** (dev gate) | Virgin not read. Dev pooled (n=726): DC Gate Zero 1X2 LL 1.0142 / RPS 0.2034 / OU2.5 LL 0.7036 vs climatology 1.0575 / 0.2176 / 0.6941 and naive trailing-10 1.1965 / 0.2268 / 0.7388 — beats both baselines on 1X2 LL and RPS, but loses OU2.5 LL to climatology, so the dev gate (all three metrics vs BOTH baselines) fails. ENTRANT also fails: 1.0159 / 0.2038 / 0.7050. |
| S-EC SOT | **NOT-BUILDABLE** | No dev window: stats feed 0% in 2021–2023, 1 match in 2024, 311/312 in 2025. No trait reliability, no 1H share, no line selectable on dev. |
| C-EC corners | **NOT-BUILDABLE** | Same stats-era cause as S-EC: no dev season with a stats feed. |
| K-EC cards | **NOT-BUILDABLE** | No cards target in dev under either source: stats yellows from 2025 only; event feed carries zero plain Yellow events 2021–2024 (Red/YellowRed only). Referee named in 0 dev matches. |
| T-EC total shots | **NOT-BUILDABLE** | Same stats-era cause as S-EC: no dev season with a stats feed. |

**Nothing ships from EC-SerieA.** No arm passed all legs; no
predictions directory is shipped (deliberately — there is no virgin
output to ship, and no `results_virgin.json` exists anywhere in this
folder).

## What Jarvis should check specifically

1. Prereg-before-fitting order: prereg commit `1a2eb96` (04:00:07 UTC)
   predates every engine/results artifact (first fitting output
   04:03:07 UTC). Full snapshot history on branch `wip-ec-seriea`:
   fase 2 `b9c18eb`, prereg `1a2eb96`, fase 4 `4e7086f`,
   fase 6 `b2b4445`.
2. Virgin discipline: there is NO `results_virgin.json`, no
   `virgin_rows_*.csv`, no `fitted_params_virgin.json` in this folder.
   G-EC failed the dev gate, so under the frozen mechanical reading
   the virgin was never read. 2026 was not scored or fitted on.
3. The central EDA finding — the stats era starts in 2025, not in
   dev: 0% stats in 2021–2023, 1 match in 2024 (All only, no splits),
   311/312 in 2025, 285/285 in 2026. The brief's "71.2% across the
   last three seasons" is entirely 2025–2026. No `expected_goals`
   key and no shotmap in any of the 1,565 payloads. The frozen split
   was NOT moved to manufacture a dev window for S/C/K/T.
4. The cards target check: stats-vs-events yellows in 2025 agree
   exactly in 80.1% of matches (mean stats−events −0.36/match) —
   descriptive only; no cards model was built because neither source
   yields a dev target.
5. Data build: `ec_matches.csv` 1,565 rows = index rows, match-id sets
   identical; `ec_team_matches.csv` 3,130 rows; 3 raw-JSON spot checks
   pass (recorded in `analysis/PREPROCESSING.md`). Two header/event
   score mismatches (3528060, 3816510; header wins). 4 team ids carry
   accent-variant spellings, canonicalised to the most frequent
   spelling, keyed by id throughout.
6. Halves constants: only `goals_1h_share: 0.4616` is frozen (dev-era
   event times, 2,474 goals, 902 matches). All four count-market
   halves constants are `null` — 0 dev matches have period splits, so
   none is computable. No halves model was built for any count market.
7. Diagnosis, recorded not acted on: the DC ratings carry across
   seasons here — unlike CH, the 1X2/RPS legs win clearly — but the
   score matrix's OU2.5 probabilities do not beat the constant base
   rate on log-loss, even though mean predicted over-rate (0.4555) is
   close to the actual (0.4642). No post-hoc repair was attempted
   inside this prereg.
