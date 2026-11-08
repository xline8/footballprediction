# RESULT — BY-PremierLeague [Muse-2]

Prereg frozen and pushed BEFORE any fitting: commit
`66cbfe459665943b113dd32946355410ddb7dada` (branch
wip-by-premierleague). Dev ≤ 2024; virgin = 2025 NOT read (G-BY failed
the dev gate); 2026 untouched. Gates exactly as pre-registered; none
moved.

## Verdicts

| Candidate | Verdict | Gate numbers |
|---|---|---|
| G-BY goals | **FAIL** (dev gate, OU leg vs climatology + 1X2/RPS legs vs naive) | Virgin not read. Dev pooled (n=690): DC Gate Zero 1X2 LL 1.0679 / RPS 0.2223 / OU LL 0.7143 vs climatology 1.0886 / 0.2327 / 0.6934 — beats climatology on 1X2 and RPS but loses the OU leg in every dev season; vs naive trailing-10 1.0534 / 0.2181 / 0.7455 — loses 1X2 and RPS pooled. SHRINK identical (n<6 never binds under season-blocked prediction). X2 worse pooled (1.0867 / 0.2257 / 0.7200): identical 2022 (offset 0), worse 2023, much worse 2024 (1.1319 vs 1.0789). |
| S-BY SOT | **NOT-BUILDABLE** | No stats feed in any season (0/1,394). No dev window, no trait, no line. |
| C-BY corners | **NOT-BUILDABLE** | No stats feed in any season (0/1,394). No dev window, no trait, no line. |
| K-BY cards | **NOT-BUILDABLE** | No yellows target in any season: stats absent AND event plain Yellows 0 in EVERY season (only YellowRed + Red); referee named in 0/1,394 matches (no X8 arm). |
| T-BY total shots | **NOT-BUILDABLE** | No stats feed in any season (0/1,394); shotmap empty in every season. No dev window, no trait, no line. |

**Nothing ships from BY-PremierLeague.** No arm passed all legs; no
predictions directory is shipped (deliberately — cf. the CH
precedent: a FAIL at the dev gate means the virgin is never read and
nothing is predicted).

## What Jarvis should check specifically

1. Prereg-before-fitting order: prereg commit `66cbfe4` (wip
   branch) predates every engine/results artifact in this folder's
   history.
2. Virgin discipline: `results_virgin.json` does NOT exist for any
   candidate — G-BY failed dev, so the virgin was never read.
   2026 untouched (no engine reads any 2026 row).
3. The dev-gate failure is split across the two baselines: Gate Zero
   beats climatology on pooled 1X2 LL (1.0679 vs 1.0886) and RPS
   (0.2223 vs 0.2327) but loses the OU leg to climatology in EVERY
   dev season (pooled 0.7143 vs 0.6934), and loses pooled 1X2 LL and
   RPS to the naive trailing-10 (1.0534 / 0.2181). Diagnosis in
   `reports/G_BY_VERDICT.md`: the fitted totals are worse-calibrated
   than the league over-rate, and recent-form goals means track this
   league better than expanding-fit ratings. No post-hoc repair was
   attempted.
4. X2 was KEPT pre-fitting (unlike CH/NO/FR) on the strongest EDA
   evidence in the programme: 8 dev entrant transitions, mean GF
   −0.325 / GA +0.426, consistent signs (GF negative 8/8, GA positive
   7/8); frozen rule recomputes the offset from completed transitions
   before each predicted season, clamped to [0.8, 1.25]. It backfired
   in 2024 (1.1319 vs 1.0789) — recorded, not acted on. The variant
   is moot under the frozen mechanical reading.
5. The cards verdict is stronger than FR's: not a definition break
   across eras but no yellows target at all — plain Yellow events are
   0 in every season (evidence in `analysis/eda_summary.json`,
   `event_cards_by_season`) and referee coverage is 0% everywhere.
6. Format facts: calendar-year seasons, single group (16 teams to
   2022, 15 in 2023, 16 from 2024; 240/240/210/240/240/224 matches).
   leagueName "Premier League" and coverageLevel "lower" for all
   1,394 matches — same competition, no split, no rebrand. Seventeen
   awarded matches (15 in 2021, all Sputnik Rechitsa withdrawal;
   3832254 in 2022; 4127429 in 2023, played 2-2, awarded 3-0), kept
   as ordinary flagged rows; none in the virgin season. One
   non-awarded score mismatch (3832371, header 0-0 vs event 4-1;
   header used). 23 team ids, 0 spelling variants; all logic keyed
   by team id.
