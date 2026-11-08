# RESULT — CN-LeagueOne [Muse-2]

Prereg frozen and pushed BEFORE any fitting: commit
`05c5870af4427871786759f7d1e6de31b548ae83` (branch
wip-cn-leagueone). Dev ≤ 2024; virgin = 2025 NOT read (G-CN failed
the dev gate); 2026 untouched. Gates exactly as pre-registered; none
moved.

## Verdicts

| Candidate | Verdict | Gate numbers |
|---|---|---|
| G-CN goals | **FAIL** (dev gate, OU leg) | Virgin not read. Dev pooled (n=786): DC Gate Zero 1X2 LL 1.0286 / RPS 0.2096 / OU LL 0.6927 vs climatology 1.0886 / 0.2293 / 0.6919 — passes 1X2 and RPS, fails OU2.5 (0.6927 > 0.6919) by 0.0007, carried by 2024 alone (model wins the OU leg in 2022 and 2023). Beats naive trailing-10 on all three (1.1995 / 0.2128 / 0.7680), but the gate requires beating BOTH baselines. SHRINK identical (n<6 never binds under season-blocked prediction). |
| S-CN SOT | **NOT-BUILDABLE** | No stats feed in any season (0/1,572). No dev window, no trait, no line. |
| C-CN corners | **NOT-BUILDABLE** | No stats feed in any season (0/1,572). No dev window, no trait, no line. |
| K-CN cards | **NOT-BUILDABLE** | No stats yellows in any season; plain Yellow events 0 in all 1,572 matches (target never exists — strongest K not-buildable case in the program); referee named in 0/1,572 matches (no X8 arm). |
| T-CN total shots | **NOT-BUILDABLE** | No stats feed in any season (0/1,572). No dev window, no trait, no line. |

**Nothing ships from CN-LeagueOne.** No arm passed all legs; no
predictions directory is shipped (deliberately — cf. the CH
precedent: a FAIL at the dev gate means the virgin is never read and
nothing is predicted).

## What Jarvis should check specifically

1. Prereg-before-fitting order: prereg commit `05c5870` (wip
   branch) predates every engine/results artifact in this folder's
   history.
2. Virgin discipline: `results_virgin.json` does NOT exist for any
   candidate — G-CN failed dev, so the virgin was never read.
   2026 untouched (no engine reads any 2026 row).
3. The dev-gate failure is the same mode as the FI reference
   itself (G-FI: Gate Zero OU 0.7231 vs climatology 0.6921, FAIL dev
   gate OU leg) and NO (0.6835 vs 0.6501) — but the narrowest miss
   in the program so far (0.0007 pooled, 2024 alone). Diagnosis in
   `reports/G_CN_VERDICT.md`: fitted mu falls 1.362 → 1.328 →
   1.219 across the three dev fits; predicted totals 2.35 / 2.25 /
   2.32 vs actual 2.61 / 2.26 / 2.48. No post-hoc repair was
   attempted.
4. The X2 entrant offset was DROPPED pre-fitting (EDA F4): 15 dev
   entrant transitions, mean GF +0.095 / GA −0.034, median −0.042 /
   −0.065, mixed signs — no systematic tilt. Arms are Gate Zero +
   SHRINK only.
5. The cards target choice: no K model was built — not because the
   event target breaks across eras (as in NO) but because plain
   Yellow events never occur in any season (0 in 1,572 matches).
   Evidence in `analysis/eda_summary.json`
   (`event_cards_by_season`) and EDA F5.
6. Format facts: single group every season (FotMob leagueName
   "China League"); the league shrank after 2022 (18 teams / 34
   rounds / 306 matches in 2021–2022; 16 teams / 30 rounds / 240
   matches from 2023). Three awarded matches, all in 2022
   (3892074, 3892065, 3946586), kept as ordinary flagged rows.
   Bundle note: the release tarball carries JSONs under
   `China/China League One/<season>/` (no
   `data_enrichment/fotmob_world/` prefix); files were moved into
   the warehouse layout at extraction, content untouched.
