# RESULT — KW-PremierLeague [Muse-2]

Prereg frozen and pushed BEFORE any fitting: commit
`c8988cf143b507f0f5c6d6e15f466d84e1f248e5` (branch
wip-kw-premierleague). Dev ≤ 2024/2025 (warm-up 2021, scored
2021/2022–2024/2025); virgin = 2025/2026 NOT read (G-KW failed the
dev gate); 2026/2027 untouched. Gates exactly as pre-registered;
none moved.

## Verdicts

| Candidate | Verdict | Gate numbers |
|---|---|---|
| G-KW goals | **FAIL** (dev gate, OU leg vs climatology only) | Virgin not read. Dev pooled (n=422): DC Gate Zero 1X2 LL 0.9436 / RPS 0.1882 / OU2.5 LL 0.7293 vs climatology 1.0767 / 0.2357 / 0.6806 and naive trailing-10 1.0108 / 0.2086 / 0.7405 — beats BOTH baselines on 1X2 LL and RPS and beats naive on OU, but loses the OU leg to climatology (pooled and in the first three dev seasons). SHRINK identical (n<6 never binds under season-blocked prediction). X2 worse pooled (0.9496 / 0.1899 / 0.7371): identical in 2021/2022 + 2022/2023 (offset 0, <3 prior transitions), worse in 2023/2024, mixed in 2024/2025. |
| S-KW SOT | **NOT-BUILDABLE** | No stats feed in any season (0/711); shotmap 0/711. No dev window, no trait, no line. |
| C-KW corners | **NOT-BUILDABLE** | No stats feed in any season (0/711); no corners source at all. No dev window, no trait, no line. |
| K-KW cards | **NOT-BUILDABLE** | No yellows target in any season: stats absent AND event plain Yellow / YellowRed = 0 in the ENTIRE corpus (only 53 straight Reds); referee named in 0/711 matches (no X8 arm). |
| T-KW total shots | **NOT-BUILDABLE** | No stats feed in any season (0/711); shotmap empty in every season. No dev window, no trait, no line. |

**Nothing ships from KW-PremierLeague.** No arm passed all legs; no
predictions directory is shipped (deliberately — a FAIL at the dev
gate means the virgin is never read and nothing is predicted).

## What Jarvis should check specifically

1. Prereg-before-fitting order: prereg commit `c8988cf` (wip
   branch) predates every engine/results artifact in this folder's
   history.
2. Virgin discipline: `results_virgin.json` does NOT exist for any
   candidate — G-KW failed dev, so the virgin was never read.
   2026/2027 untouched (no engine reads any 2026/2027 row; the dev
   harness loads only 2021–2024/2025). Re-run reproduces
   results_dev.json exactly (md5 67e9e6f0ea63509fb13b64cb0f0a8d2e).
3. The BRIEF's dual-label caution, resolved with evidence: "2021"
   and "2021/2022" are DISTINCT seasons (0 shared match ids,
   disjoint date ranges Jan–May 2021 vs Nov 2021–Apr 2022, differing
   team sets) — Kuwait switched from a calendar to a split season
   mid-2021. Both are kept verbatim in the canonical season order;
   NO deduplication was applied because there is nothing to
   deduplicate (PREPROCESSING.md decision 1).
4. The BRIEF's "711 played" is the index row count: 69 index rows
   are unplayed fixtures (finished=false, started=false, index
   score placeholder "0-0"; 26/21/12/10 in the first four seasons).
   Played corpus = 642. This thinning is also the recorded
   diagnosis for the OU-leg failure: the model loses OU to
   climatology exactly in the fixture-thinned seasons and beats it
   on all three metrics in 2024/2025 (111/111 played).
5. X2 was KEPT pre-fitting (EDA F4): 8 dev entrant transitions,
   mean GF −0.390 (7/8 negative) / GA +0.404 (5/8 positive), rule
   recomputed from completed transitions before each season,
   clamped to [0.8, 1.25]. One documented port divergence: the
   entrant rule uses the frozen canonical season ORDER instead of
   integer-year arithmetic (split-season labels) — the rule itself
   is unchanged (PREREG_G_KW.md).
6. The halves constant is the thinnest in the programme: goals 1H
   share 0.4411 from 2024/2025 event matches only (87 matches, 297
   goals) because the event feed exists in dev only in that season.
   It is presentation-only and enters no gate.
7. Cards: the event feed records ONLY straight Reds (53 total);
   Yellow/YellowRed events are 0 in the whole corpus including the
   virgin and reserve (`analysis/eda_summary.json`,
   `event_cards_by_season`). K is not-buildable in the strongest
   form, as in CN.
