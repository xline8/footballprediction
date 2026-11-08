# RESULT — SG-PremierLeague [Muse-2]

Prereg frozen and pushed BEFORE any fitting: commit
`9b5d46b22406c37c37a314074d8a76585878cae0` (branch
`wip-sg-premierleague`). Dev ≤ 2024/2025 (goals scored 2022,
2023, 2024/2025; warm-up 2021); virgin = 2025/2026 (n=84)
read ZERO times — no arm passed dev, so no virgin was scored;
2026/2027 untouched confirmatory reserve. Gates exactly as
pre-registered; none moved.

## Verdicts

| Candidate | Verdict | Gate numbers |
|---|---|---|
| G-SG goals | **FAIL** (dev gate, OU leg) | Virgin not read. Dev pooled (n=364): DC Gate Zero 1X2 LL 0.9607 / RPS 0.2056 / OU2.5 LL 0.5507 vs climatology 1.0521 / 0.2421 / 0.5338 and naive trailing-10 0.9633 / 0.2080 / 0.5783 — beats BOTH baselines on 1X2 LL and RPS, but loses OU2.5 LL to climatology pooled and in every dev season (0.5546/0.5548/0.5446 vs 0.5428/0.5412/0.5213), so the dev gate (all three metrics vs BOTH baselines) fails on the OU leg. SHRINK identical (n<6 never binds under season-blocked prediction). X2 was DROPPED pre-fitting (EDA F4: 1 dev entrant transition only). |
| S-SG SOT | **NOT-BUILDABLE** | No target in any season: stats feed 0% in 2021–2026/2027 (0/555 matches), no shotmap (0/555). No trait reliability, no 1H share, no line selectable on dev. |
| C-SG corners | **NOT-BUILDABLE** | Same stats-absence cause as S-SG: no corners target in any season under any source; X7 input (`touches_opp_box`) absent too. |
| K-SG cards | **NOT-BUILDABLE** | No yellows target in ANY season under either source: stats yellows absent everywhere; event feed carries ZERO plain Yellow events in all 555 matches (only YellowRed + Red — YellowRed 32 in the dev era). Referee named in 0 dev matches (no X8 arm). Strongest form of the K verdict, identical in structure to K-BY. |
| T-SG total shots | **NOT-BUILDABLE** | Same stats-absence cause as S-SG: no total-shots target in any season, no shotmap. |

**Nothing ships from SG-PremierLeague.** No arm passed all
legs; no predictions directory is shipped (deliberately —
there is no virgin output to ship, and no `results_virgin.json`
exists anywhere in this folder).

## What Jarvis should check specifically

1. Prereg-before-fitting order: prereg snapshot commit
   `9b5d46b` (branch `wip-sg-premierleague`) predates every
   engine/results artifact. Full snapshot history on that
   branch: fase 3 (prereg) `9b5d46b`, fase 4–7 snapshot at
   delivery.
2. Virgin discipline: there is NO `results_virgin.json`, no
   `virgin_rows_*.csv`, no `fitted_params_virgin.json` in this
   folder. G-SG failed the dev gate, so under the frozen
   mechanical reading the virgin was never read. 2026/2027
   was not scored or fitted on.
3. Scores-only in the strongest sense: stats feed 0% in EVERY
   season (0/555 matches), shotmap 0/555, referee 0 in all dev
   and virgin matches (13/23 only in the untouched reserve).
   No `expected_goals` key anywhere, so the X1 blend runs in
   its documented goals-only fallback. The frozen split was
   NOT moved to manufacture a dev window for S/C/K/T.
4. X2 dropped, not silently absent: EDA F4 measures exactly 1
   dev entrant transition (Brunei DPMM returning 2023,
   GF −0.468 / GA −0.301) — below the ≥3 minimum and with the
   GA sign contradicting the entrant pattern. The engine
   therefore carries Gate Zero + SHRINK only (see
   `engine/goals/README.md` and `arms.py` header).
5. League quirks worth a ledger note: (a) season structure
   switches from calendar-year (2021–2023) to split seasons
   (2024/2025 on) mid-corpus; `general.leagueName` is
   "S.League" in 2021–2022, "Premier League" after — one
   competition; (b) team id 67377 carries two names (FC
   Jurong / Albirex Niigata FC); all logic keys by id;
   (c) all 12 matches with an empty events payload are 0-0,
   and event goals match the header score in all 555 matches
   (0 mismatches, 0 awarded).
6. The recorded calibration risk was real but moot: virgin
   goals/match (3.607, inventory) sits −0.71 below the dev
   scored mean (4.316) — it never mattered because G-SG died
   at the dev gate on totals pricing, the same OU leg that
   killed G-BY/G-NO/G-UY/G-CN.
